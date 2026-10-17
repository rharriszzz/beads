"""Existing annulus, two historical placement implementations, frozen local fields."""
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT, read
from photo2.r299.forward import Surface
from photo2.r307.fast import Chain as Fast
from photo2.r309.geometry import Chain
from photo2.r295.geometry import AXES

# Finite exploration box, explicitly NOT measured physical parameter limits.
BOUNDS = dict(phase=(-np.pi, np.pi), s0=(-40., 40.), elevation=(20., 89.5),
              roll=(-90., 90.), tilt=(-45., 45.), minor=(2.5, 6.5),
              scale=(5.5, 12.), axial=(.3, 1.4))
VARIABLES = list(BOUNDS)
PAIRS = [('phase', 's0'), ('phase', 'elevation'), ('roll', 'elevation'),
         ('minor', 'scale'), ('tilt', 'elevation')]

class Legacy(Surface):
    """R297 placement retained; the existing global tilt law is available at zero."""
    trace = Fast.trace
    blocked = Fast.blocked
    def placement(self, k):
        line, g, phase = super().placement(k)
        tilt = np.radians(self.p.get('tilt', 0.))
        if tilt:
            # Same transported orientation law as R306, no new geometry.
            circum = np.cos(phase)[:, None]*g[AXES[1]]-np.sin(phase)[:, None]*g[AXES[2]]
            body = np.cos(tilt)*g[AXES[0]]+np.sin(tilt)*circum
            other = np.cross(g['radial'], body)
            other /= np.linalg.norm(other, axis=1)[:, None]
            g.update(zip(AXES, (body, other, np.cross(body, other))))
        return line, g, phase

def scene(p, data, implementation):
    return Legacy(p, data) if implementation == 'R297' else Chain(p, data)

def starts():
    files = [('R297-2337', 'r307', 'R297', 'R297'),
             ('R306-2405', 'r306', 'primary', 'R306'),
             ('R306-2733', 'r306', 'alternative-2665', 'R306'),
             ('R309-2733', 'r309', 'primary', 'R306'),
             ('R306-plus-open', 'r306', 'alternative-1857', 'R306'),
             ('R306-plus-closed', 'r306', 'alternative-2433', 'R306')]
    out = []
    for name, folder, stem, impl in files:
        path = ROOT/f'photo2/{folder}/results/campaign/exports/{stem}.json.gz'
        doc = read(path); p = deepcopy(doc['parameters'])
        p.setdefault('roll', 0.); p.setdefault('tilt', 0.)
        out.append(dict(name=name, parameters=p, implementation=impl,
                        source=str(path.relative_to(ROOT)), principal=len(out)<3))
    return out

def canonical(p):
    q = deepcopy(p)
    q['phase'] = float((q['phase']+np.pi)%(2*np.pi)-np.pi)
    return q

def validate(p):
    for k, (lo, hi) in BOUNDS.items():
        if not np.isfinite(p[k]) or not lo <= p[k] <= hi:
            return 'exploration bound: '+k
    if p['count'] < 2000: return 'maker minimum count'
    turn = p['count']/p['winding'] if p['topology']=='closed' else p['turn']
    if abs(p['count']*(1/turn-1/6.5)) > 1.000001: return 'closure twist bound'
    return None
