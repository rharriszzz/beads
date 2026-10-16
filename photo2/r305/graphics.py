"""Native-photo diagnostic crops and unsmoothed reflection plots; no synthetic photo."""
import os,json,textwrap
os.environ.setdefault('MPLCONFIGDIR','/tmp/r305-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .model import *
from photo2.r297.common import save
from photo2.r302.experiment import clean
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def main():
    for name in FAMILIES:
        corr=read(BASE/f'results/{name}-correspondences.json');rr=[q for q in corr['records'] if q['index'] is not None];groups=corr['groups'];rolling=corr['rolling']
        for signed in [False,True]:
            fig,axs=plt.subplots(2 if signed else 3,1,figsize=(14,8),sharex=True,constrained_layout=True,gridspec_kw={'height_ratios':[3,1] if signed else [3,1,1]})
            for strong,status,marker,col in [(True,'confident conditional','o','#168366'),(True,'ambiguous','o','#bd6818'),(False,'ambiguous','^','#9654b5')]:
                rows=[r for r in rr if r['strong']==strong and r['status']==status]
                if signed:
                    for field,color in [('tangent_px','#bc4c28'),('normal_px','#257fa8')]:axs[0].scatter([r['index'] for r in rows],[r[field] for r in rows],s=20,marker=marker,c=color,alpha=.6,label=f'{field[:-3]} / {"strong" if strong else "weak"} / {status}')
                else:axs[0].scatter([r['index'] for r in rows],[r['error_px'] for r in rows],s=25,marker=marker,c=col,alpha=.8,label=f'{"strong" if strong else "weak"} / {status}')
            if not signed:
                for field,col in [('median','#9b4095'),('rms','#2368b0')]:axs[0].plot([r['index'] for r in rolling],[r[field] if r['n']>=3 else np.nan for r in rolling],color=col,lw=1,label=f'±25 index rolling {field} (n≥3)')
                for g in groups:
                    rows=[r for r in rr if r['strong'] and g['first']<=r['index']<=g['last']]
                    if len(rows)>=3:axs[0].hlines(np.mean([r['error_px'] for r in rows]),g['first'],g['last'],color='#555',lw=1);axs[0].text((g['first']+g['last'])/2,37,f'n={len(rows)}',fontsize=7,ha='center')
                axs[1].plot([r['index'] for r in rolling],[r['n'] for r in rolling],color='#2368b0',label='Strong contributing pairs / rolling window');axs[1].legend(fontsize=8);axs[1].set_ylabel('Rolling n')
            else:axs[0].axhline(0,color='#333',lw=.7)
            last=axs[-1];gx=[(g['first']+g['last'])/2 for g in groups]
            for key,label,col in [('unmatched_observations','Unmatched observed','#b04d39'),('unmatched_predictions','Unassigned predicted','#8652a5'),('no_predicted_reflection','Visible bead / no lobe','#276888'),('occluded','Occluded','#777')]:last.plot(gx,[g[key] for g in groups],'-o',ms=3,c=col,label=label)
            last.legend(fontsize=8,ncol=2);last.set_ylabel('Count / group');last.set_xlabel('Conditional bead_index (S1 origin, not R294 origin)');axs[0].set_ylabel('Signed residual (native px)' if signed else 'Reflection error magnitude (native px)');axs[0].legend(fontsize=8,ncol=2);axs[0].set_ylim((-40,40) if signed else (0,40))
            for ax in axs:
                ax.set_xlim(FIRST,LAST);ax.grid(alpha=.2)
                for g in groups:
                    if g['insufficient_evidence']:ax.axvspan(g['first'],g['last'],color='#bbb',alpha=.3)
            fig.suptitle(f'{name}: fixed continuous geometry; individual global pairs\nGray: fewer than3 strong observations. Curves descriptive only; gaps are not zero errors.',fontsize=12)
            suffix='signed-errors' if signed else 'errors-index';fig.savefig(REVIEW/f'{name}-{suffix}.png',dpi=150);fig.savefig(BASE/f'results/{name}-{suffix}.svg');plt.close(fig)
            svg=BASE/f'results/{name}-{suffix}.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    primary=read(BASE/'results/primary.json.gz');core=[b for b in primary['positions'] if b['displayed']];by={b['index']:b for b in core};corr=read(BASE/'results/primary-correspondences.json');rr=corr['records'];material=read(BASE/'results/primary-material.json.gz');red=[r for r in read(BASE/'results/starting-red-diagnosis.json') if r['model']=='primary'];photo=Image.open(REVIEW/'photo.png').convert('RGB');gallery=[]
    cases=[]
    for r in red:
        cases.append((r['index'],r['id'],f"Saved red interior: {r['assigned_fraction']:.1%} assigned, {r['other_fraction']:.1%} another owner, {r['outside_fraction']:.1%} outside union. Magenta dashed: unobstructed model; white: uncertain interior edge. Interior coverage does not establish a full-bead contour.",r))
    cases[0]=(cases[0][0],cases[0][1],cases[0][2]+' Orange polygon: existing B15 uncertain outer contour;92.6% assigned,7.2% misses even the unobstructed bead. ±3px contour controls give76.0–99.7% coverage.',cases[0][3])
    cases.extend([(48,'First error increase / artificial splice','The4→12 radius quintic changes curvature and frame orientation. Pink boxes mark uncertified contacts. The diagnostic wider splice does not restore reflection agreement.',None),(140,'Top-region physical failure','Small optical residuals can coexist with intersecting solid beads. Pink boxes identify uncertified pairs; the bodies have not been repaired or removed.',None),(190,'Recovery after the early deterioration','A useful agreement control: strong errors recover around160–209. Recovery under an alignment with gaps is not proof of physical index identity.',None)])
    chosen=[k for k,_,_,_ in cases]
    for q in sorted([q for q in rr if q['strong'] and q['index'] is not None and q['index']>=330],key=lambda q:-q['error_px']):
        if all(abs(q['index']-k)>55 for k in chosen):
            cases.append((q['index'],'Large new reflection mismatch',f"{q['observation']}: {q['error_px']:.2f}px, tangent {q['tangent_px']:+.2f}, normal {q['normal_px']:+.2f}. {q['status']}; alternative owners remain inspectable.",None));chosen.append(q['index'])
        if len(cases)>=10:break
    cases.extend([(760,'Low reflection error / poor material coverage','Signed tangent slope here is+5.51px/50 addresses (7 strong pairs), unlike the abrupt next-group jump. Low residuals coexist with41.2% colored omission. Red dots: omitted frozen colored samples.',None),(580,'File seam / continued photographic trace','The stored closed trace wraps here without a phase or index reset. Inspect residuals and material coverage; the trace is not a calibrated physical axis.',None)])
    pg=max(corr['groups'],key=lambda g:g['paper_occupation'] or 0);cases.append(((pg['first']+pg['last'])//2,'Modeled surface on photographic paper',f"Group {pg['first']}…{pg['last']}: {pg['paper_occupation']:.1%} of frozen paper samples occupied. Magenta dots are occupied paper samples, not inferred bead colors.",None))
    sensitive=[q for q in rr if q['index'] is not None and not q['stable_across_gap_penalties'] and q['index']>330];q=max(sensitive,key=lambda q:q['error_px']);cases.append((q['index'],'Assignment-sensitive reflection',f"{q['observation']}: owners at gap costs12/24/48 are {q['penalty_owners']}. Orange/violet dashed arrows remain ambiguous. The selected path is not silently replaced by a closer owner.",None))
    unmatched=[q for q in rr if q['index'] is None];q=unmatched[-1];k=min(core,key=lambda b:abs(b['photo_arc']-q['photo_arc']))['index'];cases.append((k,'Unmatched observation / incomplete catalog',f"{q['observation']} is unpaired; white X marks its original coordinates. No error vector is invented. Unassigned modeled lobes are not proof of missing real reflections.",None))
    cases.append((830,'Sudden deterioration after recovery','Strong RMS rises from6.11px at760–809 to15.23px at810–859, then recovers again. This is a local jump, not uniform pitch drift.',None))
    cases.append((274,'Largest strong reflection displacement','RF70T-K-1965-0575:25.66px; tangent+17.50px, normal+18.78px. This original R304 failure persists exactly; the extension has not repaired or hidden it.',None))
    overview=photo.copy();od=ImageDraw.Draw(overview);font=ImageFont.truetype(FONT,18)
    for number,(k,title,caption,redrow) in enumerate(cases,1):
        center=np.array(redrow['point'] if redrow else by[k]['projected_center']);half=np.array([65,55] if redrow else [130,95]);lo=np.maximum([0,0],np.floor(center-half)).astype(int);hi=np.minimum(photo.size,np.ceil(center+half)).astype(int);box=(*lo,*hi);raw=photo.crop(box);scale=4 if redrow else 3;marked=raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST);draw=ImageDraw.Draw(marked)
        def p(xy):return tuple((np.array(xy)-lo)*scale)
        def line(seg,color,width=1):draw.line([p(seg[:2]),p(seg[2:])],fill=color,width=width)
        for b in core:
            if np.linalg.norm(np.array(b['projected_center'])-center)>220:continue
            for seg in b['boundary_segments']:line(seg,'#fff46b' if b['index']==k else '#40cbdc',2 if b['index']==k else 1)
            if b['uncertified_pairs']:
                x,y=p(b['projected_center']);draw.rectangle((x-7,y-7,x+7,y+7),outline='#ff2d91',width=2)
        if redrow:
            if redrow['id']=='C-1116-0328':
                polygon=source('primary')[1]['bead_dimensions'][0]['polygon'];draw.line([p(q) for q in polygon+[polygon[0]]],fill='#ffbc57',width=2)
            for a,b,c,d in redrow['unobstructed_segments']:
                if int(a+b)%3==0:line([a,b,c,d],'#ef75db',2)
            points=np.array([(x,y) for y,a,b in redrow['photographic_runs'] for x in range(a,b+1)]);mn=points.min(0);mx=points.max(0);mask=np.zeros((mx[1]-mn[1]+3,mx[0]-mn[0]+3),bool);mask[points[:,1]-mn[1]+1,points[:,0]-mn[0]+1]=True
            from scipy.ndimage import binary_erosion
            yy,xx=np.where(mask&~binary_erosion(mask));
            for x,y in zip(xx+mn[0]-1,yy+mn[1]-1):draw.rectangle((*p([x-.3,y-.3]),*p([x+.3,y+.3])),fill='white')
        for q in material['cues']:
            if lo[0]<=q['point'][0]<hi[0] and lo[1]<=q['point'][1]<hi[1] and ((q['colored'] and not q['predicted_material']) or (q['paper'] and q['predicted_material'])):
                x,y=p(q['point']);draw.ellipse((x-2,y-2,x+2,y+2),fill='#ff3b35' if q['colored'] else '#ef3aba')
        for q in rr:
            if not(lo[0]<=q['observed'][0]<hi[0] and lo[1]<=q['observed'][1]<hi[1]):continue
            a=np.array(p(q['observed']))
            if q['index'] is None:draw.line([tuple(a-4),tuple(a+4)],fill='white',width=2);draw.line([(a[0]-4,a[1]+4),(a[0]+4,a[1]-4)],fill='white',width=2);continue
            b=np.array(p(q['predicted']));col='#009a66' if q['status']=='confident conditional' else '#ed8d23' if q['strong'] else '#b561dd';delta=b-a;length=np.linalg.norm(delta)
            if q['status']=='ambiguous':
                for t in np.arange(0,max(length,1),8):draw.line([tuple(a+delta*(t/max(length,1))),tuple(a+delta*(min(t+5,length)/max(length,1)))],fill=col,width=2)
            else:draw.line([tuple(a),tuple(b)],fill=col,width=2)
            if length>0:
                v=delta/length;n=np.array([-v[1],v[0]]);head=min(7,length*.5);draw.polygon([tuple(b),tuple(b-head*v+head*.43*n),tuple(b-head*v-head*.43*n)],fill=col)
        rawbig=raw.resize(marked.size,Image.Resampling.NEAREST);width=2*marked.width+24;lines=textwrap.wrap(caption,width=max(70,int(width/10)));header=72;footer=28*len(lines)+20;out=Image.new('RGB',(width,marked.height+header+footer),'#13232f');dd=ImageDraw.Draw(out);ft=ImageFont.truetype(FONT,18);small=ImageFont.truetype(FONT,16)
        visible=[b['index'] for b in core if lo[0]<=b['projected_center'][0]<hi[0] and lo[1]<=b['projected_center'][1]<hi[1]];interval=[min(visible),max(visible)] if visible else [k,k]
        dd.text((12,8),f'{number:02d} · {title} · indices {interval[0]}…{interval[1]}',font=ft,fill='white');dd.text((12,40),'Unmarked native photograph (nearest-pixel enlargement)',font=small,fill='#b4d4e2');dd.text((marked.width+18,40),'Visible boundaries + reflection displacements',font=small,fill='#b4d4e2');out.paste(rawbig,(8,header));out.paste(marked,(marked.width+16,header))
        for i,line0 in enumerate(lines):dd.text((12,header+marked.height+10+28*i),line0,font=small,fill='white')
        image=f'diagnostic-{number:02d}.png';out.save(REVIEW/image);raw.save(REVIEW/f'diagnostic-{number:02d}-raw.png');gallery.append(dict(number=number,index=k,interval=interval,title=title,caption=caption,image=image,raw=f'diagnostic-{number:02d}-raw.png',box=list(map(int,box)),scale=scale))
        x,y=by[k]['projected_center'];od.ellipse((x-20,y-20,x+20,y+20),outline='#e02737',width=5);od.text((x+22,y-12),str(number),font=font,fill='#e02737')
    overview.save(REVIEW/'overview.png');save(BASE/'results/gallery.json',gallery);(REVIEW/'gallery.js').write_text('const GALLERY='+json.dumps(gallery)+';\n')
if __name__=='__main__':main()
