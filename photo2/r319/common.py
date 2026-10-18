from copy import deepcopy
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,save,digest,sha,utc
OUT=ROOT/'photo2/r319/results'
OLD=ROOT/'photo2/r318/results'

def change(p,key,d):
    q=deepcopy(p)
    if isinstance(key,(tuple,list)):q[key[0]][key[1]]+=float(d)
    else:q[key]=q.get(key,0.)+float(d)
    return q

def variables(p):
    # Scales are diagnostic changes, not claimed physical ranges.
    rows=[]
    def add(key,scale,unit,interpretation):rows.append(dict(key=key,scale=scale,unit=unit,interpretation=interpretation))
    specs=[('translation',1,'photo px','image registration'),('phase',.04,'rad','global minor phase'),('s0',1,'photo px','major station origin'),('tilt',1,'deg','tangent/circumferential hole-axis angle'),('axial',.02,'ratio','shared axial thickness'),('radius',.015,'source units','shared outer radius'),('minor',.03,'source units','minor helix radius'),('elevation',.5,'deg','camera elevation and deprojected planar axis'),('roll',.5,'deg','camera roll and deprojected planar axis'),('scale',.04,'px/source unit','image/world scale'),('perspective',.00001,'1/source unit','camera inverse distance'),('turn',.003,'beads/revolution','open-chain phase advance'),('gap_steps',.25,'addresses','open-chain uncovered station span'),('light_az',3,'deg','shared light azimuth'),('light_el',2,'deg','shared light elevation'),('roughness',1,'deg','shared specular angular width'),('light_inverse',.0002,'1/source unit','finite shared light inverse distance'),('light_width',.5,'deg','extended shared light angular width'),('radial_cant',1,'deg inward','shared radial hole-axis cant'),('tilt_y',1,'deg','linear image-height orientation'),('tilt_y2',1,'deg','quadratic image-height orientation'),('minor_y',.005,'fraction','image-height minor-radius slope'),('trajectory_mix',.03,'fraction','blend hole axis toward center trajectory')]
    for k,h,u,i in specs:
        if k=='translation':
            for j in range(2):add([k,j],h,u,i)
        else:add(k,h,u,i)
    for k,h,u in [('axis_nodes',1,'photo px'),('local_phase',.04,'rad'),('local_spacing',.002,'fraction'),('compact_phase',.04,'rad'),('compact_spacing',.002,'fraction'),('compact_tilt',1,'deg'),('compact_cant',1,'deg inward')]:
        for j in range(len(p[k])):add([k,j],h,u,'periodic 32-node field' if k.startswith(('axis','local')) else 'compact smooth bump coefficient')
    for k in ['phase_halfwidth','spacing_halfwidth','orientation_halfwidth']:add(k,1,'addresses','compact basis support halfwidth')
    for j in range(len(p['compact_centers'])):add(['compact_centers',j],1,'addresses','shared compact basis location')
    return rows

def positions(r):return np.array([z['predicted'] for z in r['rows']],float)
