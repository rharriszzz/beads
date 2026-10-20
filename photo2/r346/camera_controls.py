"""Global camera controls, all rejected; bead geometry never changes."""
from photo2.r346.shadows import *
from photo2.r345.render import observations

def main():
    c=read(ROOT/'photo2/r345/config.json');m=Model(c);_,k,xy=observations();g=m.geometry(k);points=g['centers']+.75*m.r*g['radial'];y0=-np.cos(np.radians(80))/np.sin(np.radians(80))*m.height
    profiles=read(OUT/'profiles.json.gz')['profiles'];work=Path('/tmp/r346-shadow-trials');ledger=[]
    cameras={}
    for D in [250,500,1000]:
     def prediction(v):
      scale=v[0];cam=np.array([-(v[1]-1269.5)/scale,y0+(v[2]-1590.5)/scale,m.height+D]);return np.c_[points[:,0]-cam[0],-(points[:,1]-cam[1])]*(scale*D/(cam[2]-points[:,2])[:,None])+[1269.5,1590.5]
     fit=least_squares(lambda v:(prediction(v)-xy).ravel(),[8.4,1269.5,1590.5],loss='soft_l1',f_scale=10)
     v=fit.x;new=prediction(v);diff=np.linalg.norm(new-m.project(points),axis=1);err=np.linalg.norm(new-xy,axis=1)
     camera=dict(distance=D,scale=v[0],location=[-(v[1]-1269.5)/v[0],y0+(v[2]-1590.5)/v[0],m.height+D],elevation=90,proxy_rms=float(np.sqrt(np.mean(err**2))),projection_change_rms=float(np.sqrt(np.mean(diff**2))),projection_change_p95=float(np.percentile(diff,95)),projection_change_max=float(diff.max()))
     cameras[D]=camera
    save(OUT/'camera-controls.json',dict(policy='Geometry fixed; three camera scale/XY nuisance parameters fit all1041 existing bright-support locations, no pigment selection. Camera distances prespecified; normal view instead of R34580deg. These are projection approximations, not recovered calibrated poses.',cameras=cameras))
    candidates=[]
    for D in [250,500,1000]:candidates.append(dict(id=f'perspective{D}',position=[-5000,0,4000],diameter=2400,camera=cameras[D]))
    for pos in [[-5000,-700,4000],[-1000,-150,850],[-1500,-150,850]]:candidates.append(dict(id='orthographic'+str(pos[0]),position=pos,diameter=(2400 if pos[2]==4000 else 500)))
    for params in candidates:
     folder=work/params['id'];folder.mkdir(exist_ok=True)
     if (folder/'ratio.npy').exists():ratio=np.load(folder/'ratio.npy')
     else:ratio=pass_images(params,folder);np.save(folder/'ratio.npy',ratio)
     if params.get('camera'):
      mask=folder/'mask.png'
      if not mask.exists():scene(params,folder/'mask.pov','mask');run_pov(folder/'mask.pov',1270,1591)
     else:mask=None
     pred=rendered_profiles(ratio,profiles,mask);metrics=score(pred,profiles);ledger.append(dict(parameters=params,metrics=metrics));save(OUT/'camera-light-controls.json',ledger);print(params['id'],metrics,flush=True)

if __name__=="__main__":main()
