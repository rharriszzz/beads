"""Scientific contracts on actual photographic maps and deliberately corrupt predictions."""
import unittest
import numpy as np
from photo2.r297.common import ROOT,read,sha
from .objective import Objective,boundaries

OUT=ROOT/'photo2/r313/results';EV=ROOT/'photo2/r313/evidence'
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps=dict(np.load(EV/'maps.npz'));cls.doc=read(EV/'freeze.json');cls.engine=Objective(cls.maps,cls.doc)
        cls.model=read(OUT/'models/R306-2405.json.gz');cls.rays=dict(np.load(OUT/'models/R306-2405.npz'));cls.indices=np.array(cls.model['positions']['indices'])
    def test_frozen_photo_independent_maps(self):
        self.assertEqual(sha(EV/'maps.npz'),self.doc['maps_sha256'])
        self.assertFalse(self.doc['policy']['contours_used']);self.assertFalse(self.doc['policy']['black_material_inferred'])
        self.assertGreater(self.maps['material'].sum(),20000);self.assertGreater(self.maps['edges'].sum(),1000)
        self.assertFalse(np.any(self.maps['material']&self.maps['paper']))
    def test_native_200_hidden_and_context_present(self):
        self.assertEqual(self.indices[(self.indices>=-100)&(self.indices<=99)].tolist(),list(range(-100,100)))
        self.assertGreater(len(self.indices),2000)
    def test_corrupt_prediction_controls(self):
        controls=read(OUT/'controls.json');base=controls[0]['development']['score']
        for row in controls[1:]:self.assertGreater(row['development']['score'],base,str((row['kind'],row.get('dx'),row.get('dy'))))
    def test_unknown_never_earns_explanation(self):
        r=self.engine.measure(self.rays['owner'],np.ones_like(self.rays['unknown']),self.indices)
        self.assertEqual(r['material_explained_pixels'],0);self.assertEqual(r['background_intrusion_percent'],100.)
    def test_comparison_pixels_never_enter_training(self):
        a=self.engine.measure(self.rays['owner'],self.rays['unknown'],self.indices)
        changed=self.rays['owner'].copy();comparison=self.maps['split'].ravel()!=0;changed[comparison]=-1
        b=self.engine.measure(changed,self.rays['unknown'],self.indices)
        # Transition distance uses neighboring prediction context, so only material
        # and core terms are strictly separable; no photographic comparison cues used.
        for k in ['material_explained_pixels','modal_ownership_percent','mixed_pigment_pixels','background_intrusion_pixels']:self.assertEqual(a[k],b[k])
    def test_unknown_edges_excluded(self):
        own=self.rays['owner'].reshape(tuple(self.maps['shape']));u=np.ones(own.shape,bool)
        self.assertEqual(boundaries(own,u).sum(),0)
if __name__=='__main__':unittest.main()
