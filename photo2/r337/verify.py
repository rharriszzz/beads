"""Independent checks from serialized inputs; no detector or inference rerun."""
import argparse,json,gzip,hashlib,math,re,time
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2]
def read(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rem(v,H):
    return int(v[0])%H[0],int(v[1])-(int(v[0])//H[0])*H[1]
def minority(k,colors):
    groups=defaultdict(Counter)
    for key,c in zip(k,colors):groups[int(key)][c]+=1
    return sum(sum(ct.values())-max(ct.values()) for ct in groups.values())
def independent_prediction(k,col,block):
    out=np.zeros((len(k),3));baselines=np.zeros_like(out);palette=['red','yellow','black']
    for b in range(12):
        train=[j for j in range(len(k)) if int(block[j]) not in {(b-1)%12,b,(b+1)%12}];base=Counter(col[j] for j in train);den=sum(base.values())+3;prior=np.array([(base[c]+1)/den for c in palette]);counts=defaultdict(Counter)
        for j in train:counts[int(k[j])][col[j]]+=1
        for j in range(len(k)):
            if block[j]!=b:continue
            ct=counts[int(k[j])];out[j]=(np.array([ct[c] for c in palette])+3*prior)/(sum(ct.values())+3);baselines[j]=prior
    return float(np.mean([math.log(out[j,palette.index(col[j])]/baselines[j,palette.index(col[j])]) for j in range(len(k))]))

def run(root):
    started=time.perf_counter();root=Path(root);seal=read(root/'results/input-seal.json');assert all(digest(ROOT/p)==h for p,h in seal.items())
    g=read(ROOT/'photo2/r336/results/graph.json.gz');co={r['id']:r['ab'] for r in g['coordinates']};obs={r['id']:r for r in g['observations']};H=g['H'];ids=sorted(co);colors=[obs[o]['color'] for o in ids];core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']);assert len(ids)==1039 and len(core)==710 and len(g['edges'])==2284
    for e in g['edges']:assert rem([co[e['target']][j]-co[e['source']][j]-e['delta_ab'][j] for j in range(2)],H)==(0,0)
    assert len({rem(v,H) for v in co.values()})==1039
    old=read(ROOT/'photo2/r335/results/graph.json.gz');oldobs={r['id']:r for r in old['observations']}
    for o in ids:assert obs[o]['xy']==oldobs[o]['xy']
    topology=read(root/'results/topology.json');assert topology['cycle_rank']==2284-1039+1 and topology['generator']==H and len(topology['integer_neighbor_maps'])==12
    a=read(root/'results/analysis.json.gz');transcount=0;domaincount=0;pathincidences=0
    ctrl=read(ROOT/'photo2/r334/controls/controls.json.gz');blocks={r['id']:r['section'] for r in ctrl['rows']+ctrl['maker_geography']}
    for cohort,names in [('active',ids),('interior',sorted(core))]:
        for row in read(root/f'results/{cohort}-translations.json'):
            dx,dy=row['vector'];lookup={tuple(co[o]):o for o in names};pairs=[(o,lookup[(co[o][0]+dx,co[o][1]+dy)]) for o in names if (co[o][0]+dx,co[o][1]+dy) in lookup];assert len(pairs)==row['pairs'];assert sum(obs[o]['color']==obs[z]['color'] for o,z in pairs)==row['agree'];transcount+=len(pairs)
        domains=read(root/f'results/{cohort}-domains.json.gz');assert domains['enumerated']==1969
        for d in domains['ranking']:
            p,q,r=d['p'],d['q'],d['r'];assert 1<=p*q<=399 and p*q==d['area'] and 16%q==0 and (16-r*(16//q))%p==0;domaincount+=1
        for trace in read(root/f'results/{cohort}-staircases.json.gz')['traces']:
            for x,y,v in zip(trace['ids'],trace['ids'][1:],trace['word']):
                assert [co[y][j]-co[x][j] for j in range(2)]==v;assert any({e['source'],e['target']}=={x,y} for e in g['edges']);assert obs[x]['color'] in (['black','red'] if trace['palette']=='BR' else ['black','yellow']);pathincidences+=1
        for model in a['cohorts'][cohort]['scores']:
            if model['model'] in ['A208','B207','B299','A306','B305']:
                family,L={'A208':([7,6],208),'B207':([6,7],207),'B299':([6,7],299),'A306':([7,6],306),'B305':([6,7],305)}[model['model']];k=[sum(x*y for x,y in zip(co[o],family))%L for o in names];assert minority(k,[obs[o]['color'] for o in names])==model['minimum_record_disagreements']
    for fam,w,expected in [('A',[7,6],[208,338]),('B',[6,7],[207,299])]:
        N=sum(x*y for x,y in zip(H,w));assert [L for L in range(200,400) if N%L==0]==expected
    assert 299==13*23 and 207%13!=0
    paths=read(root/'search-results/replays.json.gz');scope=read(root/'search-results/scope.json');common=scope['common_ids'];cand=read(root/'search-results/candidates.json.gz');edgechecks=0;score_delta=0;motifslots=0
    for name,r in paths.items():
        coords=r['extension_coordinates'];HH=r['H'];bad=[]
        for e in g['edges']:
            res=[coords[e['target']][j]-coords[e['source']][j]-e['delta_ab'][j] for j in range(2)]
            if rem(res,HH)!=(0,0):bad.append((e['source'],e['target']))
            edgechecks+=1
        assert set(bad)=={(e['source'],e['target']) for e in r['extension']['violated_edges']}
        for e in r['proposed_changed_links']:assert rem([coords[e['target']][j]-coords[e['source']][j]-e['delta_ab'][j] for j in range(2)],HH)==(0,0)
        protected={frozenset(e['ids']) for e in scope['protected_pairs']};assert sum(frozenset(z) in protected for z in bad)==r['extension']['maker_violations']
    scorecache={}
    for row in cand:
        coords=co if row['map']=='R336' else paths[row['map']]['extension_coordinates'];w=[7,6] if row['family']=='A' else [6,7];N=abs(sum(x*y for x,y in zip(row['H'],w)));L=row['L'];assert N==row['N'] and N%L==0 and 200<=L<=399;k=[sum(x*y for x,y in zip(coords[o],w))%L for o in common];cs=[obs[o]['color'] for o in common];assert minority(k,cs)==row['minimum_record_disagreements']
        key=tuple(k)
        if key not in scorecache:scorecache[key]=independent_prediction(k,cs,[blocks[o] for o in common])
        score_delta=max(score_delta,abs(scorecache[key]-row['score']['gain_nats']));assert score_delta<1e-12
        for slot in row['motif']:
            oo=[o for o,kk in zip(common,k) if kk==slot['residue']];assert oo==slot['ids'];assert dict(Counter(obs[o]['color'] for o in oo))==slot['counts'];assert slot['color']=='?' or oo;motifslots+=1
    # Verify reviewed displayed R331 relations from the actual historical HTML.
    source=(ROOT/'photo2/r331/review/index.html').read_text();reviewed_pairs=set()
    for label,svg in re.findall(r'aria-label="([^"]+): original photograph with labeled supports">(.*?)</svg>',source,re.S):
        if label in ['g-working','inward-working','black-direction']:
            for aa,zz in re.findall(r'<title>([^< ]+) to ([^< ,]+), delta',svg):reviewed_pairs.add(frozenset((aa,zz)))
    protected={frozenset(e['ids']) for e in scope['protected_pairs']};assert reviewed_pairs<=protected
    consequences=read(root/'results/consequences.json.gz');assert not any(r['equation_errors'] for r in consequences['constructed_graph_checks']);assert all(r['component_sizes']==[1039] for r in consequences['constructed_graph_checks'])
    pattern=read(root/'results/pattern208.json');sequence=pattern['strict_sequence'];assert len(sequence)==208 and sequence.count('?')==32 and pattern['strict_known']==176
    assert [13*16+6,13*16-7]==H and 7*6+6*(-7)==0
    for i,ch in enumerate(sequence):
        oo=[o for o in ids if (7*co[o][0]+6*co[o][1])%208==i]
        if ch!='?':assert len(oo)>=3 and len({blocks[o] for o in oo})>=3 and {obs[o]['color'][0].upper() for o in oo}=={ch}
    for d in [1,2,4,8,13,16,26,52,104]:assert any(sequence[i]!='?' and sequence[j]!='?' and sequence[i]!=sequence[j] for i in range(208) for j in range(i+1,208) if i%d==j%d)
    assert {(x['family'],x['L']) for x in cand if x['map']=='R336'}=={('A',208),('A',338),('B',207),('B',299)}
    for row in pattern['geographic_predictions']:
        assert all(blocks[z] not in {(blocks[row['id']]-1)%12,blocks[row['id']],(blocks[row['id']]+1)%12} for z in row['training_ids'])
        assert all((7*co[z][0]+6*co[z][1])%208==row['residue'] for z in row['training_ids'])
    crops=read(root/'review/native-crops.json');im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');assert im.size==(2540,3182)
    for cr in crops:
        assert np.array_equal(np.array(im.crop(cr['bbox'])),np.array(Image.open(root/'review'/cr['file'])))
        for k in cr['key']:assert k['xy']==obs[k['id']]['xy'] and k['ab']==co[k['id']] and k['color']==obs[k['id']]['color'] and list(k['alternative_ab'])==paths[cr['map']]['extension_coordinates'][k['id']]
    report=dict(passed=True,historical_files_exact=len(seal),active_equations=2284,quotient_sites=1039,independent_cycle_rank=1246,translation_pair_checks=transcount,domain_memberships=domaincount,staircase_link_incidences=pathincidences,complete_path_extensions=len(paths),extension_equations=edgechecks,exact_candidate_evaluations=len(cand),independent_predictive_max_delta=score_delta,motif_entries=motifslots,historical_reviewed_pairs_in_current_hard_constraints=len(reviewed_pairs),native_crops=len(crops),strict_partial_pattern_known=176,strict_unknown=32,proper_divisors_rejected=9,multiples13_included=True,closure_13_spatial_copies_plus_zero_index_wrap=True,seconds=time.perf_counter()-started,limitation='Numerical/provenance verification; no new independently labeled photographic truth.')
    (root/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='photo2/r337');run(p.parse_args().root)
