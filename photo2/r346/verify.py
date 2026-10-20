"""Independent source seals, paper sampling, feature units and global-light checks."""
import argparse,gzip,hashlib,json,re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.special import erfc,ndtri
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=HERE/'output';BASE=ROOT/'photo2/r345/output'
def read(p):return json.loads(gzip.open(p,'rt').read() if str(p).endswith('.gz') else Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def linear(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def image(p):return linear(np.asarray(Image.open(p).convert('RGB'),float)/255)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);args=ap.parse_args();out=args.output
    seal=read(OUT/'input-seal.json')
    for p,h in seal.items():assert digest(ROOT/p)==h,p
    source=(BASE/'scene.inc').read_text();generated=(out/'scene.pov').read_text()
    def unlit(s):
        s=re.sub(r'^#version[^\n]+\n','',s)
        start=s.index('light_source {');end=s.index('// Paper is',start);s=s[:start]+s[end:]
        return re.sub(r'ambient_light rgb <[^>]+>','ambient_light RGB_ROOM',s).strip()
    assert unlit(source)==unlit(generated),'Camera, glass, shape or paper changed'
    assert generated.count('light_source {')==2 and 'no_image' not in generated
    assert generated.count('#include "beads.inc"')==1
    beads=read(BASE/'beads.json');sequence=read(ROOT/'photo2/r344/pattern208.json')['provisional_sequence'];assert len(beads)==2704
    assert all(row['k']==k and row['color']==sequence[k%208] for k,row in enumerate(beads))
    config=read(HERE/'config.json');p=config['parameters'];assert not p.get('camera') and p['fixed_plane'] and p['intensity']>0 and p['fill']>=0
    pos=np.array(p['position'],float);unit=pos/np.linalg.norm(pos);a=np.cross([0,0,1],unit);a/=np.linalg.norm(a);b=np.cross(unit,a);minimum=pos[2]-.5*p['diameter']*abs(b[2]);assert minimum>0
    data=read(OUT/'profiles.json.gz')['profiles'];original=read(OUT/'observations.json')['rows'];assert len(data)==len(original)==192 and {r['station'] for r in data}==set(range(96))
    assert all({r['side'] for r in data if r['station']==i}=={-1,1} for i in range(96))
    assert all(r['paper_guard']>=12 for r in data)
    # Frozen photometry and source reference remain exactly those used for search.
    freeze=read(OUT/'measurement-freeze.json');assert digest(OUT/'profiles.json.gz')==freeze['profiles_sha256'];assert digest(OUT/'background.json')==freeze['background_sha256']
    saved=read(out/'comparison-metrics.json');pred=np.load(out/'rendered-profiles.npz');observed=np.array([r['photo_deficit'] for r in data],float);d=np.arange(observed.shape[1]);eligible=np.array([r['eligible'] for r in data]);guard=np.array([r['paper_guard'] for r in data]);fit=np.array([r['split']=='fit' for r in data]);independent={}
    for name in ['R345','R346']:
        value=pred[name];valid=eligible[:,None]&(d[None,:]>=guard[:,None])&(d[None,:]<=200)&np.isfinite(observed)&np.isfinite(value);errors=value-observed;independent[name]={}
        for split,selector in [('all',valid),('fit',valid&fit[:,None]),('validation',valid&~fit[:,None])]:
            e=errors[selector];rms=float(np.sqrt(np.mean(e*e)));mae=float(np.mean(abs(e)));expected=saved['profile_scores'][name][split];assert expected['points']==selector.sum();assert abs(rms-expected['rms'])<1e-12 and abs(mae-expected['mae'])<1e-12;independent[name][split]=dict(points=len(e),rms=rms,mae=mae)
    assert independent['R346']['validation']['rms']<independent['R345']['validation']['rms']
    assert saved['same_pixel_scores']['R346']['validation']['rms']<saved['same_pixel_scores']['R345']['validation']['rms']
    # Re-sample actual PNG paper ratios, independent of producer profile helpers.
    ratio=(image(out/'render.png')/image(out/'clear.png')).astype(np.float32);height,width=ratio.shape[:2];mask=np.asarray(Image.open(OUT/'mask.png').convert('L'))>128;outside=ndi.distance_transform_edt(~mask);max_error=0.;samples=0
    for i,r in enumerate(data):
        if not r['eligible'] or r['station']%8:continue
        for dist in [20,40,80,120,160,200]:
            if dist<r['paper_guard'] or not np.isfinite(pred['R346'][i,dist]):continue
            xy=np.array(r['point'])+np.arange(-18,19,3)[:,None]*r['tangent']+(r['model_edge_radius']+dist)*np.array(r['outward']);safe=ndi.map_coordinates(outside,[xy[:,1],xy[:,0]],order=1,mode='constant',cval=0)>=2
            xy=(xy+.5)*[width/2540,height/3182]-.5;weights=np.exp(np.array(r['background_log_planes'],float)[:,0])*[.2126,.7152,.0722];weights/=weights.sum();transmission=[]
            for c in range(3):
                values=ndi.map_coordinates(ratio[:,:,c],[xy[:,1],xy[:,0]],order=1,mode='constant',cval=np.nan);transmission.append(np.nanmedian(values[safe]))
            value=1-np.array(transmission)@weights;error=abs(value-pred['R346'][i,dist]);assert error<1e-7;max_error=max(max_error,error);samples+=1
    # An analytic broad shadow checks feature dimensions and explicit censoring.
    from .analysis import features
    distance=np.arange(261,dtype=float);profile=.8*.5*erfc((distance-100)/(np.sqrt(2)*15));row=dict(distance=distance.tolist(),paper_guard=12.)
    result=features(row,profile);expected_width=2*ndtri(.9)*15;assert abs(result['penumbra_px']-expected_width)<2
    clipped=features(dict(distance=distance[:91].tolist(),paper_guard=12.),profile[:91]);assert clipped['extent10_censored'] and clipped['extent_10percent_px'] is None
    blank=features(row,np.zeros_like(distance));assert blank['extent_10percent_px']==0 and blank['penumbra_px'] is None
    # Full measurement CSV includes every failed boundary rather than hiding it.
    import csv
    with (out/'shadow-measurements.csv').open() as f:csv_rows=list(csv.DictReader(f))
    assert len(csv_rows)==192*3
    convergence=read(OUT/'sampling-convergence.json');assert convergence['selected17_vs33_profile_rms']<.015
    color=read(OUT/'color-profile-sensitivity.json');assert abs(color['R346_validation_RMS_change'])<.015
    assert color['profile_scores_after_ICC']['R346']['validation']['rms']<color['profile_scores_after_ICC']['R345']['validation']['rms']
    result=dict(all_passed=True,sealed_R344_R345_files=len(seal),physical_beads=2704,pattern_repeats=13,camera_geometry_material_paper_unchanged=True,global_light_sources=2,section_specific_lights=False,minimum_emitter_height=minimum,contours=192,stations=96,eligible_contours=int(eligible.sum()),independent_profile_metrics=independent,actual_png_paper_resamples=samples,maximum_png_profile_error=max_error,synthetic_penumbra_expected_px=float(expected_width),synthetic_penumbra_measured_px=result['penumbra_px'],censored_and_zero_shadow_controls_pass=True,CSV_rows=len(csv_rows),area17_vs33_profile_rms=convergence['selected17_vs33_profile_rms'],ICC_R346_validation_RMS_change=color['R346_validation_RMS_change'])
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
