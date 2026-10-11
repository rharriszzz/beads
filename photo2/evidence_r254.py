"""Stage-by-stage review artifacts. All rejected templates remain labeled rejected."""
import argparse,csv,json,math,os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-r254-mpl")
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from pattern_r254 import OUT,OLD,diagnostic,propagate
import global_fit_r253 as old
from camera_r254 import Model,rays,maker_chart
from alternatives_r254 import solve
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COL={'R':'#e63832','Y':'#ffe34b','B':'#111111','?':'#cccccc','!':'#be6fc7'}

def load_models(out):
    mm={m['model_id']:m for f in ['camera-results.json','extended-results.json'] for m in json.loads((out/f).read_text())}
    return list(mm.values())

def evaluate(out):
    models=load_models(out);summaries=[];evaluations=[];proofs=[];ledgers=[]
    for m in models:
        mid=m['model_id'];rr=json.loads((out/f'{mid}-assignments.json').read_text());n=m['n'];periods=[P for P in range(1,400) if n%P==0 and P%13]
        allscan=[diagnostic(rr,P,n) for P in periods];unique=[r for r in rr if r['conditional_unique']];uscan=[diagnostic(unique,P,n) for P in periods];train=[r for r in rr if r['split']=='train' and r['conditional_unique']];tscan=[diagnostic(train,P,n) for P in periods]
        # Complexity is explicit: choose shortest P among equal contradiction
        # counts; never call a longer, sparsely constrained partial strip recovered.
        best=min(allscan,key=lambda d:(d['minimum_conflicting_assignments'],d['P']));ubest=min(uscan,key=lambda d:(d['minimum_conflicting_assignments'],d['P']));selected=min(tscan,key=lambda d:(d['minimum_conflicting_assignments'],d['P']))
        outs=[]
        for r in rr:
            if r['split']!='test':continue
            pred=selected['template'][r['k']%selected['P']];actual=r['color'][0].upper();status='correct' if pred==actual else 'wrong' if pred in 'RYB' else 'abstain'
            outs.append(dict(observation_id=r['observation_id'],x=r['x'],y=r['y'],k=r['k'],residue=r['k']%selected['P'],predicted=pred,actual=actual,status=status,ownership=r['owns_representative'],conditional_unique=r['conditional_unique']))
        evaluation=dict(model_id=mid,P=selected['P'],train_conflicts=selected['minimum_conflicting_assignments'],train_template=selected['template'],determined=sum(selected['template'].count(c) for c in 'RYB'),unknown=selected['unknown'],conflicted=selected['conflict_residues'],correct=sum(r['status']=='correct' for r in outs),wrong=sum(r['status']=='wrong' for r in outs),abstain=sum(r['status']=='abstain' for r in outs),outcomes=outs)
        evaluations.append(evaluation)
        metrics=m['metrics'];summaries.append(dict(model_id=mid,N=n,h=m['h'],focal=m['focal'],turn_delta=m.get('turn_delta',0),geometry_train=metrics['train']['geometry_cost'],geometry_test=metrics['test']['geometry_cost'],anchor_owned=metrics['anchor_owned'],chart_owned=metrics['chart_owned'],chart_heldout=metrics['chart_holdout_owned'],star_retained=metrics['star_identity_retained'],star_total=metrics['star_total'],representatives_owned=metrics['train']['ownership']+metrics['test']['ownership'],admissible_periods=';'.join(map(str,periods)),P_all=best['P'],conflicts_all=best['minimum_conflicting_assignments'],P_unique=ubest['P'],conflicts_unique=ubest['minimum_conflicting_assignments'],unique_n=len(unique),P_train=selected['P'],train_conflicts=selected['minimum_conflicting_assignments'],holdout_correct=evaluation['correct'],holdout_wrong=evaluation['wrong'],holdout_abstain=evaluation['abstain'],changed_indices=metrics['changed_indices']))
        for r in rr:ledgers.append(dict(model_id=mid,observation_id=r['observation_id'],color=r['color'],old_k=r['old_k'],new_k=r['k'],changed=r['index_changed'],patch_support=r['patch_support'],owns_representative=r['owns_representative'],cost=r['exact_audit_cost']))
        for delta in [.15,.5,1.]:
            domains=[[a['k'] for a in r['alternatives'] if a['exact_audit_cost']<=r['exact_audit_cost']+delta+1e-12] for r in rr]
            for P in periods:
                result=propagate(rr,domains,P);record=dict(model_id=mid,P=P,delta_cost=delta,status=result['status'],witness=result['witness'])
                if result['status']=='unresolved':
                    record['solver']=solve(rr,result['domains'],P);record['status']='infeasible' if record['solver']['status']==2 else 'optimistic_feasible' if 'indices' in record['solver'] else 'bounded_unsolved'
                proofs.append(record)
    old.table(out/'comparison.csv',summaries);old.table(out/'index-changes.csv',ledgers);old.save(out/'refined-heldout.json',evaluations);old.save(out/'refined-alternative-proofs.json',proofs)
    return models,summaries,evaluations


def figures(out,models,summary,evaluations):
    selected=json.loads((OLD/'selected.json').read_text());fixed=list(csv.DictReader((out/'fixed-periods.csv').open()));photo=Image.open(old.ROOT/'beads-photo-2.jpg').convert('RGB')
    fig,axes=plt.subplots(2,1,figsize=(13,9))
    for mid in selected:
        rr=[r for r in fixed if r['model_id']==mid and r['subset']=='unique'];xx=[int(r['P']) for r in rr];yy=[int(r['minimum_conflicting_assignments']) for r in rr]
        axes[0].plot(xx,yy,lw=.9,label=mid)
        admiss=[r for r in rr if r['admissible_by_maker']=='True'];axes[1].scatter([int(r['P']) for r in admiss],[int(r['minimum_conflicting_assignments']) for r in admiss],label=mid)
    axes[0].set(title='A: exhaustive fixed-mapping diagnostic — all P, including excluded combinations',ylabel='Minimum contradictory assignments');axes[0].legend(fontsize=8,ncol=2)
    axes[1].set(title='Only P dividing N and P not divisible by 13 are admissible',xlabel='Repeat period P',ylabel='Minimum contradictory assignments');axes[1].legend(fontsize=8,ncol=2)
    fig.tight_layout();fig.savefig(out/'A-period-conflicts.png',dpi=170);plt.close(fig)
    # Explicitly nominate by training geometry, not by heldout/color outcome.
    nominees=[]
    for h in [1,-1]:
        ss=[r for r in summary if r['h']==h and r['anchor_owned'] and r['admissible_periods']!='1']
        nominees.append(min(ss,key=lambda r:r['geometry_train'])['model_id'])
    # Post-hoc color leader is a diagnostic, never independent validation.
    colorleader=min((r for r in summary if r['anchor_owned'] and r['admissible_periods']!='1'),key=lambda r:(r['conflicts_all'],r['P_all']))['model_id']
    display=list(dict.fromkeys(nominees+[colorleader,'N2670_h+1_f0','N2679_h-1_f0']))
    old.save(out/'display-selection.json',dict(training_geometry_nominees=nominees,posthoc_color_diagnostic=colorleader,display=display))
    # Residue strip + full exact constraint CSV; purple conflicts are not colors.
    fig,axes=plt.subplots(len(display),1,figsize=(15,2.2*len(display)),squeeze=False);constraints=[];coverage=[];conflict_examples=[]
    for ax,mid in zip(axes[:,0],display):
        m=next(m for m in models if m['model_id']==mid);s=next(s for s in summary if s['model_id']==mid);rr=json.loads((out/f'{mid}-assignments.json').read_text());d=diagnostic(rr,s['P_all'],m['n']);P=d['P'];byid={r['observation_id']:r for r in rr}
        array=np.array([to_rgb(COL[c]) for c in d['template']]).reshape(1,P,3);ax.imshow(array,aspect='auto',extent=(-.5,P-.5,0,1));ax.set_yticks([]);ax.set_xlim(-.5,P-.5);ax.set_title(f"{mid}, P={P}: REJECTED, {d['minimum_conflicting_assignments']} contradictions; {d['unknown']} unknown residues",fontsize=10)
        for residue,group in enumerate(d['groups']):
            status=d['template'][residue];constraints.append(dict(model_id=mid,P=P,residue=residue,status=status,red_observation_ids=';'.join(group['red']),yellow_observation_ids=';'.join(group['yellow']),black_observation_ids=';'.join(group['black']),admitted_colors='red;yellow;black' if status=='?' else '' if status=='!' else next(c for c in group if group[c]),inconsistent_template=True))
            ks=[r['k'] for r in rr if r['k']%P==residue];coverage.append(dict(model_id=mid,P=P,residue=residue,observations=len(ks),k_values=';'.join(map(str,ks)),k_mod13=';'.join(map(str,sorted({k%13 for k in ks}))),gcd_P_13=math.gcd(P,13),model_repeat_instances=len(range(residue,m['n'],P)),status=status))
            if status=='!' and len([x for x in conflict_examples if x['model_id']==mid])<2:
                conflict_examples.append(dict(model_id=mid,P=P,residue=residue,red=byid[group['red'][0]],yellow=byid[group['yellow'][0]]))
    fig.suptitle('B: residue evidence, NOT surviving templates — red / yellow / gray ? / purple conflict !',fontsize=13);fig.tight_layout(rect=[0,0,1,.97]);fig.savefig(out/'B-rejected-residue-strips.png',dpi=170);plt.close(fig)
    old.table(out/'residue-constraints.csv',constraints);old.table(out/'residue-coverage.csv',coverage);old.save(out/'conflict-examples.json',conflict_examples)
    fig,axes=plt.subplots(1,2,figsize=(14,6))
    for h,marker in [(1,'o'),(-1,'^')]:
        rr=[r for r in summary if r['h']==h and r['admissible_periods']!='1'];axes[0].scatter([r['geometry_train'] for r in rr],[r['conflicts_all'] for r in rr],s=30,marker=marker,label=f'h={h:+d}',alpha=.65)
        axes[1].scatter([r['geometry_train'] for r in rr],[r['geometry_test'] for r in rr],s=30,marker=marker,label=f'h={h:+d}',alpha=.65)
    for mid in display:
        s=next(s for s in summary if s['model_id']==mid);axes[0].annotate(mid,(s['geometry_train'],s['conflicts_all']),fontsize=6)
    axes[0].set(xlabel='Training geometry cost (lower better)',ylabel='All-310 minimum admissible color contradictions',title='C: separate geometry and pattern costs');axes[1].set(xlabel='Training geometry cost',ylabel='Heldout geometry cost',title='Same spatial holdouts for every model')
    for ax in axes:ax.legend()
    fig.tight_layout();fig.savefig(out/'C-geometry-pattern.png',dpi=170);plt.close(fig)
    for mid in display:
        m=next(m for m in models if m['model_id']==mid);rr=json.loads((out/f'{mid}-assignments.json').read_text());model=Model(m['n'],m['h'],m['p'],m['focal'],m.get('turn_delta',0));geom=model.geometry(np.arange(m['n']))
        im=photo.copy();draw=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,13)
        for r in rr:
            x,y=r['x'],r['y'];cx,cy=r['projected_center'];color=COL[r['color'][0].upper()]
            draw.line((x,y,cx,cy),fill='white',width=1);draw.line((cx-3,cy,cx+3,cy),fill='cyan',width=1);draw.line((cx,cy-3,cx,cy+3),fill='cyan',width=1)
            draw.ellipse((x-5,y-5,x+5,y+5),outline=color,width=2);label=f"{r['k']}"+('!' if not r['owns_representative'] else '')
            draw.text((x+6,y-14),label,font=font,fill=color,stroke_width=1,stroke_fill='black')
        draw.rectangle((0,0,2540,76),fill='white');draw.text((15,12),mid+' | model-conditional k; observed R/Y rings; calculated center +; ! = failed ownership',font=ImageFont.truetype(FONT,23),fill='black');draw.text((15,43),'No recovered repeating sequence. Full native 2540 x 3182 photograph.',font=ImageFont.truetype(FONT,21),fill='black');im.save(out/f'{mid}-indexed-photo.png')
        # Raw and exact local ownership near the known graph, including point 7.
        box=(1160,210,1470,410);xx,yy=np.meshgrid(np.arange(box[0],box[2],2),np.arange(box[1],box[3],2));own,_,un=rays(model,np.c_[xx.ravel(),yy.ravel()],geom);own=own.reshape(xx.shape);chart=maker_chart();target={r['maker_number']:(m['origin']+r['k_'+m['chart_family']])%m['n'] for r in chart}
        fig,axs=plt.subplots(1,2,figsize=(13,5));extent=(box[0],box[2],box[3],box[1])
        for ax in axs:ax.imshow(photo.crop(box),extent=extent);ax.set_xlim(box[0],box[2]);ax.set_ylim(box[3],box[1])
        axs[0].set_title('Raw photograph: maker-chart region');axs[1].set_title(mid+' — exact surface ownership, 2px display grid')
        for r in chart:
            k=target[r['maker_number']];mask=(own==k).astype(float);axs[1].contour(xx,yy,mask,levels=[.5],colors=['cyan'],linewidths=.5) if mask.any() else None
            test=next(x for x in m['metrics']['chart_records'] if x['maker_number']==r['maker_number']);color='lime' if test['owned'] else 'magenta';axs[1].plot(r['x'],r['y'],'+',color=color,ms=7);axs[1].text(r['x']+2,r['y']-2,str(r['maker_number']),color=color,fontsize=7,bbox=dict(facecolor='black',alpha=.45,pad=.2))
        fig.suptitle('D: known identities — green point owned; magenta fails; contours are computed surface boundaries',fontsize=11);fig.tight_layout();fig.savefig(out/f'{mid}-maker-ownership.png',dpi=160);plt.close(fig)
    # Raw-vs-marked conflict witnesses for a leading near-count model.
    for mid in [colorleader,'N2670_h+1_f0']:
        cases=[r for r in conflict_examples if r['model_id']==mid][:2]
        if not cases:continue
        m=next(m for m in models if m['model_id']==mid);model=Model(m['n'],m['h'],m['p'],m['focal'],m.get('turn_delta',0));geom=model.geometry(np.arange(m['n']));pc=model.view.project(geom['centers'])
        fig,axs=plt.subplots(2*len(cases),2,figsize=(17,5*len(cases)),squeeze=False)
        for j,case in enumerate(cases):
            for z,color in enumerate(['red','yellow']):
                r=case[color];x,y=r['x'],r['y'];box=(int(x)-90,int(y)-65,int(x)+90,int(y)+65);extent=(box[0],box[2],box[3],box[1])
                for ax in axs[2*j+z]:ax.imshow(photo.crop(box),extent=extent);ax.set_xlim(box[0],box[2]);ax.set_ylim(box[3],box[1])
                axs[2*j+z,0].set_title(f"Raw {r['observation_id']} ({color})",fontsize=9)
                ax=axs[2*j+z,1];ax.plot(x,y,'o',mfc='none',mec='lime',ms=9)
                for ai,a in enumerate(r['alternatives']):
                    cx,cy=pc[a['generator_index']];ax.plot(cx,cy,'+',color='cyan');ax.text(cx+3,cy,chr(65+ai),color='white',fontsize=8,bbox=dict(facecolor='black',alpha=.5,pad=.2))
                    ax.text(1.02,.94-ai*.22,f"{chr(65+ai)}: k={a['k']}\npatch {a['patch_support']:.0%}; owns point: {a['owns_representative']}",transform=ax.transAxes,fontsize=8,va='top')
                ax.set_title(f"P={case['P']}, shared residue {case['residue']}; assigned k={r['k']}",fontsize=9)
        fig.suptitle('E: conflicting observed colors and four nearby index alternatives — + is a calculated center',fontsize=12);fig.tight_layout();fig.savefig(out/f'{mid}-conflict-crops.png',dpi=180);plt.close(fig)
    # Honest heldout visual: template derived only from training unique points,
    # with conflicted/unknown residues abstaining. These templates are rejected.
    fig,axs=plt.subplots(1,2,figsize=(11,7))
    for ax,mid in zip(axs,nominees):
        e=next(e for e in evaluations if e['model_id']==mid);ax.imshow(photo);ax.axis('off')
        for status,c,marker in [('correct','lime','o'),('wrong','magenta','x'),('abstain','cyan','s')]:
            rr=[r for r in e['outcomes'] if r['status']==status];style={'color':c} if marker=='x' else {'facecolors':'none','edgecolors':c};ax.scatter([r['x'] for r in rr],[r['y'] for r in rr],s=25,marker=marker,label=f"{status}: {len(rr)}",**style)
        ax.set_title(f"{mid}, train P={e['P']}\nREJECTED: {e['train_conflicts']} training contradictions",fontsize=9);ax.legend(fontsize=7,loc='center')
    fig.suptitle('F: heldout prediction audit — no majority vote, conflicted/unknown residues abstain',fontsize=11);fig.tight_layout();fig.savefig(out/'F-heldout-map.png',dpi=180);plt.close(fig)
    # No logically valid template exists. Show the requested prediction map
    # without pretending that unconflicted fragments of an inconsistent theory
    # entail photographed or recovered colors.
    mid=nominees[0];m=next(m for m in models if m['model_id']==mid);model=Model(m['n'],m['h'],m['p'],m['focal'],m.get('turn_delta',0));g=model.geometry(np.arange(m['n']));pc=model.view.project(g['centers']);fig,ax=plt.subplots(figsize=(8,10));ax.scatter(pc[:,0],pc[:,1],s=2,c='#999999');ax.invert_yaxis();ax.set_aspect('equal');ax.set_title('G: template prediction status — all colors unknown\nNo viable template; gray calculated centers include hidden beads');ax.set(xlabel='Native image x',ylabel='Native image y');fig.tight_layout();fig.savefig(out/'G-prediction-status.png',dpi=170);plt.close(fig)
    old.table(out/'template-prediction-status.csv',[dict(model_id=mid,k=int((i-m['origin'])%m['n']),x=float(x),y=float(y),predicted_color='?',reason='no_viable_template') for i,(x,y) in enumerate(pc)])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();models,ss,ee=evaluate(a.output);figures(a.output,models,ss,ee)
