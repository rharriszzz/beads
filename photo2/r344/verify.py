"""Independent overlay, closure, support and direct held-out arithmetic."""
from common import *
from PIL import Image, ImageOps
import math


def direct_predictions(obs,co,ids,blocks,model,holdout):
    """Plain counted dictionaries; no producer motif/predict/cv helpers."""
    name,hand,length,parent=model
    key={o:((7*co[o][0]+6*co[o][1])%2704 if hand=='A' else (6*co[o][0]+7*co[o][1])%2691) for o in ids}
    occ={o:((7*co[o][0]+6*co[o][1])%2704)//208 for o in ids}
    result={}
    for fold in range(12 if holdout=='geographic' else 13):
        train=[o for o in ids if (blocks[o] not in [(fold-1)%12,fold,(fold+1)%12] if holdout=='geographic' else occ[o]!=fold)]
        test=[o for o in ids if (blocks[o]==fold if holdout=='geographic' else occ[o]==fold)]
        counts=Counter(obs[o]['color'] for o in train);prior=[(counts[c]+1)/(len(train)+3) for c in COLORS]
        cells=defaultdict(Counter);parents=defaultdict(Counter)
        for o in train:
            cells[key[o]%length][obs[o]['color']]+=1
            if parent:parents[key[o]%parent][obs[o]['color']]+=1
        for o in test:
            ct=cells[key[o]%length];n=sum(ct.values())
            if name=='frequency':prob=prior
            elif parent:
                pt=parents[key[o]%parent];np_=sum(pt.values());pp=[(pt[c]+3*prior[j])/(np_+3) for j,c in enumerate(COLORS)]
                prob=[(ct[c]+pp[j])/(n+1) for j,c in enumerate(COLORS)]
            else:prob=[(ct[c]+3*prior[j])/(n+3) for j,c in enumerate(COLORS)]
            result[o]=dict(prob=prob,baseline=prior,prediction=COLORS[max(range(3),key=lambda j:prob[j])],support=n)
    return result


def check_summary(rows,saved):
    assert saved['n']==len(rows)
    assert saved['agree']==sum(r['agrees'] for r in rows)
    assert saved['disagree']==sum(not r['agrees'] for r in rows)
    for field in ['color','region','occurrence','authority']:
        for val,group in saved['by_'+field].items():
            subset=[r for r in rows if str(r[field])==val]
            assert group==dict(n=len(subset),agree=sum(r['agrees'] for r in subset),disagree=sum(not r['agrees'] for r in subset))


def main():
    seal=read(OUT/'input-seal.json');prior_seal=read(ROOT/'photo2/r343/input-seal.json')
    assert all(sha(ROOT/p)==h for p,h in {**prior_seal,**seal}.items())
    g,obs,co=load_graph(OUT/'graph.json.gz');old,oldobs,oldco=load_graph(ROOT/'photo2/r343/graph.json.gz')
    assert len(obs)==1059 and len(co)==1041 and len(g['edges'])==2290
    assert g['coordinates']==old['coordinates'] and g['edges']==old['edges'] and g['H']==old['H']==[214,201]
    assert set(obs)==set(oldobs)
    assert {o for o in obs if obs[o]['color']!=oldobs[o]['color']}==set(CORRECTIONS)
    for o in oldobs:
        for k,v in oldobs[o].items():
            if k!='color':assert obs[o][k]==v
        if o in CORRECTIONS:assert obs[o]['color']=='yellow' and obs[o]['r344_pigment_authority']['category']=='explicit_individual_pigment'
    ledger=read(OUT/'corrections.json')['authoritative_labels']
    for o,r in ledger.items():
        if o in obs:assert obs[o]['color']==r['color']
    assert all(o not in obs for o in ['NEW-1927-2829','REC266-P146299','C-1979-2669','R332-B-0105-0098','R332-B-0138-0130','E5-1499-3037'])
    seen={g['reference']};adj=defaultdict(set);allowed={(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)}
    for e in g['edges']:
        a,b=e['source'],e['target'];d=[co[b][i]-co[a][i]-e['delta_ab'][i] for i in range(2)]
        assert tuple(e['delta_ab']) in allowed and d[0]%214==0 and d[1]==201*(d[0]//214)
        adj[a].add(b);adj[b].add(a)
    todo=list(seen)
    while todo:
        o=todo.pop()
        for z in adj[o]-seen:seen.add(z);todo.append(z)
    assert seen==set(co)
    assert len({(a-(a//214)*214,b-(a//214)*201) for a,b in co.values()})==1041
    assert len({(7*a+6*b)%2704 for a,b in co.values()})==1041
    freeze=read(OUT/'freeze.json')
    assert sha(OUT/'graph.json.gz')==freeze['graph_sha256'] and sha(OUT/'corrections.json')==freeze['corrections_sha256']
    assert sha(ROOT/'photo2/r342/recognize.py')==freeze['black_detector_sha256']
    ev=read(OUT/'evaluation.json');blocks=ev['geographic_blocks'];p=read(OUT/'pattern208.json');train=read(OUT/'training-agreement.json')
    _,hobs,hc=load_graph(ROOT/'photo2/r336/results/graph.json.gz');core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids'])
    layers={'R336_original1039':(hobs,hc),'R343_historical1039':(oldobs,hc),'R344_historical1039':(obs,hc),
            'R343_current1041':(oldobs,co),'R344_current1041':(obs,co),'R343_frozen710':(oldobs,{o:co[o] for o in core}),'R344_frozen710':(obs,{o:co[o] for o in core})}
    support_checks=0
    for name,(oo,cc) in layers.items():
        saved=ev['strict_cohorts'][name];sequence='';counts=Counter()
        for k,e in enumerate(saved['entries']):
            names=sorted(o for o in cc if (7*cc[o][0]+6*cc[o][1])%208==k);ct=Counter(oo[o]['color'] for o in names)
            strong=len(ct)==1 and len(names)>=3 and len({blocks[o] for o in names})>=3
            status='conflict' if len(ct)>1 else 'strong' if strong else 'observed' if names else 'unknown'
            assert e['status']==status and e['ids']==names and e['counts']==dict(ct)
            sequence+=next(iter(ct))[0].upper() if strong else '?';counts[status]+=1;support_checks+=1
        assert sequence==saved['strict_sequence'] and counts['strong']==saved['supported'] and counts['conflict']==saved['conflicting']
    assert (p['supported'],p['conflicting'],p['insufficient'])==(199,2,7)
    assert p['strict_sequence'].count('?')==9 and len(p['provisional_sequence'])==208 and '?' not in p['provisional_sequence']
    prior=[(sum(obs[o]['color']==c for o in co)+1)/(len(co)+3) for c in COLORS]
    for e in p['entries']:
        ct=Counter(obs[o]['color'] for o in e['ids']);win=max(COLORS,key=lambda c:ct[c])
        assert e['provisional_color']==win and e['tentative']==(e['status']!='strong')
        assert e['strict_color']==(win if e['status']=='strong' else '?')
        for j,c in enumerate(COLORS):
            assert abs(e['smoothing_probability'][c]-(ct[c]+3*prior[j])/(len(e['ids'])+3))<1e-12
            assert e['candidate_agreement'][c]==dict(agree=ct[c],disagree=len(e['ids'])-ct[c])
        for r in e['evidence']:
            assert r['xy']==obs[r['id']]['xy'] and r['ab']==co[r['id']] and r['color']==obs[r['id']]['color']
    for cohort,ids in [('current1041',co),('historical1039',hc)]:
        rows=[];strict=[]
        for o in sorted(ids):
            e=p['entries'][(7*co[o][0]+6*co[o][1])%208];k=(7*co[o][0]+6*co[o][1])%2704
            r=dict(id=o,color=obs[o]['color'],prediction=e['provisional_color'],agrees=obs[o]['color']==e['provisional_color'],region=blocks[o],occurrence=k//208,authority=authority(o,ledger));rows.append(r)
            if e['status']=='strong':strict.append(r)
        check_summary(rows,train[cohort]['provisional']);check_summary(strict,train[cohort]['strict'])
        assert train[cohort]['strict']['abstentions']==len(rows)-len(strict)
    assert {r['id'] for r in train['current1041']['mismatches']}=={'R332-R-0037-0040','REC266-P035619','R332-R-0197-0183'}
    # All current model/holdout predictions are independently recomputed.
    model_specs=[('frequency','A',1,None),('phase13','A',13,None),('A104','A',104,None),('A208','A',208,None),('A208_hier104','A',208,104),('A338','A',338,None),('B207','B',207,None),('B299','B',299,None),('A306_alias','A',306,None)]
    saved_rows=read(OUT/'heldout-predictions.json.gz');prediction_checks=0
    for model in model_specs:
        for hold in ['geographic','occurrence']:
            key=model[0]+'_'+hold;values=direct_predictions(obs,co,sorted(co),blocks,model,hold);rows=saved_rows[key]
            for r in rows:
                z=values[r['id']];assert r['prediction']==z['prediction'] and r['training_same_key_records']==z['support']
                assert max(abs(a-b) for a,b in zip(r['probabilities'],z['prob']))<1e-12
                assert r['agrees']==(z['prediction']==obs[r['id']]['color']);prediction_checks+=1
            result=ev['heldout'][key];check_summary(rows,result)
            loss=-sum(math.log(values[o]['prob'][COLORS.index(obs[o]['color'])]) for o in co)/len(co)
            gain=sum(math.log(values[o]['prob'][COLORS.index(obs[o]['color'])]/values[o]['baseline'][COLORS.index(obs[o]['color'])]) for o in co)/len(co)
            assert abs(loss-result['log_loss'])<1e-12 and abs(gain-result['gain_nats'])<1e-12
    historical_checks=0
    for name,(oo,cc) in list(layers.items())[:5]:
        for hold in ['geographic','occurrence']:
            values=direct_predictions(oo,cc,sorted(cc),blocks,('A208','A',208,None),hold)
            saved=ev['cohort_comparisons'][name][hold]
            for label,ids in [('all_targets',set(cc)),('unchanged_color_targets',set(cc)-set(CORRECTIONS))]:
                assert saved[label]['agree']==sum(values[o]['prediction']==oo[o]['color'] for o in ids) and saved[label]['n']==len(ids);historical_checks+=1
    for d in ev['proper_divisor_obstructions']:
        i,j=d['witness_positions'];assert 208%d['period']==0 and i%d['period']==j%d['period']
        assert p['strict_sequence'][i]!='?' and p['strict_sequence'][j]!='?' and p['strict_sequence'][i]!=p['strict_sequence'][j]
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    panels=read(OUT/'review/panels.json')
    for panel in panels:
        x0,y0,x1,y1=panel['crop_box'];assert np.array_equal(np.array(Image.open(OUT/'review'/panel['filename'])),photo[y0:y1,x0:x1]);assert panel['key'][0]==panel['id']
    save(OUT/'verification.json',dict(passed=True,historical_hashes=len(set(seal)|set(prior_seal)),old_records_preserved=1059,coordinates_preserved=1041,links_preserved=2290,
                                    maker_pigments_preserved=True,changed_pigments=CORRECTIONS,strict_entries_checked=support_checks,heldout_probabilities_checked=prediction_checks,
                                    matched_historical_summaries_checked=historical_checks,proper_divisor_witnesses=9,literal_native_crops=len(panels),pattern=[199,2,7],
                                    limits='Independent arithmetic and exact native crop checks; no new independent physical ground truth or proof of identities/winding.'))
    print('PASS independent R344',support_checks,'strict entries;',prediction_checks,'held-out predictions;',historical_checks,'matched summaries')


if __name__=='__main__':
    main()
