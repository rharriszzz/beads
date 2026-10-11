"""R250 dense native FFT observations and conservative axial association graph.

R249 extraction is unchanged. Fast FFT path omits its GUI displays; parity tested.
Tracks are graph components of accepted links, NOT physical direction labels.
"""
import argparse,csv,gzip,json,time,itertools,inspect,hashlib
from pathlib import Path
import numpy as np
from scipy.interpolate import splprep,splev
from photo2 import fft_explorer_core as core
from photo2.fft_spectrum_led import ROOT,read,save,sha,image_rgb,extract,wrap
from photo2.fft_transfer import qualify,verify_freeze,RULES
from photo2.fft_curvature import Curve

BUNDLE=ROOT/'photo2/review/r250'
CACHE=ROOT/'photo2/output/r250'
SIGMA=30;SIZE=301;DELTA=1/(2*np.pi*SIGMA);LOW=2*DELTA
TRACK=dict(gate=1.,margin=.25,gap_pixels=60.,frame='tangent-relative axial frequency vector',brightness_used=False)


def curve_samples(n=2000):
    pts=np.array(read(ROOT/'photo2/spline-seed-r175.json')['points'])
    tck,_=splprep(pts.T,s=len(pts)*4,per=True,k=3)
    curve=Curve(np.array(splev(np.linspace(0,1,16001),tck)).T)
    rows=[]
    for i,s in enumerate(np.arange(n)*curve.length/n):
        xy,t,_=curve.at(s);d=curve.spline(s,1);dd=curve.spline(s,2)
        # Image y points down. Positive signed curvature here uses Cartesian y up.
        curvature=-(d[0]*dd[1]-d[1]*dd[0])/np.linalg.norm(d)**3
        rows.append(dict(index=i,s=float(s),x=float(xy[0]),y=float(xy[1]),tangent_deg=float(np.degrees(np.arctan2(-t[1],t[0]))),curvature=float(curvature)))
    return curve.length,rows


class Scanner:
    def __init__(self,rgb):
        self.rgb=rgb;h=150
        self.g=core.make_mask((SIZE,SIZE),'Ellipse/circle','Gaussian',h,h,300,300,0,.2)
        yy,xx=np.mgrid[:SIZE,:SIZE];self.fx=(xx-h)/SIZE;self.fy=(h-yy)/SIZE;self.rad=np.hypot(self.fx,self.fy)
    def products(self,q):
        x,y=np.round([q['x'],q['y']]).astype(int);h=150
        if x-h<0 or y-h<0 or x+h>=self.rgb.shape[1] or y+h>=self.rgb.shape[0]:raise ValueError('Full five-sigma native crop unavailable')
        patch=self.rgb[y-h:y+h+1,x-h:x+h+1];bank=core.make_channel_bank(patch)
        arrays={}
        for ch,label in [('V','HSV V'),('Y','Y luminance')]:
            z=bank.arrays[label]
            # Exact source unpadded/unfiltered complex path, including complex64 return.
            f=np.fft.fftshift(np.fft.fft2(z.astype(np.float32)*self.g)).astype(np.complex64).astype(complex)
            arrays[ch]=dict(patch=patch,g=self.g,x=z,f=f,n=SIZE,sigma=SIGMA,fx=self.fx,fy=self.fy,rad=self.rad,origin=[int(x-h),int(y-h)])
        return arrays
    def measure(self,q):
        base=dict(**q)
        try:arrays=self.products(q)
        except ValueError as e:return [dict(base,channel=c,failure=str(e),peaks=[],trios=[]) for c in ('V','Y')]
        patch=arrays['V']['patch'];v=arrays['V']['x'];h,s,_=core.rgb_to_hsv_np(patch);g=self.g;ws=float(g.sum())
        # Descriptive appearance proxies only; never used to select or associate peaks.
        proxies=dict(red_proxy=float(np.sum(g*((h<.07)|(h>.94))*(s>.4))/ws),yellow_proxy=float(np.sum(g*(h>.10)*(h<.20)*(s>.4))/ws),dark_proxy=float(np.sum(g*(v<.2))/ws),highlight_proxy=float(np.sum(g*(v>.9)*(s<.25))/ws))
        out=[]
        for ch,a in arrays.items():
            r=extract(a,LOW,np.sqrt(.5),q['tangent_deg']);c=SIZE//2;lp=np.log(np.maximum(abs(a['f'])**2,1e-20))
            for p in r['peaks']:
                dx,dy=p['offset'];iy,ix=c-dy,c+dx;p['peak_bin_power']=float(abs(a['f'][iy,ix])**2)
                # Local quadratic log-power curvature: diagnostic broadness, not a fitted uncertainty.
                width=None
                if 0<iy<SIZE-1 and 0<ix<SIZE-1:
                    dxx=lp[iy,ix+1]+lp[iy,ix-1]-2*lp[iy,ix];dyy=lp[iy+1,ix]+lp[iy-1,ix]-2*lp[iy,ix]
                    dxy=(lp[iy+1,ix+1]-lp[iy+1,ix-1]-lp[iy-1,ix+1]+lp[iy-1,ix-1])/4
                    ev=np.linalg.eigvalsh(-np.array([[dxx,dxy],[dxy,dyy]]))
                    if ev.min()>0:width=float(np.sqrt(2/ev.min())/SIZE)
                p.update(normalized_peak_power=p['peak_bin_power']/ws**2,broad=width is None or width>2*DELTA,broad_width=width)
            r['peaks'].sort(key=lambda p:p['peak_bin_power'],reverse=True)
            strongest=r['peaks'][0]['peak_bin_power'] if r['peaks'] else 1
            for i,p in enumerate(r['peaks']):
                p.update(candidate=i+1,relative_brightness=p['peak_bin_power']/strongest,weak=p['peak_bin_power']/strongest<RULES['weak_peak_ratio'],shortlisted=i<4,physical_assignment='unassigned',observation=f"{ch}:{q['index']:04}:{i+1}")
            rec=dict(base,channel=ch,n=SIZE,**r,**proxies)
            rec['trios'],_=qualify(rec);out.append(rec)
        return out


def distance(a,b,frame='relative_angle'):
    aa=np.radians(a[frame]);bb=np.radians(b[frame]);x=a['frequency']*np.array([np.cos(aa),np.sin(aa)]);y=b['frequency']*np.array([np.cos(bb),np.sin(bb)])
    return float(min(np.linalg.norm(x-y),np.linalg.norm(x+y))/np.hypot(a['frequency_resolution'],b['frequency_resolution']))


def match_edges(left,right,gate=1.,margin=.25,frame='relative_angle'):
    """Eligible graph plus mutual-nearest links with an explicit ambiguity margin."""
    if not left or not right:return []
    costs=np.array([[distance(a,b,frame) for b in right] for a in left]);edges=[]
    for i,j in zip(*np.where(costs<=gate)):
        other_row=np.delete(costs[i,:],j);other_col=np.delete(costs[:,j],i)
        second=min(float(other_row.min()) if len(other_row) else float('inf'),float(other_col.min()) if len(other_col) else float('inf'))
        mutual=int(np.argmin(costs[i]))==j and int(np.argmin(costs[:,j]))==i
        accepted=mutual and second-costs[i,j]>=margin
        edges.append(dict(source=left[i]['observation'],target=right[j]['observation'],cost=float(costs[i,j]),margin=None if not np.isfinite(second) else float(second-costs[i,j]),accepted=bool(accepted)))
    return edges


def associate(records,length,gate=1.,margin=.25,frame='relative_angle',gaps=True):
    """Closed-loop adjacent graph; no rank/brightness term or fitted motion model.

    Ambiguous adjacency breaks identity. Gap links only between endpoints with
    NO eligible immediate continuation, not across competing adjacent identities.
    Gap links remain tentative and never merge measured track fragments.
    """
    records=sorted(records,key=lambda r:r['s']);n=len(records);obs={p['observation']:dict(p,index=r['index'],s=r['s'],curvature=r['curvature']) for r in records for p in r['peaks']};edges=[]
    for k,r in enumerate(records):
        nxt=records[(k+1)%n]
        for e in match_edges(r['peaks'],nxt['peaks'],gate,margin,frame):
            e.update(kind='adjacent',wrap=bool(k==n-1),arc_gap=float((nxt['s']-r['s'])%length));edges.append(e)
    accepted=[e for e in edges if e['accepted']];incoming={e['target']:e for e in accepted};outgoing={e['source']:e for e in accepted}
    parent={p:p for p in obs}
    def root(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for e in accepted:parent[root(e['target'])]=root(e['source'])
    groups={}
    for o in obs:groups.setdefault(root(o),[]).append(o)
    ordered=sorted(groups.values(),key=lambda g:(-len(g),min(obs[o]['s'] for o in g),min(g)))
    ch=records[0]['channel'];assignment={o:f'{ch}{i+1:04}' for i,g in enumerate(ordered) for o in g}
    eligible_out={e['source'] for e in edges};eligible_in={e['target'] for e in edges}
    # Keep all plausible reappearance proposals, flag uniqueness; no hidden interpolation.
    gap_edges=[]
    if gaps:
        ends=[p for o,p in obs.items() if o not in outgoing and o not in eligible_out]
        starts=[p for o,p in obs.items() if o not in incoming and o not in eligible_in]
        for a in ends:
            for b in starts:
                ds=(b['s']-a['s'])%length
                if 0<ds<=TRACK['gap_pixels']:
                    d=distance(a,b,frame)
                    if d<=gate:gap_edges.append(dict(source=a['observation'],target=b['observation'],cost=d,margin=None,accepted=False,kind='tentative_gap',wrap=b['s']<a['s'],arc_gap=ds))
        for e in gap_edges:
            e['unique_gap']=sum(x['source']==e['source'] for x in gap_edges)==1 and sum(x['target']==e['target'] for x in gap_edges)==1
    ambiguous={e['source'] for e in edges if e['source'] not in outgoing} | {e['target'] for e in edges if e['target'] not in incoming}
    tracks=[]
    for i,g in enumerate(ordered):
        ps=[obs[o] for o in g];links=[outgoing[o] for o in g if o in outgoing];span=sum(e['arc_gap'] for e in links)
        tracks.append(dict(track=f'{ch}{i+1:04}',observations=g,count=len(g),measured_span=span,closed=len(links)==len(g),wrap=any(e['wrap'] for e in links),rank_min=min(p['candidate'] for p in ps),rank_max=max(p['candidate'] for p in ps),weak_count=sum(p['weak'] for p in ps)))
    return dict(channel=ch,tracks=tracks,associations=edges+gap_edges,assignment=assignment,ambiguous=sorted(ambiguous),parameters=dict(gate=gate,margin=margin,frame=frame))


def write_csv(path,rows):
    rows=list(rows)
    if not rows:return
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def scan(n):
    BUNDLE.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True);cfg=verify_freeze();length,sites=curve_samples()
    manifest=dict(image=cfg['image_sha256'],seed=sha(ROOT/'photo2/spline-seed-r175.json'),r249_freeze=sha(ROOT/'photo2/review/r249/freeze.json'),scanner=hashlib.sha256(inspect.getsource(Scanner).encode()).hexdigest(),geometry=hashlib.sha256(inspect.getsource(curve_samples).encode()).hexdigest())
    fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()[:16]
    cache=CACHE/fingerprint;cache.mkdir(exist_ok=True);save(cache/'manifest.json',manifest)
    scanner=Scanner(image_rgb(ROOT/cfg['image']));t=time.perf_counter();records=[];computed=0
    for i in range(0,2000,2000//n):
        path=cache/f'{i:04}.json'
        if path.exists():rr=read(path)
        else:rr=scanner.measure(sites[i]);save(path,rr);computed+=1
        records.extend(rr)
        if (i//(2000//n))%50==0:print(n,i,'elapsed',round(time.perf_counter()-t,1),flush=True)
    dt=time.perf_counter()-t
    with gzip.open(BUNDLE/f'measurements-{n}.json.gz','wt') as f:json.dump(dict(length=length,n=n,records=records),f,separators=(',',':'),allow_nan=False)
    save(BUNDLE/f'timing-{n}.json',dict(n=n,new_locations=computed,seconds=dt,length=length,spacing=length/n,source_sha256=sha(__file__),cache_fingerprint=fingerprint))
    print('Scan complete',n,dt,flush=True)


def load_measurements(n):
    with gzip.open(BUNDLE/f'measurements-{n}.json.gz','rt') as f:return json.load(f)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('n',type=int,choices=[200,500,1000,2000]);scan(p.parse_args().n)
