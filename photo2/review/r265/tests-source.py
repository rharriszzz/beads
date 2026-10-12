"""R265 exact invariants and adversarial small grids; deterministic randomized tests."""
import unittest
from dataclasses import replace
import numpy as np
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from scipy import ndimage as ndi
from . import repaired_detect as new
from . import bounded_detect as old


def gray(v):return rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255.)


def audit(v,hsv,mask,t,p):
    a=t['accepted'];ox,oy=t.get('source_offset',[0,0]);mx,my=t['mask_offset']
    assert 1<=len(a)<=p.max_region_pixels
    assert len({tuple(r[:2]) for r in a})==len(a)
    for i,r in enumerate(a):
        x,y,prev,dn=r[:4];assert dn==int(v[y-oy,x-ox])
        np.testing.assert_allclose(r[4:7],hsv[y-oy,x-ox]*[360,1,1],rtol=0,atol=1e-12)
        assert bool(mask[y-my,x-mx])==r[7]
        if i:
            assert 0<=prev<i
            q=a[prev];assert max(abs(x-q[0]),abs(y-q[1]))==1
            path=[a[j][:2] for j in t['straight_path_indices'][i]]
            assert path==[list(xy) for xy in new.straight_pixels(tuple(a[0][:2]),(x,y))]
            floor=a[0][3]
            for j in t['straight_path_indices'][i][1:]:
                assert a[j][3]<=floor+p.rise_budget_dn;floor=min(floor,a[j][3])
            assert t['path_floor_dn'][i]==floor
            anchor=None
            for j in t['straight_path_indices'][i]:
                sample=a[j];hue,sat,val=sample[4:7]
                reliable=sat>=p.reliable_saturation and val>=.20 and sat*val>=.08
                if anchor is not None and reliable:
                    delta=abs(hue-anchor[0]);assert min(delta,360-delta)<p.hue_stop_deg
                if anchor is not None and j!=0:
                    assert not (anchor[1]-sat>=p.saturation_drop and sample[3]<a[0][3]-p.patch_drop_dn)
                if anchor is None and reliable:anchor=(hue,sat)
                if j!=0:assert not (sample[3]<=p.dark_dn and a[0][3]-sample[3]>=p.reflection_drop_dn)
        else:assert prev==-1 and r[7]
    assert ndi.label(mask,np.ones((3,3)))[1]==1
    points=np.array([r[:2] for r in a if r[7]])
    measured=new.measure(mask,mx,my)
    np.testing.assert_allclose(measured['centroid'],points.mean(axis=0),rtol=0,atol=1e-12)
    assert measured['location'] in points.tolist()
    accepted={tuple(r[:2]) for r in a};stops={(r[2],r[0],r[1]) for r in t['stops']}
    for i,r in enumerate(a):
        for dy,dx in new.N8:
            x,y=r[0]+dx,r[1]+dy
            if 0<=x-ox<v.shape[1] and 0<=y-oy<v.shape[0] and (x,y) not in accepted:
                assert (i,x,y) in stops
    for row in t['stops']:
        q=a[row[2]];assert max(abs(row[0]-q[0]),abs(row[1]-q[1]))==1
        assert row[3]==int(v[row[1]-oy,row[0]-ox])
    if p.local_retreat:
        for r,threshold,reason in zip(a,t['retreat_threshold_dn'],t['retreat_reasons']):
            if r[7]:assert r[3]==a[0][3] or r[3]>threshold
            if reason=='local-darkness':assert r[3]<=threshold and r[3]!=a[0][3]
    return len(a),len(t['stops'])


class RepairTests(unittest.TestCase):
    def run_grid(self,v,**kwargs):
        v=np.array(v,np.uint8);p=replace(new.Parameters(),**kwargs)
        mask,t=new.grow(v,gray(v),(0,0),p);audit(v,gray(v),mask,t,p)
        return mask,t

    def test_bright_terminal_survives(self):
        v=np.array([[220,210,200]],np.uint8)
        _,before=old.grow(v,gray(v),(0,0))
        _,after=self.run_grid(v)
        self.assertFalse(before['accepted'][-1][7]);self.assertTrue(after['accepted'][-1][7])

    def test_independent_path_floor_with_noise_allowance(self):
        # A dark branch must not consume the other branch's rise allowance.
        v=np.array([[220,215,210,211],[0,0,0,0],[0,0,0,0]],np.uint8)
        _,t=self.run_grid(v,rise_budget_dn=1,valley_guard=False)
        self.assertIn([3,0],[r[:2] for r in t['accepted']])
        _,t=self.run_grid([[220,210,211,212]],rise_budget_dn=1,valley_guard=False)
        self.assertNotIn([3,0],[r[:2] for r in t['accepted']])

    def test_other_path_cannot_veto_valid_bright_leaf(self):
        # Enqueue220 from230, then encounter it from210: old destination locks it.
        v=np.array([[230,210],[220,0]],np.uint8)
        _,t=self.run_grid(v,valley_guard=False)
        self.assertEqual(len(t['accepted']),3)

    def test_valley_and_diagonal_corner(self):
        _,t=self.run_grid([[220,170,190],[210,100,180],[200,160,170]],dark_dn=0)
        self.assertNotIn([2,0],[a[:2] for a in t['accepted']])
        self.assertTrue(any(r[7]=='local-valley' for r in t['stops']))
        _,t=self.run_grid([[220,50],[50,180]])
        self.assertNotIn([1,1],[a[:2] for a in t['accepted']])
        self.assertTrue(any(r[7]=='valley-corner' for r in t['stops']))

    def test_descending_detour_cannot_circumvent_trench(self):
        v=np.array([[220,210,200,190,180],[210,50,50,50,170],[200,50,150,150,160]],np.uint8)
        _,t=old.grow(v,gray(v),(0,0))
        self.assertIn([2,2],[a[:2] for a in t['accepted']])
        _,t=self.run_grid(v)
        self.assertNotIn([2,2],[a[:2] for a in t['accepted']])
        self.assertTrue(any(s[7]=='dark-frontier' for s in t['stops']))

    def test_retreat_does_not_depend_on_predecessor_tree(self):
        v=np.array([[220,200],[210,190]],np.uint8)
        a=[[0,0,-1,220,0,0,0,True],[1,0,0,200,0,0,0,True],[0,1,0,210,0,0,0,True],[1,1,1,190,0,0,0,True]]
        b=[r.copy() for r in a];b[-1][2]=2
        ma=new.retreat(v,dict(accepted=a,mask_offset=[0,0]),new.Parameters())
        mb=new.retreat(v,dict(accepted=b,mask_offset=[0,0]),new.Parameters())
        np.testing.assert_array_equal(ma,mb);self.assertTrue(ma.all())

    def test_local_retreat_dark_tail_and_connectivity(self):
        _,t=self.run_grid([[220,200,180,160,140,120,100]])
        self.assertEqual([a[3] for a in t['accepted'] if a[7]],[220,200,180,160,140])
        # Directly exercise disconnection after a dim bridge, independent of growth.
        a=[[0,0,-1,220,0,0,0,True],[1,0,0,100,0,0,0,True],[2,0,1,200,0,0,0,True]]
        t=dict(accepted=a,mask_offset=[0,0]);mask=new.retreat(np.array([[220,100,200]],np.uint8),t,new.Parameters())
        self.assertEqual(mask.tolist(),[[True,False,False]])
        self.assertEqual(t['retreat_reasons'][-1],'disconnected-after-retreat')

    def test_cap(self):
        for n in (869,870,871):
            _,t=self.run_grid(np.full((1,n),200))
            self.assertEqual(len(t['accepted']),min(n,870));self.assertEqual(t['size_limited'],n>870)
        v=np.full((35,35),200,np.uint8);p=new.Parameters();m,t=new.grow(v,gray(v),(17,17),p);audit(v,gray(v),m,t,p)
        self.assertTrue(t['size_limited'])

    def test_exact_circular_hue_threshold_stops(self):
        for h0,h1 in [(355,5),(5,355),(0,10),(10,0)]:
            hsv=np.array([[[h0/360,.8,220/255],[h1/360,.8,200/255]]])
            _,t=new.grow(np.array([[220,200]],np.uint8),hsv,(0,0))
            self.assertEqual(len(t['accepted']),1)
            self.assertEqual(t['stops'][0][7],'relative-hue-change')

    def test_background_learning_preserves_uncertainty_and_palette(self):
        for hue in (0,.25,.60,.9):
            hsv=np.full((15,15,3),[hue,.45,.8]);border=np.ones((15,15),bool)
            model=new.learn_background(hsv,border)
            self.assertTrue(new.obvious_background(hsv,3,3,model))
            hsv[3,3]=[(hue+.25)%1,.45,.8]
            self.assertFalse(new.obvious_background(hsv,3,3,model))
            hsv[3,3]=[hue,.45,.3] # unseen shadow stays uncertain
            self.assertFalse(new.obvious_background(hsv,3,3,model))

    def test_precheck_occurs_before_growth(self):
        from unittest.mock import patch
        hsv=np.full((15,15,3),[.6,.5,.8]);hsv[7,7,2]=.81
        rgb=np.round(hsv_to_rgb(hsv)*255).astype(np.uint8)
        with patch.object(new,'grow',side_effect=AssertionError('background was grown')):
            data,_,_=new.detect(rgb,replace(new.Parameters(),prominence_dn=1))
        self.assertTrue(any(m['reason']=='obvious-background-before-growth' for m in data['maxima']))

    def test_randomized_exact_invariants(self):
        rng=np.random.default_rng(265)
        for i in range(240):
            v=rng.integers(0,256,(rng.integers(3,15),rng.integers(3,15)),dtype=np.uint8);v[0,0]=255
            p=replace(new.Parameters(),rise_budget_dn=i%3,valley_guard=i%2==0,max_region_pixels=10+i%50)
            m,t=new.grow(v,gray(v),(0,0),p,offset=(13,17));audit(v,gray(v),m,t,p)
            m2,t2=new.grow(v,gray(v),(0,0),p,offset=(13,17))
            self.assertEqual(t,t2);np.testing.assert_array_equal(m,m2)

    def test_flat_bright_support_has_no_holes(self):
        v=np.full((15,15),200,np.uint8);m,t=new.grow(v,gray(v),(7,7))
        self.assertTrue(m.all());self.assertEqual(len(t['accepted']),225)

if __name__=='__main__':unittest.main()
