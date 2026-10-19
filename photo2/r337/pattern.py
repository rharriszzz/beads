"""Partial208 string block, honest conflicts, occurrence prediction and primitivity."""
import argparse,csv
from .common import *

def run(out):
    out=Path(out);g,obs,co,ids,ab,c,b,core=data();N=int(np.dot(g['H'],[7,6]));k=ab@[7,6]%N;rows=motif(k%208,c,b,ids,208);strict=[];consensus=[]
    for r in rows:
        strict.append(r['color'] if r['status']=='strong' else '?');consensus.append(r['color'])
    # Explicit subset of accepted recorded evidence: no conflict is resolved by
    # plurality, and weaker/unseen positions remain unknown in the strict block.
    proper=[]
    for d in range(1,208):
        if 208%d:continue
        conflicts=[]
        for i in range(208):
            if strict[i]=='?':continue
            for j in range(i+1,208):
                if i%d==j%d and strict[j]!='?' and strict[i]!=strict[j]:conflicts.append([i,j,strict[i],strict[j]])
        proper.append(dict(divisor=d,strict_color_conflicts=conflicts))
    prediction=[]
    for i,o in enumerate(ids):
        train=~np.isin(b,[(int(b[i])-1)%12,int(b[i]),(int(b[i])+1)%12]);examples=[j for j in range(len(ids)) if train[j] and k[j]%208==k[i]%208];counts=Counter(COLORS[c[j]] for j in examples);win,n=counts.most_common(1)[0] if counts else ('?',0);sections={int(b[j]) for j in examples if COLORS[c[j]]==win};strong=n>=3 and len(sections)>=3 and n/max(len(examples),1)>=.8
        prediction.append(dict(id=o,residue=int(k[i]%208),observed=COLORS[c[i]],prediction=win if strong else '?',training_ids=[ids[j] for j in examples],agrees=bool(strong and win==COLORS[c[i]])))
    scores=[]
    for cohort,mask in [('active',np.ones(len(ids),bool)),('interior',np.array([o in core for o in ids]))]:
        for kind in ['flat','hier104']:
            sc,_,_=predict((k%208)[mask],c[mask],b[mask],parent=(k%104)[mask] if kind=='hier104' else None,occ=(k//208)[mask]);scores.append(dict(cohort=cohort,model=kind,leave_complete_occurrence_out=sc))
    save(out/'pattern208.json',dict(length=208,conditional_total=N,repeat_count=N//208,spatial_generator=[16,16],A_zero_index_kernel=[6,-7],closure_decomposition=dict(H=g['H'],spatial_copies=13,kernel_copies=1,exact=bool(np.array_equal(13*np.array([16,16])+[6,-7],g['H']))),maker_preference='The maker hopes the length is not divisible by13; multiples13 are allowed, not penalized or excluded.',strict_sequence=''.join(x[0].upper() if x!='?' else '?' for x in strict),strict_known=sum(x!='?' for x in strict),strict_unknown=[i for i,x in enumerate(strict) if x=='?'],majority_sequence=''.join(x[0].upper() if x!='?' else '?' for x in consensus),majority_known=sum(x!='?' for x in consensus),conflicted_residues=[r['residue'] for r in rows if r['status']=='conflict'],entries=rows,proper_divisors=proper,all_proper_divisors_contradicted_by_strict_subset=all(r['strict_color_conflicts'] for r in proper),geographic_predictions=prediction,occurrence_scores=scores,status='Leading closure-compatible partial pattern, not an exact complete recovered sequence. Strict known entries are supported uncontradicted observations; unknown includes conflicts and insufficient repetition. Global photographic indexing remains conditional.'))
    with (out/'pattern208.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['residue','strict','majority','status','red','yellow','black','original_ids'])
        for r,st in zip(rows,strict):w.writerow([r['residue'],st,r['color'],r['status'],r['counts'].get('red',0),r['counts'].get('yellow',0),r['counts'].get('black',0),' '.join(r['ids'])])
    print('PATTERN208 strict',sum(x!='?' for x in strict),'unknown',sum(x=='?' for x in strict),'majority',sum(x!='?' for x in consensus),'proper divisors all contradicted',all(r['strict_color_conflicts'] for r in proper))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
