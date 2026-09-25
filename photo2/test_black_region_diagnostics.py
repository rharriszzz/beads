"""Controls for measurements; no tests equate highlights with bead counts."""
import copy
import unittest
import numpy as np
from black_region_diagnostics import sample_rgb, line_profile, local_model, exterior_scan


class DiagnosticControls(unittest.TestCase):
    def test_bilinear_sampling(self):
        y,x=np.indices((20,20));rgb=np.stack([x+2*y,2*x+y,x+y],axis=-1)
        np.testing.assert_allclose(sample_rgb(rgb,[[3.25,4.5]]),[[12.25,11,7.75]])

    def test_black_is_uninformative(self):
        result=line_profile(np.zeros((40,40,3)),[10,20],[30,20])
        self.assertFalse(result['valid_hue'].any())
        self.assertEqual(result['metrics']['measured_peaks'],[])
        self.assertEqual(result['metrics']['centerline_dark_fraction_between_endpoints'],1)
        with self.assertRaises(ValueError):line_profile(np.zeros((2,2,3)),[0,0],[0,0])

    def test_two_glints_are_measurements_only(self):
        y,x=np.indices((50,80));value=180*np.exp(-((x-25)**2+(y-25)**2)/8)+100*np.exp(-((x-50)**2+(y-25)**2)/8)
        result=line_profile(np.repeat(value[:,:,None],3,axis=2),[20,25],[55,25])
        peaks=result['metrics']['measured_peaks']
        self.assertEqual(len(peaks),2)
        np.testing.assert_allclose([p['xy'][0] for p in peaks],[25,50],atol=.3)
        self.assertNotIn('bead_count',result['metrics'])

    def test_held_out_target_cannot_teach_its_own_step(self):
        rows={i:{'marker_xy':[10+15*i,20]} for i in range(1,5)}
        labels=np.zeros((45,90),int);y,x=np.indices(labels.shape)
        for i,row in rows.items():
            cx,cy=row['marker_xy'];labels[((x-cx)/4)**2+((y-cy)/6)**2<=1]=i
        case=dict(step_pairs=[[1,2],[2,3],[3,4]],reference_ids=[1,2],prediction_anchor=4,validation_anchor=3)
        model=local_model(case,rows,labels,4)
        self.assertEqual(model['target_holdout']['error_px'],0)
        changed=copy.deepcopy(rows);changed[4]['marker_xy'][1]+=8
        model=local_model(case,changed,labels,4)
        self.assertEqual(model['target_holdout']['predicted_marker_xy'],[70,20])
        self.assertEqual(model['target_holdout']['error_px'],8)

    def test_exterior_clipping_and_saturated_neighbor(self):
        case={'exterior':dict(origin=[5,5],along=[1,0],outward=[0,1],span=[-2,2],depth=[0,10])}
        rgb=np.zeros((30,30,3));_,edges=exterior_scan(rgb,case)
        self.assertTrue(all(np.isnan(edge).all() for edge in edges.values()))
        rgb[:]=255;rgb[5:10]=0;rgb[12:14]=[30,0,0]
        _,edges=exterior_scan(rgb,case)
        # A separated saturated red neighbor must not extend the neutral edge.
        self.assertTrue(np.all(edges['40']<5))


if __name__=='__main__':unittest.main()
