"""Weighted closed-loop pattern hypotheses. Never modifies upstream inventories."""
from copy import deepcopy
import math
import numpy as np
from .common import OUT,read,save,sha,COLORS,validate


def periods(n, exclude_multiple13=True):
    return [p for p in range(1,n//4+1) if n%p==0 and (not exclude_multiple13 or p%13!=0)]


def votes(records,n,strict=False,leave_fold=None):
    result=[]
    for r in records:
        if r['color'] not in COLORS or not r['visibility']:continue
        if strict and (r['phase1_reliability']<.9 or r['color_reliability']<.75 or r['phase2_identity_reliability']<.5):continue
        k=r['physical_model_index'];fold=(k*5//n)%5
        if leave_fold is not None and fold==leave_fold:continue
        weight=float(r['visibility']*r['color_reliability']*r['phase2_identity_reliability'])
        if weight<=0:continue
        result.append((k,COLORS.index(r['color']),weight))
    return result


def consensus(observations,period):
    matrix=np.zeros((period,3));count=np.zeros(period,int)
    for k,c,w in observations:matrix[k%period,c]+=w;count[k%period]+=1
    mass=matrix.sum(1);dominance=matrix.max(1)/np.maximum(mass,1e-12)
    sequence=[COLORS[int(matrix[j].argmax())] if mass[j]>=.5 and dominance[j]>=.75 and count[j]>=2 else 'unknown' for j in range(period)]
    conflict=float(np.sum(mass-matrix.max(1)));total=float(mass.sum())
    return dict(period=period,sequence=sequence,weights=matrix.tolist(),slot_weight=mass.tolist(),
                slot_observations=count.tolist(),slot_confidence=dominance.tolist(),
                unknown_slots=sequence.count('unknown'),conflict_weight=conflict,total_weight=total,
                disagreement=conflict/total if total else None)


def search(records,n,strict=False):
    obs=votes(records,n,strict);result=[]
    for period in periods(n):
        c=consensus(obs,period);loss=total=0.;tested=unknown=0
        for fold in range(5):
            train=[o for o in obs if (o[0]*5//n)%5!=fold];model=consensus(train,period)
            for k,color,w in obs:
                if (k*5//n)%5!=fold:continue
                seq=model['sequence'][k%period];tested+=1;total+=w
                if seq=='unknown':loss+=w*.75;unknown+=1
                elif seq!=COLORS[color]:loss+=w
        score=loss/total+.01*period/math.sqrt(max(len(obs),1)) if total else None
        witnesses=[dict(index=k,observed=COLORS[color],slot=k%period,weight=w)
                   for k,color,w in obs if c['sequence'][k%period] not in ('unknown',COLORS[color])]
        c.update(repeats=n//period,complete_repeat_rule=(n%period==0 and n//period>=4),
                 maker_period_not_multiple13=period%13!=0,validation_score=score,
                 heldout_queries=tested,heldout_unknown=unknown,
                 conflict_witnesses=witnesses,strict_evidence=strict,observations=len(obs))
        c['accepted']=bool(c['unknown_slots']==0 and (c['disagreement'] or 0)<=.02 and total>10 and score is not None and score<.1)
        c['rejection_reasons']=[] if c['accepted'] else ['unknown slots, color conflicts or insufficient held-out predictive support']
        result.append(c)
    return sorted(result,key=lambda c:(c['validation_score'] is None,c['validation_score'] or 0,c['period']))


def main():
    p2=read(OUT/'phase2.json');models=[];hashes={OUT/'phase1.json.gz':sha(OUT/'phase1.json.gz'),OUT/'phase2.json':sha(OUT/'phase2.json')}
    for name in p2['selected_ids']:
        path=OUT/(name+'-inventory.json.gz');hashes[path]=sha(path);d=read(path);n=d['model']['n']
        weighted=search(d['records'],n);strict=search(d['records'],n,True)
        best=weighted[0] if weighted else None;inferred=[]
        if best:
            for original in d['records']:
                row=deepcopy(original);slot=row['physical_model_index']%best['period']
                row['phase_origin']=list(dict.fromkeys(row['phase_origin']+['phase3']));row['phase_history'].append('phase3')
                row['pattern_color']=best['sequence'][slot];row['pattern_color_reliability']=float(best['slot_confidence'][slot]) if row['pattern_color']!='unknown' else 0.
                row['pattern_period']=best['period'];row['pattern_slot']=slot;row['pattern_accepted']=False
                row['notes'].append('Pattern-only conditional inference; measured color/support preserved. Count/hand/identity unresolved.')
                validate(row);inferred.append(row)
        save(OUT/(name+'-patterns.json'),dict(weighted=weighted,strict=strict,
            excluded=[dict(period=p,reason='not an exact divisor or fewer than four full repeats' if n%p or n//p<4 else 'maker: repeat length not divisible by13')
                      for p in range(1,n//4+1) if p not in periods(n)]))
        save(OUT/(name+'-phase3-inventory.json.gz'),dict(records=inferred,upstream_sha256=sha(path)))
        models.append(dict(id=name,n=n,hand=d['model']['hand'],leading_periods=[c['period'] for c in weighted[:5]],
                           leading_scores=[c['validation_score'] for c in weighted[:5]],
                           leading_unknown=[c['unknown_slots'] for c in weighted[:5]],
                           strict_leading=[c['period'] for c in strict[:5]],
                           accepted=False,reason='No unique validated physical inventory; pattern candidates remain conditional even if an internal score gate passes.'))
    assert all(sha(p)==digest for p,digest in hashes.items()),'Phase3 must not mutate earlier evidence'
    result=dict(models=models,unique_pattern=False,upstream_hashes={str(p.relative_to(OUT)):digest for p,digest in hashes.items()},
                rule='N divisible by L, N/L>=4; separately preserve maker statement L not divisible by13',
                confidence='Engineering weights, not calibrated probabilities; rotation/reversal origin unresolved')
    save(OUT/'phase3.json',result);print('phase3',models,flush=True);return result


if __name__=='__main__':main()
