"""Fit one physical direct/room-fill balance after whole-necklace light search."""
from .shadows import *
from scipy.optimize import minimize_scalar

def best_proxy():
    trials=[]
    for name in ['refinement.json','wide-refinement.json','final-refinement.json']:
        trials.extend(read(OUT/name))
    return min(trials,key=lambda row:row['metrics']['fit']['robust_loss'])

def fit(reuse=False):
    selected=best_proxy();params=copy.deepcopy(selected['parameters']);params.update(grid=17,fixed_plane=True)
    profiles=read(OUT/'profiles.json.gz')['profiles'];work=Path('/tmp/r346-physical');work.mkdir(exist_ok=True)
    # A fixed planar diffuser, wholly above the paper, replaces the approximate
    # orient-per-receiver disk used during the broad exploratory grid.
    if not reuse or not all((work/(name+'.png')).exists() for name in ['paper','direct','room']):
        ratio=pass_images(params,work)
        for name,settings in [('direct',dict(params,intensity=1.,fill=0.,ambient_multiplier=0.)),('room',dict(params,intensity=0.,fill=.13,ambient_multiplier=1.))]:
            scene(settings,work/(name+'.pov'),'clear');run_pov(work/(name+'.pov'))
    D=linear(rgb(work/'direct.png'));K=linear(rgb(work/'room.png'));P=linear(rgb(work/'paper.png'));A=D-(P-K)/1.05
    sy,sx=D.shape[0]/H,D.shape[1]/W;lanes=np.arange(-18,19,3);arrays=[[],[],[]];weights=[]
    for row in profiles:
        q=np.array(row['point']);t=np.array(row['tangent']);n=np.array(row['outward']);dist=np.array(row['distance']);xy=q+lanes[:,None,None]*t+(row['model_edge_radius']+dist)[None,:,None]*n;outside=sample(paper_distance(),xy)>=2;xy=(xy+.5)*[sx,sy]-.5
        for target,field in zip(arrays,[D,K,A]):target.append(np.stack([np.where(outside,sample(field[:,:,c],xy),np.nan) for c in range(3)]))
        weight=np.exp(np.array(row['background_log_planes'],float)[:,0])*[.2126,.7152,.0722];weights.append(weight/weight.sum())
    DS,KS,AS=[np.array(a) for a in arrays];weights=np.array(weights)
    def predictions(t):
        deficit=np.nanmedian(AS/(DS+t*KS),axis=2)
        return np.sum(weights[:,:,None]*deficit,axis=1)
    def loss(t):return score(predictions(t),profiles,False)['fit']['robust_loss']
    fit=minimize_scalar(loss,bounds=(.02,8.),method='bounded',options={'xatol':.002})
    balance=float(fit.x);pred=predictions(balance)
    neutral_metrics=score(pred,profiles,False)
    observed=np.array([row['photo_rgb_deficit'] for row in profiles],dtype=float).transpose(0,2,1)
    distance=np.arange(observed.shape[-1]);guards=np.array([r['paper_guard'] for r in profiles])
    eligible=np.array([r['eligible'] and r['split']=='fit' for r in profiles]);valid=eligible[:,None,None]&(distance[None,None,:]>=guards[:,None,None])&(distance[None,None,:]<=200)&np.isfinite(observed)
    def color_prediction(t):return np.nanmedian(AS/(DS+t[None,:,None,None]*KS),axis=2)
    valid=np.broadcast_to(valid,observed.shape)&np.isfinite(color_prediction(np.full(3,balance)))
    def color_residual(logt):
        residual=color_prediction(np.exp(logt))-observed
        return residual[valid]
    colorfit=least_squares(color_residual,np.full(3,np.log(balance)),bounds=(np.full(3,np.log(.02)),np.full(3,np.log(8.))),loss='soft_l1',f_scale=.07,max_nfev=35)
    channel_balance=np.exp(colorfit.x);balance=float(channel_balance@[.2126,.7152,.0722]);tint=channel_balance/balance
    pred=np.sum(weights[:,:,None]*color_prediction(channel_balance),axis=1)
    # One global exposure/intensity scale matches unobstructed paper, independently
    # of the shadow-only contrast ratio. Albedo and all glass materials stay R345.
    from scipy.spatial import cKDTree
    yy,xx=np.mgrid[6:H:24,6:W:24];xy=np.c_[xx.ravel(),yy.ravel()];curve=Model(read(ROOT/'photo2/r345/config.json')).image;xy=xy[cKDTree(curve).query(xy)[0]>260]
    xy_small=(xy+.5)*[sx,sy]-.5
    field=D+channel_balance*K;expected=np.stack([sample(field[:,:,c],xy_small) for c in range(3)],axis=1);target=background_at(xy);luma=np.array([.2126,.7152,.0722]);scale=float(np.median((target@luma)/(expected@luma)))
    params.update(intensity=scale,fill=.13*balance*scale,ambient_multiplier=balance*scale,fill_tint=tint.tolist())
    # Reject an emitter crossing the paper plane: all points of one fixed disk
    # are above the paper, not independently rotated section-specific lights.
    direction=np.array(params['position'],float);direction/=np.linalg.norm(direction);u=np.cross([0,0,1.],direction);u/=np.linalg.norm(u);v=np.cross(direction,u)
    minimum_height=params['position'][2]-.5*params['diameter']*abs(v[2]);assert minimum_height>0
    result=dict(source_commit=read(OUT/'measurement-freeze.json')['source_commit'],parameters=params,selected_grid=selected,room_to_direct_multiplier=balance,room_to_direct_rgb=channel_balance.tolist(),neutral_fill_metrics=neutral_metrics,analytic_metrics=score(pred,profiles,False),emitter_minimum_height=minimum_height,angular_diameter_deg=float(np.degrees(2*np.arctan(params['diameter']/2/np.linalg.norm(params['position'])))),camera_changed=False,scope='Exactly R345 bead transforms, shape, colors, camera and paper; one fixed planar area key and one uniform room-fill contribution. No section-specific corrections.',calibration='Relative RGB paper-shadow profiles fit a single global room/direct ratio and fill tint; independent global unobstructed-paper brightness sets common intensity scale. Absolute light power/distance not uniquely recovered. Bead materials unchanged.')
    save(HERE/'config.json',result);print(json.dumps(result,indent=2))
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--reuse-basis',action='store_true');args=ap.parse_args();fit(args.reuse_basis)
