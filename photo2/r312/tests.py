"""Scientific contracts for minimax, immutable cohorts and exact acceleration."""
import itertools,unittest
from copy import deepcopy
import numpy as np
from photo2.r306.evidence import load
from photo2.r309.render import predict
from photo2.r309.geometry import Chain as Previous
from .model import seeds,scene,geometry_key
from .search import proposal
from .objective import Engine,bottleneck,statistics,MISSING

class Contracts(unittest.TestCase):
    def test_bottleneck_matches_exhaustive_minimax(self):
        rng=np.random.default_rng(312)
        for _ in range(10):
            obs=[dict(id=str(i),point=x.tolist()) for i,x in enumerate(rng.random((3,2))*40)]
            pred=[dict(index=i,point=x.tolist()) for i,x in enumerate(rng.random((4,2))*40)]
            result=bottleneck(obs,pred)
            actual=max(np.linalg.norm(np.array(o['point'])-pred[result[o['id']]]['point']) for o in obs)
            expected=min(max(np.linalg.norm(np.array(o['point'])-pred[j]['point']) for o,j in zip(obs,perm)) for perm in itertools.permutations(range(4),3))
            self.assertAlmostEqual(actual,expected)
    def test_missing_never_improves_maximum(self):
        full=[dict(error_px=5.),dict(error_px=30.)];missing=[dict(error_px=5.),dict(error_px=None)]
        self.assertGreater(statistics(missing)['objective_px'],statistics(full)['objective_px'])
        self.assertEqual(statistics(missing)['missing'],1)
    def test_frozen_assignment_cannot_relabel(self):
        e=Engine(1);e.obs=e.obs[:2]
        pred=[dict(index=0,point=e.obs[1]['point']),dict(index=1,point=e.obs[0]['point'])]
        mapping={e.obs[0]['id']:0,e.obs[1]['id']:1}
        rows=e.records(pred,mapping)
        self.assertTrue(all(r['error_px']>0 for r in rows));self.assertEqual([r['index'] for r in rows],[0,1])
    def test_200_consecutive_all_chain_native_exact(self):
        data,_,_=load();p=seeds()[0]['parameters'];s=scene(p,data);old=Previous(p,data)
        owners=np.flatnonzero((s.indices>=-100)&(s.indices<=99))
        np.testing.assert_array_equal(s.indices[owners],np.arange(-100,100))
        self.assertEqual(s.n,p['count']);self.assertGreater(s.n,200)
        a,am=predict(s,2.,owners=owners);b,bm=predict(old,2.,owners=owners)
        self.assertEqual(a,b);self.assertEqual(am,bm)
        for offset in [1,6,7]:
            for k in [-90,0,90]:
                np.testing.assert_array_equal(s.centers[np.searchsorted(s.indices,k+offset)]-s.centers[np.searchsorted(s.indices,k)],old.centers[np.searchsorted(old.indices,k+offset)]-old.centers[np.searchsorted(old.indices,k)])
    def test_camera_cache_preserves_changed_light(self):
        e=Engine(1);p=seeds()[0]['parameters'];r=e.evaluate(p)
        q=dict(p,light_az=p['light_az']-20,light_inverse=.001)
        a=e.evaluate(q,r['mapping']);b=Engine(1).evaluate(q,r['mapping'])
        self.assertEqual(a['reflections'],b['reflections']);self.assertEqual(a['safeguards'],b['safeguards'])
        self.assertTrue(a['numerics']['camera_reused']);self.assertEqual(geometry_key(p),geometry_key(q))
    def test_fields_are_explored_as_existing_smooth_laws(self):
        p=seeds()[0]['parameters'];q=proposal(p,['axis_nodes','local_phase','local_spacing'],np.linspace(.1,.9,24),amplitude=.5)
        for k in ['axis_nodes','local_phase','local_spacing']:self.assertNotEqual(p[k],q[k])
        self.assertEqual(p['count'],q['count']);self.assertEqual(p['hand'],q['hand'])
    def test_unannotated_hole_does_not_penalize_outer_contour(self):
        from scipy.ndimage import distance_transform_edt
        e=Engine(1);c=e.contours[0];owner=np.full(len(e.xy),-1,int)
        start=int(e.bounds[-1])+len(e.cues['xy']);n=len(c['xy']);owner[start:start+n]=np.where(c['inside'].ravel(),0,-1)
        class Dummy:indices=np.arange(-1200,1200)
        tr=dict(owner=owner,unknown=np.zeros(len(owner),bool));before=e.safeguards(tr,Dummy())
        where=int(distance_transform_edt(c['inside']).argmax());owner[start+where]=-1
        after=e.safeguards(tr,Dummy())
        self.assertEqual(before['boundary_rms_px'],after['boundary_rms_px'])

if __name__=='__main__':unittest.main()
