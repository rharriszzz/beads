"""Read-only independent arithmetic, replay, provenance and native-crop checks."""
import json,subprocess,time
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r329.common import ROOT,read,sha
from .pattern import dataset,COLORS,OUTER

BASE='381d27f5220f2a6adf5fbf5d6b04b49957e0b3ac'

def main():
    start=time.perf_counter();root=ROOT/'photo2/r330';receipt={}
    for name,value in read(root/'results/input-seal.json')['sources'].items():assert sha(ROOT/name)==value,name
    # Tracked science at the starting commit must remain byte-for-byte intact.
    changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines()
    assert all(n.startswith('photo2/r330/') or n in ['photo2/R330_REPORT.md','photo2/R330_SPECIFICATION.md','photo2/R330_REPRODUCE.md'] for n in changed),changed
    receipt['historical_tracked_files_unchanged']=True;receipt['baseline_commit']=BASE
    g,states,ids,obs,station,blocks,c,w=dataset();index={o:i for i,o in enumerate(ids)}
    def co(state):
        result={}
        for r in state['coords']:
            a=tuple(r['ab'][d]-r['turn']*state['H'][d] for d in range(2))
            if r['observation'] in result:assert result[r['observation']]==a
            result[r['observation']]=a
        origin=result['C-1302-0316'];return {o:tuple(a[d]-origin[d] for d in range(2)) for o,a in result.items()}
    patterns=read(root/'results/patterns.json.gz');gaugechecks=dpchecks=0
    for cand in patterns['candidates']:
        name,fam=cand['map'].rsplit('-',1);coord=co(states[name]);wt=[7,6] if fam=='A' else [6,7];p=cand['period'];N=sum(a*b for a,b in zip(states[name]['H'],wt));assert N==cand['N'];assert cand['exact_cyclic_compatible']==(N%p==0)
        rows=cand['rows'];train=[r for r in rows if r['section'] not in OUTER];tot=np.ones(3);counts=np.zeros((p,3));votes=defaultdict(list)
        for r in train:
            j=COLORS.index(r['color']);tot[j]+=r['weight'];counts[r['index']%p,j]+=r['weight'];votes[r['index']%p].append(r)
        base=tot/tot.sum();theta=(counts+3*base)/(counts.sum(1)[:,None]+3)
        for r in rows:
            assert r['index']==sum(a*b for a,b in zip(coord[r['id']],wt));assert r['color']==obs[r['id']]['color'];assert r['xy']==obs[r['id']]['xy'];assert r['held_out']==(r['section'] in OUTER);assert abs(r['probability']-theta[r['residue'],COLORS.index(r['color'])])<1e-12
        held=[r for r in rows if r['held_out']];gain=sum(r['weight']*np.log(r['probability']/base[COLORS.index(r['color'])]) for r in held)/sum(r['weight'] for r in held);assert abs(gain-cand['outer_gain_nats'])<1e-12
        for e in cand['entries']:
            rr=votes[e['residue']];win=int(counts[e['residue']].argmax());support=[r for r in rr if r['color']==COLORS[win]];groups=set(r['section'] for r in support);fraction=counts[e['residue'],win]/max(counts[e['residue']].sum(),1e-9);known=len(groups)>=3 and fraction>=.8 and theta[e['residue'],win]>=.6;assert e['color']==(COLORS[win] if known else '?');assert e['supporting_observations']==len(support)
        # Origin and sequence direction change the motif labels, not predictions.
        for direction in [-1,1]:
            for origin in [0,37,N]:
                transformed=np.zeros_like(theta)
                for residue in range(p):transformed[(direction*residue+origin)%p]=theta[residue]
                for r in rows:assert np.array_equal(theta[r['index']%p],transformed[(direction*r['index']+origin)%p])
                gaugechecks+=len(rows)
        # Independently coded sparse-state DP; no calls to the solver under test.
        kk=np.array([r['index'] for r in rows]);cc=np.array([COLORS.index(r['color']) for r in rows]);ww=np.array([r['weight'] for r in rows]);ss=np.array([station[index[r['id']]] for r in rows]);bins=np.minimum((ss/ss.max()*95).astype(int),95);fit=np.array([not r['held_out'] for r in rows])
        for alignment in cand['alignments']:
            penalty=alignment['penalty'];offsets=range(-21,22);cost={d:(0. if d==0 else penalty) for d in offsets}
            for b in range(96):
                if b:cost={d:min(cost[e]+(0 if e==d else penalty) for e in offsets if abs(d-e) in [0,1,6,7]) for d in offsets}
                use=(bins==b)&fit
                cost={d:val-float(np.sum(ww[use]*np.log(theta[(kk[use]+d)%p,cc[use]]))) for d,val in cost.items()}
            assert abs(min(cost.values())-alignment['cost'])<1e-8;dpchecks+=1
    receipt['independent_period_prediction_and_gauge_rows']=gaugechecks;receipt['independent_viterbi_optima']=dpchecks
    # Reconstruct every new path using local translated integer coordinates.
    bank=read(ROOT/'photo2/r327/results/graph.json.gz');prep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz');paths=[]
    for trial in read(root/'photography/g-replays.json.gz'):paths.extend(r['state'] for r in trial['candidates'])
    paths.extend(r['state'] for r in read(root/'checks/h-bundle-repair.json.gz')['candidates']);equations=0
    for state in paths:
        seed='C-0986-0371';turn=round((bank['windows'][0]['arc_px']-bank['stations_px'][seed])/bank['period_px']);coords={(seed,turn):(0,0)}
        for step,r in enumerate(state['path']):
            assert not r.get('skipped');wi=r['window'];patch=prep['patches'][wi][r['patch']];arc=bank['windows'][wi]['arc_px']+(bank['period_px'] if step==187 else 0);local={(o,round((arc-bank['stations_px'][o])/bank['period_px'])):tuple(ab) for o,ab in patch['assignments'].items()};common=coords.keys()&local.keys();assert len(common)>=(1 if step==0 else 2);shifts={tuple(coords[o][d]-local[o][d] for d in range(2)) for o in common};assert len(shifts)==1;shift=next(iter(shifts));assert list(shift)==r['offset'];occupied={v:o for o,v in coords.items()}
            for o,ab in local.items():
                target=tuple(ab[d]+shift[d] for d in range(2));assert target not in occupied or occupied[target]==o;coords[o]=target;occupied[target]=o;equations+=1
            for a,b,delta in patch['edges']:assert [patch['assignments'][b][d]-patch['assignments'][a][d] for d in range(2)]==list(delta);equations+=1
        assert coords=={(r['observation'],r['turn']):tuple(r['ab']) for r in state['coords']};returns=defaultdict(list)
        for (o,turn),ab in coords.items():returns[o].append((turn,ab))
        matched=[]
        for o,rr in returns.items():
            if len(rr)>1:
                rr.sort();a,b=rr[0],rr[1];assert [b[1][d]-a[1][d] for d in range(2)]==[(b[0]-a[0])*state['H'][d] for d in range(2)];matched.append(o)
        assert sorted(matched)==state['returns'];assert len(matched)==17
    receipt['new_complete_paths']=len(paths);receipt['independent_local_equations']=equations
    refine=read(root/'refinement/refinement.json.gz');assert len({r['id'] for r in refine['cross_predictions']})==900
    for r in refine['cross_predictions']:
        assert all(s['id']!=r['id'] and s['section']!=r['section'] and (s['index']-r['index'])%208==0 for s in r['support'])
    for o,color in refine['color_candidates'].items():
        r=next(r for r in refine['suspects'] if r['id']==o);a=r['photographic_color_audit'];assert obs[o]['color']=='red' and color=='black';assert r['strong'] and a['stable'] and a['min_vote']>=.55 and max(a['mean_votes'])>=.75;assert not r['strict_correction_candidate']
    receipt['color_proposals']=len(refine['color_candidates']);receipt['strict_color_proposals']=0
    # Independently recompute own-map hierarchical prediction on a fixed cohort.
    audit=read(root/'audit/mapping-followup.json.gz');gs=read(root/'photography/g-replays.json.gz')[-1]['candidates'];hs=read(root/'checks/h-bundle-repair.json.gz')['candidates'];names=sorted(co(states['working']));ii=np.array([index[o] for o in names]);auditchecks=0
    for r in audit['runs']:
        state=states[r['name']] if r['kind']=='saved' else (gs if r['kind']=='G' else hs)[int(r['name'].split('-')[1])]['state'];coords=co(state);present=np.array([o in coords for o in names]);weights=[7,6] if r['family']=='A' else [6,7];kk=np.array([sum(a*b for a,b in zip(coords[o],weights)) if o in coords else 0 for o in names]);gain=den=0.
        for block in range(12):
            counts104=np.zeros((104,3));counts208=np.zeros((208,3));freq=np.ones(3)
            for j,i in enumerate(ii):
                if blocks[i]==block or not present[j]:continue
                counts104[kk[j]%104,c[i]]+=w[i];counts208[kk[j]%208,c[i]]+=w[i];freq[c[i]]+=w[i]
            freq/=freq.sum();parent=(counts104+3*freq)/(counts104.sum(1)[:,None]+3);theta=(counts208+parent[np.arange(208)%104])/(counts208.sum(1)[:,None]+1)
            for j,i in enumerate(ii):
                if blocks[i]!=block:continue
                value=theta[kk[j]%208,c[i]] if present[j] else freq[c[i]];gain+=w[i]*np.log(value/freq[c[i]]);den+=w[i]
        assert abs(gain/den-r['own_motif_gain_nats'])<1e-11;auditchecks+=1
    receipt['independent_own_map_predictions']=auditchecks
    # Native crops are exactly the original RGB photograph, before overlays.
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');figures=read(root/'review/figures.json')
    for f in figures:assert np.array_equal(np.array(Image.open(root/'review'/f['file'])),np.array(photo.crop(f['bbox'])))
    receipt['exact_native_crops']=len(figures)
    # Independent pigment coverage lookup, including the translated raster.
    diag=read(root/'photography/photography.json.gz');m=np.load(ROOT/'photo2/r329/photographic_diagnostics/model-geometry.npz');owner=m['owner'].reshape(m['shape']);bbox=m['bbox'];step=float(m['step']);coverage=0
    for row in diag['F']['rows']:
        px=np.array(row['pixels'])
        for trial in row['trials']:
            address=row['address']+trial['address_delta'];j=int(np.flatnonzero(m['indices']==address)[0]);x=np.rint((px[:,0]-trial['dx']-bbox[0])/step).astype(int);y=np.rint((px[:,1]-trial['dy']-bbox[1])/step).astype(int);valid=(x>=0)&(y>=0)&(x<owner.shape[1])&(y<owner.shape[0]);v=int(np.count_nonzero(owner[y[valid],x[valid]]==j))/len(px);assert abs(v-trial['coverage'])<1e-12;coverage+=1
    receipt['f_material_trials']=coverage
    e=read(root/'checks/e-regression-and-extension.json.gz')['regression'];assert e['working']['status']=='same_family' and e['closest']['status']=='family_mismatch';receipt['E_regression']=True
    receipt.update(passed=True,seconds=time.perf_counter()-start,limitations='Numerical/provenance verification does not certify photographic labels, motif truth or whole-bracelet topology.')
    (root/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
