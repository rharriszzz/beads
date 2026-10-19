"""Matched color/association comparisons and bounded renewed pattern discovery."""
import argparse,time,copy,csv
from collections import Counter
from pathlib import Path
from .common import *
from photo2.r333.common import spatial_keys,cross_predict,score
from photo2.r331.analyze import evaluate,motif_entries
from photo2.r330.pattern import scan,dataset as saved_dataset
from photo2.r329.common import canonical
PERIODS=[104]+list(range(200,400))

def copies_prediction(ids,co,obs,blocks):
    ix={o:i for i,o in enumerate(ids)};occ={tuple(v):o for o,v in co.items()};rows=[]
    for o in ids:
        block=int(blocks[ix[o]]);examples=[]
        for mul in range(-15,16):
            if not mul:continue
            z=occ.get(tuple(np.array(co[o])+mul*np.array([16,16])))
            if z and int(blocks[ix[z]]) not in [(block-1)%12,block,(block+1)%12]:examples.append(z)
        cc=Counter(obs[z]['color'] for z in examples);win,num=cc.most_common(1)[0] if cc else ('?',0);sections={int(blocks[ix[z]]) for z in examples if obs[z]['color']==win};strong=num>=3 and len(sections)>=3 and num/max(len(examples),1)>=.8
        rows.append(dict(id=o,original=obs[o]['color'],prediction=win if strong else '?',support=num,examples=examples,strong=strong,disagreement=bool(strong and win!=obs[o]['color'])))
    return rows

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();import photo2.r333.spirals as spiral;import photo2.r333.staircases as staircase
    old_spiral_dataset=spiral.dataset;old_stair_dataset=staircase.dataset;old_artifact=staircase.artifact;layers=[];full=[];motifs=[];alltraces={};stageroot=out
    for layer in ['raw','color','relocated','provisional']:
        g,obs,co,ids,ab,c,w,b,station=reviewed_dataset(layer);this=stageroot/layer;this.mkdir()
        # Reuse the historical algorithms in memory; every output path is NEW.
        # Frozen R333 source/results are never changed.
        spiral.dataset=lambda layer=layer:reviewed_dataset(layer);spiral.run(this/'spirals',controls=0)
        staircase.dataset=lambda layer=layer:reviewed_dataset(layer);staircase.artifact=lambda path:this/path;staircase.run(this/'staircases',trials=0)
        sp=read(this/'spirals/spirals.json.gz');st=read(this/'staircases/staircases.json.gz');pred=copies_prediction(ids,co,obs,b);breaks=[r for r in pred if r['disagreement']];alltraces[layer]=st['traces']
        baseline=read(ROOT/'photo2/r333/diagnosis/diagnosis.json.gz')['breaks'];remaining=[];resolved=[]
        for r in baseline:
            now=next(x for x in pred if x['id']==r['id']);change=dict(id=r['id'],before_color=r['original'],after_color=obs[r['id']]['color'],frozen_expectation=r['prediction'],relearned=now)
            (resolved if obs[r['id']]['color']==r['prediction'] else remaining).append(change)
        for fam,wt in [('A',[7,6]),('B',[6,7])]:
            k=ab@wt;N=int(np.dot(g['H'],wt))
            for p in PERIODS:
                r=evaluate(k,c,w,b,p);full.append(dict(r,layer=layer,family=fam,N=N,cyclic=N%p==0,maker=200<=p<=399 and p%13!=0))
            for guard in [0,1]:full.append(dict(evaluate(k,c,w,b,208,parent=104,guard=guard),layer=layer,family=fam,N=N,cyclic=N%208==0,maker=False))
            for p in ([104,208,306] if fam=='A' else [207,299,305]):
                entries=motif_entries(ids,k,c,w,b,p);motifs.append(dict(layer=layer,family=fam,period=p,N=N,cyclic=N%p==0,known=sum(e['color']!='?' for e in entries),unknown=sum(e['color']=='?' for e in entries),unobserved=sum(not e['observations'] for e in entries),entries=entries))
        layers.append(dict(layer=layer,indexed=len(ids),recorded=len(obs),colors=dict(Counter(obs[o]['color'] for o in ids)),pixel_locations_changed=int(layer in ['relocated','provisional']),lattice_coordinates_changed=0,links_changed=0,flexible_coverage=sp['coverage'],regular_coverage=st['coverage'],selected_models=st['selected_models'],guarded_predictions=pred,breaks=breaks,resolved_R333_breaks=resolved,remaining_R333_breaks=remaining,translation16=next(r for r in sp['translations'] if r['delta_ab']==[16,16])))
        print('LAYER',layer,'breaks',len(breaks),'resolved',len(resolved),'motif208',motifs[-6]['known'] if False else next(x['known'] for x in motifs if x['layer']==layer and x['family']=='A' and x['period']==208),flush=True)
    spiral.dataset=old_spiral_dataset;staircase.dataset=old_stair_dataset;staircase.artifact=old_artifact
    # Primary final inference excludes every automatic proposal. Reweighting
    # sensitivity is separate from the exactly matched R333-weight comparison.
    g,obs,co,ids,ab,c,w,b,station=reviewed_dataset('relocated');lookup={o:i for i,o in enumerate(ids)};_,states,*_=saved_dataset();names=sorted(canonical(states['working']));ii=np.array([lookup[o] for o in names]);scans=[];compatible=[];maps=[]
    for name,state in states.items():
        coord=canonical(state);present=np.array([o in coord for o in names]);aa=np.array([coord.get(o,(0,0)) for o in names])
        for fam,wt in [('A',[7,6]),('B',[6,7])]:
            k=aa@wt;N=int(np.dot(state['H'],wt));key=name+'-'+fam;ranking=scan(k[present],c[ii][present],w[ii][present],b[ii][present],PERIODS);scans.append(dict(map=key,H=state['H'],N=N,ranking=ranking));maps.append((key,k,present,N))
            for p in PERIODS:
                if p%13 and N%p==0:compatible.append(dict(evaluate(k,c[ii],w[ii],b[ii],p,present),map=key,N=N))
    # All cached coherent G replays retain their own maps and original cohort.
    G=[]
    for j,row in enumerate(read(ROOT/'photo2/r330/photography/g-replays.json.gz')[-1]['candidates']):
        coord=canonical(row['state']);present=np.array([o in coord for o in names]);aa=np.array([coord.get(o,(0,0)) for o in names])
        for fam,p,parent in [('A',208,104),('A',306,None),('B',207,None),('B',305,None)]:G.append(dict(evaluate(aa@([7,6] if fam=='A' else [6,7]),c[ii],w[ii],b[ii],p,present,parent),G=j,family=fam,H=row['state']['H']))
    # Other global family conventions preserve triangular adjacency but may
    # change which observed family is string-step1. Treat as diagnostics, checking
    # duplicate sequence occupancy and the frozen R161 direction references.
    family_diagnostics=[]
    for wt in [[7,1],[1,7],[6,-1],[-1,6]]:
        k=ab@wt;N=abs(int(np.dot(g['H'],wt)));ranking=scan(k,c,w,b,PERIODS);duplicates=len(k)-len(set((k%N).tolist()));rows=[]
        for p in sorted(set([r['period'] for r in ranking[:3]]+[p for p in range(200,400) if p%13 and N%p==0])):rows.append(dict(evaluate(k,c,w,b,p),N=N,cyclic=N%p==0,maker=p%13!=0))
        family_diagnostics.append(dict(weights=wt,N=N,duplicate_indices=duplicates,ranking=ranking,heldout=rows,changes_which_family_is_step1=True,adopted=False,reason='Different primitive-family/stringing convention; cannot override established R161 direction references or duplicate physical indices.'))
    # A tempting repeat-derived index transformation: shift an entire diagonal
    # stripe after every(16,16) repeat. Test all16 cuts; KEEP integer-edge audit.
    # It maps spatial208 toward207, but violating an actual edge forbids adoption.
    transforms=[]
    A=ab@[7,6]
    for cut in range(16):
        offset=np.floor_divide(ab[:,0]-cut,16);aa=ab+np.c_[-offset,offset];k=aa@[7,6];violations=[];duplicates=[];occupied={}
        for i,o in enumerate(ids):
            key=tuple(aa[i]);other=occupied.get(key)
            if other:duplicates.append([other,o])
            occupied[key]=o
        for e in g['edges']:
            old=ab[lookup[e['target']]]-ab[lookup[e['source']]];new=aa[lookup[e['target']]]-aa[lookup[e['source']]]
            if not np.array_equal(old,new):violations.append(dict(source=e['source'],target=e['target'],old_delta=old.tolist(),new_delta=new.tolist()))
        r=evaluate(k,c,w,b,207);transforms.append(dict(cut=cut,**r,boundary_links_changed=len(violations),violations=violations,duplicate_lattice_sites=duplicates,conditional_N=2691,cyclic=2691%207==0,adopted=False,reason='Repeat-based whole-stripe index compression is a counterfactual; changed primitive equations/duplicate sites prevent adoption.'))
    sensitivities=[]
    for blackweight in [.25,.55,1.]:
        ww=np.where(c==2,blackweight,1.);ww[np.array(['provisional' in str(obs[o]).lower() for o in ids])]=.25
        for fam,p,parent in [('A',208,104),('A',306,None),('B',207,None),('B',305,None)]:sensitivities.append(dict(evaluate(ab@([7,6] if fam=='A' else [6,7]),c,ww,b,p,parent=parent,guard=1),family=fam,black_weight=blackweight))
    # Controlled continuation comparisons at frozen starting sites/template phases
    # separate a color repair's local path effect from path-cover reselection.
    continuation=[]
    for trace in alltraces['raw']:
        o=trace['ids'][0];oldset=set(trace['ids']);matches=[]
        for new in alltraces['relocated']:
            if new['palette']==trace['palette'] and len(oldset&set(new['ids']))>=max(3,len(oldset)//2):matches.append(dict(trace=new['id'],length=new['length'],shared=len(oldset&set(new['ids'])),new_nodes=[q for q in new['ids'] if q not in oldset]))
        continuation.append(dict(before=trace['id'],before_length=trace['length'],palette=trace['palette'],best_matches=sorted(matches,key=lambda r:(-r['shared'],-r['length']))[:3]))
    # Correlation-preserving null with full40-map development selection, bounded
    # nine trials; report both original diagnostic and maker-eligible winners.
    rng=np.random.default_rng(334);null=[]
    for trial in range(9):
        shifts=rng.integers(0,64,12)*13;best=None;maker=None
        for key,k,present,N in maps:
            ranking=scan((k+shifts[b[ii]])[present],c[ii][present],w[ii][present],b[ii][present],PERIODS)
            r=dict(ranking[0],map=key);mr=dict(next(x for x in ranking if x['period']%13),map=key)
            if best is None or r['selection_score']>best['selection_score']:best=r
            if maker is None or mr['selection_score']>maker['selection_score']:maker=mr
        null.append(dict(trial=trial,best=best,best_maker=maker))
    result=dict(layers=layers,period_fits=full,motifs=motifs,saved_map_scans=scans,compatible_saved_maps=sorted(compatible,key=lambda r:-r['gain_nats']),G=G,family_diagnostics=family_diagnostics,repeat_derived_stripe_transforms=transforms,sensitivities=sensitivities,continuation=continuation,nulls=null,seconds=time.perf_counter()-t,policy='Raw/color-only/relocated/provisional layers share IDs, lattice coordinates, links, original R333 weights and geography. Only maker-reviewed layer is authoritative. Association movement changes image location, not lattice indices. No count, period or row transform adopted.')
    save(out/'analysis.json.gz',result)
    with (out/'periods.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,['layer','family','period','parent','guard','N','cyclic','maker','gain_nats','gain_over_phase13','agreement'],extrasaction='ignore',lineterminator='\n');wr.writeheader();wr.writerows(full)
    save(out/'summary.json',dict(layers=[{k:v for k,v in x.items() if k not in ['guarded_predictions','breaks','resolved_R333_breaks','remaining_R333_breaks']}|dict(observed_breaks=len(x['breaks']),resolved_R333_breaks=len(x['resolved_R333_breaks'])) for x in layers],strongest_maker=sorted([r for r in full if r['layer']=='relocated' and r['maker']],key=lambda r:-r['penalized_gain'])[:8],best_compatible=sorted(compatible,key=lambda r:-r['gain_nats'])[:5],seconds=result['seconds']))
    print('ANALYSIS seconds',result['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
