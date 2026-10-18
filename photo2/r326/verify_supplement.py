"""Independent arithmetic for context fits, counterfactual paths and native crops."""
import json,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r323.tracker import save
from photo2.r325.verify import path_objective
from .verify import verify_equations
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def read(p):return json.load(open(p))
def main():
    start=time.perf_counter();g=read(OUT/'full/graph.json');op={o['id']:o for o in g['observations']};contexts=read(OUT/'full/contexts.json');count=0;fits=0
    for c in contexts:
        R=np.array(c['frame']);cen=np.array(c['center'])
        for h in c['hypotheses']:
            cells={tuple(a['ab']) for a in h['assignments'].values()};assert len(cells)==len(h['assignments']);score=0;tri=0
            for oid,a in h['assignments'].items():
                pred=np.array(h['basis'])@a['ab']+h['offset'];local=(np.array(op[oid]['xy'])-cen)@R;err=float(np.linalg.norm(pred-local));assert np.max(abs(pred-a['predicted_xy']))<1e-8;assert abs(err-a['residual_px'])<1e-8;sig=8 if op[oid]['color']=='black' else 5;assert err<2*sig+1e-8;wt=1 if op[oid]['band_clearance_px']>=18 else .55;score+=wt*(1-.25*(err/sig)**2);aa,bb=a['ab'];tri+=int((aa+1,bb) in cells and (aa,bb+1) in cells);count+=1
            assert tri==h['triangles'];assert abs(score+.18*tri-h['score'])<1e-8;fits+=1
    alt=read(OUT/'alternatives.json');checks=[]
    for w in alt['witnesses']:
        assert abs(path_objective(g['windows'],w['choices'])-w['cyclic_objective'])<1e-8;assert w['cyclic_gap']<=3+1e-8
        p=w['request'];assert w['selected_window_states'][p['window']]==[p['hypothesis']]
        eq=verify_equations(dict(g,selected_window_states=w['selected_window_states']));checks.append(eq)
        for a,b,da,db in w['edges']:
            witness=0
            for wi,ss in enumerate(w['selected_window_states']):
                if not ss:continue
                aa=g['windows'][wi]['hypotheses'][ss[0]]['assignments']
                if a in aa and b in aa:assert (np.array(aa[b]['ab'])-aa[a]['ab']).tolist()==[da,db];witness+=1
            assert witness>=2
    original=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    for r in read(OUT/'native-crop-verification.json'):
        x0,y0,x1,y1=r['crop_box'];assert np.array_equal(np.array(Image.open(OUT/r['file'])),original[y0:y1,x0:x1])
    # Exact fixed model constraints remain unchanged after alternative metadata.
    model=read(OUT/'model-input.json');initial=read(OUT/'full/model-input.json')
    for k in initial:
        if k!='alternative_assignments':assert model[k]==initial[k],k
    closure=read(OUT/'closure-investigation.json');closure['compatible_whole_hypothesis_proposals']=dict(primary=g['compatibility']['cycle_audit']['possible_holonomies'],iterations=[dict(iteration=h['iteration'],holonomies=h['compatibility']['cycle_audit']['possible_holonomies']) for h in g['iterations']],counterfactuals=[dict(request=w['request'],holonomies=w['compatibility']['cycle_audit']['possible_holonomies']) for w in alt['witnesses']],warning='Whole-hypothesis proposals have unstable conditional winding. The accepted two-window link graph has no winding cycle. All four old gap links are now accepted conditionally but remain context-contested and excluded from strict model constraints; other gaps prevent closure.')
    save(OUT/'closure-investigation.json',closure)
    save(OUT/'supplement-verification.json',dict(passed=True,contexts=len(contexts),context_hypotheses=fits,context_assignments=count,compatible_alternative_paths=len(checks),alternative_equations=checks,native_crops=4,strict_model_constraints_unchanged=True,seconds=time.perf_counter()-start))
    print('PASS',len(contexts),fits,count,len(checks))
if __name__=='__main__':main()
