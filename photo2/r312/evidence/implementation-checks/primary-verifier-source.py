"""Independent analytic witnesses, historical Python rays, optics and arithmetic."""
from pathlib import Path
from types import MethodType
import hashlib,math,subprocess,tarfile,time
import numpy as np
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as OriginalGeometry
from photo2.r309.geometry import Chain as Previous
from photo2.r299.forward import Surface
from photo2.r295.geometry import AXES
from photo2.r295.physical_audit import independent_support
from photo2.r309.render import predict

def recompute(rows):
    errors=[];missing=0
    for row in rows:
        if row['predicted'] is None:
            assert row['error_px'] is None;missing+=1;continue
        x,y=row['observed'];u,v=row['predicted'];e=math.hypot(u-x,v-y)
        assert abs(e-row['error_px'])<1e-10
        assert abs(u-x-row['dx_px'])<1e-10 and abs(v-y-row['dy_px'])<1e-10
        assert abs(row['tangent_px']**2+row['normal_px']**2-e*e)<1e-8
        errors.append(e)
    return dict(maximum_px=max(errors) if errors else None,rms_px=math.sqrt(math.fsum(e*e for e in errors)/len(errors)) if errors else None,p95_px=float(np.percentile(errors,95)) if errors else None,missing=missing,objective_px=10000*missing+max(errors,default=0.))

def run(root):
    root=Path(root);began=time.monotonic();data,m,obs=load();allmodels=[];trials=0;stages=[]
    milestone=read(root/'stage1/milestone.json')
    assert milestone['sealed_selection_and_initial_static_diagnostics_completed_before_stage2']
    assert sha(root/'stage1/checkpoint.json')==milestone['checkpoint_sha256']
    assert sha(root/'stage1/selection.json')==milestone['selection_sha256']
    assert sha(root/'stage1'/milestone['diagnostics_snapshot'])==milestone['diagnostics_sha256']
    for stage in [1,2]:
        directory=root/f'stage{stage}';checkpoint=read(directory/'checkpoint.json');assert checkpoint['sealed']
        selection=read(directory/'selection.json');assert selection['sealed']
        archive=directory/'fitting-source/source.tar.gz'
        if not archive.exists():archive=ROOT/f'photo2/r312/evidence/stage{stage}-source/source.tar.gz'
        with tarfile.open(archive,'r:gz') as tar:
            stored={member.name:hashlib.sha256(tar.extractfile(member).read()).hexdigest() for member in tar.getmembers()}
        assert stored==checkpoint['sources'],'Fitting-source archive differs'
        keys=set();count=0
        local_checkpoint=directory/'local/checkpoint.json'
        if stage==2 and local_checkpoint.exists():
            local=read(local_checkpoint);assert local['sealed']
            with tarfile.open(directory/'local/fitting-source/source.tar.gz','r:gz') as tar:
                local_sources={member.name:hashlib.sha256(tar.extractfile(member).read()).hexdigest() for member in tar.getmembers()}
            assert local_sources==local['sources']
            for file in sorted((directory/'local/calibration').glob('*.gz')):
                control=read(file);old=read(directory/'calibration'/file.name)
                assert control['parameters']==old['parameters']
                mapping=control['result']['mapping'];assert len(mapping)==269
                values=[v for v in mapping.values() if v is not None]
                assert len(values)==len(set(values))
                arithmetic=recompute(control['result']['reflections'])
                for key,value in arithmetic.items():
                    actual=control['result']['metrics'][key]
                    assert value is actual is None or (value is not None and actual is not None and abs(value-actual)<1e-8)
        trialfiles=sorted((directory/'trials').glob('*.gz'))
        if stage==2:trialfiles+=sorted((directory/'local/trials').glob('*.gz'))
        for file in trialfiles:
            row=read(file);count+=1;assert row['key'] not in keys;keys.add(row['key'])
            if not row.get('feasible'):continue
            expected_map=checkpoint['mappings'][row['family']]
            if stage==2 and file.parent.parent.name=='local':expected_map=read(directory/'local/calibration'/f'{row["family"]}.json.gz')['result']['mapping']
            assert row['result']['physical']['certified'];assert row['result']['mapping']==expected_map
            arithmetic=recompute(row['result']['reflections'])
            for key,value in arithmetic.items():
                actual=row['result']['metrics'][key]
                assert value is actual is None or (value is not None and actual is not None and abs(value-actual)<1e-8),(file,key)
        trials+=count
        for file in sorted((directory/'exports').glob('*.json.gz')):
            model=read(file);p=model['parameters'];s=Previous(p,data)
            np.testing.assert_allclose(s.centers,[b['center'] for b in model['positions']],atol=1e-10,rtol=0)
            expected_indices=np.arange(s.indices[0],s.indices[0]+p['count'])
            np.testing.assert_array_equal([b['index'] for b in model['positions']],expected_indices)
            assert sum(b['stage1_cohort'] for b in model['positions'])==200
            frame=np.stack([s.g[k] for k in AXES],axis=1)
            np.testing.assert_allclose(frame@np.swapaxes(frame,1,2),np.broadcast_to(np.eye(3),frame.shape),atol=1e-12,rtol=0)
            assert np.min(np.linalg.det(frame))>1-1e-12
            original=OriginalGeometry(p,data);height=(original.project(original.line)[:,1]-1591)/1591
            expected=original.line+p['minor']*(1+p.get('minor_y',0)*height)[:,None]*original.g['radial']
            np.testing.assert_allclose(expected,s.centers,atol=1e-10,rtol=0)
            fine=Previous(p,data,resolution=32769);arc_delta=float(np.linalg.norm(fine.pc-s.pc,axis=1).max());assert arc_delta<.005
            pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray');by_pair={tuple(w['pair']):w for w in model['physical']['witnesses']}
            assert len(pairs)==len(by_pair)
            gaps=[]
            for a,b in pairs:
                w=by_pair[(int(a),int(b))];n=np.array(w['normal']);gap=float((s.centers[b]-s.centers[a])@n-independent_support(n,s.g[AXES[0]][a],s.radius,s.axial)-independent_support(n,s.g[AXES[0]][b],s.radius,s.axial))
                assert gap>0 and abs(gap-w['gap_units'])<1e-8;gaps.append(gap)
            native=directory/'exports'/f'{model["name"]}-native.npz';assert sha(native)==model['raster_sha256'];raster=np.load(native)
            sample=np.linspace(0,len(raster['xy'])-1,min(12000,len(raster['xy']))).astype(int)
            s.trace=MethodType(OriginalGeometry.trace,s);s.blocked=MethodType(Surface.blocked,s)
            xy=raster['xy'][sample];tr=s.trace(xy)
            np.testing.assert_array_equal(tr['owner'],raster['owner'][sample]);np.testing.assert_array_equal(tr['unknown'],raster['unknown'][sample])
            np.testing.assert_allclose(tr['points'],raster['points'][sample],atol=1e-8,rtol=0)
            guard_ix=np.linspace(0,len(raster['guard_xy'])-1,min(16000,len(raster['guard_xy']))).astype(int)
            tr=s.trace(raster['guard_xy'][guard_ix]);np.testing.assert_array_equal(tr['owner'],raster['guard_owner'][guard_ix]);np.testing.assert_array_equal(tr['unknown'],raster['guard_unknown'][guard_ix])
            # Original compiled predictor recomputes EVERY fitted native lobe.
            fast=Previous(p,data);owners=np.flatnonzero((fast.indices>=-100)&(fast.indices<=99)) if stage==1 else np.array(sorted({v-int(fast.indices[0]) for v in model['mapping'].values() if v is not None}),int)
            predictions,meta=predict(fast,1.,owners=owners);lookup={r['index']:r for r in predictions}
            for row in model['result']['reflections']:
                r=lookup.get(row['index']);assert (r is None)==(row['predicted'] is None)
                if r:np.testing.assert_allclose(r['point'],row['predicted'],atol=1e-9,rtol=0)
            # Independent Python optics for the actual twenty worst errors.
            worst=sorted([r for r in model['result']['reflections'] if r['error_px'] is not None],key=lambda r:-r['error_px'])[:20]
            selected=np.array(sorted({r['index']-int(s.indices[0]) for r in worst}),int)
            python_pred,python_meta=predict(s,1.,owners=selected);python_lookup={r['index']:r for r in python_pred}
            for row in worst:
                assert row['index'] in python_lookup
                np.testing.assert_allclose(python_lookup[row['index']]['point'],row['predicted'],atol=1e-9,rtol=0)
            arithmetic=recompute(model['result']['reflections'])
            for key,value in arithmetic.items():
                actual=model['result']['metrics'][key];assert value is actual is None or (value is not None and actual is not None and abs(value-actual)<1e-8)
            assert model['top20']==worst
            if stage==2 and model.get('correspondence_epoch')=='full-chain':
                calibration=read(directory/'local/calibration'/f'{model["family"]}.json.gz');assert model['mapping']==calibration['result']['mapping']
                assert len(model['mapping'])==269
            elif stage==2:
                prior=read(root/'stage1/checkpoint.json')['mappings'].get(model.get('family',model['name'].removeprefix('baseline-')),{})
                for key,value in prior.items():assert model['mapping'][key]==value
            receipt=dict(name=model['name'],stage=stage,positions=s.n,independent_contact_pairs=len(pairs),minimum_independent_margin=min(gaps),python_camera_and_guard_rays=len(sample)+len(guard_ix),original_compiled_optical_rays=meta['rays'],python_top20_optical_rays=python_meta['rays'],arclength_refinement_max_px=arc_delta,all_primary_centroids_agree_1e_minus9_px=True,top20_python_centroids_agree_1e_minus9_px=True,all_200_physical_addresses_present=True)
            allmodels.append(receipt);print('independently verified',stage,model['name'],flush=True)
        stages.append(dict(stage=stage,trial_vectors=count,source_files=len(stored),source_archive_sha256=sha(archive),frozen_mapping_exact=True))
    protected=read(ROOT/'photo2/r312/evidence/preservation.json.gz');head=read(ROOT/'photo2/r312/evidence/start.json')['head'];additive=[]
    for path,h in protected.items():
        if sha(ROOT/path)==h:continue
        assert path in ['AGENTS.md','PLAN.md','METHODS.md','REQUEST_LOG.md','SESSION_HANDOFF.md','.gitignore'],path
        before=subprocess.check_output(['git','show',head+':'+path]);assert before in (ROOT/path).read_bytes(),path;additive.append(path)
    result=dict(passed=True,utc=utc(),models=allmodels,stages=stages,unique_trial_vectors=trials,
                positions=sum(r['positions'] for r in allmodels),independent_contact_witnesses=sum(r['independent_contact_pairs'] for r in allmodels),
                original_python_camera_and_guard_rays=sum(r['python_camera_and_guard_rays'] for r in allmodels),
                original_compiled_optical_rays=sum(r['original_compiled_optical_rays'] for r in allmodels),
                original_python_top20_optical_rays=sum(r['python_top20_optical_rays'] for r in allmodels),
                historical_files_checked=len(protected),historical_science_changed=[],additive_handoffs=additive,physical_identities_verified=0,seconds=time.monotonic()-began)
    save(root/'verification.json',result);return result

if __name__=='__main__':run(ROOT/'photo2/r312/results/campaign')
