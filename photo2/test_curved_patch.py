"""Source-placement, legacy-limit, exposure, and withheld-data guards."""
import unittest
import numpy as np
from bead_placement import Rope,minor_outward_point
from local_surface_fit import trace as straight_trace,centers as straight_centers
from curved_surface_fit import geometry,trace,anchors,project
from fit_curved_patch import load,setup,HELD,NUMBERS,proposals


class CurvedPatchTests(unittest.TestCase):
    def test_exact_source_circle(self):
        indices=np.arange(-40,28)
        for hand in [-1,1]:
            rope=Rope(744,helicity=hand)
            p=[0,0,1,0,55,10,0,1/rope.chain_major,rope.exact_beads_per_row]
            c,t,n,line,outer=geometry(p,indices,hand)
            actual,angle=rope.place(indices)
            shift=np.array([rope.chain_major,0,4+2*rope.bead_radius])
            def transform(v):
                v=v-shift
                return np.column_stack((v[:,1],-v[:,0],v[:,2]))
            np.testing.assert_allclose(c,transform(actual),atol=2e-14)
            np.testing.assert_allclose(outer,transform(np.array([minor_outward_point(rope,int(i)) for i in indices])),atol=2e-14)
            np.testing.assert_allclose(t[:,:2],np.column_stack((np.cos(np.radians(angle)),np.sin(np.radians(angle)))),atol=2e-14)

    def test_zero_curvature_is_legacy_surface(self):
        p=np.array([0,0,7,-8,60,15,10,0,6.5])
        indices=np.arange(-15,16)
        yy,xx=np.mgrid[-45:46:3,-65:66:3];xy=np.column_stack((xx.ravel(),yy.ravel()))
        for hand in [-1,1]:
            c,*_=geometry(p,indices,hand)
            np.testing.assert_allclose(c,straight_centers(p[:7],indices,hand),atol=1e-14)
            old,od,ou=straight_trace(p[:7],xy,hand,indices)
            new,nd,nu,_=trace(p,xy,hand,indices)
            np.testing.assert_array_equal(old,new)
            np.testing.assert_allclose(od,nd,atol=1e-12)
            self.assertEqual(ou,nu)

    def test_same_owner_can_hide_its_own_outward_point(self):
        # Back wall point of one annulus: first ray hit is the front wall of the
        # very same bead. Ownership alone must not count it as exposed.
        p=np.array([0,0,8,0,89,0,180,0,6.5])
        xy,exposed,owner,gap,u=anchors(p,np.array([0]),1,model_indices=np.array([0]))
        self.assertEqual(owner[0],0)
        self.assertFalse(exposed[0])
        self.assertGreater(gap[0],1)

    def test_whole_group_excluded_from_bounds_and_proposals(self):
        xy,mappings=load();changed=xy.copy()
        changed[[n-1 for n in HELD]]=[-99999,99999]
        for a,b in zip(setup(xy,mappings['A'],NUMBERS),setup(changed,mappings['A'],NUMBERS)):
            np.testing.assert_array_equal(a,b)
        # All 32 proposals and their training-only rankings must be identical.
        a,_=proposals(xy,mappings['A'],1,NUMBERS)
        b,_=proposals(changed,mappings['A'],1,NUMBERS)
        self.assertEqual(a,b)


if __name__=='__main__':unittest.main()
