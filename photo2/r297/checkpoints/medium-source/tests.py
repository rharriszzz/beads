"""Real-photo, geometry, accounting and transactional contracts."""
import copy
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from .common import *
from .geometry import *
from .objective import Objective,balanced_material
from .search import Runner,starting_models
from .experiments import settings
from photo2.r296.tests import science
from photo2.r296.geometry import Chain as OldChain


class Geometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,_=load_evidence()
        cls.old=read(ROOT/'photo2/r296/results/pilot/candidates/000188.json.gz')['parameters']
        cls.local=read(ROOT/'photo2/r295/results/joint.json')['selected']['parameters']

    def test_unmodified_r296_geometry_exact(self):
        a=Chain(self.old,self.data);b=OldChain(self.old,self.data)
        for key in ['centers','station_px','pc','phase']:np.testing.assert_array_equal(getattr(a,key),getattr(b,key))
        np.testing.assert_array_equal(a.trace([[1499,271],[2038,658]])['owner'],b.trace([[1499,271],[2038,658]])['owner'])

    def test_local_restoration_and_exterior_preservation(self):
        p=full_parameters(self.local,2337);base=Chain(p,self.data)
        p.update(local_metric=1.,local_turn=1.);s=Chain(p,self.data);local=LocalChain(self.local,self.data)
        i=np.flatnonzero((s.indices>=-20)&(s.indices<=200));j=np.searchsorted(local.indices,s.indices[i])
        self.assertLess(np.max(np.linalg.norm(s.pc[i]-local.pc[j],axis=1)),.03)
        outside=(s.indices< -151)|(s.indices>401)
        np.testing.assert_allclose(s.pc[outside],base.pc[outside],atol=1e-10)
        self.assertTrue(np.all(np.diff(s.station_px)>0))
        self.assertTrue(contact(s,exact=True)['certified'])

    def test_every_seam_family_closure_and_gap(self):
        for topo in ['open','closed']:
            for cut in [-.25,-.5,-.75]:
                p=full_parameters(self.local,2337,topo);p.update(local_metric=1.,local_turn=1.,seam_fraction=cut,gap_steps=2.)
                s=Chain(p,self.data);c=s.closure();self.assertIn(0,s.indices);self.assertIn(200,s.indices)
                self.assertEqual(len(s.indices),2337)
                if topo=='closed':
                    for key in ['axis_endpoint_gap','radial_endpoint_gap','tangent_endpoint_gap']:self.assertLess(c[key],1e-7)
                    self.assertAlmostEqual(abs(c['phase_turns']),p['winding'],places=9)
                else:self.assertGreater(c['axis_endpoint_gap'],.1);self.assertIsNone(c['integer_winding'])
                cert=contact(s,exact=True)
                if topo=='closed':self.assertTrue(cert['certified'],(topo,cut,cert['state']))
                elif not cert['certified']:
                    self.assertIn(cert['state'],['unresolved','demonstrated-interpenetration'])
                    if cert['state']=='demonstrated-interpenetration':self.assertTrue(any(r['state']=='demonstrated-interpenetration' and max(r['implicit_values'])<0 for r in cert['fallback']))

    def test_isolation_and_direct_material_score(self):
        with self.assertRaisesRegex(ValueError,'sealed'):Objective(self.data,'reserved')
        s=Chain(self.old,self.data)
        m=Objective(self.data,'validation').assess(s)
        self.assertAlmostEqual(m['score'],sum(m['objective_terms'].values()))
        self.assertTrue(all(r['split']=='validation' for r in Objective(self.data,'validation').rows))
        regions=[dict(kind='region',station=1.,containment=.8),dict(kind='region',station=400.,containment=.2)]
        a,_=balanced_material(regions,10000)
        b,_=balanced_material(regions+[dict(kind='patch',station=1.,containment=1.)]*10000,10000)
        self.assertEqual(a,b)

    def test_starts_keep_both_hands_counts_topologies_and_cuts(self):
        starts,bounds=starting_models(self.data,297)
        self.assertEqual(len(starts),32)
        self.assertGreater(len({r['parameters']['count'] for r in starts}),5)
        self.assertEqual({r['parameters']['hand'] for r in starts},{-1,1})
        self.assertEqual({r['parameters']['topology'] for r in starts},{'open','closed'})
        self.assertEqual({r['parameters'].get('seam_fraction',-.5) for r in starts},{-.25,-.5,-.75})


class Transactions(unittest.TestCase):
    def test_restart_and_postwrite_crash_equivalence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=Runner(root/'a',settings(42));a.run()
            b=Runner(root/'b',settings(35));b.run();b=Runner(root/'b',settings(42),True);b.run()
            self.assertEqual(a.state['rng'],b.state['rng']);self.assertEqual(a.state['pool'],b.state['pool'])
            for i in range(42):self.assertEqual(science(read(a.path(i))),science(read(b.path(i))))
            c=Runner(root/'c',settings(2));c.state['pending']=copy.deepcopy(read(a.path(0)));c.checkpoint();save(c.path(0),read(a.path(0)))
            c=Runner(root/'c',settings(2),True);original=c.evaluate
            def guard(trial,i):
                self.assertNotEqual(i,0);return original(trial,i)
            with patch.object(c,'evaluate',side_effect=guard):c.run()
            self.assertEqual(science(read(a.path(1))),science(read(c.path(1))))

    def test_changed_settings_sealed_sources_and_lock_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Runner(tmp,settings(1));a.checkpoint()
            with self.assertRaisesRegex(ValueError,'objective'):Runner(tmp,settings(2,'legacy'),True)
            a.state['sealed']=True;a.checkpoint()
            with self.assertRaisesRegex(ValueError,'Sealed'):Runner(tmp,settings(2),True)
            a.state['sealed']=False;a.state['sources']={};a.checkpoint()
            with self.assertRaisesRegex(ValueError,'Implementation'):Runner(tmp,settings(2),True)
            with run_lock(tmp):
                with self.assertRaises(SystemExit):
                    with run_lock(tmp):pass

    def test_actual_signal(self):
        import subprocess,time,signal
        with tempfile.TemporaryDirectory() as tmp:
            command=[str(ROOT/'.venv/bin/python'),str(ROOT/'photo2/phase2_autofit.py'),'--output',tmp,'--max-evaluations','100','--seal']
            p=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            try:
                deadline=time.monotonic()+40
                while time.monotonic()<deadline:
                    path=Path(tmp)/'checkpoint.json'
                    if path.exists() and read(path)['next_id']>=1:break
                    if p.poll() is not None:self.fail('Exited before interrupt')
                    time.sleep(.05)
                p.send_signal(signal.SIGTERM);_,err=p.communicate(timeout=40)
                self.assertEqual(p.returncode,0,err);self.assertEqual(read(path)['stop_reason'],'signal')
                self.assertFalse((Path(tmp)/'final-freeze.json').exists())
            finally:
                if p.poll() is None:p.kill();p.communicate()

if __name__=='__main__':unittest.main()
