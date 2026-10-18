import unittest
import numpy as np
from .detect import principal
from .optics import objective
from .optics import Engine
from photo2.r297.common import read
from .detect import OUT

class Contracts(unittest.TestCase):
    def test_disconnected_lobes_never_average(self):
        xy=np.array([[0,0],[1,0],[10,0],[11,0]])
        h=principal(xy,np.array([1.,.8,.9,.7]))
        self.assertLess(h['point'][0],1);self.assertEqual(len(h['secondary_components']),1)
    def test_tied_connected_peak_retained(self):
        h=principal(np.array([[0,0],[1,0],[2,0]]),np.array([1.,1.,.2]))
        self.assertEqual(len(h['ties']),2);self.assertEqual(h['point'],[.5,0.])
    def test_missing_cannot_improve_maximum(self):
        self.assertGreater(objective(dict(feasible=True,missing=1,emax_px=None)),10000)
    def test_exact_maximum_not_mean(self):
        a=dict(feasible=True,missing=0,emax_px=10,rms_px=3)
        b=dict(feasible=True,missing=0,emax_px=9,rms_px=8)
        self.assertLess(objective(b),objective(a))
    def test_frozen_map_cannot_change(self):
        epoch=read(OUT/'epoch.json');key=next(iter(epoch['mapping']));epoch['mapping'][key]+=1
        with self.assertRaises(ValueError):Engine(epoch)

if __name__=='__main__':unittest.main()
