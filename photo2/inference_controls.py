"""Authored 2-D geometry controls, not POV renders or photo observations."""
import numpy as np


def brick_ring(columns=40, rows=5):
    """Hand-authored staggered grid bent into a circle; not a POV bead model."""
    xy, cov, truth = [], [], []
    for column in range(columns):
        angle = 2*np.pi*column/columns
        radial=np.array([np.cos(angle),np.sin(angle)])
        tangent=np.array([-radial[1],radial[0]])
        for row in range(rows):
            offset=row-.5*(column%2)-(rows-1)/2
            xy.append((columns*42/(2*np.pi)-offset*32)*radial)
            cov.append(12**2*np.outer(tangent,tangent)+18**2*np.outer(radial,radial))
            truth.append(int(6.5*column)+row)
    return np.array(xy),np.array(cov),np.array(truth),int(6.5*columns)
