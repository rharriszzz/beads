"""Broad finite exploration of existing physical hypotheses and smooth laws."""
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,digest
from photo2.r311.model import starts as historical,Legacy
from .fast import Chain

# Numerical exploration limits, not measured physical ranges. Radius fixes units.
BOX=dict(phase=(-np.pi,np.pi),s0=(-100.,100.),elevation=(25.,88.),roll=(-180.,180.),
         tilt=(-35.,35.),minor=(2.5,6.5),scale=(5.5,12.),axial=(.30,1.35),
         perspective=(0.,.0015),light_az=(-180.,180.),light_el=(15.,88.),
         roughness=(5.,24.),light_inverse=(0.,.002),gap_steps=(.25,12.),
         twist=(-1.,1.),tilt_y=(-6.,6.),tilt_y2=(-6.,6.),minor_y=(-.08,.08))
WIDTH=dict(phase=.65,s0=14.,elevation=12.,roll=30.,tilt=8.,minor=.55,scale=.8,
           axial=.15,perspective=.00025,light_az=35.,light_el=15.,roughness=4.,
           light_inverse=.0005,gap_steps=2.,twist=.4,tilt_y=2.,tilt_y2=2.,minor_y=.025)
GROUPS=[['phase','s0','elevation','roll'],['minor','scale','axial','tilt'],
        ['phase','s0','light_az','light_el','roughness','light_inverse'],
        ['elevation','roll','perspective','scale','tilt','minor'],
        ['twist','gap_steps','phase','s0','minor','axial'],
        ['tilt_y','tilt_y2','minor_y','elevation','light_az','light_el'],
        list(BOX),['axis_nodes','local_phase','local_spacing','phase','s0','scale']]

def canonical(p):
    p=deepcopy(p)
    for k in ['phase']:p[k]=float((p[k]+np.pi)%(2*np.pi)-np.pi)
    for k in ['roll','light_az']:p[k]=float((p[k]+180)%360-180)
    p.setdefault('light_inverse',0.)
    for k in ['tilt_y','tilt_y2','minor_y']:p.setdefault(k,0.)
    # Explicit existing twist coordinate. Closed hypotheses use integer winding.
    if 'twist' in p:
        if p['topology']=='closed':p['winding']=int(round(p['count']/6.5+p['twist']))
        else:p['turn']=p['count']/(p['count']/6.5+p['twist'])
        p.pop('twist')
    return p

def coordinate(p,k):
    if k=='twist':return p['count']/(p['count']/p['winding'] if p['topology']=='closed' else p['turn'])-p['count']/6.5
    return p.get(k,0.)

def validate(p):
    for k,(lo,hi) in BOX.items():
        value=coordinate(p,k)
        if not np.isfinite(value) or value<lo-1e-8 or value>hi+1e-8:return 'numerical exploration bound: '+k
    if p['count']<2000:return 'maker minimum count 2000'
    if p['hand'] not in [-1,1] or p['topology'] not in ['open','closed']:return 'invalid discrete hypothesis'
    for key,limit in [('axis_nodes',40.),('local_phase',.8),('local_spacing',.018)]:
        if not np.isfinite(p[key]).all() or max(abs(np.array(p[key])))>limit:return 'numerical smooth-field bound: '+key
    return None

def seeds():
    out=[]
    for s in historical():
        if s['implementation']=='R297':continue
        out.append(dict(s,parameters=canonical(s['parameters'])))
    # R311 distant basins retain their original family's fixed correspondences.
    for ident,parent in [(163,'R306-2405'),(663,'R306-2733'),(796,'R306-2405')]:
        row=read(ROOT/f'photo2/r311/results/campaign/trials/{ident:06d}.json.gz')
        out.append(dict(name=f'R311-{ident}',family=parent,parameters=canonical(row['parameters']),implementation='R306',source=f'photo2/r311/results/campaign/trials/{ident:06d}.json.gz'))
    # New counts across the earlier minimum-to-dense interval, both hands/topologies.
    base=next(s for s in out if s['name']=='R306-2405')
    for i,count in enumerate([2000,2132,2265,2535,2860,3068,3200]):
        for hand in [-1,1]:
            topology='closed' if (i+(hand==1))%2 else 'open'
            p=deepcopy(base['parameters']);p.update(count=count,hand=hand,topology=topology,winding=round(count/6.5),turn=6.5)
            out.append(dict(name=f'N{count}-h{hand}-{topology}',parameters=canonical(p),implementation='R306',source=base['source']))
    for s in out:s.setdefault('family',s['name'])
    return out

def scene(p,data):return Chain(canonical(p),data)

def geometry_key(p):
    return digest({k:v for k,v in p.items() if k not in ['light_az','light_el','roughness','light_inverse']})

def distance(a,b):
    if any(a[k]!=b[k] for k in ['count','hand','topology']):return 10.
    vals=[]
    for k,(lo,hi) in BOX.items():
        d=coordinate(a,k)-coordinate(b,k)
        if k in ['roll','light_az']:d=(d+180)%360-180
        if k=='phase':d=(d+np.pi)%(2*np.pi)-np.pi
        vals.append(d/(hi-lo))
    for k,scale in [('axis_nodes',40),('local_phase',.8),('local_spacing',.018)]:
        vals.append(float(np.sqrt(np.mean((np.array(a[k])-b[k])**2)))/scale)
    return float(np.linalg.norm(vals))
