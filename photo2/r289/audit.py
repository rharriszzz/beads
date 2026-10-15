"""Complete denominator, native crop, historical preservation and replay audits."""
import subprocess,hashlib
from scipy import ndimage as ndi
from PIL import Image
from .common import *
from .physics import bright_truth

def main():
    synth=[];spec=[];oracle=[];prediction_replay=0
    for folder in sorted((OUT/'synthetic').glob('scene-*')):
        truth=np.load(folder/'truth.npz');owner=truth['owner'];data=read(folder/'evaluation.json');sp=np.asarray(Image.open(folder/'specular.png'))@np.array([.2126,.7152,.0722])/255
        for b in data['beads']:
            pred=bright_truth(truth['predicted_specular'],owner==b['owner']);assert pred==b['normal_prediction'];prediction_replay+=1
            mask=owner==b['owner'];vals=sp[mask]
            if len(vals) and vals.max()>=.01:
                connected,n=ndi.label(mask&(sp>=.85*vals.max()),np.ones((3,3)));spec.append(dict(scene=folder.name,owner=b['owner'],components=n,peak_ties=int(np.sum(mask&(sp==vals.max())))))
        for mode in ('on','off'):
            rgb=np.asarray(Image.open(folder/('photo.png' if mode=='on' else 'diffuse.png')));field=rgb@np.array([.2126,.7152,.0722])/255
            for b in data['beads']:
                mask=owner==b['owner'];yy,xx=np.where(mask);v=field[mask];k=int(np.argmax(v));x,y=int(xx[k]),int(yy[k]);lab,_=ndi.label(mask&(field>=.85*v[k]),np.ones((3,3)));py,px=np.where(lab==lab[y,x])
                oracle.append(dict(scene=folder.name,mode=mode,owner=b['owner'],color=b['color'],peak=[x,y],peak_Y=float(v[k]),peak_ties=int(np.sum(v==v[k])),has_contrast=bool(v.max()>v.min()),connected_patch_centroid=np.c_[px,py].mean(0).tolist(),connected_patch_area=len(px),visible_centroid=b['visible_centroid'],physical_center=b['physical_center'],scope='Known-owner oracle only, including dim/off features below detector threshold; never a Phase1 input.'))
            rr=read(folder/(mode+'-inference.json.gz'))['records'];good=[r for r in rr if r['accepted']];purity=[];background=0;small=0
            for r in good:
                x,y=r['point'];j=owner[y,x];background+=int(j<0)
                if j>=0:small+=int((owner==j).sum()<40)
                pts=pixels(r);purity.append(float(np.mean(owner[pts[:,1],pts[:,0]]==j)) if j>=0 else 0.)
            synth.append(dict(scene=folder.name,split=data['scene']['split'],mode=mode,accepted=len(good),background_seed=background,small_visible_body=small,pure95=sum(p>=.95 for p in purity),mixed_or_background=sum(p<.95 for p in purity)))
    native,_,_=photo();crops=[]
    for r in read(OUT/'review-manifest.json'):
        x0,y0,x1,y1=r['box'];a=np.asarray(Image.open(REVIEW/(r['name']+'-native.png')));np.testing.assert_array_equal(a,native[y0:y1,x0:x1]);crops.append(r['name'])
    # Git blob hash for every preexisting scientific file, avoiding old outputs writes.
    raw=subprocess.check_output(['git','ls-tree','-r',BASE,'photo2','beads.pov','beads-photo-2.jpg'],text=True);checked=0;bad=[]
    for line in raw.splitlines():
        left,name=line.split('\t');mode,kind,h=left.split()
        if kind!='blob':continue
        path=ROOT/name
        if not path.is_file():bad.append(name);continue
        b=path.read_bytes();actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if actual!=h:bad.append(name)
        checked+=1
    assert not bad,bad
    save(OUT/'synthetic-oracle-landmarks.json.gz',oracle)
    save(OUT/'audit.json',dict(historical_blobs_unchanged=checked,changed=bad,native_crops=len(crops),synthetic_detection=synth,specular_lobes=spec,synthetic_prediction_replay=prediction_replay,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r289').glob('*.py'))},inputs={p:sha(ROOT/p) for p in ('beads-photo-2.jpg','beads.pov','photo2/R289_SPECIFICATION.md')}))
    print('Preserved',checked,'blobs;',len(crops),'exact crops;',prediction_replay,'predictions')
if __name__=='__main__':main()
