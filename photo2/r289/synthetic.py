"""Fresh independent POV-Ray scenes; inference saved before opening identity truth."""
import argparse,subprocess
from collections import Counter
from PIL import Image
from photo2.r280.synthetic import render
from photo2.r280.geometry import certify
from photo2.r279.geometry import R,INDICES,trace,project,centers
from photo2.bead_detection.brightness_r270 import encode
from .landmark import detect
from .physics import forward,bright_truth
from .common import *

COLORS=('red','yellow','black')

def plan():
    rng=np.random.default_rng(2891703);scenes=[]
    # Each split has all three materials and independent phase/roll. Heldout lights
    # differ from development: correction is explicitly tested for transfer.
    for i in range(12):
        p=dict(hand=(-1,1)[i%2],phase=float(rng.uniform(-np.pi,np.pi)),pitch=1.20,inclination=(-25,0,25)[i%3],roll=float(rng.uniform(-40,40)),scale=9.,translation=[159.5,111.5],light=([-.6,-.8,1.],[.7,-.4,1.],[-.4,.5,1.],[.3,-.9,.55])[i//3],light_power=.55,specular=(.35,.70)[i%2],roughness=(.025,.06)[i%2],ambient=.08,background=[.47,.31,.43])
        classes=rng.integers(0,3,29).tolist()
        scenes.append(dict(id=f'scene-{i:02}',split='development' if i<6 else 'evaluation',parameters=p,classes=classes))
    save(OUT/'synthetic-plan.json',dict(seed=2891703,scenes=scenes,source_hashes={n:sha(Path(__file__).parent/n) for n in ('landmark.py','physics.py','synthetic.py')},semantics='Fixed before renders; no photo pose/light fits; source rounded annuli same dimensions for all colors'))

def extra_render(folder,source,name):
    path=folder/(name+'.pov');path.write_text(source)
    cmd=['povray','+I'+str(path.resolve()),'+O'+str((folder/(name+'.png')).resolve()),'+W320','+H224','+FN','-D','-A','+WT2','File_Gamma=1.0']
    rr=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(folder/(name+'.log')).write_bytes(rr.stdout)
    if rr.returncode:raise RuntimeError(rr.stdout.decode()[-1000:])
    return np.asarray(Image.open(folder/(name+'.png')).convert('RGB'))

def run():
    frozen=read(OUT/'synthetic-plan.json')
    for n,h in frozen['source_hashes'].items():assert sha(Path(__file__).parent/n)==h
    for scene in frozen['scenes']:
        folder=OUT/'synthetic'/scene['id'];folder.mkdir(parents=True,exist_ok=True);p=scene['parameters'];classes=scene['classes']
        if (folder/'evaluation.json').exists():continue
        cert=certify(p);assert cert['certified']
        on=render(folder,p,classes);source=(folder/'photo.pov').read_text()
        off=extra_render(folder,source.replace(f'specular {p["specular"]}', 'specular 0'),'diffuse')
        # Dedicated specular-only pass avoids subtraction corruption from clipping.
        pure_source=source.replace(f'ambient {p["ambient"]} diffuse .75','ambient 0 diffuse 0').replace('ambient .18 diffuse .8','ambient 0 diffuse 0')
        pure=extra_render(folder,pure_source,'specular')
        allrecords={}
        for name,rgb in [('on',on),('off',off)]:
            srgb=np.uint8(np.rint(255*np.clip(encode(rgb/255.),0,1)));Image.fromarray(srgb).save(folder/(name+'-srgb.png'))
            records,info=detect(srgb)
            if not np.isfinite(info['background_hue']):
                info['background_hue']=None;info['background_warning']='No saturated border pixels: paper hue and pigment palette unidentifiable; existing detector paper gate is inactive. Color labels untrusted.'
            allrecords[name]=records;save(folder/(name+'-inference.json.gz'),dict(records=records,info=info))
        # Membership, physical centers and surfaces are evaluation-only from here.
        identity=render(folder,p,classes,True);truth=identity[:,:,0].astype(int)-1;phys=forward(p)
        expected=np.where(truth>=0,truth-14,-999);valid=~phys['unknown'];agree=bool(np.array_equal(expected[valid],phys['owner'][valid]));assert agree
        np.savez_compressed(folder/'truth.npz',owner=truth,predicted_specular=phys['specular'],unknown=phys['unknown'])
        sp=pure@np.array([.2126,.7152,.0722])/255.;diff=np.maximum(on.astype(float)-off,0)@np.array([.2126,.7152,.0722])/255.;beads=[]
        for j in range(29):
            mask=truth==j;y,x=np.where(mask)
            if not len(x):continue
            # Occlusion fraction uses isolated same-shape ray tracing, not brightness.
            pc=phys['centers'][j];lo=np.maximum(0,np.floor(pc-23).astype(int));hi=np.minimum([320,224],np.ceil(pc+24).astype(int));iy,ix=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]]
            own,_,unk=trace(p,np.c_[ix.ravel(),iy.ravel()],[j-14]);isolated=int(np.sum(own==j-14))
            true_spec=bright_truth(sp,mask);pred=bright_truth(phys['specular'],mask);pair_spec=bright_truth(diff,mask)
            row=dict(owner=j,color=COLORS[classes[j]],visible_area=len(x),visible_centroid=np.c_[x,y].mean(0).tolist(),physical_center=pc.tolist(),diameter=2*R*p['scale'],visible_fraction=len(x)/max(isolated,1),specular=true_spec,paired_difference=pair_spec,normal_prediction=pred,measurements={})
            for name,records in allrecords.items():
                accepted=[r for r in records if r['accepted'] and truth[r['point'][1],r['point'][0]]==j]
                measurements=[]
                for r in accepted:
                    pts=pixels(r);purity=float(np.mean(truth[pts[:,1],pts[:,0]]==j));xx,yy=r['point']
                    measurements.append(dict(id=r['id'],point=r['point'],patch=r['centroid'],weighted=r['weighted'],purity=purity,threshold_sensitivity_px=r['threshold_sensitivity_px'],dark=r['dark'],specular_fraction_at_peak=float(diff[yy,xx]/max((on[yy,xx]@np.array([.2126,.7152,.0722]))/255.,1e-10))))
                row['measurements'][name]=measurements
                # Whole-visible-surface brightest measurement is an ORACLE diagnostic,
                # explicitly separate from the independent inference above.
                field=(on if name=='on' else off)@np.array([.2126,.7152,.0722])/255
                row['measurements'][name+'_oracle']=bright_truth(field,mask)
            beads.append(row)
        save(folder/'evaluation.json',dict(scene=scene,beads=beads,certificate=cert,projection_check=dict(exact_resolved_agreement=agree,unknown=int(phys['unknown'].sum()),shadow_unfinished=phys['shadow_unfinished']),inference_hashes={n:sha(folder/(n+'-inference.json.gz')) for n in ('on','off')},saturated_channels=int(np.sum(on==255))))
        print(scene['id'],'beads',len(beads),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['plan','run']);a=p.parse_args();plan() if a.stage=='plan' else run()
