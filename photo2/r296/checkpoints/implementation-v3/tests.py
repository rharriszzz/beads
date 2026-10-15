"""Geometry, evidence isolation, transactional resume and real-photo contracts."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from .common import *
from .geometry import *
from .objective import Objective,beam_assign
from .search import Runner,select_population,starting_models


def settings(n):
    return dict(seed=296,population=8,patience=256,min_delta=.0005,count_min=None,count_max=None,seconds=1000,max_evaluations=n)


def science(value):
    if isinstance(value,dict):return {k:science(v) for k,v in value.items() if k not in ('seconds','elapsed_seconds','created','utc')}
    if isinstance(value,list):return [science(x) for x in value]
    return value

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read(EVIDENCE/'inputs.json.gz')
        base=read(ROOT/'photo2/r295/results/hand-plus-evaluation.json')['parameters']
        cls.p=full_parameters(base,2709)
        cls.scene=Chain(cls.p,cls.data)

    def test_full_domain_historical_labels_and_monotonic_spacing(self):
        s=self.scene
        self.assertEqual(len(s.indices),2709)
        self.assertEqual(list(s.indices[(s.indices>=-20)&(s.indices<=200)]),list(range(-20,201)))
        self.assertTrue(np.all(np.diff(s.station_px)>0))
        self.assertGreater(np.ptp(s.pc[:,0]),2000)
        self.assertGreater(np.ptp(s.pc[:,1]),2600)
        self.assertTrue(np.isfinite(s.centers).all())

    def test_closed_position_orientation_phase_spacing(self):
        s=self.scene;c=s.closure()
        for key in ('axis_endpoint_gap','radial_endpoint_gap','tangent_endpoint_gap'):self.assertLess(c[key],1e-8)
        self.assertAlmostEqual(c['phase_turns'],s.p['hand']*s.p['winding'],places=10)
        k=np.array([-s.n/2-.1,-s.n/2+.1,s.n/2-.1,s.n/2+.1]);line,g,_=s.placement(k)
        np.testing.assert_allclose(line[1]-line[0],line[3]-line[2],atol=1e-9)
        np.testing.assert_allclose(np.cross(g[AXES[0]],g[AXES[1]]),g[AXES[2]],atol=1e-10)

    def test_open_topology_is_not_forced_periodic(self):
        p=copy.deepcopy(self.p);p['topology']='open';p['gap_steps']=2.
        c=Chain(p,self.data).closure()
        self.assertGreater(c['axis_endpoint_gap'],.1)
        self.assertIsNone(c['integer_winding'])

    def test_contact_includes_seam_and_independent_witness(self):
        c=contact(self.scene,exact=True)
        self.assertTrue(c['certified'])
        pairs=[w['pair'] for w in c['witnesses']]
        self.assertIn([0,self.scene.n-1],pairs)
        self.assertGreater(c['independent_minimum_gap'],0)

    def test_r295_extension_collision_is_demonstrated(self):
        b=read(ROOT/'photo2/r295/results/joint.json')['selected']['parameters']
        c=contact(Chain(full_parameters(b,2540),self.data))
        self.assertFalse(c['certified']);self.assertEqual(c['state'],'demonstrated-interpenetration')
        witness=next(r for r in c['fallback'] if r['state']=='demonstrated-interpenetration')
        self.assertTrue(max(witness['implicit_values'])<0)

    def test_volume_budget_exhaustion_not_separation(self):
        b=read(ROOT/'photo2/r295/results/joint.json')['selected']['parameters'];s=Chain(full_parameters(b,2540),self.data)
        cert=s.certify();w=next(r for r in cert['witnesses'] if not r['separated'])
        r=audit_pair(s,*w['pair'],max_nodes=0,max_depth=0)
        self.assertIn(r['state'],['unresolved','demonstrated-interpenetration'])

    def test_frozen_geographic_separation_and_human_provenance(self):
        f=read(EVIDENCE/'freeze.json')
        self.assertEqual(sha(EVIDENCE/'inputs.json.gz'),f['inputs_sha256'])
        self.assertGreater(f['min_train_withheld_pixel_distance'],35)
        for r in self.data['rows']:
            if r['accepted']:self.assertEqual(r['split'],'train');self.assertTrue(r['provenance'])
        self.assertGreater(f['counts']['reserved']['region'],10)

    def test_reserved_access_guard(self):
        with self.assertRaisesRegex(ValueError,'sealed'):Objective(self.data,'reserved')
        obj=Objective(self.data,'train','coarse')
        self.assertTrue(all(r['split']=='train' for r in obj.rows))
        a=obj.assess(self.scene)
        ids={r['id'] for r in a['assignments']}
        self.assertFalse(ids & {r['id'] for r in self.data['rows'] if r['split']=='reserved'})

    def test_trace_inherited_and_minus999_is_real_site(self):
        self.assertIs(Chain.trace,LocalChain.trace)
        self.assertIn(-999,self.scene.indices)
        xy=np.asarray(self.data['anchor']['measured_photo_location'])[None]
        a=self.scene.trace(xy);b=self.scene.trace(np.vstack([xy,xy]))
        self.assertEqual(a['owner'][0],b['owner'][1])
        self.assertTrue(np.isfinite(a['points']).all())

    def test_seed_counts_derive_from_image_not_generator(self):
        starts,bounds=starting_models(self.data,296)
        counts={r['parameters']['count'] for r in starts}
        self.assertGreater(len(counts),10)
        self.assertEqual({r['parameters']['hand'] for r in starts},{-1,1})
        self.assertEqual({r['parameters']['topology'] for r in starts},{'open','closed'})
        self.assertLess(bounds[0],2500);self.assertGreater(bounds[1],3000)

    def test_population_preserves_best_and_topology_hand(self):
        rows=[]
        for i,(h,t) in enumerate([(-1,'closed'),(-1,'open'),(1,'closed'),(1,'open')]*3):
            p=copy.deepcopy(self.p);p.update(hand=h,topology=t,count=2709+i)
            rows.append(dict(id=i,parameters=p,train=dict(score=float(i)),validation=dict(score=float(i))))
        pop=select_population(rows,8)
        self.assertEqual(pop[0]['id'],11)
        self.assertEqual({(r['parameters']['hand'],r['parameters']['topology']) for r in pop},{(-1,'closed'),(-1,'open'),(1,'closed'),(1,'open')})

    def test_atomic_save_and_immutable_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'state.json.gz';save(p,dict(a=1));before=p.read_bytes();save(p,dict(a=1));self.assertEqual(before,p.read_bytes())
            self.assertFalse(p.with_name(p.name+'.tmp').exists())

class Transactions(unittest.TestCase):
    def test_no_feasible_start_stops_with_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Runner(tmp,settings(100));run.state['starts']=[];state=run.run()
            self.assertEqual(state['stop_reason'],'no-feasible-start')
            self.assertEqual(state['next_id'],0)

    def test_actual_sigterm_does_not_seal_or_export(self):
        import subprocess,time,signal
        with tempfile.TemporaryDirectory() as tmp:
            command=[str(ROOT/'.venv/bin/python'),str(ROOT/'photo2/phase2_autofit.py'),'--output',tmp,'--max-evaluations','100','--seal']
            process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            try:
                deadline=time.monotonic()+30
                while time.monotonic()<deadline:
                    path=Path(tmp)/'checkpoint.json'
                    if path.exists() and read(path)['next_id']>=1:break
                    if process.poll() is not None:self.fail('Search exited before signal')
                    time.sleep(.05)
                process.send_signal(signal.SIGTERM)
                _,errors=process.communicate(timeout=30)
                self.assertEqual(process.returncode,0,errors)
                state=read(Path(tmp)/'checkpoint.json')
                self.assertEqual(state['stop_reason'],'signal');self.assertFalse(state['sealed'])
                self.assertFalse((Path(tmp)/'final-freeze.json').exists())
            finally:
                if process.poll() is None:process.kill();process.communicate()

    def test_uninterrupted_vs_resume_and_postwrite_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);full=Runner(root/'full',settings(8));full.run()
            short=Runner(root/'resumed',settings(4));short.run()
            resumed=Runner(root/'resumed',settings(8),True);resumed.run()
            for n in range(8):self.assertEqual(science(read(full.path(n))),science(read(resumed.path(n))))
            self.assertEqual(full.state['pool'],resumed.state['pool']);self.assertEqual(full.state['rng'],resumed.state['rng'])
            # Simulate crash after durable candidate write, before incorporation.
            crashed=Runner(root/'crashed',settings(2));crashed.state['pending']=copy.deepcopy(full.state['starts'][0])
            crashed.state['pending'].update(stage='A',parent=None,operation='global hypothesis');crashed.checkpoint()
            save(crashed.path(0),read(full.path(0)))
            recovered=Runner(root/'crashed',settings(2),True)
            original=recovered.evaluate
            def guard(trial,n):
                self.assertNotEqual(n,0,'Completed evaluation repeated')
                return original(trial,n)
            with patch.object(recovered,'evaluate',side_effect=guard):recovered.run()
            self.assertEqual(science(read(full.path(1))),science(read(recovered.path(1))))

    def test_sealed_run_and_changed_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Runner(tmp,settings(1));run.checkpoint();state=read(Path(tmp)/'checkpoint.json')
            state['sealed']=True;save(Path(tmp)/'checkpoint.json',state)
            with self.assertRaisesRegex(ValueError,'Sealed'):Runner(tmp,settings(2),True)
            state['sealed']=False;state['sources']={};save(Path(tmp)/'checkpoint.json',state)
            with self.assertRaisesRegex(ValueError,'Implementation changed'):Runner(tmp,settings(2),True)

    def test_time_budget_and_signal_stop_before_trial(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Runner(tmp,settings(100));run.config['seconds']=1e-9;state=run.run()
            self.assertEqual(state['next_id'],0);self.assertEqual(state['stop_reason'],'time-budget')
        with tempfile.TemporaryDirectory() as tmp:
            run=Runner(tmp,settings(100));run.interrupt(None,None);state=run.run()
            self.assertEqual(state['next_id'],0);self.assertEqual(state['stop_reason'],'signal')

if __name__=='__main__':unittest.main()
