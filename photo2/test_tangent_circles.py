"""Forward geometry/occlusion checks; no photo-center or automatic inverse claim."""
import unittest
import numpy as np
from bead_placement import Rope,minor_outward_point
from tangent_circles import View,SplineRope,tangent_circles,visible_anchors,RADIUS
from curved_surface_fit import sdf


def circular_model(hand=1):
    source=Rope(312,helicity=hand);view=View(elevation=80.,scale=10.)
    theta=np.linspace(0,2*np.pi,257)
    line=np.column_stack((source.chain_major*np.cos(theta),source.chain_major*np.sin(theta),np.zeros(len(theta))))
    model=SplineRope(view.project(line),view,312,hand,smoothing=0.)
    return source,model


class TangentCircleTests(unittest.TestCase):
    def test_circular_limit_matches_literal_source_placement_for_both_hands(self):
        for hand in [-1,1]:
            source,model=circular_model(hand);indices=np.arange(312)
            g=model.geometry(indices);expected,_=source.place(indices)
            expected[:,2]-=4+2*RADIUS
            np.testing.assert_allclose(g['centers'],expected,atol=3e-5)
            outward=np.array([minor_outward_point(source,int(i)) for i in indices]);outward[:,2]-=4+2*RADIUS
            np.testing.assert_allclose(g['outward'],outward,atol=3e-5)

    def test_circle_lies_in_tangent_plane_at_minor_outward_point(self):
        _,model=circular_model();g=model.geometry(np.arange(312));circles,offset=tangent_circles(g)
        np.testing.assert_allclose(np.sum(circles*g['radial'][:,None,:],axis=2),offset[:,None]+np.zeros((312,49)),atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(circles-g['outward'][:,None,:],axis=2),.18*RADIUS,atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(g['outward']-g['line'],axis=1),4+RADIUS,atol=1e-12)

    def test_hidden_outward_points_are_not_drawn_even_if_other_parts_may_show(self):
        _,model=circular_model();g=model.geometry(np.arange(312));vis=visible_anchors(model,g)
        self.assertGreater(int(vis['exposed'].sum()),30)
        self.assertGreater(int((~vis['exposed']).sum()),100)
        self.assertFalse(np.any(vis['exposed']&(vis['facing']<=0)))
        self.assertFalse(np.any(vis['exposed']&(vis['first_owner']!=g['indices'])))
        self.assertFalse(np.any(vis['exposed']&(np.abs(vis['front_minus_anchor'])>=.002)))

    def test_plane_normal_is_the_actual_annular_surface_normal(self):
        _,model=circular_model();g=model.geometry(np.arange(312))
        delta=g['outward']-g['centers']
        local=np.column_stack((np.sum(delta*g['tangent'],axis=1),np.sum(delta*g['normal'],axis=1),delta[:,2]))
        np.testing.assert_allclose(sdf(local),0.,atol=1e-12)
        eps=1e-6;gradient=np.column_stack([(sdf(local+eps*np.eye(3)[j])-sdf(local-eps*np.eye(3)[j]))/(2*eps) for j in range(3)])
        world=gradient[:,0,None]*g['tangent']+gradient[:,1,None]*g['normal']
        world[:,2]+=gradient[:,2]
        np.testing.assert_allclose(world,g['radial'],atol=1e-8)


if __name__=='__main__':unittest.main()
