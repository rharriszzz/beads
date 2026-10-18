"""Post-freeze same-bank unablated proposal control; primary is unchanged."""
import time,hashlib
from PIL import Image,ImageOps
from photo2.r325.tracker import preprocess
from photo2.r325.global_solver import solve
from photo2.r326.runner import key
from .continue_run import graph_for
from .runner import ROOT,OUT,read,save

def main():
    start=time.perf_counter();g=read(OUT/'graph.json.gz');data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));sol=solve(g['windows']);doc=graph_for(g,g['windows'],g['observations'],data,sol);primary={key(e) for e in g['graph']['edges']};full={key(e) for e in doc['graph']['edges']};rows=[]
    for a in read(OUT/'ablations.json.gz'):
        alternate=(primary-set(map(tuple,a['removed_vs_primary'])))|set(map(tuple,a['added_vs_primary']));rows.append(dict(mode=a['mode'],added_vs_same_bank_full=[list(k) for k in sorted(alternate-full)],removed_vs_same_bank_full=[list(k) for k in sorted(full-alternate)],primary_relative_differences_are_not_alone_causal=True))
    save(OUT/'ablation-comparison.json',dict(unablated_selected_window_states=doc['selected_window_states'],unablated_compatibility=doc['compatibility'],full_proposal_vs_saved_primary=dict(added=[list(k) for k in sorted(full-primary)],removed=[list(k) for k in sorted(primary-full)]),controls=rows,seconds=time.perf_counter()-start,source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest(),policy='Same candidate bank and solver, compare each ablation with a fresh unablated proposal. The saved working primary is chosen over all archived witnesses; distinguish that incumbent comparison from a causal ablation.'))
    print([(r['mode'],len(r['added_vs_same_bank_full']),len(r['removed_vs_same_bank_full'])) for r in rows],flush=True)
if __name__=='__main__':main()
