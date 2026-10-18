"""Independent arithmetic/preservation checks; no writes to historical results."""
import hashlib,time
from collections import defaultdict
import numpy as np
from PIL import Image,ImageOps
from .compatibility import relations,cycle_audit
from photo2.r326.runner import key
from .runner import ROOT,OLD,OUT,read,save

def native_response(rgb,xy,color):
    # Direct 25x25 Gaussian convolution and bilinear interpolation on original
    # integer pixels, independent of evidence.py's full-image filters/sampler.
    x,y=xy;ix,iy=int(np.floor(x)),int(np.floor(y));kernel=np.exp(-.5*(np.arange(-12,13)/3.)**2);kernel/=kernel.sum();total=0.
    for dx,dy,weight in [(0,0,(1-x+ix)*(1-y+iy)),(1,0,(x-ix)*(1-y+iy)),(0,1,(1-x+ix)*(y-iy)),(1,1,(x-ix)*(y-iy))]:
        patch=rgb[iy+dy-12:iy+dy+13,ix+dx-12:ix+dx+13].astype(float)/255
        lin=np.where(patch<=.04045,patch/12.92,((patch+.055)/1.055)**2.4);r,g,b=lin.transpose(2,0,1)
        channel=np.minimum(np.minimum(r,g),b) if color=='black' else (np.maximum(r-np.maximum(g,b),0) if color=='red' else np.maximum(np.minimum(r,g)-b,0))
        total+=weight*float(kernel@channel@kernel)
    return total

def main():
    start=time.perf_counter();g=read(OUT/'graph.json.gz');old=read(OLD/'graph.json');ws=g['windows'];op={o['id']:o for o in g['observations']};seal=read(OUT/'scientific-seal.json')
    assert hashlib.sha256((OUT/'graph.json.gz').read_bytes()).hexdigest()==seal['graph_sha256']
    for p,digest in seal.items():
        if p!='graph_sha256':assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
    preserved=0
    for w,b in zip(ws,old['windows']):
        for h,k in zip(w['hypotheses'],b['hypotheses']):
            for field in ('assignments','basis','offset','edges'):assert h[field]==k[field]
            preserved+=1
    assert hashlib.sha256((ROOT/'beads-photo-2.jpg').read_bytes()).hexdigest()==g['image_sha256']
    assert g['observations']==old['observations'];pixels=read(OLD/'observation-pixels.json');rgb=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));pixel_count=0
    for p in pixels:
        assert p['id'] in op;xy=np.array(p['pixels_xy']);assert np.all(xy>=0) and np.all(xy[:,0]<rgb.shape[1]) and np.all(xy[:,1]<rgb.shape[0]);pixel_count+=len(xy)
    choices=[s[0] if s else None for s in g['selected_window_states']];active,conflicts,links=relations(ws,choices,g['stations_px'],g['period_px']);assert not conflicts;bad,audit=cycle_audit(set(active),links);assert not bad
    edge_count=0
    for e in g['graph']['edges']:
        a,b=e['source'],e['target'];d=e['delta_ab'];support=[]
        for wi,s in enumerate(g['selected_window_states']):
            if not s:continue
            aa=ws[wi]['hypotheses'][s[0]]['assignments']
            if a in aa and b in aa and (np.array(aa[b]['ab'])-aa[a]['ab']).tolist()==d:support.append(wi)
        assert len(support)>=2 and not e['intervening_observations'] and e['foreground_fraction']>.95;edge_count+=1
    rows=0;manual=0;maxdelta=0.;runs=0
    for wi,w in enumerate(ws):
        for hi,h in enumerate(w['hypotheses']):
            ev=h['r327_evidence'];support=0.
            for ri,r in enumerate(ev['rows']):
                target=r['observation'];assert target not in r['anchor_ids'];assert all(o in h['assignments'] for o in r['anchor_ids'])
                if r['anchor_kind']=='colored supports only':assert all(op[o]['color']!='black' for o in r['anchor_ids'])
                errors=np.linalg.norm(np.array(r['predictions_xy'])-op[target]['xy'],axis=1);assert np.allclose(errors,r['errors_px'],atol=1e-9)
                geom=float(np.mean(np.exp(-.5*(errors/r['sigma_px'])**2)));pix=float(np.mean(np.clip(np.array(r['predicted_native_responses'])/max(r['observed_native_response'],1e-6),0,1)));assert abs(r['utility']-(.75*geom+.25*pix))<1e-10;support+=r['utility'];rows+=1
                if wi%11==0 and hi==0 and ri<3:
                    # Independent augmented least squares, rather than normal equations.
                    anchors=r['anchor_ids'];a0=np.array(h['assignments'][target]['ab']);ab=np.array([h['assignments'][o]['ab'] for o in anchors])-a0;scale=max(float(np.median(np.linalg.norm(ab,axis=1))),1.);u=ab/scale;X=np.column_stack([np.ones(len(u)),u]);wt=np.exp(-np.sum(u*u,axis=1)/8);y=np.array([op[o]['xy'] for o in anchors]);coef=np.linalg.lstsq(X*np.sqrt(wt[:,None]),y*np.sqrt(wt[:,None]),rcond=None)[0];assert abs(native_response(rgb,op[target]['xy'],op[target]['color'])-r['observed_native_response'])<1e-10
                    assert abs(native_response(rgb,r['predictions_xy'][0],op[target]['color'])-r['predicted_native_responses'][0])<1e-10
                    delta=float(np.linalg.norm(coef[0]-r['predictions_xy'][0]));assert delta<1e-7;maxdelta=max(maxdelta,delta);manual+=1
            assert abs(support-ev['support'])<1e-8
            for run in ev['runs']:
                aa=[np.array(h['assignments'][o]['ab']) for o in run['observations']];assert all(np.array_equal(b-a,run['step']) for a,b in zip(aa,aa[1:]));runs+=1
            assert abs(h['score']-(.35*h['photo_score']+ev['support']+.35*ev['sequence']))<1e-8
    # Each diagnostic alternative has simultaneous whole-hypothesis support.
    alts=read(OUT/'lower-bend-alternatives.json.gz')['alternatives']
    for alt in alts:
        c=[s[0] if s else None for s in alt['selected_window_states']];act,conf,ll=relations(ws,c,g['stations_px'],g['period_px']);assert not conf;bb,au=cycle_audit(set(act),ll);assert not bb
    receipt=dict(pass_all=True,old_hypotheses_preserved=preserved,observations=len(op),native_support_pixels=pixel_count,selected_overlap_equations=len(links),working_edges=edge_count,cross_prediction_rows=rows,independent_affine_predictions=manual,max_independent_prediction_delta_px=maxdelta,supported_runs=runs,compatible_alternatives=len(alts),seconds=time.perf_counter()-start,limitations='Checks arithmetic, retention and compatibility. No new independent photographic labels; no claim that model agreement certifies identity.')
    save(OUT/'verification.json',receipt);print(receipt)
if __name__=='__main__':main()
