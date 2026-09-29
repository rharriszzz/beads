import unittest
import numpy as np
from refine_surface_constraints import constraints,score


class SurfaceConstraintTests(unittest.TestCase):
    def setUp(self):
        yy,xx=np.mgrid[:25,:25]
        self.xy=np.column_stack((xx.ravel(),yy.ravel()));self.shape=xx.shape
        self.mask=(xx>=5)&(xx<=18)&(yy>=5)&(yy<=18)
        self.point=[12,12]

    def test_unknown_ownership_cannot_change_constraints_or_score(self):
        unknown,a=constraints(self.xy,self.shape,{'C':self.mask},None,self.point,4,2)
        changed=self.mask.copy();changed[unknown]=~changed[unknown]
        _,b=constraints(self.xy,self.shape,{'C':changed},None,self.point,4,2)
        for key in ['core','inside','outside']:np.testing.assert_array_equal(a['C'][key],b['C'][key])
        self.assertEqual(a['C']['normalization'],b['C']['normalization'])
        labels=np.full(self.shape,6);altered=labels.copy();altered[unknown]=0
        for method in ['cores','masked_regions']:
            self.assertEqual(score(labels,{'C':0},a,method),score(altered,{'C':0},a,method))

    def test_tracing_only_supported_pixels_preserves_core_score(self):
        from refine_surface_constraints import cast
        import json
        from local_surface_fit import ROOT,polygons
        cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
        prior=json.loads((ROOT/'photo2/review/r126/perspective-report.json').read_text())
        f=next(x for x in prior['results'] if x['hypothesis']=='H1' and x['focal_ratio']==1.)
        camera=dict(kind='perspective',focal_px=prior['nominal_focal_px'],principal_xy=prior['principal_xy'])
        xy,shape,masks=polygons(cfg,spacing=3)
        _,data=constraints(xy,shape,masks,'G',[1364,278],6,3,spacing=3)
        active=np.logical_or.reduce([x['core'] for x in data.values()]).ravel()
        full=cast(np.array(f['parameters']),xy,f,camera)
        partial=np.full(len(xy),-999,int)
        partial[active]=cast(np.array(f['parameters']),xy[active],f,camera)
        np.testing.assert_array_equal(full[active],partial[active])
        self.assertEqual(score(full.reshape(shape),f['mapping'],data,'cores'),
                         score(partial.reshape(shape),f['mapping'],data,'cores'))

    def test_holdout_and_unassigned_pixels_have_no_core_penalty(self):
        _,data=constraints(self.xy,self.shape,{'C':self.mask,'G':~self.mask},'G',self.point,4,2)
        self.assertNotIn('G',data)
        labels=np.where(data['C']['core'],0,-999)
        self.assertEqual(score(labels,{'C':0},data,'cores'),0)
        # Oversized regions are deliberately not penalized by positive cores;
        # held-out overlap and area diagnostics must expose this limitation.
        self.assertEqual(score(np.zeros(self.shape,int),{'C':0},data,'cores'),0)


if __name__=='__main__':unittest.main()
