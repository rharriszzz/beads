"""Image-only curved phase-band lattice. No maker graph or 3D imports.

Band tracing reads only the original RGB photograph. Crossing evidence reuses the
image-only R275 catalog, with no physical identities or graph links. The historical
viewing rectangle chooses geography, not bead positions. Band crossings remain
hypotheses until associated with saved native pigment/reflection observations.
"""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from skimage.feature import peak_local_max
from skimage.measure import find_contours, regionprops
from skimage.restoration import unwrap_phase
from skimage.segmentation import watershed
from matplotlib.colors import rgb_to_hsv

ROOT=Path(__file__).resolve().parents[2]
CROP=(1180,130,1540,520)
CONFIG=dict(crop=CROP,fft_size=1024,frequency_range=[.018,.060],spectral_closure_sigma=2/1024,
            demodulation_sigma=35,controls=[28,42],minimum_band_clearance=6,
            interior_clearance=18,phase_amplitude_fraction=.22,maximum_phase_gradient=.085,
            stable_crossing_px=6,uncertain_crossing_px=12,
            bright_support_location_allowance=18,
            evidence_assignment_margin=3,minimum_pigment_pixels=24)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,obj): Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def sample(a,xy): return ndi.map_coordinates(a,[np.asarray(xy)[...,1],np.asarray(xy)[...,0]],order=1,mode='nearest')

def preprocess(image,crop=CROP):
    rgb=np.asarray(image.crop(crop).convert('RGB'),float)/255
    r,g,b=rgb.transpose(2,0,1);v=rgb.max(2)
    # Pink paper is excluded by chromaticity, while genuinely dark material remains.
    fg=((r>1.5*b)&(r>.13))|(v<.30)
    fg=ndi.binary_fill_holes(ndi.binary_closing(fg,iterations=5))
    lab,_=ndi.label(fg);sz=np.bincount(lab.ravel());sz[0]=0
    if not sz.max(): raise ValueError('No foreground')
    fg=lab==sz.argmax();clearance=ndi.distance_transform_edt(fg)
    z=np.log(.05+v);z-=ndi.gaussian_filter(z,8)
    z/=np.sqrt(ndi.gaussian_filter(z*z,16)+.03)
    weight=ndi.gaussian_filter(fg.astype(float),5)*np.hanning(rgb.shape[1])[None,:]
    return dict(rgb=rgb,fg=fg,clearance=clearance,z=z,weight=weight)

def directions(data):
    n=CONFIG['fft_size'];f=np.fft.fftshift(np.fft.fft2(data['z']*data['weight'],s=(n,n)));p=abs(f)**2
    fy,fx=np.meshgrid(np.fft.fftshift(np.fft.fftfreq(n)),np.fft.fftshift(np.fft.fftfreq(n)),indexing='ij');rad=np.hypot(fx,fy)
    loc=peak_local_max(p*((rad>.018)&(rad<.060)&(fx>0)),min_distance=6,num_peaks=24)
    ks=np.array([[fx[y,x],fy[y,x]] for y,x in loc]);powers=np.array([p[y,x] for y,x in loc])
    coords=np.argwhere(data['fg'])[:,::-1];_,vec=np.linalg.eigh(np.cov(coords.T));t=vec[:,-1];t*=np.sign(t[0]);normal=np.array([-t[1],t[0]])
    angles=np.degrees(np.arctan2(ks@normal,ks@t));triples=[]
    for i in range(len(ks)):
        for j in range(len(ks)):
            if not(-80<angles[i]<-25 and 25<angles[j]<80):continue
            for l in range(len(ks)):
                err=float(np.linalg.norm(ks[i]+ks[j]-ks[l]))
                if abs(angles[l])>=25 or err>=.008:continue
                score=float((powers[i]*powers[j]*powers[l])**(1/3)*np.exp(-.5*(err/CONFIG['spectral_closure_sigma'])**2))
                triples.append(dict(peaks=[i,j,l],score=score,closure_error=err))
    triples.sort(key=lambda a:-a['score'])
    if not triples: raise ValueError('No reciprocal triangle; abstain')
    selected=ks[triples[0]['peaks'][:2]]
    peaks=[dict(id=i,frequency_xy=k.tolist(),power=float(powers[i]),angle_relative_strip=float(angles[i])) for i,k in enumerate(ks)]
    return selected,dict(strip_tangent=t.tolist(),peaks=peaks,triangles=triples,selected=selected.tolist(),
        warning='Spectral normal directions, not point-to-point bead directions. All competing triples retained.')

def phases_and_tracks(data,ks,sigma):
    z=data['z'];fg=data['fg'];h,w=z.shape;y,x=np.mgrid[:h,:w];phases=[];amps=[];masks=[];tracks=[]
    for family,k in enumerate(ks):
        carrier=k[0]*x+k[1]*y;zz=z*fg*np.exp(-2j*np.pi*carrier)
        env=ndi.gaussian_filter(zz.real,sigma)+1j*ndi.gaussian_filter(zz.imag,sigma)
        phase=carrier+unwrap_phase(np.ma.array(np.angle(env),mask=~fg),rng=0).filled(np.nan)/(2*np.pi)
        amp=abs(env);floor=CONFIG['phase_amplitude_fraction']*np.median(amp[data['clearance']>18])
        dy,dx=np.gradient(phase);grad=np.hypot(dx,dy)
        mask=(data['clearance']>=6)&(amp>=floor)&(grad<CONFIG['maximum_phase_gradient'])&np.isfinite(grad)
        phases.append(phase);amps.append(amp);masks.append(mask)
        lo=int(np.floor(np.nanmin(phase[mask])));hi=int(np.ceil(np.nanmax(phase[mask])))
        for level in range(lo,hi+1):
            for path in find_contours(phase,level,mask=mask):
                xy=path[:,::-1];length=float(np.linalg.norm(np.diff(xy,axis=0),axis=1).sum())
                if length<12:continue
                tracks.append(dict(id=f'F{family}-{sum(t["family"]==family for t in tracks)+1:02}',family=family,
                    phase_level=level,length_px=length,points=(xy+np.array(CROP[:2])).tolist(),
                    amplitude_min=float(sample(amp,xy).min()),status='photographic band fragment; not automatically a bead sequence'))
    return np.array(phases),np.array(amps),np.array(masks),tracks

def crossings(phases,tracks):
    # Every crossing comes from an actual pair of saved contour polylines.
    out=[];byfamily={f:[t for t in tracks if t['family']==f] for f in (0,1)}
    for t0 in byfamily[0]:
        xy=np.array(t0['points'])-np.array(CROP[:2]);val=sample(phases[1],xy)
        for t1 in byfamily[1]:
            level=t1['phase_level'];other=np.array(t1['points'])-np.array(CROP[:2])
            for i in np.flatnonzero((val[:-1]-level)*(val[1:]-level)<=0):
                if not np.isfinite(val[i:i+2]).all() or abs(val[i+1]-val[i])<1e-10:continue
                fraction=(level-val[i])/(val[i+1]-val[i]);point=xy[i]+fraction*(xy[i+1]-xy[i])
                if np.linalg.norm(other-point,axis=1).min()>1.6:continue
                if any(np.linalg.norm(np.array(q['xy_local'])-point)<2 for q in out):continue
                out.append(dict(id=f'X{len(out)+1:03}',xy_local=point.tolist(),xy=(point+np.array(CROP[:2])).tolist(),
                    track_ids=[t0['id'],t1['id']],ab=[t1['phase_level'],t0['phase_level']]))
    return out

def observations(data):
    # Reuse measured pigment/reflection evidence instead of inventing segmentation.
    # Deliberately ignore historical centerline groups, graph/physical identities,
    # region outlines and black-body collars. Only bright native supports are read.
    path=ROOT/'photo2/review/r275/inventory.json';catalog=json.loads(path.read_text())
    obs=[];support=[]
    for record in catalog['locations']:
        patch=record['bright_patch'];point=np.array(patch['centroid'])
        if not(CROP[0]<=point[0]<CROP[2] and CROP[1]<=point[1]<CROP[3]):continue
        pixels=np.array([[x,y] for y,xa,xb in patch['runs'] for x in range(xa,xb)])
        if not len(pixels):continue
        oid=record['id'];local=point-np.array(CROP[:2])
        clearance=float(sample(data['clearance'],local[None])[0])
        obs.append(dict(id=oid,kind='specular-reflection' if record['color']=='black' else 'pigment-bright-patch',
            color=record['color'],xy=point.tolist(),allowance_px=18,area=len(pixels),source_pixel_count=len(pixels),
            location_kind='observed bright support centroid; not bead center',pixel_support=oid,
            source='photo2/review/r275/inventory.json:locations:'+oid,source_sha256=sha(path),
            historical_interior_status=record['interior_status'],band_clearance_px=clearance,
            note='Historical image-only color cue; no bead index, centerline grouping or full outline reused.'))
        support.append(dict(id=oid,pixels_xy=pixels.tolist()))
    # Supplemental local white reflections, using only the original RGB. These
    # are not predictions at lattice sites. Existing observations retain priority;
    # nearby new components are not counted as separate beads.
    rgb=data['rgb'];lin=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
    white=lin.min(2);smooth=ndi.gaussian_filter(white,.65);contrast=smooth-ndi.gaussian_filter(white,5)
    loc=peak_local_max(smooth,min_distance=9,threshold_abs=.07,labels=data['fg'])
    for yy,xx in loc:
        if contrast[yy,xx]<.025 or data['clearance'][yy,xx]<11:continue
        y0=max(0,yy-10);x0=max(0,xx-10);patch=white[y0:yy+11,x0:xx+11]
        lab,_=ndi.label(patch>=.5*white[yy,xx],np.ones((3,3)))
        label=lab[yy-y0,xx-x0]
        if not label:continue
        py,px=np.where(lab==label)
        if len(px)<2:continue
        pixels=np.column_stack([px+x0,py+y0]);point=np.average(pixels,axis=0,weights=white[pixels[:,1],pixels[:,0]])+np.array(CROP[:2])
        nearby=[o for o in obs if np.linalg.norm(np.array(o['xy'])-point)<12]
        if nearby:continue  # location-level deduplication; not an identity proof
        clipped=bool(np.any((px==0)|(py==0)|(px==patch.shape[1]-1)|(py==patch.shape[0]-1)))
        if clipped:continue
        surround=rgb[max(0,yy-8):yy+9,max(0,xx-8):xx+9];med=np.median(surround.reshape(-1,3),axis=0)
        color='black' if med.max()<90/255 else ('yellow' if med[1]>.5*med[0] and med[2]<.6*med[0] else 'red')
        oid=f'NEW-{xx+CROP[0]}-{yy+CROP[1]}'
        obs.append(dict(id=oid,kind='fresh-bright-component',color=color,xy=point.tolist(),allowance_px=18,
            area=len(px),source_pixel_count=len(px),pixel_support=oid,source='original RGB, linear minimum-channel half-maximum component',
            location_kind='bright component; not bead center',band_clearance_px=float(data['clearance'][yy,xx]),
            color_status='automatic local pigment/darkness cue'))
        support.append(dict(id=oid,pixels_xy=(pixels+np.array(CROP[:2])).tolist()))
    return obs,support

def associate_crossings(nodes,obs,data,controls):
    xy=np.array([p['xy'] for p in nodes]);oxy=np.array([p['xy'] for p in obs]);dist=np.linalg.norm(xy[:,None]-oxy[None,:],axis=2)
    allow=np.array([p['allowance_px'] for p in obs]);cost=dist/allow
    # Dummy unmatched columns prevent a remote observation forcing assignment.
    rows,cols=linear_sum_assignment(np.column_stack([np.where(cost<=1,cost,100),np.ones((len(nodes),len(nodes)))*1.05]))
    assignment={int(i):int(j) for i,j in zip(rows,cols) if j<len(obs) and cost[i,j]<=1}
    for i,node in enumerate(nodes):
        node['band_clearance_px']=float(sample(data['clearance'],np.array(node['xy_local'])[None])[0])
        node['region_priority']='interior' if node['band_clearance_px']>=18 else 'edge'
        node['alternatives']=[dict(observation=obs[j]['id'],distance_px=float(dist[i,j])) for j in np.argsort(dist[i]) if dist[i,j]<=allow[j]]
        shifts=[]
        for variant in controls:
            # Coordinate-free nearest crossing is a stability diagnostic only; not a relabeling.
            if variant:shifts.append(float(min(np.linalg.norm(np.array(p['xy'])-xy[i]) for p in variant)))
            else:shifts.append(None)
        node['bandwidth_crossing_shifts_px']=shifts
        stable=all(d is not None and d<=6 for d in shifts)
        node['observation']=obs[assignment[i]]['id'] if i in assignment else None
        node['color']=obs[assignment[i]]['color'] if i in assignment else None
        node['status']='unsupported geometric crossing'
        node['reasons']=[]
        if i in assignment:
            j=assignment[i];others=np.delete(dist[:,j],i)
            row_others=[dist[i,k] for k in range(len(obs)) if k!=j and dist[i,k]<=allow[k]]
            margin=min(float(others.min()-dist[i,j]) if len(others) else 999,
                       min(row_others)-dist[i,j] if row_others else 999)
            node['assignment_margin_px']=margin
            node['observation_distance_px']=float(dist[i,j])
            if margin<3:
                node['status']='ambiguous or unresolved';node['reasons'].append('competing observation or crossing')
            elif stable and node['region_priority']=='interior':node['status']='confident bead'
            elif stable:node['status']='probable bead';node['reasons'].append('edge visibility')
            else:node['status']='ambiguous or unresolved';node['reasons'].append('bandwidth changes crossing by more than 6px')
        else:node['reasons'].append('no uniquely assigned photographic observation; not confirmed absence')
    return nodes

def graph(nodes,tracks):
    supported=[p for p in nodes if p['status'] in ('confident bead','probable bead')]
    origin=min(supported or nodes,key=lambda p:np.linalg.norm(np.array(p['xy'])-np.median([n['xy'] for n in nodes],axis=0)))
    base=np.array(origin['ab']);edges=[];conflicts=[];lookup={}
    for p in nodes:
        a,b=np.array(p['ab'])-base;p['relative_ab']=[int(a),int(b)]
        p['conditional_indices']={'A':int(7*a+6*b),'B':int(6*a+7*b),'reverse_A':int(-7*a-6*b),'reverse_B':int(-6*a-7*b)}
        p['index_status']='conditional on band topology' if p in supported else 'unresolved hypothesis only'
        lookup.setdefault(tuple(p['ab']),[]).append(p)
    for ab,group in lookup.items():
        if len(group)>1:conflicts.append(dict(kind='multiple crossings at same chart coordinates',ab=list(ab),nodes=[p['id'] for p in group],xy=[p['xy'] for p in group]))
    for p in supported:
        a,b=p['ab']
        for family,delta in [('F0',(1,0)),('F1',(0,1)),('difference',(1,-1))]:
            for q in lookup.get((a+delta[0],b+delta[1]),[]):
                if q not in supported:continue
                continuous=(p['track_ids'][int(family[-1])]==q['track_ids'][int(family[-1])]) if family!='difference' else True
                # An implied third link additionally needs one shared supported triangle witness.
                witnesses=[]
                if family=='difference':
                    for mid_ab in ((a+1,b),(a,b-1)):
                        witnesses += [r['id'] for r in lookup.get(mid_ab,[]) if r in supported]
                    continuous=bool(witnesses)
                status='accepted conditional' if continuous else 'unresolved track break'
                edges.append(dict(source=p['id'],target=q['id'],family=family,delta_ab=list(delta),status=status,
                    kind='implied triangular relation' if family=='difference' else 'traced common band',
                    triangle_witnesses=witnesses,priority='interior' if p['region_priority']==q['region_priority']=='interior' else 'edge'))
    # Independent edge propagation exposes inconsistent coordinates if future links disagree.
    accepted=[e for e in edges if e['status']=='accepted conditional'];adj={p['id']:[] for p in supported}
    for e in accepted:
        d=np.array(e['delta_ab']);adj[e['source']].append((e['target'],d));adj[e['target']].append((e['source'],-d))
    assigned={};components=[]
    for start in adj:
        if start in assigned:continue
        assigned[start]=np.zeros(2,int);todo=[start];component=[]
        while todo:
            p=todo.pop();component.append(p)
            for q,delta in adj[p]:
                value=assigned[p]+delta
                if q in assigned:
                    if not np.array_equal(assigned[q],value):conflicts.append(dict(kind='cycle conflict',source=p,target=q,residual=(value-assigned[q]).tolist()))
                else:assigned[q]=value;todo.append(q)
        components.append(component)
    identifications=[]
    for name in ('A','B'):
        byindex={}
        for p in supported:byindex.setdefault(p['conditional_indices'][name],[]).append(p)
        for k,group in byindex.items():
            if len(group)>1:identifications.append(dict(interpretation=name,index=k,nodes=[p['id'] for p in group],
                status='possible wrapping identification or wrong topology; same integer alone proves neither duplicate nor collision'))
    return dict(origin=dict(id=origin['id'],xy=origin['xy'],ab=origin['ab']),edges=edges,components=components,
        cycle_rank=len(accepted)-len(supported)+len(components),conflicts=conflicts,weighted_index_identifications=identifications,
        warning='Cycles close partly by construction. This is algebraic consistency, not independent photographic validation.',
        coordinate_convention='a advances along F0; b advances along F1. F0 line label is b; F1 line label is a. A: u=b,v=a; B: u=a,v=b.')

def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);times={};t=time.perf_counter()
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    data=preprocess(image);times['image_preprocessing']=time.perf_counter()-t;t=time.perf_counter()
    ks,direction_record=directions(data);times['local_direction_analysis']=time.perf_counter()-t;t=time.perf_counter()
    phases,amps,masks,tracks=phases_and_tracks(data,ks,CONFIG['demodulation_sigma'])
    variants=[phases_and_tracks(data,ks,s) for s in CONFIG['controls']]
    times['diagonal_tracing_including_bandwidth_controls']=time.perf_counter()-t;t=time.perf_counter()
    nodes=crossings(phases,tracks);control_nodes=[crossings(v[0],v[3]) for v in variants]
    obs,pixels=observations(data);associate_crossings(nodes,obs,data,control_nodes)
    times['intersection_identification_and_photographic_support']=time.perf_counter()-t;t=time.perf_counter()
    g=graph(nodes,tracks);times['graph_consistency']=time.perf_counter()-t
    times.update(pattern_search=None,frozen_3d_comparison=None)
    document=dict(schema='r322-image-only-lattice-v1',created_utc=datetime.now(timezone.utc).isoformat(),configuration=CONFIG,
        image_sha256=sha(ROOT/'beads-photo-2.jpg'),source_sha256=sha(__file__),directions=direction_record,tracks=tracks,
        intersections=nodes,observations=obs,graph=g,timings_seconds=times,
        controls=[dict(sigma=s,crossings=c,tracks=v[3]) for s,c,v in zip(CONFIG['controls'],control_nodes,variants)],
        provenance='Band tracing: original RGB and fixed crop only. Crossing evidence: image-only R275 bright supports/colors. No R161 points/links, historical station groups or 3D inputs.')
    save(output/'graph.json',document);save(output/'observation-pixels.json',pixels)
    np.savez_compressed(output/'fields.npz',rgb=(data['rgb']*255).astype(np.uint8),foreground=data['fg'],clearance=data['clearance'],
        phases=phases,amplitudes=amps,valid_masks=masks)
    print(json.dumps(dict(tracks=[sum(t['family']==f for t in tracks) for f in (0,1)],crossings=len(nodes),
        status={s:sum(p['status']==s for p in nodes) for s in sorted({p['status'] for p in nodes})},observations=len(obs),
        links=len(g['edges']),cycle_rank=g['cycle_rank'],timings=times),indent=2))
    return document

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/r322/results');args=ap.parse_args();run(args.output)
