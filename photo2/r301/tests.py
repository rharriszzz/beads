"""Scientific contracts: independent geometry checks and durable search replay."""
import copy,tempfile,unittest
from pathlib import Path
import numpy as np
from .model import Local,DEFAULT,BOUNDS,predict
from .objective import assignment,evaluate
from .search import run
from .evidence import BASE,read

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.section=read(BASE/'evidence/frozen.json.gz')['sections'][0]
    def scene(self):return Local(DEFAULT,self.section,-1)

    def test_legacy_annular_shape(self):
        from photo2.r279.geometry import sdf,R
        p=DEFAULT.copy();p[0]=.7;p[1]=.8;p[2]=.14;s=Local(p,self.section,-1)
        q=np.random.default_rng(1).uniform(-1.2,1.2,(2000,3))
        # Kernels use different conservative SDF scale; signs and zeros agree.
        np.testing.assert_allclose(s.local_sdf(q),sdf(q*R)/R,atol=1e-12)

    def test_surface_normals(self):
        s=self.scene();xyz,n=s.samples(1);axes=np.stack([s.g[k][0] for k in ['surface_tangent','surface_normal','surface_binormal']]);q=(xyz[0]-s.centers[0])@axes.T
        self.assertLess(np.max(abs(s.local_sdf(q))),1e-10)
        gradient=np.stack([(s.local_sdf(q+np.eye(3)[j]*1e-6)-s.local_sdf(q-np.eye(3)[j]*1e-6))/2e-6 for j in range(3)],axis=1);gradient/=np.linalg.norm(gradient,axis=1)[:,None]
        np.testing.assert_allclose(s.normal(q),gradient,atol=2e-5)

    def test_support_bounds_independent_samples(self):
        s=self.scene();xyz,_=s.samples(1);rng=np.random.default_rng(3);directions=rng.normal(size=(100,3));directions/=np.linalg.norm(directions,axis=1)[:,None]
        for k in [0,20,44,88]:
            h=s.support(directions,s.g['surface_tangent'][k]);sample=(xyz[k]-s.centers[k])@directions.T
            self.assertLessEqual(np.max(sample-h),1e-10)
            self.assertLess(np.max(h-sample.max(0)),.015)

    def test_tilt_and_constant_turn(self):
        s=self.scene();p=DEFAULT.copy();p[6]=-8;t=Local(p,self.section,-1)
        self.assertGreater(np.max(abs(s.g['surface_tangent']-t.g['surface_tangent'])),.05)
        np.testing.assert_allclose(np.diff(t.phase),-2*np.pi/p[5],atol=1e-13)
        self.assertEqual(len(t.indices),89)

    def test_contact_witnesses(self):
        s=self.scene();c=s.certify(iterations=180);self.assertTrue(c['certified'])
        for row in c['witnesses']:
            a,b=row['pair'];n=np.array(row['normal']);gap=(s.centers[b]-s.centers[a])@n-s.support(n,s.g['surface_tangent'][a])-s.support(n,s.g['surface_tangent'][b]);self.assertAlmostEqual(gap,row['gap_units'],places=10);self.assertGreater(gap,1e-6)
        self.assertTrue(any(abs(s.indices[a]-s.indices[b])>=7 for a,b in [w['pair'] for w in c['witnesses']]))

    def test_one_owner_no_unlimited_duplicates(self):
        s=dict(center=[0,0],tangent=[1,0]);pred=[dict(owner=0,index=0,point=[0,0])];rows=[dict(id=str(i),point=[i,0],weight=1,split='train',color='black') for i in range(5)]
        a=assignment(pred,rows,s);self.assertEqual(a['unmatched'],3);self.assertLessEqual(a['used'].count(0),2)
        rows[1]['point']=[20,0];a=assignment(pred,rows[:2],s);self.assertEqual(a['unmatched'],1)
        a=assignment(pred,rows,s,blocked=[0]);self.assertEqual(a['unmatched'],5)

    def test_unknown_observations_retained(self):
        d=read(BASE/'evidence/frozen.json.gz');self.assertEqual(len(d['all_original_observations']),810)
        for s in d['sections']:
            self.assertTrue(any(r['split']=='withheld' for r in s['observations']));self.assertTrue(any(s['cues']['withheld']))

    def test_resume_and_evidence_guard(self):
        with tempfile.TemporaryDirectory() as d:
            a=run(Path(d)/'full',self.section,-1,987,24)
            run(Path(d)/'part',self.section,-1,987,9)
            b=run(Path(d)/'part',self.section,-1,987,24)
            self.assertEqual(a['population'],b['population']);self.assertEqual(a['scores'],b['scores']);self.assertEqual(a['rng'],b['rng'])
            for x,y in zip(a['history'],b['history']):
                self.assertEqual(x['parameters'],y['parameters']);self.assertAlmostEqual(x['loss'],y['loss'],places=12)
            with self.assertRaises(ValueError):run(Path(d)/'part',self.section,1,987,25)

    def test_process_kill_resume(self):
        import subprocess,sys,time
        from photo2.r297.common import ROOT
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)/'crash';p=subprocess.Popen([sys.executable,'-m','photo2.r301.search','--output',str(folder),'--budget','100000','--seed','987'],cwd=ROOT,stdout=subprocess.DEVNULL)
            try:
                deadline=time.monotonic()+15
                while not (folder/'checkpoint.json.gz').exists() and time.monotonic()<deadline:time.sleep(.03)
                self.assertTrue((folder/'checkpoint.json.gz').exists());p.kill();p.wait(timeout=5)
                committed=len(read(folder/'checkpoint.json.gz')['history']);target=committed+7
                resumed=run(folder,self.section,-1,987,target);full=run(Path(d)/'control',self.section,-1,987,target)
                self.assertEqual(resumed['population'],full['population']);self.assertEqual(resumed['scores'],full['scores']);self.assertEqual(resumed['rng'],full['rng'])
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=5)

if __name__=='__main__':unittest.main()
