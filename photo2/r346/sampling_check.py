"""Convergence of the entire necklace's paper shadow under one area source."""
from .shadows import *

def main():
    params=read(HERE/'config.json')['parameters'];profiles=read(OUT/'profiles.json.gz')['profiles'];work=Path('/tmp/r346-sampling');work.mkdir(exist_ok=True)
    scene(params,work/'clear.pov','clear');run_pov(work/'clear.pov');clear=linear(rgb(work/'clear.png'));predictions={};rows=[]
    for grid in [9,17,33]:
        p=dict(params,grid=grid);path=work/f'grid{grid}.pov';scene(p,path,'paper');run_pov(path);image=linear(rgb(path.with_suffix('.png')));ratio=image/clear;pred=rendered_profiles(ratio,profiles);predictions[grid]=pred;rows.append(dict(grid=grid,metrics=score(pred,profiles,False)))
    selected=np.array([r['eligible'] for r in profiles]);d=np.arange(predictions[17].shape[1]);g=np.array([r['paper_guard'] for r in profiles]);valid=selected[:,None]&(d[None,:]>=g[:,None])&(d[None,:]<=200)&np.isfinite(predictions[17])&np.isfinite(predictions[33]);delta=(predictions[17]-predictions[33])[valid]
    result=dict(trials=rows,selected17_vs33_profile_rms=float(np.sqrt(np.mean(delta**2))),selected17_vs33_profile_p95=float(np.percentile(abs(delta),95)),selected17_vs33_profile_max=float(np.max(abs(delta))),comparison_pixels=int(valid.sum()),policy='Same whole2704-body occluder, camera, geometry, color, light position/diameter/fill. Only area-light sample count changes.635x796 images, distances sampled in native coordinates. No per-bead shadows isolated.')
    save(OUT/'sampling-convergence.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
