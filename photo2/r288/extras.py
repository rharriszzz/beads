"""Post-confirmation review targeting only; no inference inputs or retuning."""
from .review import panel
from .common import *
def main():
    native,_,_=photo();curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);cases=read(OUT/'confirmation.json.gz')['cases'];rows=[]
    for name,case,identifier,reason in [('Q01-merge','Q01','C-1007-2241','Independent high-source red merger reduction, visible in full atlas.'),('Q01-weak','Q01','D40-K-0971-2274','Preserved selector failure on old rejected tinted dark/reflection cue.'),('Q09-weak','Q09','R282-2256-2004','Tiny red interpretation on a dark-bead reflection remains dubious.')]:
        q=next(q for q in cases if q['name']==case);o=next(o for o in q['observations'] if o['id']==identifier);panel(o,name,native,curve);rows.append(dict(name=name,id=o['id'],origin=o['origin'],reason=reason))
    save(OUT/'additional-review-manifest.json',rows)
if __name__=='__main__':main()
