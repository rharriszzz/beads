"""R253 indexing, camera sensitivity, reporting and reproducibility diagnostics."""
import sys,json,csv,hashlib,platform
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ExifTags
sys.path.insert(0,str(Path(__file__).resolve().parent))
from global_fit_r253 import OUT,ROOT,Model,save,table,data,harmonics,correction,RADIUS,ROW


def neighborhood(out=OUT):
    graph=json.loads((ROOT/'photo2/review/r144/corrected-report.json').read_text())
    points=json.loads((ROOT/'photo2/manual-labels-r146.json').read_text())['annotations']
    coord=graph['conditional_charts'][0]['coordinates'];base=np.array(coord['20'])
    rr=[]
    for p in points:
        u,v=(np.array(coord[str(p['number'])])-base).tolist()
        rr.append(dict(maker_number=p['number'],maker_observation_id=p['id'],x=p['x'],y=p['y'],u=u,v=v,k_A=u+7*v,k_B=-u+6*v,k_reverse_A=-u-7*v,k_reverse_B=u-6*v))
    table(out/'maker-local-chart.csv',rr)
    model_results=[]
    models=json.loads((out/'models.json').read_text())
    for summary in models:
        mid=summary['model_id'];model=Model(summary['n'],summary['h'],summary['p']);origin=summary['origin_generator_index']
        # Evaluate both charts without treating local graph points as physical
        # centers. Surface membership checked with the same complete occluders.
        from visible_correspondence import rays
        g=model.geometry(np.arange(summary['n']));xy=np.array([[r['x'],r['y']] for r in rr]);own,_,un=rays(model,xy,g)
        for family in ['A','B','reverse_A','reverse_B']:
            target=np.array([(origin+r['k_'+family])%summary['n'] for r in rr]);pc=model.view.project(g['centers'][target])
            model_results.append(dict(model_id=mid,family=family,owned=int(((own==target)&(un==0)).sum()),total=len(rr),center_rms=float(np.sqrt(np.mean(np.sum((xy-pc)**2,axis=1)))),per_bead=[dict(maker_number=r['maker_number'],target_index=int(k),observed_owner=int(o),ownership=bool(o==k)) for r,k,o in zip(rr,target,own)]))
    save(out/'maker-chart-audit.json',model_results)
    # Draw confirmed geometric direction star; no fitted model required.
    photo=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB');box=(1260,220,1440,355)
    raw=photo.crop(box).resize((1080,810));im=Image.new('RGB',(2160,930),'white');im.paste(raw,(0,100));im.paste(raw,(1080,100));d=ImageDraw.Draw(im)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    d.text((20,15),'Maker 20 = C252-A948 = relative k=0 | raw photograph',font=font,fill='black')
    d.text((1100,15),'A: d1=+1, d2=+7, d3=+6; B: d1=-1, d2=+6, d3=+7',font=font,fill='black')
    pp={r['maker_number']:r for r in rr};x0=(pp[20]['x']-box[0])*6+1080;y0=(pp[20]['y']-box[1])*6+100
    labels={21:('+d1 | A +1 / B -1','white'),19:('-d1 | A -1 / B +1','white'),23:('+d2 | A +7 / B +6','#00dfff'),16:('-d2 | A -7 / B -6','#00dfff'),22:('+d3 | A +6 / B +7','#ffb000'),17:('-d3 | A -6 / B -7','#ffb000')}
    for number,(label,color) in labels.items():
        x=(pp[number]['x']-box[0])*6+1080;y=(pp[number]['y']-box[1])*6+100
        d.line((x0,y0,x,y),fill=color,width=4);d.ellipse((x-7,y-7,x+7,y+7),outline=color,width=3)
        d.text((x+8,y+8),str(number)+' '+label,font=font,fill=color,stroke_width=2,stroke_fill='black')
    d.ellipse((x0-12,y0-12,x0+12,y0+12),outline='lime',width=4);d.text((x0+10,y0-35),'20: k=0',font=font,fill='lime',stroke_width=2,stroke_fill='black')
    d.rectangle((0,885,2160,930),fill='white');d.text((20,890),'All27 maker nodes retain both charts and global reversal; local graph consistency does not establish the photo model.',font=font,fill='black');im.save(out/'indexing-star.png')


def perspective_sensitivity(out=OUT):
    # Reconstruct planar seed under nominal pinhole camera before comparing;
    # do not mistake global planar projective warp for a centerline correction.
    models=json.loads((out/'models.json').read_text());selected=json.loads((out/'selected.json').read_text());results=[]
    exif=Image.open(ROOT/'beads-photo-2.jpg').getexif().get_ifd(34665)
    metadata={ExifTags.TAGS.get(k,str(k)):(str(exif[k]) if isinstance(exif[k],str) else float(exif[k])) for k in [37386,41989,41988,42036] if k in exif}
    nominal=float(np.hypot(2540,3182)*51/np.hypot(36,24))
    for mid in selected:
        summary=next(r for r in models if r['model_id']==mid);m=Model(summary['n'],summary['h'],summary['p']);p=m.p
        r,d,eye=m.view.basis();A=np.array([r[:2],d[:2]])
        for focal in [nominal,2*nominal]:
            P=m.seed_image_curve-np.array([1269.5,1590.5]);mat=A[None,:,:]+P[:,:,None]*eye[None,None,:2]/focal
            plane=np.linalg.solve(mat,P[...,None])[...,0]
            arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))];length=arc[-1];scale=length/(ROW*m.source.nrows)
            arc/=length;t=np.arange(m.source.nbeads)/m.source.nbeads;ds,tw=correction(t,p);f=(t+p[1]/m.source.nbeads+ds)%1
            xy=np.column_stack([np.interp(f,arc,plane[:,j]) for j in [0,1]])/scale
            dt=np.gradient(plane,axis=0);tt=np.column_stack([np.interp(f,arc,dt[:,j]) for j in [0,1]]);tt/=np.linalg.norm(tt,axis=1)[:,None]
            normal=np.c_[-tt[:,1],tt[:,0],np.zeros(len(tt))];phase=p[0]+m.source.helicity*2*np.pi*m.source.nrows*t+tw
            radial=np.sin(phase)[:,None]*normal;radial[:,2]=np.cos(phase)
            centers=np.c_[xy,np.zeros(len(xy))]+4*radial
            def project(x):return np.c_[x@r,x@d]*scale/(1-scale*(x@eye)[:,None]/focal)+[1269.5+p[2],1590.5+p[3]]
            old=m.view.project(m.geometry(np.arange(m.source.nbeads))['centers']);new=project(centers);delta=np.linalg.norm(new-old,axis=1)
            # Same image arc at sampled plane points must be preserved exactly.
            repro=project(np.c_[plane/scale,np.zeros(len(plane))])-[p[2],p[3]]
            results.append(dict(model_id=mid,focal_pixels=focal,centerline_reprojection_max=float(np.linalg.norm(repro-m.seed_image_curve,axis=1).max()),same_index_center_shift_rms=float(np.sqrt(np.mean(delta**2))),same_index_center_shift_max=float(delta.max()),scale_ratio=scale/m.view.scale,status='Sensitivity only; no camera refit, pinhole visibility fit or calibrated intrinsics'))
    save(out/'perspective-sensitivity.json',dict(metadata=metadata,nominal_focal_pixels=nominal,results=results,warning='35mm equivalent plus digital zoom and unknown crop does not establish intrinsics. Reparameterizing arc in a tilted perspective plane redistributes string stations; same-index displacements include that change.'))


def charts_and_tables(out=OUT):
    models=json.loads((out/'models.json').read_text());rows=[]
    for m in models:
        rows.append(dict(model_id=m['model_id'],N=m['n'],h=m['h'],T=m['turns'],q=m['q'],kind=m['kind'],train_n=m['train']['center']['count'],test_n=m['test']['center']['count'],score=m['train_score'],all_center_mean=m['all']['center']['mean'],all_center_SSE=m['all']['center']['sse'],all_center_RMS=m['all']['center']['rms'],all_center_median=m['all']['center']['median'],all_center_p90=m['all']['center']['p90'],all_surface_mean=m['all']['surface']['mean'],all_surface_SSE=m['all']['surface']['sse'],all_surface_RMS=m['all']['surface']['rms'],all_surface_median=m['all']['surface']['median'],all_surface_p90=m['all']['surface']['p90'],test_surface_RMS=m['test']['surface']['rms'],test_surface_balanced_RMS=m['test']['balanced_surface_rms'],test_ownership=m['test']['ownership'],all_ownership=m['all']['ownership'],test_patch_support=m['test']['patch_support'],conditional_unique=m['all']['conditional_unique'],stretch_max=m['stretch_max'],stretch_RMS=m['stretch_rms'],twist_max_deg=m['twist_max_deg'],twist_RMS_deg=m['twist_rms_deg']))
    table(out/'model-comparison.csv',rows)
    # Cross-model assignment alternatives kept explicit: same numerical k across
    # different N is not itself agreement about physical identity.
    choices=[]
    for row in data():
        options=[]
        for m in models:
            rr=json.loads((out/f'{m["model_id"]}-assignments.json').read_text());r=next(r for r in rr if r['observation_id']==row['observation_id'])
            options.append(dict(model_id=m['model_id'],k=r['k'],ownership=r['ownership'],conditional_unique=r['conditional_unique'],alternatives=r['alternatives']))
        choices.append(dict(observation_id=row['observation_id'],models=options,status='No cross-model physical identity certified'))
    save(out/'cross-model-identities.json',choices)
    # Residual vector means quantify centerline/registration mismatch before any
    # centerline correction; interior-to-center offset remains a confounder.
    diagnostics=[]
    for mid in json.loads((out/'selected.json').read_text()):
        rr=json.loads((out/f'{mid}-assignments.json').read_text())
        for sector in range(1,33):
            use=[r for r in rr if r['sector']==sector];delta=np.array([[r['x'],r['y']] for r in use])-np.array([r['projected_center'] for r in use])
            diagnostics.append(dict(model_id=mid,sector=sector,n=len(use),mean_dx=float(delta[:,0].mean()),mean_dy=float(delta[:,1].mean()),mean_vector_length=float(np.linalg.norm(delta.mean(axis=0))),center_rms=float(np.sqrt(np.mean(np.sum(delta**2,axis=1))))))
    table(out/'sector-vector-mismatch.csv',diagnostics)
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(12,4))
    for channel in ['V','Y']:
        rr=[r for r in csv.DictReader((out/'fft-profile.csv').read_text().splitlines()) if r['channel']==channel];ax.plot([float(r['s']) for r in rr],[float(r['local_n_equivalent']) for r in rr],lw=.7,label=channel)
    ax.set(xlabel='Image centerline arc length (pixels)',ylabel='Local tangent frequency × loop length ×6.5');ax.legend();fig.tight_layout();fig.savefig(out/'fft-count-profile.png',dpi=170);plt.close(fig)


# This second, independent plot separates added winding phase from the change
# in winding per physical arc induced by longitudinal redistribution.
def winding_profiles(out=OUT):
    import matplotlib.pyplot as plt
    models=json.loads((out/'models.json').read_text());selected=json.loads((out/'selected.json').read_text())
    t=np.arange(2048)/2048;rows=[];fig,axs=plt.subplots(2,1,figsize=(12,7))
    for mid in selected:
        m=next(m for m in models if m['model_id']==mid);p=np.array(m['p']);model=Model(m['n'],m['h'],p)
        a=2*np.pi*t;stretch=harmonics(t)@p[6:10]
        derivative=np.array([2*np.pi*np.cos(a),-2*np.pi*np.sin(a),4*np.pi*np.cos(2*a),-4*np.pi*np.sin(2*a)]).T@p[10:14]
        extra=derivative/(m['h']*2*np.pi*m['turns']);total=(1+extra)/(1+stretch)-1
        f=model.geometry(t*m['n'])['fraction'];u=np.interp(f,model.arc_fraction,model.u_table);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(model.seed_image_curve,axis=0),axis=1))];s=np.interp(u,model.u_table,arc);order=np.argsort(s)
        axs[0].plot(s[order],extra[order]*100,label=mid);axs[1].plot(s[order],total[order]*100,label=mid)
        rows.extend(dict(model_id=mid,s_px=float(ss),material_fraction=float(tt),stretch=float(st),added_winding_rate_relative=float(er),total_winding_per_arc_relative=float(tr)) for ss,tt,st,er,tr in zip(s,t,stretch,extra,total))
    for ax,label in zip(axs,['Extra winding rate at fixed material coordinate (%)','Total winding rate per redistributed physical arc (%)']):ax.set(xlabel='Image spline arc length (pixels)',ylabel=label);ax.legend(fontsize=7,ncol=2)
    fig.tight_layout();fig.savefig(out/'winding-rate.png',dpi=170);plt.close(fig);table(out/'correction-profiles.csv',rows)

if __name__=='__main__':
    neighborhood();perspective_sensitivity();charts_and_tables();winding_profiles()
