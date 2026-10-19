"""Independent arithmetic, prediction, path, photo provenance and preservation.

Does not import the spiral tracer, pattern fitting, classifier or diagnosis
implementations. This verifies numerics and provenance, not physical bead truth.
"""
import argparse,math,time,subprocess,json,gzip,hashlib,os
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2];BASE='d726ef590e56bfaa29f54f8ba142a054ba88019e'
def read(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='photo2/r333');ap.add_argument('--output',default='photo2/r333/verification.json');args=ap.parse_args();run=Path(args.run);t=time.perf_counter();g=read(ROOT/'photo2/r332/results/graph.json.gz');obs={o['id']:o for o in g['observations']};co={x['id']:tuple(x['ab']) for x in g['coordinates']};ids=sorted(co);ix={o:i for i,o in enumerate(ids)};colors=['red','yellow','black'];ab=np.array([co[o] for o in ids]);c=np.array([colors.index(obs[o]['color']) for o in ids]);w=np.array([.25 if 'provisional' in str(obs[o]).lower() else .55 if obs[o]['color']=='black' else 1 for o in ids]);H=g['H'];n=len(ids);assert n==1041;assert len(obs)==1064;assert Counter(obs[o]['color'] for o in ids)==dict(red=378,yellow=317,black=346)
    # Independently rebuild geographic bins from immutable station cache; new
    # observations use three closest original measured supports with seam lift.
    old=read(ROOT/'photo2/r328/results/graph.json.gz');names=sorted(old['stations_px']);xy=np.array([obs[o]['xy'] for o in names]);period=old['period_px'];station=[]
    for o in ids:
        if o in old['stations_px']:station.append(old['stations_px'][o]%period);continue
        dist=np.linalg.norm(xy-obs[o]['xy'],axis=1);jj=np.argsort(dist)[:3];ss=np.array([old['stations_px'][names[j]]%period for j in jj]);ss-=np.rint((ss-ss[0])/period)*period;station.append(np.average(ss,weights=1/np.maximum(dist[jj],1))%period)
    station=np.array(station);blocks=np.minimum((station/period*12).astype(int),11);edges={frozenset((e['source'],e['target'])):e for e in g['edges']};equations=0
    for e in g['edges']:
        dv=ab[ix[e['target']]]-ab[ix[e['source']]]-e['delta_ab'];assert dv[0]%H[0]==0 and dv[1]==dv[0]//H[0]*H[1];equations+=1
    sp=read(run/'spirals/spirals.json.gz');st=read(run/'staircases/staircases.json.gz');di=read(run/'diagnosis/diagnosis.json.gz');pe=read(run/'periods-selected/periods.json.gz');fo=read(run/'followup/followup.json.gz');paths=0;pathlinks=0
    for p in sp['segments']+st['traces']:
        assert len(p['ids'])==p['length'];assert len(set(p['ids']))==len(p['ids']);assert p['inferred_links']==0
        assert all(obs[o]['color'] in p['palette'] for o in p['ids']);assert all(sum(obs[o]['color']==col for o in p['ids'])>=1 for col in p['palette'])
        for j,(o,z) in enumerate(zip(p['ids'],p['ids'][1:])):
            assert frozenset((o,z)) in edges;assert tuple(np.array(co[z])-co[o])==tuple(p['word'][j]);assert tuple(p['word'][j]) in [(1,0),(0,1)];pathlinks+=1
        paths+=1
    covered=set(o for p in sp['segments'] for o in p['ids']);assert len(covered)==sp['coverage']['unique']==537
    repeated=set();repeatcount=0
    for p in st['traces']:
        good=[]
        for e in p['repeated_examples']:
            for o,z in e['pairs']:
                assert tuple(np.array(co[z])-co[o])==tuple(e['translation']);dd=abs(int(blocks[ix[o]])-int(blocks[ix[z]]));assert min(dd,12-dd)>=2
            agree=sum(obs[o]['color']==obs[z]['color'] for o,z in e['pairs']);assert agree==e['agree']
            el=sum(frozenset((e['pairs'][j][1],e['pairs'][j+1][1])) in edges for j in range(len(e['pairs'])-1) if frozenset((e['pairs'][j][0],e['pairs'][j+1][0])) in edges);assert el==e['measured_example_links']
            if agree/len(e['pairs'])>=.85 and el>=4:good.append(e)
        assert p['repeat_supported']==(len(good)>=2)
        if p['repeat_supported']:repeated|=set(p['ids']);repeatcount+=1
    assert len(repeated)==201 and repeatcount==17
    # Independent fixed-template exhaustive scores (all starts and all phases),
    # implemented as scalar walks rather than the vectorized search.
    directions=[(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)];occ={v:o for o,v in co.items()};templatechecks=0
    for row in st['template_ranking']:
        palette=['black','red' if row['palette']=='BR' else 'yellow'];cone=row['cone'];word=[directions[cone]]*row['runs'][0]+[directions[(cone+1)%6]]*row['runs'][1];tot=0;maxlen=0;ge8=ge12=0
        for start in ids:
            best=0
            for phase in range(len(word)):
                at=start;length=1 if obs[at]['color'] in palette else 0;seen={obs[at]['color']} if length else set()
                if length:
                    for step in range(32):
                        cell=tuple(co[at][j]+word[(phase+step)%len(word)][j] for j in range(2));z=occ.get(cell)
                        if z is None or frozenset((at,z)) not in edges or obs[z]['color'] not in palette:break
                        at=z;length+=1;seen.add(obs[at]['color'])
                if len(seen)==2:best=max(best,length)
            tot+=max(best-5,0);maxlen=max(maxlen,best);ge8+=best>=8;ge12+=best>=12
        assert abs(tot/n-row['score'])<1e-12;assert maxlen==row['maximum'];assert ge8==row['starts_at_least8'] and ge12==row['starts_at_least12'];templatechecks+=1
    # Independent twelve-section predictions for EVERY primary candidate period.
    # Scalar dictionaries explicitly build weighted counts; no fitting imports.
    def fit(k,p,train,parent=None):
        counts=defaultdict(lambda:np.zeros(3));base=np.ones(3);pc=defaultdict(lambda:np.zeros(3))
        for j in train:counts[int(k[j]%p)][c[j]]+=w[j];base[c[j]]+=w[j];pc[int(k[j]%(parent or 1))][c[j]]+=w[j]
        base/=base.sum();theta=[]
        for r in range(p):
            if parent:
                prior=(pc[r%parent]+3*base)/(pc[r%parent].sum()+3);theta.append((counts[r]+prior)/(counts[r].sum()+1))
            else:theta.append((counts[r]+3*base)/(counts[r].sum()+3))
        return np.array(theta),base
    maxdelta=0;fits=0
    for row in pe['full_R332']:
        k=ab@([7,6] if row['family']=='A' else [6,7]);pred=np.zeros((n,3));ba=np.zeros((n,3))
        for block in range(12):
            tr=np.flatnonzero(blocks!=block);te=blocks==block;theta,base=fit(k,row['period'],tr,row.get('parent'));pred[te]=theta[k[te]%row['period']];ba[te]=base
        gain=float(np.average(np.log(pred[np.arange(n),c]/ba[np.arange(n),c]),weights=w));agreement=float(np.mean(pred.argmax(1)==c));maxdelta=max(maxdelta,abs(gain-row['gain_nats']));assert abs(gain-row['gain_nats'])<1e-12;assert agreement==row['agreement'];assert row['N']==np.dot(g['H'],[7,6] if row['family']=='A' else [6,7]);assert row['cyclic']==(row['N']%row['period']==0);fits+=1
    assert len(pe['common900_scans'])==40;assert all(len(r['ranking'])==201 for r in pe['common900_scans']);assert len(pe['G'])==176
    # Check all full-motif entries and their uncertainty thresholds independently.
    motifentries=0
    for row in pe['motifs']:
        k=ab@([7,6] if row['family']=='A' else [6,7]);known=0
        for e in row['entries']:
            jj=np.flatnonzero(k%row['period']==e['residue']);cc=np.array([w[jj[c[jj]==q]].sum() for q in range(3)]);win=int(cc.argmax());support=jj[c[jj]==win];section=set(blocks[support].tolist());fraction=float(cc[win]/max(cc.sum(),1e-12));yes=len(support)>=3 and len(section)>=3 and fraction>=.8
            assert e['color']==(colors[win] if yes else '?');assert set(e['ids'])=={ids[j] for j in jj};assert abs(fraction-e['fraction'])<1e-12;known+=yes;motifentries+=1
        assert known==row['known'];assert known+row['unknown']==row['period']
    # Exact spatial translation statistics and expanded alias pairs.
    for row in sp['translations']:
        pairs=[(o,occ[v]) for o in ids if (v:=tuple(np.array(co[o])+row['delta_ab'])) in occ];assert len(pairs)==row['pairs'];assert sum(obs[o]['color']==obs[z]['color'] for o,z in pairs)==row['agree']
    for row in pe['alias_pairs']:
        v=np.array(co[row['target']])-co[row['source']];assert v.tolist()==row['delta_ab'];assert v@[7,6]==row['deltaA'] and v@[6,7]==row['deltaB']
    A=ab@[7,6];B=ab@[6,7];pairchecks=0
    for i in range(n):
        for j in range(i):assert ((A[i]-A[j])%306==0)==((B[i]-B[j])%305==0);pairchecks+=1
    # Every guarded color-rule flag, source ID, context and gap is audited.
    for row in di['all_predictions']:
        o=row['id'];block=int(blocks[ix[o]]);examples=[]
        for mul in range(-15,16):
            if mul==0:continue
            z=occ.get(tuple(np.array(co[o])+mul*np.array([16,16])))
            if z and int(blocks[ix[z]]) not in [(block-1)%12,block,(block+1)%12]:examples.append(z)
        assert set(examples)=={e['id'] for e in row['examples']};cc=Counter(obs[z]['color'] for z in examples);winner,number=cc.most_common(1)[0] if cc else ('?',0);sections={int(blocks[ix[z]]) for z in examples if obs[z]['color']==winner};strong=number>=3 and len(sections)>=3 and number/max(len(examples),1)>=.8;assert row['strong']==strong;assert row['prediction']==(winner if strong else '?')
    assert len(di['breaks'])==19 and len(di['gaps'])==128 and len(di['color_hypotheses'])==3
    for row in di['breaks']:
        o=row['id'];assert row['original']==obs[o]['color'];assert tuple(row['ab'])==co[o];a=row['appearance'];photo=a['suggestion']==row['prediction'] and a['stable'] and a['minimum_vote']>=.55 and max(a['mean_votes'])>=.75;assert photo==row['photographic_support'];assert (o in di['color_hypotheses'])==photo
        for ex in row['comparisons']:
            for r in ex['context']:
                for key,source in [('target_neighbor',o),('example_neighbor',ex['id'])]:
                    if r[key]:assert tuple(np.array(co[r[key]])-co[source])==tuple(r['delta_ab'])
    def rep(v):turn=v[0]//H[0];return(v[0]-turn*H[0],v[1]-turn*H[1])
    occupied={rep(v) for v in co.values()}
    for row in di['gaps']:
        assert rep(row['ab']) not in occupied;assert row['original']=='?';assert row['proposed']['color'] is None
        for r in row['neighbors']:assert rep(np.array(row['ab'])+r['delta_ab'])==rep(co[r['id']])
    for patch in di['coherent_patches']:
        pp=set(patch['ids']);boundary=[e for e in g['edges'] if (e['source'] in pp)!=(e['target'] in pp)];assert boundary==patch['boundary_links']
        for r in patch['alternatives']:assert r['boundary_edges_violated']==len(boundary)>0 and not r['admissible']
    # Original native pixels, photographed appearance controls independently
    # regenerated for all 19 observed flags (not just the three positive flags).
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo/255.;features={}
    for radius in [8,12,16]:
        f=[]
        for o in ids:
            x,y=np.rint(obs[o]['xy']).astype(int);pixels=[]
            for yy in range(y-radius,y+radius+1):
                for xx in range(x-radius,x+radius+1):
                    if (xx-x)**2+(yy-y)**2<=radius**2:pixels.append(rgb[yy,xx])
            f.append(np.quantile(pixels,[.1,.3,.5,.7,.9],axis=0).reshape(-1))
        features[radius]=np.array(f)
    for row in di['breaks']:
        j=ix[row['id']];tr=np.flatnonzero(blocks!=blocks[j]);vv=[]
        for radius in [8,12,16]:
            f=features[radius];scale=np.maximum(np.percentile(f[tr],75,axis=0)-np.percentile(f[tr],25,axis=0),.05);near=tr[np.argsort(np.sum(((f[tr]-f[j])/scale)**2,axis=1))]
            for kn in [15,31,51]:vv.append([float(np.mean(c[near[:kn]]==a)) for a in range(3)])
        assert np.max(np.abs(np.array(vv)-row['appearance']['variants']))<1e-12
    crops=read(run/'review/native-crops.json')
    for row in crops:
        x,y,z,v=row['bbox'];assert np.array_equal(np.asarray(Image.open(run/'review'/row['file'])),photo[y:v,x:z])
    # Broad historical preservation: only scoped R333 and authorized handoffs.
    allowed={'AGENTS.md','PLAN.md','SESSION_HANDOFF.md','REQUEST_LOG.md','INITIAL_QUESTION.md','photo2/R333_REPORT.md','photo2/R333_SPECIFICATION.md','photo2/R333_REPRODUCE.md'};changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines();assert all(p.startswith('photo2/r333/') or p in allowed for p in changed),changed
    seal=read(ROOT/'photo2/r333/input-seal.json')
    for p,h in seal['sources'].items():assert digest(ROOT/p)==h,p
    receipt=dict(passed=True,baseline_commit=BASE,indexed=n,observations=len(obs),edge_equations=equations,measured_paths=paths,path_links_checked=pathlinks,repeat_supported_segments=17,repeat_supported_observations=201,exhaustive_staircase_scores=templatechecks,primary_geographic_period_fits=fits,period_score_max_delta=maxdelta,motif_entries=motifentries,translation_rows=len(sp['translations']),alias_pairs=len(pe['alias_pairs']),partition_pair_decisions=pairchecks,guarded_observation_predictions=n,observed_breaks=19,gaps=128,coherent_patch_alternatives=sum(len(x['alternatives']) for x in di['coherent_patches']),independent_appearance_audits=19,literal_native_crops=len(crops),historical_input_hashes=len(seal['sources']),historical_preservation=True,seconds=time.perf_counter()-t,limitations='Independent numerical and pixel-provenance verification; no new blind photographic labels, physical centers or certified complete design.')
    Path(args.output).write_text(json.dumps(receipt,indent=2)+'\n');print(receipt,flush=True)
if __name__=='__main__':main()
