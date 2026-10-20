"""Bounded fixed-model evaluations. Targets are recorded labels, not physical truth."""
from common import *
from photo2.r337.common import motif, predict

# Predeclared comparisons, not a period scan. All use the same current observations.
MODELS = [('frequency','A',1,None), ('phase13','A',13,None), ('A104','A',104,None),
          ('A208','A',208,None), ('A208_hier104','A',208,104), ('A338','A',338,None),
          ('B207','B',207,None), ('B299','B',299,None), ('A306_alias','A',306,None)]


def entries_for(obs, co, ids, blocks):
    ids = sorted(ids)
    keys = np.array([index(co[o]) % 208 for o in ids])
    colors = np.array([COLORS.index(obs[o]['color']) for o in ids])
    entries = motif(keys, colors, np.array([blocks[o] for o in ids]), ids, 208)
    sequence = ''.join(LETTERS[e['color']] if e['status'] == 'strong' else '?' for e in entries)
    return dict(n=len(ids), supported=sum(e['status']=='strong' for e in entries), conflicting=sum(e['status']=='conflict' for e in entries),
                insufficient=sum(e['status'] in ['observed','unknown'] for e in entries), strict_sequence=sequence, entries=entries)


def summarize(rows):
    result = dict(n=len(rows), agree=sum(r['agrees'] for r in rows), disagree=sum(not r['agrees'] for r in rows))
    result['accuracy'] = result['agree']/len(rows) if rows else None
    for field in ['color','region','occurrence','authority']:
        result['by_'+field] = {str(v):dict(n=sum(r[field]==v for r in rows), agree=sum(r['agrees'] and r[field]==v for r in rows),
                                        disagree=sum(not r['agrees'] and r[field]==v for r in rows)) for v in sorted({r[field] for r in rows})}
    return result


def cv(obs, co, ids, blocks, ledger, model, holdout):
    name, hand, period, parent = model
    ids = sorted(ids)
    k = np.array([index(co[o], hand) for o in ids])
    a = np.array([index(co[o]) for o in ids])
    c = np.array([COLORS.index(obs[o]['color']) for o in ids])
    b = np.array([blocks[o] for o in ids])
    # Occurrence folds ALWAYS use the same leading-A partition for fair comparison.
    occ = a//208 if holdout == 'occurrence' else None
    _, probs, base = predict(k%period, c, b, parent=k%parent if parent else None, occ=occ)
    if name == 'frequency':
        probs = base.copy()  # Exact training-only smoothed color-frequency baseline.
    rows = []
    for i,o in enumerate(ids):
        prediction = COLORS[int(probs[i].argmax())]
        train = ~np.isin(b,[(b[i]-1)%12,b[i],(b[i]+1)%12]) if occ is None else occ!=occ[i]
        same_key = train & (k%period == k[i]%period)
        rows.append(dict(id=o, color=obs[o]['color'], prediction=prediction, agrees=prediction==obs[o]['color'],
                         probabilities=probs[i].tolist(), frequency_probabilities=base[i].tolist(), region=blocks[o], occurrence=int(a[i]//208),
                         position=int(a[i]%208), authority=authority(o,ledger), training_same_key_records=int(same_key.sum())))
    report = summarize(rows)
    report['same_key_support'] = {kind: summarize([r for r in rows if (r['training_same_key_records']>0)==supported])
                                  for kind,supported in [('present',True),('absent',False)]}
    report.update(log_loss=float(-np.log(probs[np.arange(len(ids)),c]).mean()), gain_nats=float(np.log(probs[np.arange(len(ids)),c]/base[np.arange(len(ids)),c]).mean()),
                  model=name, holdout=holdout, probability_order=COLORS,
                  fold_rule='Withhold geographic block AND its two adjacent blocks from training' if holdout=='geographic' else 'Withhold all observations in one leading-A 208-position occurrence')
    return report, rows


def main():
    g, obs, co = load_graph(OUT/'graph.json.gz')
    _, before, _ = load_graph(ROOT/'photo2/r343/graph.json.gz')
    _, historical, hc = load_graph(ROOT/'photo2/r336/results/graph.json.gz')
    ledger = read(OUT/'corrections.json')['authoritative_labels']
    prior_ledger = read(ROOT/'photo2/r343/maker-decisions.json')['authoritative_labels']
    blocks = frozen_inputs()
    core = set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids'])
    cohorts = {}
    layers = [('R336_original1039',historical,hc), ('R343_historical1039',before,hc), ('R344_historical1039',obs,hc),
              ('R343_current1041',before,co), ('R344_current1041',obs,co), ('R343_frozen710',before,{o:co[o] for o in core}), ('R344_frozen710',obs,{o:co[o] for o in core})]
    for name,oo,coords in layers:
        cohorts[name] = entries_for(oo,coords,coords,blocks)
    p = cohorts['R344_current1041']
    assert cohorts['R343_current1041']['strict_sequence'] == read(ROOT/'photo2/r343/pattern208.json')['strict_sequence']
    prior = np.array([sum(obs[o]['color']==c for o in co)+1 for c in COLORS],float)
    prior /= prior.sum()
    entries = []
    for e in p['entries']:
        ct = np.array([e['counts'].get(c,0) for c in COLORS])
        chosen = COLORS[int(ct.argmax())]
        prob = (ct+3*prior)/(ct.sum()+3)
        evidence = [dict(id=o,color=obs[o]['color'],xy=obs[o]['xy'],ab=co[o],index_A=index(co[o]),occurrence=index(co[o])//208,
                         region=blocks[o],authority=authority(o,ledger),authority_source=ledger.get(o,{}).get('source',obs[o].get('source','historical native label')),
                         original_record_source='photo2/r343/graph.json.gz; R344 corrections overlay if listed') for o in e['ids']]
        confidence = ('Strict empirical support; conditional indexing' if e['status']=='strong' else
                      'Contested: plurality prediction only; contrary photographic records retained' if e['status']=='conflict' else
                      'Limited: unanimous recorded color, geographic support below strict requirement')
        entries.append(dict(**e, strict_color=e['color'] if e['status']=='strong' else '?', provisional_color=chosen,
                            tentative=e['status']!='strong', confidence=confidence, smoothing_probability=dict(zip(COLORS,prob.tolist())),
                            probability_warning='Descriptive fixed shrinkage score, not calibrated probability of physical correctness',
                            alternative_colors=[c for c in COLORS if c!=chosen],
                            explicit_pigment_records=sum(r['authority']=='explicit_individual_pigment' for r in evidence),
                            candidate_agreement={c:dict(agree=int(ct[j]),disagree=int(ct.sum()-ct[j])) for j,c in enumerate(COLORS)}, evidence=evidence))
    strict = ''.join(LETTERS[e['strict_color']] if e['strict_color']!='?' else '?' for e in entries)
    provisional = ''.join(LETTERS[e['provisional_color']] for e in entries)
    pattern = dict(length=208, mapping='A=7a+6b modulo2704', origin=g['reference'], direction='Positive A; cyclic origin and reversal are conventional, not known original string start',
                   N_conditional=2704,repeats_conditional=13,supported=p['supported'],conflicting=p['conflicting'],insufficient=p['insufficient'],
                   strict_sequence=strict, provisional_sequence=provisional, entries=entries, actual_shortest_physical_repeat_established=False)
    save(OUT/'pattern208.json',pattern)
    for kind in ['strict','provisional']:
        with (OUT/(kind+'-pattern.csv')).open('w',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['position','color','status','tentative','confidence','source_ids'])
            for e in entries:w.writerow([e['residue'],e[kind+'_color'],e['status'],e['tentative'] if kind=='provisional' else False,e['confidence'],';'.join(e['ids'])])
    (OUT/'strict-sequence.txt').write_text(strict+'\n')
    (OUT/'provisional-sequence.txt').write_text(provisional+'\n')
    # Resubstitution is explicitly separate from held-out prediction.
    training = {}
    for name,ids in [('current1041',co),('historical1039',hc)]:
        rows=[];strictrows=[];abstained=[]
        for o in sorted(ids):
            k=index(co[o]);e=entries[k%208]
            r=dict(id=o,color=obs[o]['color'],prediction=e['provisional_color'],agrees=obs[o]['color']==e['provisional_color'],
                   xy=obs[o]['xy'],ab=co[o],index_A=k,position=k%208,occurrence=k//208,region=blocks[o],authority=authority(o,ledger))
            rows.append(r)
            if e['status']=='strong':strictrows.append(r)
            else:abstained.append(o)
        training[name]=dict(provisional=summarize(rows),strict=dict(**summarize(strictrows),abstentions=len(abstained),abstained_ids=abstained),mismatches=[r for r in rows if not r['agrees']])
    save(OUT/'training-agreement.json',training)
    evaluations={};predictions={}
    for model in MODELS:
        for hold in ['geographic','occurrence']:
            report,rows=cv(obs,co,co,blocks,ledger,model,hold)
            key=model[0]+'_'+hold;evaluations[key]=report;predictions[key]=rows
    comparisons={}
    for name,oo,coords in layers[:5]:
        ll=ledger if name.startswith('R344') else prior_ledger
        comparisons[name]={}
        for hold in ['geographic','occurrence']:
            report,rows=cv(oo,coords,coords,blocks,ll,MODELS[3],hold)
            unchanged=[r for r in rows if r['id'] not in CORRECTIONS]
            comparisons[name][hold]=dict(all_targets=report,unchanged_color_targets=summarize(unchanged))
    # The same fitted provisional completion scored on the entire unchanged historical set, with its actual old labels.
    old_label_rows=[]
    for o in sorted(hc):
        k=index(hc[o]);pred=entries[k%208]['provisional_color'];old_label_rows.append(dict(id=o,color=historical[o]['color'],prediction=pred,agrees=historical[o]['color']==pred,region=blocks[o],occurrence=k//208,authority=authority(o,prior_ledger)))
    comparisons['frozen_R336_labels_vs_current_provisional']=summarize(old_label_rows)
    # Conditional mathematical minimality: each proper divisor of208 is contradicted by two STRICT entries.
    divisors=[]
    for d in [1,2,4,8,13,16,26,52,104]:
        pairs=[(i,j) for i in range(208) for j in range(i+1,208) if i%d==j%d and strict[i]!='?' and strict[j]!='?' and strict[i]!=strict[j]]
        i,j=pairs[0];divisors.append(dict(period=d,strict_contradictory_pairs=len(pairs),witness_positions=[i,j],colors=[strict[i],strict[j]],source_ids=[entries[i]['ids'],entries[j]['ids']]))
    closure=[dict(model=m[0],hand=m[1],period=m[2],conditional_total=2704 if m[1]=='A' else 2691,divides_own_total=(2704 if m[1]=='A' else 2691)%m[2]==0) for m in MODELS]
    save(OUT/'evaluation.json',dict(inventory=dict(active_records=len(obs),indexed=len(co),unindexed=len(obs)-len(co),indexed_colors=dict(Counter(obs[o]['color'] for o in co)),active_colors=dict(Counter(r['color'] for r in obs.values())),
                                                       observed_positions=sum(bool(e['ids']) for e in entries),conditional_string_positions=2704,without_indexed_observation=2704-len(co)),
                                  strict_cohorts=cohorts,heldout=evaluations,cohort_comparisons=comparisons,proper_divisor_obstructions=divisors,model_closure=closure,
                                  evaluation_scope='Computational reuse of one photograph and previously selected 208 hypothesis; no independent physical validation. No label or geometry decisions use these predictions.',
                                  geographic_blocks=blocks,authority_analysis='Source-statement strata only; explicit pigments distinguished from displayed-label approvals. No broad authority metadata rewriting.',
                                  statistical_rules=dict(flat_concentration=3,frequency_pseudocount_per_color=1,hierarchy_parent_concentration=3,hierarchy_child_concentration=1,guard_blocks=1,tie_order=COLORS)))
    save(OUT/'heldout-predictions.json.gz',predictions)
    print('STRICT',[(name,v['supported'],v['conflicting'],v['insufficient']) for name,v in cohorts.items()])
    print('TRAIN',[(n,r['provisional']['agree'],r['provisional']['n'],r['strict']['n']) for n,r in training.items()])
    print('HELDOUT',[(k,v['agree'],v['n'],round(v['gain_nats'],4)) for k,v in evaluations.items()])


if __name__ == '__main__':
    main()
