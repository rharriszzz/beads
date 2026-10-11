"""Physical sensitivity, distributed curve assembly, native ownership audits."""
import copy,csv,json
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from .refit import OUT,ROOT,BeadCurve,SurfaceLoss,apply,audit,physical,evidence
from .raycast import trace
from .generate import save,sha


def run():
    results=json.loads((OUT/'results.json').read_text());base=json.loads((OUT/'initial.json').read_text());bm=BeadCurve(base);n=base['n'];origin=base['origin'];t=(origin+2)/n
    ev=json.loads((OUT/'origin-evidence.json').read_text());rows=ev['observations'];pp=np.array(next(r for r in rows if r['identity']==2)['patch']);b2=origin+2
    perturbations=[];names=['curve_x','curve_y','tangent_x','tangent_y','curvature_x','curvature_y','phase','winding','elevation','roll','registration_x','registration_y','longitudinal_spacing','camera_log_scale'];magnitudes=[3,3,12,12,24,24,.2,.3,2,.3,3,3,4,.005]
    def score(c,label,amount,size=1,axial=1):
        m=BeadCurve(c);g=m.geometry(np.arange(n));own,_,un=trace(m,pp,g,size,axial);records=[]
        for r in rows:
            p=np.array(r['patch']);oo,_,uu=trace(m,p,g,size,axial);v,ct=np.unique(oo[(oo>=0)&(uu==0)],return_counts=True);j=int(v[np.argmax(ct)]) if len(v) else -1
            if r['identity'] is not None:j=(origin+r['identity'])%n
            records.append(dict(id=r['id'],owner=j,fraction=float(np.mean((oo==j)&(j>=0)&(uu==0)))))
        line=m.view.project(g['line']);old=bm.view.project(bm.geometry(np.arange(n))['line']);der=m.curve(t,1);dder=m.curve(t,2)
        return dict(parameter=label,amount=float(amount),bead2_confirmed_fraction=float(np.mean((own==b2)&(un==0))),candidate_ownership_mean=float(np.mean([r['fraction'] for r in records])),records=records,physical=physical(m),curve_max_displacement_px=float(np.linalg.norm(line-old,axis=1).max()),tangent_at_origin=der.tolist(),curvature_at_origin=float(np.linalg.norm(np.cross(der,dder))/np.linalg.norm(der)**3))
    perturbations.append(score(base,'baseline',0))
    for j,(name,mag) in enumerate(zip(names,magnitudes)):
        for sign in [-1,1]:
            p=np.zeros(14);p[j]=mag*sign;perturbations.append(score(apply(base,t,p,'D'),name,mag*sign))
    for v in [.95,1.05]:perturbations.append(score(base,'bead_radius_factor',v,size=v))
    for v in [.9,1.1]:perturbations.append(score(base,'axial_height_factor',v,axial=v))
    for focal in [4799.175227618243,9598.350455236487,19196.700910472974]:
        c=copy.deepcopy(base);c['focal']=focal;perturbations.append(score(c,'pinhole_focal_px_uncalibrated',focal))
    save(OUT/'sensitivity.json',perturbations)
    # One-at-a-time removals from each fitted origin variant are conditional
    # contributions, not uniquely identifiable causal attributions.
    ablations=[]
    for variant in ['C','D']:
        r=next(r for r in results if r['id']==f'R258_origin_{variant}');p=np.array(r['parameters']);loss=SurfaceLoss(ev['box'],rows)
        for label,indices in [('full',[]),('no displacement',[0,1]),('no tangent',[2,3]),('no curvature',[4,5]),('no phase',[6]),('no winding',[7]),('no camera',[8,9,10,11,13]),('no spacing',[12])]:
            q=p.copy();q[indices]=0;c=apply(base,t,q,variant);a=audit(c,loss);ablations.append(dict(variant=variant,removed=label,metrics=a['metrics'],bead2=next(x for x in a['observations'] if x['identity']==2)))
    save(OUT/'ablations.json',ablations)
    # Native all-neighbor metrology: current assignments retained and tracked.
    neighbors=sorted({(origin+k+d)%n for k in range(8) for d in [0,-1,1,-6,6,-7,7]});native=[];index_tests=[]
    y,x=np.mgrid[ev['box'][1]:ev['box'][3],ev['box'][0]:ev['box'][2]];xy=np.c_[x.ravel(),y.ravel()]
    for variant in ['A','B','C','D']:
        c=json.loads((OUT/f'R258_origin_{variant}.json').read_text());m=BeadCurve(c);g=m.geometry(np.arange(n));owner,_,un=trace(m,xy,g)
        for i in neighbors:
            fp=xy[(owner==i)&(un==0)];iso={k:v[g['indices']==i] for k,v in g.items()};isolated,_,_ =trace(m,pp,iso)
            oo,_,uu=trace(m,pp,g)
            native.append(dict(variant=variant,generator_index=i,k=(i-origin)%n,visible_area_px2=len(fp),visible_centroid=fp.mean(axis=0).tolist() if len(fp) else None,physical_center=m.view.project(g['centers'][i:i+1])[0].tolist(),bead2_evidence_owned=float(np.mean((oo==i)&(uu==0))),bead2_evidence_owned_without_neighbors=float(np.mean(isolated==i))))
        for offset in [0,-1,1,-6,6,-7,7]:
            i=(b2+offset)%n;fp=xy[(owner==i)&(un==0)]
            from scipy.spatial import cKDTree
            dist=cKDTree(fp).query(pp)[0] if len(fp) else np.full(len(pp),200.)
            index_tests.append(dict(variant=variant,offset=offset,hypothetical_k=(i-origin)%n,bead2_fraction=float(np.mean(oo==i)),distance_mean_px=float(dist.mean()),distance_max_px=float(dist.max()),status='Identity alternative diagnostic only; maker review address is unchanged'))
    save(OUT/'native-neighbors.json',native);save(OUT/'index-occlusion.json',index_tests)
    # Assemble the four fitted compact C supports into ONE periodic physical
    # curve. No averaging toward initial curve or old edges, no global refit.
    global_c=copy.deepcopy(base);knots=np.array(base['knots']);global_c['id']='R258_distributed_C'
    for name in ['origin','straight-black','bend','opposite']:
        c=json.loads((OUT/f'R258_{name}_C.json').read_text());knots+=np.array(c['knots'])-np.array(base['knots'])
    global_c['knots']=knots.tolist();global_c['variant']='assembled C';global_c['independence']='Four bead-fitted local supports; other spans are initialization/interpolation, not photographic reconstruction';save(OUT/'R258_distributed_C.json',global_c)
    gm=BeadCurve(global_c);measurements={};frozen=apply(base,t,np.zeros(13),'A')
    for name in ['origin','straight-black','bend','opposite']:
        e=json.loads((OUT/(name+'-evidence.json')).read_text());loss=SurfaceLoss(e['box'],e['observations']);measurements[name]=dict(before=audit(frozen,loss),after=audit(global_c,loss))
    # A fifth geographic region is never fitted/used to pick flexibility.
    j=(origin+2300)%n;p=bm.view.project(bm.geometry([j])['centers'])[0];box=[int(p[0]-110),int(p[1]-100),int(p[0]+110),int(p[1]+100)]
    inv=json.loads((ROOT/'photo2/output/debugger/generated/observations.json').read_text());held=evidence(inv,box,'spatial-holdout');loss=SurfaceLoss(box,held)
    save(OUT/'spatial-holdout-evidence.json',dict(box=box,observations=held));measurements['spatial-holdout']=dict(before=audit(frozen,loss),after=audit(global_c,loss))
    fm=BeadCurve(frozen);old=fm.view.project(fm.geometry(np.arange(n))['line']);new=gm.view.project(gm.geometry(np.arange(n))['line']);delta=np.linalg.norm(old-new,axis=1)
    save(OUT/'global-summary.json',dict(physical=physical(gm),curve_displacement_px=dict(mean=float(delta.mean()),rms=float(np.sqrt(np.mean(delta**2))),max=float(delta.max()),fraction_displaced_over_1px=float(np.mean(delta>1))),sections=measurements,
                                     status='Inspect-only partial curve candidate; no global geometry or heldout improvement claim'))
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');panels=[]
    for points,title in [(old,'Initialized physical curve'),(new,'Four bead-fitted sections; intervening spans unverified')]:
        im=photo.copy();d=ImageDraw.Draw(im);d.line([tuple(p) for p in points]+[tuple(points[0])],fill=(50,255,255),width=3);im=im.resize((635,796));out=Image.new('RGB',(635,826),(20,32,42));out.paste(im,(0,30));ImageDraw.Draw(out).text((8,8),title,fill='white');panels.append(out)
    out=Image.new('RGB',(1270,826));out.paste(panels[0],(0,0));out.paste(panels[1],(635,0));out.save(OUT/'whole-photo-before-after.png')
    ids=json.loads((OUT/'model-index.json').read_text());save(OUT/'model-index.json',list(dict.fromkeys(ids+['R258_distributed_C'])))
    # Stable photographic IDs show conditional material-index changes explicitly.
    stability=[]
    for name in ['origin','straight-black','bend','opposite']:
        baseline=next(r for r in results if r['id']==f'R258_{name}_A');ref={r['id']:r for r in baseline['observations']}
        for candidate in [r for r in results if r['section']==name]:
            for r in candidate['observations']:
                stability.append(dict(model=candidate['id'],observation_id=r['id'],old_k=ref[r['id']]['k'],new_k=r['k'],changed=ref[r['id']]['k']!=r['k'],old_support=ref[r['id']]['owned_fraction'],new_support=r['owned_fraction']))
    save(OUT/'assignment-stability.json',stability)
    paths=[ROOT/'beads-photo-2.jpg',ROOT/'beads.pov',ROOT/'photo2/output/debugger/generated/observations.json',ROOT/'photo2/output/debugger/generated/positive-patches.npz',ROOT/'photo2/review/r257/observations.json',OUT/'bead2-reviewed-support.json']+list((ROOT/'photo2/bead_debugger').glob('*.py'))
    save(OUT/'provenance.json',dict(version='R258',sources={str(p.relative_to(ROOT)):sha(p) for p in paths},fit_command='.venv/bin/python -m photo2.bead_debugger.refit --budget 400',audits=['.venv/bin/python -m photo2.bead_debugger.alternatives_r258','.venv/bin/python -m photo2.bead_debugger.audit_r258','.venv/bin/python -m photo2.bead_debugger.report_r258'],heldout_rule='whole detector connected-component groups + distant spatial regions; no per-pixel split',limitations='Component grouping conservative, but unreviewed fragmentation can cross physical bodies; no certified full masks. Source dimensions fixed; sensitivity only. Orthographic planar specialization.'))
if __name__=='__main__':run()
