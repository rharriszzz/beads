"""R258 inverse, independence and persistence regression tests."""
import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
from .refit import BeadCurve,initialize,apply,physical,SurfaceLoss,fit,audit,OUT,ROOT
from .models import model_version
from .generate import sha,save


def synthetic_case(h=1):
    c=initialize(h=h);c['phase_harmonics']=[0]*4;c['local']=[];c['freeze_B_curve']=False
    # A known analytic circle, independent of all historical/photo geometry.
    u=np.arange(192)/192;radius=__import__('tangent_circles').ROW*c['turns']/(2*np.pi)
    c['knots']=np.c_[radius*np.cos(2*np.pi*u),radius*np.sin(2*np.pi*u),np.zeros(192)].tolist()
    c['origin']=0;c['camera']=dict(elevation=78.,roll=0.,tx=1500.,ty=1500.,scale=6.);c['phase']=.3
    m=BeadCurve(c);t=.25;gi=round(t*c['n']);p=m.view.project(m.geometry([gi])['centers'])[0];box=[int(p[0]-85),int(p[1]-85),int(p[0]+85),int(p[1]+85)]
    loss=SurfaceLoss(box,[],step=2);own=loss.raster(m);rows=[]
    for i in np.unique(own[own>=0]):
        pts=loss.xy[own.ravel()==i]
        if len(pts)<20:continue
        rows.append(dict(id=str(i),component=str(i),xy=pts.mean(axis=0).tolist(),patch=pts.tolist(),color='synthetic',weight=1.,distinct=True,split='holdout-body' if len(rows)%5==0 else 'train',identity=int(i),reason='Known synthetic visible surface; truth used only to form/evaluate observations'))
    return c,t,SurfaceLoss(box,rows,2)

class RefitTests(unittest.TestCase):
    def test_no_initial_curve_target_and_rigid_invariance(self):
        c,t,l=synthetic_case();m=BeadCurve(c);before=physical(m)
        c2=copy.deepcopy(c);q=np.array(c2['knots']);q+=[20,-17,0];c2['knots']=q.tolist();after=physical(BeadCurve(c2))
        self.assertAlmostEqual(before['cost'],after['cost'],places=11)
        # No saved spline/edge or input curve is accepted by the loss API.
        self.assertNotIn('initial',SurfaceLoss.__init__.__code__.co_varnames)
        from unittest.mock import patch
        with patch('photo2.bead_debugger.refit.old_load',side_effect=AssertionError('historical read during objective')):
            self.assertLess(l.evaluate(m),.01)
    def test_wrong_initial_curve_recovered(self):
        c,t,l=synthetic_case();p=np.zeros(13);p[:2]=[7,-5];wrong=apply(c,t,p,'C');before=l.evaluate(BeadCurve(wrong));found,log=fit(wrong,t,l,'C',400)
        after=l.evaluate(BeadCurve(found));truth=BeadCurve(c);i=np.arange(round(t*c['n'])-12,round(t*c['n'])+13)
        def error(cc):
            m=BeadCurve(cc);return float(np.sqrt(np.mean(np.sum((m.view.project(m.geometry(i)['line'])-truth.view.project(truth.geometry(i)['line']))**2,axis=1))))
        result=dict(before_loss=before,after_loss=after,wrong_curve_rms_px=error(wrong),recovered_curve_rms_px=error(found),fit=log,
                    heldout_before=l.evaluate(BeadCurve(wrong),'holdout-body'),heldout_after=l.evaluate(BeadCurve(found),'holdout-body'))
        save(OUT/'synthetic-curve.json',result)
        self.assertLess(after,before*.3);self.assertLess(error(found),3.);self.assertLess(result['heldout_after'],result['heldout_before'])
    def test_phase_recovery_both_hands(self):
        results=[]
        for h in [-1,1]:
            c,t,l=synthetic_case(h);p=np.zeros(13);p[6]=.28;wrong=apply(c,t,p,'B');before=l.evaluate(BeadCurve(wrong));found,log=fit(wrong,t,l,'B',200);after=l.evaluate(BeadCurve(found))
            self.assertLess(after,before*.2);self.assertLess(abs(log['parameters'][6]+.28),.08);results.append(dict(h=h,before=before,after=after,phase_correction=log['parameters'][6]))
        save(OUT/'synthetic-phase.json',results)
    def test_closure_missing_ambiguity_holdout(self):
        c,t,l=synthetic_case();m=BeadCurve(c);r=physical(m)
        self.assertLess(r['closure_position'],1e-10);self.assertLess(r['closure_tangent'],1e-10);self.assertLess(r['winding_step_max']-r['winding_step_min'],1e-9)
        original=l.evaluate(m);rr=copy.deepcopy(l.rows);rr=[r for r in rr if r['split']=='train'];amb=copy.deepcopy(rr[0]);amb['id']='uncertain duplicate';amb['distinct']=False;amb['identity']=None;amb['weight']=.3;rr.append(amb)
        self.assertLess(SurfaceLoss(l.box,rr,2).evaluate(m),.01)
        for r in l.rows:
            if r['split']=='holdout-body':r['patch']=[[l.box[0],l.box[1]]]
        self.assertAlmostEqual(original,l.evaluate(m))
    def test_immutable_legacy_models_and_reviews(self):
        d=json.loads((OUT/'immutable-inputs.json').read_text())
        for mid,v in d['legacy_versions'].items():self.assertEqual(model_version(mid)[0],v)
        for p,h in d['files'].items():self.assertEqual(sha(ROOT/p),h,p)
    def test_dimension_tracer_matches_source_and_fixed_identity(self):
        from .raycast import trace,annulus_sdf
        from .models import rays
        from curved_surface_fit import sdf
        c,t,l=synthetic_case();m=BeadCurve(c);g=m.geometry(np.arange(c['n']))
        a=rays(m,l.xy,g);b=trace(m,l.xy,g)
        np.testing.assert_array_equal(a[0],b[0]);np.testing.assert_allclose(a[1],b[1]);np.testing.assert_array_equal(a[2],b[2])
        p=np.random.default_rng(258).normal(size=(200,3))*2;np.testing.assert_allclose(sdf(p),annulus_sdf(p),atol=1e-12)
        # A known identity must never fall through a tied dustbin cost and
        # silently become a distant bead when its support is outside the model.
        r=copy.deepcopy(l.rows[0]);r['patch']=[[l.box[0],l.box[1]]];r['split']='train'
        _,records=SurfaceLoss(l.box,[r],2).evaluate(m,'train',True)
        self.assertEqual(records[0]['owner'],r['identity'])

    def test_polygon_review_roundtrip(self):
        from .store import ReviewStore
        with tempfile.TemporaryDirectory() as tmp:
            s=ReviewStore(tmp,'test');r=dict(model_id='old',model_version='v',generation_id='d',generator_index=2,source_position=[100,100],action='location-incorrect',note='yellow',region_polygon=[[90,90],[110,90],[110,110]],region_semantics='positive-interior',region_color='yellow')
            saved=s.update(0,'review',r);s2=ReviewStore(tmp,'test');self.assertEqual(saved,s2.read());self.assertEqual(saved['reviews'][0]['region_polygon'],r['region_polygon'])
            other=ReviewStore(Path(tmp)/'import','test');self.assertEqual(other.update(0,'import',saved)['reviews'],saved['reviews'])

if __name__=='__main__':unittest.main()
