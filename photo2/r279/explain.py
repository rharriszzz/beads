"""Post-freeze review artifacts; never changes observations or predictions."""
import csv
from collections import Counter
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from .run import ROOT,OUT,read,save,gallery
from .geometry import centers,SURFACE,sdf,R

def main():
    for folder in [OUT/'real']+sorted(OUT.glob('scene-*')):
        if not (folder/'observations.json.gz').exists():continue
        photo=ROOT/'beads-photo-2.jpg' if folder.name=='real' else OUT/'synthetic-scenes'/folder.name/'photo.png'
        rgb=np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'));obs=read(folder/'observations.json.gz');cases=read(folder/'test1.json')
        coords=[]
        for o in obs:
            pix=np.array(o['pixels']);lum=rgb[pix[:,1],pix[:,0]]@np.array([.2126,.7152,.0722]);mx=lum.max();peaks=pix[lum==mx]
            coords.append(dict(id=o['id'],sigma2_feature_coordinate=o['point'],native_brightest_pixels_in_support=peaks.tolist(),interior_centroid=o['centroid'],physical_center=None))
        save(folder/'coordinate-types.json.gz',coords);gallery(rgb,obs,cases,folder)
        with (folder/'cases.csv').open('w') as f:
            writer=csv.writer(f,lineterminator='\n');writer.writerow(['case','anchor','method','top','answer','alternatives','distance','interval','same_body_possible','native_valley','hue_distance','supported_surface_gap'])
            for j,c in enumerate(cases):
                for m,v in c['methods'].items():
                    r=v['ranking'][0];q=r['cues'];writer.writerow([j+1,c['anchor'],m,v['top'],v['answer'],len(v['alternatives']),r['distance_px'],r['interval_px'],q['possible_same_body'],q['valley'],q['hue_difference'],q['supported_surface_gap_px']])
    # Evaluator-only examples chosen AFTER all results: never used for tuning.
    rows=read(OUT/'synthetic-test1-evaluation.json');chosen=[]
    for label,predicate in [('correct neighbor',lambda r:r['top_status']=='correct'),('same-body duplicate',lambda r:r['top_status']=='same_body_duplicate'),('wrong neighbor',lambda r:r['top_status']=='wrong_body'),('ambiguous decision',lambda r:r['decision']=='ambiguous')]:
        row=next(r for r in rows if predicate(r));cases=read(OUT/row['scene']/'test1.json');j=next(i for i,c in enumerate(cases) if c['anchor']==row['anchor']);chosen.append(dict(label=label,**row,image=f'{row["scene"]}/anchor-{j+1:02d}.jpg'))
    save(OUT/'review-examples.json',chosen)
    t2=read(OUT/'synthetic-test2-evaluation.json');geo=[]
    for label,predicate in [('correct image match, rejected packing',lambda r:r['C_match_correct']),('incorrect image match, rejected packing',lambda r:r['C_conditional_match'] and not r['C_match_correct']),('unmatched alternative',lambda r:not r['C_conditional_match'])]:
        row=next(r for r in t2 if predicate(r));pairs=read(OUT/row['scene']/'pairs.json.gz');pair=next(p for p in pairs if p['A']['id']==row['A'] and p['mode']==row['mode']);f=read(OUT/row['scene']/pair['before_C']);h=next(h for h in f['hypotheses'] if h['hand']==row['hand'] and h['delta']==row['delta'] and h['rank']==row['rank'])
        rgb=Image.open(OUT/'synthetic-scenes'/row['scene']/'photo.png').convert('RGB').resize((640,448));d=ImageDraw.Draw(rgb)
        for x,y in h['C_visible_pixels']:d.point((2*x,2*y),fill='lime')
        for o,l in ((pair['A'],'A'),(pair['B'],'B')):d.text(tuple(2*np.array(o['centroid'])),l,fill='cyan')
        name=f'geometry-example-{len(geo)+1}.jpg';rgb.save(OUT/name,quality=92);geo.append(dict(label=label,image=name,**row))
    save(OUT/'geometry-examples.json',geo)
    import os
    os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r279-mpl')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,pitch in zip(axes,(1.,1.1)):
        c=centers([0,6],1,0,pitch);v=c[1,1:]-c[0,1:];v/=np.linalg.norm(v)
        yy,xx=np.mgrid[-2:4:400j,-2:5:450j];pts=np.stack([xx,c[0,1]+yy*v[0],c[0,2]+yy*v[1]],axis=-1)
        a=sdf(pts-c[0]);b=sdf(pts-c[1]);ax.contourf(xx,yy,(a<0).astype(int)+(b<0).astype(int),levels=[.5,1.5,2.5],colors=['#bbd4ef','#ff6245'],alpha=.8)
        ax.contour(xx,yy,a,levels=[0],colors=['#004d8b']);ax.contour(xx,yy,b,levels=[0],colors=['#57367a']);ax.set_aspect('equal');ax.set_title(f'Pitch {pitch:.2f}: red = material overlap');ax.set_xlabel('Local centerline axis (source units)')
    axes[0].set_ylabel('Transverse section through both centers');fig.tight_layout();fig.savefig(OUT/'packing-sections.png',dpi=150);plt.close(fig)
if __name__=='__main__':main()
