"""Shared size, orientation, supporting-plane and fixed-region ownership diagnosis."""
import numpy as np
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r297.geometry import reference
from photo2.r295.geometry import AXES
from .diagnose_geometry import make
from .geometry_experiment import paper

def run(models,destination):
 data,_,_=load();ref=reference();out=[]
 for row in models:
  s=make(row['parameters'],data,row['implementation']);r=paper(s);turn=s.n/s.p['winding'] if s.closed else s.p['turn'];group=np.floor(s.indices/turn).astype(int);z=np.array([0.,0.,1.]);minimum=s.centers[:,2]-s.support(np.tile(z,(s.n,1)),s.g[AXES[0]]);clear=minimum-r['plane_z'];low=[float(clear[group==g].min()) for g in np.unique(group) if np.sum(group==g)>=5]
  r['per_minor_turn_lowest_clearance']=dict(count=len(low),median=float(np.median(low)),p95=float(np.percentile(low,95)),maximum=max(low));ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));tangent=s.g.get('axis_tangent')
  if tangent is None:
   # Original R297 planar line derivative, distinct from bead-hole orientation.
   tangent=np.gradient(s.line,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None]
  path=np.gradient(s.centers,axis=0);path/=np.linalg.norm(path,axis=1)[:,None];body=s.g[AXES[0]]
  major=np.degrees(np.arccos(np.clip(abs(np.sum(body*tangent,axis=1)),0,1)));trajectory=np.degrees(np.arccos(np.clip(abs(np.sum(body*path,axis=1)),0,1)));j=int(np.flatnonzero(s.indices==0)[0]);reg=[]
  cores=row.get('development',{}).get('cores',[])+row.get('comparison',{}).get('cores',[])
  for c in cores:
   a=float(ref.project([c['point']])['arc'][0]);signed=((a-data['arc0'])*data['direction']+ref.length/2)%ref.length-ref.length/2
   reg.append(dict(id=c['id'],point=c['point'],photo_arc_from_reference=signed,index=c['index'],modal_fraction=c['modal_fraction'],substantial_owners=c['substantial_owners'],missing=c['unexplained_fraction'],fragmented=c['fragmented_fraction']))
  events=[]
  for threshold in [.6,.7,.8]:
   for direction in [-1,1]:
    bad=sorted([c for c in reg if c['photo_arc_from_reference']*direction>2 and c['modal_fraction']<threshold],key=lambda c:abs(c['photo_arc_from_reference']))
    events.append(dict(modal_fraction_threshold=threshold,direction=direction,first=bad[0] if bad else None))
  # Shared dimensions in source units, not calibrated millimeters.
  out.append(dict(name=row['name'],supporting_plane=r,orientation=dict(bead0_major_axis_angle_deg=float(major[j]),bead0_neighbor_chord_angle_deg=float(trajectory[j]),target_major_angle_range=[float(major[ix].min()),float(major[ix].max())],target_trajectory_chord_angle_range=[float(trajectory[ix].min()),float(trajectory[ix].max())],note='Neighbor chord is not true trajectory derivative and is not assumed bead-hole direction.'),shared_dimensions=dict(outer_diameter_units=2*s.radius,axial_thickness_units=1.4*s.radius*s.axial,hole_diameter_units=2*s.radius*s.hole,rounding_fraction=s.rounding,bead_count=s.n,identical_rigid_glass=True,physical_mm_scale_identified=False),first_events=events,regions=reg))
 save(destination,out);return out
