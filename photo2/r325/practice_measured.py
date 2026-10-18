"""Fresh timed 146-support same-problem practice, in isolated processes.
Global image preprocessing is included in every run. Window geometry is a cached
geographic selection; spectra and hypotheses are regenerated from original RGB.
"""
import argparse,copy,json,time,resource
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r324 import fast_tracker as old
from . import batched_fit,spectral,observations as extraction
from .candidates import augment,inspect_black_predictions,to_world,signature
from .global_solver import solve
from .graph import infer_graph
OUT=Path(__file__).parent/'results'

def main(mode):
    geometry=json.load(open('photo2/r324/results/graph.json'))['windows'][65:94];original=mode=='reference';tm={};start=time.perf_counter();image=ImageOps.exif_transpose(Image.open('beads-photo-2.jpg')).convert('RGB');data=old.preprocess(image);tm['preprocess']=time.perf_counter()-start;t=time.perf_counter()
    old.base.CROP=(0,0,*image.size);sh=old.base.sha;cached=sh(old.ROOT/'photo2/review/r275/inventory.json');old.base.sha=lambda p:cached if str(p).endswith('photo2/review/r275/inventory.json') else sh(p)
    allobs,pixels=(old.base.observations(data) if original else extraction.observations(data));old.base.sha=sh;tm['support_extraction']=time.perf_counter()-t
    ids={o for w in geometry for o in w['observation_ids']};obs=[o for o in allobs if o['id'] in ids];op={o['id']:o for o in obs};wins=[];rng=np.random.default_rng(324);grid=np.indices((200,200))[::-1].reshape(2,-1).T-99.5;specs=0.;fits=0.
    for source in geometry:
        w={k:copy.deepcopy(source[k]) for k in ['id','center','frame','guide_index','arc_px','curvature','observation_ids']};w['hypotheses']=[];wins.append(w);R=np.array(w['frame']);cen=np.array(w['center']);pts=grid@R.T+cen;t=time.perf_counter()
        patch={k:old.base.sample(data[k],pts).reshape(200,200) for k in ['z','fg']};patch['fg']=patch['fg']>.5;patch['weight']=ndi.gaussian_filter(patch['fg'].astype(float),5)*np.hanning(200)[None,:]
        try:_,sp=(old.base.directions(patch) if original else spectral.directions(patch))
        except ValueError:specs+=time.perf_counter()-t;continue
        specs+=time.perf_counter()-t;t=time.perf_counter();bases=[]
        for tri in sp['triangles']:
            B=np.linalg.inv(np.array([sp['peaks'][k]['frequency_xy'] for k in tri['peaks'][:2]]))[:,::-1]
            if any(np.linalg.norm(B-b)<4 for b in bases):continue
            bases.append(B)
            if len(bases)>=10:break
        ii=w['observation_ids'];xy=(np.array([op[o]['xy'] for o in ii])-cen)@R;sig=np.array([8 if op[o]['color']=='black' else 5 for o in ii]);wt=np.array([1 if op[o]['band_clearance_px']>=18 else .55 for o in ii]);hs=[]
        for B in bases:hs+=(old.joint.fit_hypotheses(xy,sig,wt,B,ii,rng)[0] if original else batched_fit.fit_hypotheses(xy,sig,wt,B,ii,rng)[0])
        unique={}
        for h in sorted(hs,key=lambda h:-h['score']):
            s=signature(h)
            if s not in unique:unique[s]=to_world(h,w)
        w.update(hypotheses=list(unique.values())[:6],competing_bases_local=[b.tolist() for b in bases]);fits+=time.perf_counter()-t
    tm.update(spectral=specs,candidates=fits);t=time.perf_counter()
    if mode=='global':
        predictions,stats=augment(wins,obs,data);black=inspect_black_predictions(predictions,obs,data);tm['colored_bidirectional_and_black']=time.perf_counter()-t;t=time.perf_counter();sol=solve(wins,cyclic=False);tm['selection']=time.perf_counter()-t;t=time.perf_counter()
        gg=json.load(open(OUT/'graph.json'));ns,gr,tr,sel=infer_graph(obs,wins,sol['selected'],data,gg['stations_px'],gg['period_px'])
    else:
        beam=old.joint.joint_select(wins);chart=0
        selected=[sorted({b['choices'][i] for b in beam if b['score']>=beam[0]['score']-3 and b['choices'][i] is not None}) for i in range(len(wins))]
        for i,w in enumerate(wins):
            checks=[old.joint.overlap(wins[i-1]['hypotheses'][a],w['hypotheses'][b]) for a in selected[i-1] for b in selected[i]] if i else []
            if i and not(checks and all(c['common']>=4 and c['disagree']==0 for c in checks)):chart+=1
            w['chart']=chart
        centers=np.array([w['center'] for w in wins]);owners={o['id']:wins[np.argmin(np.linalg.norm(centers-o['xy'],axis=1))]['chart'] for o in obs};tm['selection']=time.perf_counter()-t;t=time.perf_counter();ns,gr,tr,sel=old.infer_graph(obs,wins,beam,data,owners)
    tm['graph']=time.perf_counter()-t
    science=dict(observations=[o['id'] for o in obs],edges=sorted((e['source'],e['target'],e['family']) for e in gr['edges']),unresolved=sorted((e['source'],e['target'],e['family']) for e in gr['unresolved_edges']),coords={n['id']:n['relative_ab'] for n in ns})
    before=time.perf_counter();old.save(OUT/f'practice-{mode}-science.json',science);tm['serialization']=time.perf_counter()-before
    report=dict(mode=mode,observations=len(obs),indexed=sum(n['component'] is not None for n in ns),edges=len(gr['edges']),unresolved=len(gr['unresolved_edges']),components=len(gr['components']),conflicts=len(gr['conflicts']),stages=tm,total_seconds=time.perf_counter()-start,peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    old.save(OUT/f'practice-{mode}-performance.json',report);print(report)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['reference','optimized_reference','global']);main(ap.parse_args().mode)
