"""Final-mask controls; all candidate assignments and the primary remain fixed."""
import time,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r325.tracker import preprocess
from photo2.r325.global_solver import solve
from photo2.r325.graph import infer_graph
from photo2.r326.runner import key
from .continue_run import graph_for
from .runner import ROOT,OUT,read,save

def main():
    start=time.perf_counter();g=read(OUT/'graph.json.gz');data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));sol=solve(g['windows']);doc=graph_for(g,g['windows'],g['observations'],data,sol);primary={key(e) for e in g['graph']['edges']};full={key(e) for e in doc['graph']['edges']};assert full==primary
    # Reuse the exact no-shape solution already computed on this same candidate
    # bank: prove every restored unary equals that original unablated score.
    old=read(ROOT/'photo2/r327/development/before-shape/graph.json.gz')
    for w,v in zip(g['windows'],old['windows']):
        assert len(w['hypotheses'])==len(v['hypotheses'])
        for h,k in zip(w['hypotheses'],v['hypotheses']):assert abs(h['score']+h['r327_shared_shape']['penalty']-k['score'])<1e-8
    no_shape=read(ROOT/'photo2/r327/development/before-shape/ablation-comparison.json');sels=no_shape['unablated_selected_window_states'];_,ng,_,_=infer_graph(g['observations'],g['windows'],sels,data,g['stations_px'],g['period_px']);ne={key(e) for e in ng['edges']};rows=[dict(mode='without_shared_shape',added_vs_same_bank_full=[list(k) for k in sorted(ne-full)],removed_vs_same_bank_full=[list(k) for k in sorted(full-ne)],reuse_proof='Every restored score equals the archived same-bank unablated score; selected witness and all assignments unchanged',compatibility=no_shape['unablated_compatibility'])]
    for w in g['windows']:
        for h in w['hypotheses']:
            ev=h['r327_evidence'];u={r['observation']:.75*r['geometry_support'] for r in ev['rows']};seq=sum(min(len(run['observations'])-3,3)*float(np.exp(np.mean(np.log([max(u.get(o,0),1e-4) for o in run['observations']])))) for run in ev['runs']);h['score']=.35*h['photo_score']+sum(u.values())+.35*seq-h['r327_shared_shape']['penalty']
    alt_sol=solve(g['windows']);alt_doc=graph_for(g,g['windows'],g['observations'],data,alt_sol);ne={key(e) for e in alt_doc['graph']['edges']};rows.append(dict(mode='without_native_response_in_direct_and_sequence_terms',added_vs_same_bank_full=[list(k) for k in sorted(ne-full)],removed_vs_same_bank_full=[list(k) for k in sorted(full-ne)],compatibility=alt_doc['compatibility']))
    save(OUT/'ablation-comparison.json',dict(epoch='final color-specific pigment mask',unablated_selected_window_states=doc['selected_window_states'],unablated_compatibility=doc['compatibility'],unablated_exactly_matches_primary=True,controls=rows,seconds=time.perf_counter()-start,source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest(),policy='Only these two rows are final-mask causal controls. Additional discovery/native-unary/sequence controls are explicitly archived under the broad-mask epoch; do not combine epochs as one causal experiment.'))
    print([(r['mode'],len(r['added_vs_same_bank_full']),len(r['removed_vs_same_bank_full'])) for r in rows],flush=True)
if __name__=='__main__':main()
