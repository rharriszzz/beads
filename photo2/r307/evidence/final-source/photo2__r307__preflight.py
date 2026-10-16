"""Historical preservation and required native diagnostic, before fitting."""
import subprocess,time
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save,sha,pixels
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain
from photo2.r305.diagnose import isolated
from photo2.r305.forward import segments
BASE=ROOT/'photo2/r307'
def run():
    if not (BASE/'evidence/preservation.json.gz').exists():
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
        save(BASE/'evidence/preservation.json.gz',{p:sha(ROOT/p) for p in paths if p})
    data,m,obs=load();model=read(ROOT/'photo2/r306/results/campaign/exports/primary.json.gz');s=Chain(model['parameters'],data)
    pos=next(b for b in model['positions'] if b['index']==-101);point=np.array(pos['projected_center']);lo=np.floor(point-100).astype(int);hi=lo+200
    yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];xy=np.c_[xx.ravel(),yy.ravel()];start=time.monotonic();tr=s.trace(xy);seconds=time.monotonic()-start
    raster=np.load(ROOT/'photo2/r306/results/campaign/exports/primary-raster.npz');saved=raster['owner'][yy,xx].ravel();assert np.array_equal(saved,tr['owner'])
    k=int(np.flatnonzero(s.indices==-101)[0]);visible=(saved==k).reshape(xx.shape);iso=isolated(s,-101).trace(xy)['owner'].reshape(xx.shape)>=0
    assert sorted(segments(visible,*lo))==sorted(pos['boundary_segments'])
    source=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');raw=source.crop((*lo,*hi));panels=[]
    for title,mode in [('Raw photograph','raw'),('Isolated projection / visible','iso'),('Native selected / neighbors','visible'),('Observed positive interiors','obs')]:
        im=raw.copy();d=ImageDraw.Draw(im)
        if mode=='iso':
            for seg in segments(iso,*lo):a,b,c,e=seg;d.line((a-lo[0],b-lo[1],c-lo[0],e-lo[1]),fill='#ff88ff')
        if mode in ['iso','visible']:
            for b in model['positions']:
                if mode=='iso' and b['index']!=-101:continue
                if np.linalg.norm(np.array(b['projected_center'])-point)>150:continue
                for a,c,e,f in b['boundary_segments']:d.line((a-lo[0],c-lo[1],e-lo[0],f-lo[1]),fill='#ffff00' if b['index']==-101 else '#00ddff')
            h=pos['reflection']['centroid'];d.ellipse((h[0]-lo[0]-2,h[1]-lo[1]-2,h[0]-lo[0]+2,h[1]-lo[1]+2),outline='white')
        if mode=='obs':
            arr=np.asarray(im).copy()
            for r in data['rows']:
                if r['kind']!='region' or r['reflection']:continue
                pts=pixels(r['pixels'])-lo;ok=(pts[:,0]>=0)&(pts[:,0]<200)&(pts[:,1]>=0)&(pts[:,1]<200);pts=pts[ok]
                col=np.array([255,60,60] if r['color']=='red' else [255,215,40]);arr[pts[:,1],pts[:,0]]=(.5*arr[pts[:,1],pts[:,0]]+.5*col).astype('uint8')
            im=Image.fromarray(arr)
        panel=Image.new('RGB',(400,435),'#18212a');panel.paste(im.resize((400,400),Image.Resampling.NEAREST),(0,35));ImageDraw.Draw(panel).text((6,10),title,fill='white');panels.append(panel)
    image=Image.new('RGB',(1600,435));[image.paste(p,(400*i,0)) for i,p in enumerate(panels)];image.save(BASE/'evidence/R306-minus101.png')
    overlaps=[]
    for r in data['rows']:
        if r['kind']!='region' or np.linalg.norm(np.array(r['point'])-point)>70:continue
        pts=pixels(r['pixels']);o=raster['owner'][pts[:,1],pts[:,0]];ids,cnt=np.unique(o[o>=0],return_counts=True)
        overlaps.append(dict(id=r['id'],color=r['color'],reflection=r['reflection'],accepted=r['accepted'],pixels=len(pts),selected_fraction=float(np.mean(o==k)),owners=[dict(index=int(s.indices[j]),fraction=float(c/len(pts))) for j,c in zip(ids,cnt)]))
    save(BASE/'evidence/R306-minus101.json',dict(point=point.tolist(),index=-101,raw_native_owner_exact=True,viewer_segments_exact=True,visible_pixels=int(visible.sum()),isolated_pixels=int(iso.sum()),occluded_pixels=int((iso&~visible).sum()),native_trace_seconds=seconds,overlaps=overlaps,interpretation='Jagged selected boundary is the saved native first-hit boundary, including hole and occlusion. Selection yellow is not a photo color. No independently measured complete contour exists here; positive supports and material cues constrain placement.'))
    print('Native diagnostic',seconds,'seconds',int(visible.sum()),int(iso.sum()),flush=True)
if __name__=='__main__':run()
