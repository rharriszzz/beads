"""R266 native, fixed-sector, selection and deferral contracts."""
import unittest
from dataclasses import replace
from unittest.mock import patch
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv,hsv_to_rgb
from . import annular_detect as d
from .test_repaired import gray,audit as straight_audit


def audit(v,hsv,m,t,p):
    if p.method=='straight':return straight_audit(v,hsv,m,t,p)
    a=t['accepted'];ox,oy=t['source_offset'];mx,my=t['mask_offset']
    assert 1<=len(a)<=p.max_region_pixels
    assert len({tuple(r[:2]) for r in a})==len(a)
    assert t['annular_layer']==sorted(t['annular_layer'])
    accepted={tuple(r[:2]) for r in a};stops={(r[2],r[0],r[1]) for r in t['stops']}
    for i,r in enumerate(a):
        x,y,prev,dn=r[:4];assert dn==int(v[y-oy,x-ox])
        np.testing.assert_allclose(r[4:7],hsv[y-oy,x-ox]*[360,1,1],rtol=0,atol=1e-12)
        assert bool(m[y-my,x-mx])==r[7]
        if i:
            assert 0<=prev<i
            assert max(abs(x-a[prev][0]),abs(y-a[prev][1]))==1
            assert dn<=t['path_floor_dn'][prev]+p.rise_budget_dn
            assert t['path_floor_dn'][i]==min(dn,t['path_floor_dn'][prev])
        else:assert prev==-1
        path=t['annular_path_indices'][i]
        assert path[-1]==i and (not i or path[:-1]==t['annular_path_indices'][prev])
        for dx,dy in d.N8:
            tx,ty=x+dx,y+dy
            if 0<=tx-ox<v.shape[1] and 0<=ty-oy<v.shape[0] and (tx,ty) not in accepted:assert (i,tx,ty) in stops
    for r in t['stops']:
        assert tuple(r[:2]) not in accepted
        assert r[3]==int(v[r[1]-oy,r[0]-ox])
        assert max(abs(r[0]-a[r[2]][0]),abs(r[1]-a[r[2]][1]))==1
    assert ndi.label(m,np.ones((3,3)))[1]==1
    assert d.measure(m,mx,my)['location'] in [r[:2] for r in a if r[7]]
    return len(a),len(stops)


class AnnularTests(unittest.TestCase):
    def grid(self,v,**kwargs):
        v=np.array(v,np.uint8);p=d.Parameters(method='annular',**kwargs)
        m,t=d.grow(v,gray(v),(0,0),p);audit(v,gray(v),m,t,p);return m,t

    def test_allowance_does_not_accumulate(self):
        for method in ('straight','annular'):
            for budget in range(4):
                v=np.array([[220,200,200+budget,201+budget]],np.uint8);p=d.Parameters(method=method,rise_budget_dn=budget,valley_guard=False)
                m,t=d.grow(v,gray(v),(0,0),p);audit(v,gray(v),m,t,p)
                self.assertEqual([r[0] for r in t['accepted']],[0,1,2])

    def test_stopped_sector_never_reopens(self):
        _,t=self.grid([[220,210,200,190,180],[210,50,50,50,170],[200,50,150,150,160]])
        self.assertNotIn([2,2],[r[:2] for r in t['accepted']])
        self.assertTrue(any(r[7]=='stopped-sector' for r in t['stops']))

    def test_independent_sectors(self):
        _,t=self.grid([[220,200,201],[210,0,0],[200,0,0]],rise_budget_dn=1,valley_guard=False)
        self.assertIn([2,0],[r[:2] for r in t['accepted']]);self.assertIn([0,2],[r[:2] for r in t['accepted']])

    def test_plateau_annuli_and_cap(self):
        for n in (869,870,871):
            _,t=self.grid(np.full((1,n),200))
            self.assertEqual(len(t['accepted']),min(n,870));self.assertEqual(t['size_limited'],n>870)
        v=np.full((9,9),180,np.uint8);v[3:6,3:6]=220;p=d.Parameters(method='annular')
        m,t=d.grow(v,gray(v),(4,4),p);audit(v,gray(v),m,t,p)
        self.assertEqual(len(t['bright_patch_plateau']),9)
        self.assertEqual(t['annular_layer'].count(0),9)
        self.assertTrue(m.all())

    def test_randomized_invariants_and_determinism(self):
        rng=np.random.default_rng(266)
        for i in range(100):
            v=rng.integers(0,255,(12,14),dtype=np.uint8);v[0,0]=255
            p=d.Parameters(method='annular',rise_budget_dn=i%4,max_region_pixels=10+i%30)
            m,t=d.grow(v,gray(v),(0,0),p,offset=(5,8));audit(v,gray(v),m,t,p)
            m2,t2=d.grow(v,gray(v),(0,0),p,offset=(5,8));self.assertEqual(t,t2)

    def test_dark_first_and_local_retreat(self):
        _,t=self.grid([[220,190,140,80,180]],valley_guard=False)
        self.assertNotIn([3,0],[r[:2] for r in t['accepted']])
        self.assertNotIn([4,0],[r[:2] for r in t['accepted']])
        self.assertTrue(t['accepted'][1][7])

    def test_paper_stop_local(self):
        v=np.array([[220,210,200],[210,200,190]],np.uint8);paper=np.zeros(v.shape,bool);paper[0,1]=True
        p=d.Parameters(method='annular',valley_guard=False)
        _,t=d.grow(v,gray(v),(0,0),p,paper=paper)
        self.assertNotIn([1,0],[r[:2] for r in t['accepted']]);self.assertIn([0,1],[r[:2] for r in t['accepted']])
        self.assertTrue(any(r[7]=='probable-paper' for r in t['stops']))

    def test_background_gate_before_growth(self):
        hsv=np.full((31,31,3),[.3,.5,.8]);hsv[15,15,2]=.81;rgb=np.round(hsv_to_rgb(hsv)*255).astype(np.uint8)
        with patch.object(d,'grow',side_effect=AssertionError('paper reached growth')):
            result,_,_=d.detect(rgb,d.Parameters(prominence_dn=1,background_guard=True))
        self.assertEqual(len(result['regions']),0)

    def test_deferral_does_not_become_acceptance(self):
        hsv=np.full((61,61,3),[.85,.5,.75]);y,x=np.mgrid[:61,:61]
        disc=(x-30)**2+(y-30)**2<64
        hsv[disc,0]=.90;hsv[disc,2]=.88
        hsv[30,30,2]=1
        rgb=np.round(hsv_to_rgb(hsv)*255).astype(np.uint8)
        result,labels,_=d.detect(rgb,d.Parameters(background_guard=True,prominence_dn=20))
        self.assertTrue(result['deferred']);self.assertFalse(np.any(labels))
        self.assertEqual(result['deferred'][0]['status'],'deferred')

    def records(self,v,coords,hsv):
        result=[]
        for i,(x,y) in enumerate(coords):
            result.append(dict(id=f'P{i:06}',pixel_runs=[[y,x,x]],pixel_count=1,bbox=[x,y,x+1,y+1],bright_patch=dict(peak=[x,y],prominence_lower_bound_dn=35),status='retained'))
        return result

    def test_suppression_requires_bridge_not_proximity(self):
        v=np.full((15,20),180,np.uint8);hsv=np.full((15,20,3),[.1,.8,180/255]);v[7,5]=220;v[7,10]=215
        rs=self.records(v,[(5,7),(10,7)],hsv)
        # Deep seam keeps both even with the same color and small distance.
        v[:,8]=60
        kept,suppressed,_=d.associate(rs,v,hsv,d.Parameters());self.assertEqual(len(kept),2)
        v[:]=210;v[7,5]=220;v[7,10]=215
        kept,suppressed,e=d.associate(self.records(v,[(5,7),(10,7)],hsv),v,hsv,d.Parameters())
        self.assertEqual(len(kept),1);self.assertEqual(len(suppressed),1);self.assertIn('suppressed_by',suppressed[0])

    def test_split_requires_dark_cut_and_two_seeds(self):
        v=np.full((7,15),190,np.uint8);v[:,7]=65;mask=np.ones(v.shape,bool)
        children=d.split_supported_mask(mask,v,gray(v),(0,0),[(3,3),(11,3)])
        self.assertEqual(len(children),2)
        self.assertEqual(sum(c['pixel_count'] for c in children),98)
        self.assertFalse(d.split_supported_mask(mask,v,gray(v),(0,0),[(3,3)]))
        v[:,7]=180
        self.assertFalse(d.split_supported_mask(mask,v,gray(v),(0,0),[(3,3),(11,3)]))

    def test_palette_change_preserves_background_evidence(self):
        for hue in (0,.2,.5,.85):
            hsv=np.full((35,35,3),[hue,.5,.8]);border=np.ones((35,35),bool)
            model,paper,uncertain=d.background_maps(hsv,border)
            self.assertTrue(paper.all());self.assertTrue(uncertain.all())

if __name__=='__main__':unittest.main()
