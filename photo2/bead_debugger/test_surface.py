"""R257 mathematical, ownership, lighting and backward-compatibility contracts."""
import json, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from .surface import Scene,RADIUS,EXTRA,ROUND,STRETCH,local_normal,unit,shade,highlight,directions,moments
from .detail import local_geometry
from .models import load
from .lighting import light_from,plane_points
from curved_surface_fit import sdf
from camera_r254 import Camera


def synthetic(centers,scale=10):
    s=Scene.__new__(Scene);s.config={'n':len(centers),'origin':0};s.mid='synthetic';s.version='test';s.plane_z=-4
    c=np.array(centers,float);n=len(c);s.centers=c
    s.g=dict(indices=np.arange(n),centers=c,tangent=np.tile([1.,0,0],(n,1)),normal=np.tile([0.,1,0],(n,1)),radial=np.tile([0.,0,1],(n,1)),outward=c+[0,0,RADIUS],line=c-[0,0,4])
    view=Camera(89.9,0.,50.,50.,scale);s.model=SimpleNamespace(view=view,source=SimpleNamespace(nbeads=n));s.pc=view.project(c);s.shadow_trees={}
    return s

class SurfaceTests(unittest.TestCase):
    def test_radial_extremum_and_band(self):
        r=RADIUS;theta=np.linspace(0,2*np.pi,721);# rounded rectangle section boundary
        p=[]
        for sr in [-1,1]:
            for sa in [-1,1]:
                for a in np.linspace(0,np.pi/2,91):
                    rho=.57*r+sr*(EXTRA+ROUND*np.cos(a));ax=sa*(EXTRA+ROUND*np.sin(a))*STRETCH
                    p.append([ax,rho,0])
        p=np.array(p);self.assertLess(np.max(np.abs(sdf(p))),1e-12);self.assertAlmostEqual(p[:,1].max(),r)
        for ax in [-EXTRA*STRETCH,0,EXTRA*STRETCH]:self.assertAlmostEqual(float(sdf(np.array([[ax,r,0]]))[0]),0)
    def test_normals_flat_curved_hole(self):
        pts=np.array([[0,RADIUS,0],[0,.14*RADIUS,0],[.7*RADIUS,.57*RADIUS,0],[(EXTRA+ROUND/np.sqrt(2))*STRETCH,.57*RADIUS+EXTRA+ROUND/np.sqrt(2),0]])
        normals=local_normal(pts);np.testing.assert_allclose(normals[:3],[[0,1,0],[0,-1,0],[1,0,0]],atol=1e-12)
        h=1e-6;finite=np.stack([(sdf(pts+np.eye(3)[j]*h)-sdf(pts-np.eye(3)[j]*h))/(2*h) for j in range(3)],axis=1)
        np.testing.assert_allclose(normals,unit(finite),atol=1e-8)
    def test_camera_projection_and_hole(self):
        for focal in [0,4000]:
            s=synthetic([[0,0,0]]);s.model.view.focal=focal
            xy=np.array([[50.,50.],[57.2,44.8],[39.,51.]])
            p=s.model.view.base(xy)+s.model.view.directions(xy)*1.8
            np.testing.assert_allclose(s.model.view.project(p),xy,atol=1e-10)
        # Looking down hole axis: no annulus hit through center.
        s=synthetic([[0,0,0]]);s.model.view=Camera(0.,90.,50.,50.,10.)
        # Explicit axis-oriented geometry for this camera.
        eye=s.model.view.basis()[2];s.g['tangent'][0]=eye;s.g['normal'][0]=[1,0,0]
        # source Scene local z assumes planar axes: use known tangent x camera via roll cannot set az.
        # Test hole directly with point-to-light rays parallel to tangent instead.
        s=synthetic([[0,0,0]])
        blocked,_=s.blocked(np.array([[-5.,0,0],[-5.,.57*RADIUS,0]]),[1,0,0]);self.assertEqual(blocked.tolist(),[False,True])
    def test_overlap_ownership_and_hidden(self):
        s=synthetic([[0,0,0],[0,0,5]])
        d=s.grid([30,30,71,71]);self.assertFalse(np.any(d['owner']==0));self.assertTrue(np.any(d['owner']==1))
        h=highlight(d['xy'][d['owner']==0],np.array([]));self.assertIsNone(h)
    def test_native_centroid_convergence(self):
        s=synthetic([[0,0,0]],scale=10);s.pc+=0 # keep geometry fixed
        vals=[]
        for step in [4,2,1]:
            d=s.grid([20,20,81,81],step);m=moments(d['xy'][d['owner']==0],np.ones((d['owner']==0).sum()));vals.append(np.array(m['centroid']))
        self.assertLess(np.linalg.norm(vals[-1]-[50,50]),.2);self.assertLess(np.linalg.norm(vals[0]-vals[-1]),1.5)
    def test_half_vector_and_moving_highlight(self):
        v=unit([0,0,1]);L=unit([.4,0,1]);h=unit(L+v)
        data=dict(points=np.zeros((3,3)),normal=np.array([h,v,unit([-.4,0,1])]),viewer=np.tile(v,(3,1)),owner=np.zeros(3,int))
        light=dict(direction=L.tolist(),roughness_deg=3)
        intensity=shade(None,data,light,False)['specular'];self.assertEqual(intensity.argmax(),0)
        s=synthetic([[0,0,0]]);d=s.grid([20,20,81,81]);valid=d['owner']>=0;d={k:x[valid] for k,x in d.items()}
        a=highlight(d['xy'],shade(s,d,dict(direction=unit([0,.5,1]).tolist(),roughness_deg=7))['specular'])
        b=highlight(d['xy'],shade(s,d,dict(direction=unit([0,-.5,1]).tolist(),roughness_deg=7))['specular'])
        self.assertGreater(np.linalg.norm(np.array(a['centroid'])-b['centroid']),2)
    def test_area_size_spread_and_shadow_softness(self):
        s=synthetic([[0,0,0]]);d=s.grid([20,20,81,81]);ok=d['owner']>=0;d={k:v[ok] for k,v in d.items()}
        small=dict(direction=[0,0,1],roughness_deg=7,width_deg=0,height_deg=0)
        large=dict(small,width_deg=40,height_deg=40)
        a=highlight(d['xy'],shade(s,d,small)['specular']);b=highlight(d['xy'],shade(s,d,large,order=9)['specular'])
        self.assertGreater(b['area_px2'],a['area_px2'])
        xy=np.array([[x,y] for x in np.arange(-3,3,.1) for y in np.arange(-3,3,.1)]);p=np.c_[xy,np.full(len(xy),-4.)];shadow=np.zeros(len(xy))
        for direction,w in directions(large,5):shadow+=s.blocked(p,direction)[0]*w
        self.assertGreater(np.sum((shadow>.05)&(shadow<.95)),10)
    def test_cast_shadow_direction_and_occlusion(self):
        s=synthetic([[0,0,0]]);d=unit([0,.5,1]);p=np.array([[0,-2,-4],[0,3,-4]])
        b,_=s.blocked(p,d);self.assertEqual(b.tolist(),[True,False])
        # First point outside outer rim toward open sky; second crosses bead.
        b,_=s.blocked(np.array([[0,0,RADIUS+.001],[0,0,-RADIUS-.001]]),[0,0,1]);self.assertEqual(b.tolist(),[False,True])
    def test_real_bead2_native_and_origin_preserved(self):
        s=Scene('N2696_h+1_f0');meta,_=local_geometry(s,2164);b=next(b for b in meta['beads'] if b['generator_index']==2164)
        self.assertEqual(b['legacy_k'],2);self.assertEqual(s.config['origin'],2162)
        self.assertLess(b['convergence']['1']['distance_to_adaptive_px'],.3)
        hidden=next(b for b in meta['beads'] if b['legacy_k']==3);self.assertIsNone(hidden['centroid'])
    def test_known_light_recovery_on_heldout_surface(self):
        from scipy.optimize import least_squares
        s=synthetic([[0,0,0]]);d=s.grid([20,20,81,81]);keep=d['owner']>=0;d={k:v[keep] for k,v in d.items()}
        known=light_from([70,65,8],'known');truth=shade(s,d,known)['specular'];train=np.arange(len(truth))%3!=0
        def residual(p):return (shade(s,d,light_from(p,'fit'))['specular']-truth)[train]
        fit=least_squares(residual,[60,60,9],bounds=([-180,15,3],[180,89,20]),diff_step=1e-4)
        pred=shade(s,d,light_from(fit.x,'fit'))['specular']
        np.testing.assert_allclose(fit.x,[70,65,8],atol=.02)
        self.assertLess(np.sqrt(np.mean((pred[~train]-truth[~train])**2)),1e-5)

    def test_self_and_neighbor_blocker_classification(self):
        s=synthetic([[0,0,0],[0,0,5]])
        blocked,unknown,owner=s.blocked(np.array([[0,0,RADIUS+.01],[0,0,-RADIUS-.01]]),[0,0,1],return_owner=True)
        self.assertEqual(owner.tolist(),[1,0]);self.assertEqual(unknown,0)

    def test_new_actions_accept_old_backup(self):
        from .store import ReviewStore,ACTIONS
        with tempfile.TemporaryDirectory() as d:
            s=ReviewStore(Path(d),'image');old=s.read();s.update(0,'import',old)
            for action in ['visible-centroid-incorrect','predicted-reflection-incorrect','observed-reflection-incorrect-or-missing','lighting-mismatch']:self.assertIn(action,ACTIONS)

if __name__=='__main__':unittest.main()
