"""Independent numerical/provenance checks, no scientific writes to history."""
import argparse,json,subprocess,time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r329.common import ROOT,read,sha

BASE='422a85ea10974f54ad5345b337d778448e7be48a'

def coordinates(state):
    result={}
    for r in state['coords']:
        xy=tuple(r['ab'][d]-r['turn']*state['H'][d] for d in range(2))
        if r['observation'] in result:assert result[r['observation']]==xy
        result[r['observation']]=xy
    origin=result['C-1302-0316']
    return {o:tuple(xy[d]-origin[d] for d in range(2)) for o,xy in result.items()}

def independent(k,c,w,b,p,present=None,parent=None,guard=0):
    present=np.ones(len(k),bool) if present is None else present;gain=den=correct=0;pred=np.zeros((len(k),3))
    for block in range(12):
        freq=np.ones(3);cc=np.zeros((p,3));pc=np.zeros((parent or 1,3))
        excluded={(block+d)%12 for d in range(-guard,guard+1)}
        for j in range(len(k)):
            if b[j] in excluded or not present[j]:continue
            freq[c[j]]+=w[j];cc[int(k[j])%p,c[j]]+=w[j]
            if parent:pc[int(k[j])%parent,c[j]]+=w[j]
        freq/=freq.sum()
        if parent:
            pp=(pc+3*freq)/(pc.sum(1)[:,None]+3)
            th=(cc+pp[np.arange(p)%parent])/(cc.sum(1)[:,None]+1)
        else:th=(cc+3*freq)/(cc.sum(1)[:,None]+3)
        for j in np.flatnonzero(b==block):
            pr=th[int(k[j])%p] if present[j] else freq;pred[j]=pr
            gain+=w[j]*np.log(pr[c[j]]/freq[c[j]]);den+=w[j];correct+=int(pr.argmax()==c[j])
    return gain/den,correct/len(k),pred

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(ROOT/'photo2/r331/verification.json'));args=ap.parse_args();start=time.perf_counter();root=ROOT/'photo2/r331';receipt={}
    seal=read(root/'results-final/input-seal.json')
    for file,digest in seal['sources'].items():assert sha(ROOT/file)==digest,file
    # Diff all tracked historical paths, including original photo/model sources.
    changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines()
    allowed={'AGENTS.md','PLAN.md','SESSION_HANDOFF.md','REQUEST_LOG.md','photo2/R331_REPORT.md','photo2/R331_REPRODUCE.md','photo2/R331_SPECIFICATION.md'}
    assert all(f.startswith('photo2/r331/') or f in allowed for f in changed),changed
    receipt['historical_tracked_files_preserved']=True
    data=read(root/'results-final/analysis.json.gz');extra=read(root/'followup-final/followup.json.gz');error=read(root/'errors-v2/errors.json.gz')
    # Independently load original frozen tables; no call to the fitting module.
    g=read(ROOT/'photo2/r328/results/graph.json.gz');obs={o['id']:o for o in g['observations']};ss=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'];nov=read(ROOT/'photo2/r329/results/novel-windings.json.gz')['alternatives']
    states={('working' if j==0 else 'closest' if j==1 else 'lower' if j==5 else f'saved-{j}'):s for j,s in enumerate(ss)}
    for j,r in enumerate(nov):states['early' if r['state']['H']==[214,176] else f'novel-{j}']=r['state']
    co=coordinates(states['working']);names=sorted(co);colors=['red','yellow','black'];c=np.array([colors.index(obs[o]['color']) for o in names]);w=np.array([.25 if 'provisional' in str(obs[o]).lower() else .55 if obs[o]['color']=='black' else 1. for o in names]);b=np.array([min(int((g['stations_px'][o]%g['period_px'])/g['period_px']*12),11) for o in names]);ab=np.array([co[o] for o in names]);A=ab@[7,6];B=ab@[6,7]
    assert np.all(A-B==ab[:,0]-ab[:,1]);assert np.all(A+B==13*ab.sum(1));assert np.all((A+B)%13==0)
    for fam,N,wt in [('A',2704,[7,6]),('B',2691,[6,7])]:
        assert np.dot([214,201],wt)==N
        assert [p for p in range(200,400) if N%p==0]==data['alias']['divisors_'+fam]
    for pair in data['alias']['pairs']:
        i,j=names.index(pair['a']),names.index(pair['z']);assert A[j]-A[i]==pair['deltaA'];assert B[j]-B[i]==pair['deltaB'];assert (ab[j]-ab[i]).tolist()==pair['delta_ab'];assert pair['same_color']==(c[i]==c[j]);assert pair['deltaA']==pair['deltaB']
    receipt['exact_alias_pairs']=len(data['alias']['pairs']);checks=0
    for r in data['loso']:
        name,fam=r['map'].rsplit('-',1);coords=coordinates(states[name]);present=np.array([o in coords for o in names]);xy=np.array([coords.get(o,(0,0)) for o in names]);wt=[7,6] if fam=='A' else [6,7];k=xy@wt
        N=int(np.dot(states[name]['H'],wt));assert N==r['N'];assert r['cyclic']==(N%r['period']==0)
        gain,acc,_=independent(k,c,w,b,r['period'],present);assert abs(gain-r['gain_nats'])<1e-11;assert abs(acc-r['agreement'])<1e-12;checks+=1
    receipt['independent_common_cohort_period_fits']=checks
    # Independent G own-map likelihoods; no transferred working motif.
    gc=read(ROOT/'photo2/r330/photography/g-replays.json.gz')[-1]['candidates'];gchecks=0
    for r in data['G']+extra['G']:
        state=states[r['name']] if r['name'] in states else gc[int(r['name'].split('-')[1])]['state'];coords=coordinates(state);present=np.array([o in coords for o in names]);wt=[7,6] if r['family']=='A' else [6,7];k=np.array([np.dot(coords[o],wt) if o in coords else 0 for o in names]);parent=r.get('parent')
        gain,acc,_=independent(k,c,w,b,r['period'],present,parent);assert abs(gain-r['gain_nats'])<1e-11;assert abs(acc-r['agreement'])<1e-12;gchecks+=1
    receipt['independent_own_map_G_fits']=gchecks
    # Every phase-preserving section translation keeps all 900 local colors,
    # relative indices and geometric phases; boundary relations are broken on
    # purpose. Null tail arithmetic and global selection are independently read.
    for null in data['nulls']:
        assert len(null['records'])==19
        for r in null['records']:
            if null['kind']=='section_translation13':
                kk=A+np.array(r['section_offsets'])[b];assert np.all((kk-A)%13==0)
                for block in range(12):
                    jj=np.flatnonzero(b==block);assert np.array_equal(kk[jj]-kk[jj[0]],A[jj]-A[jj[0]])
        expected=(1+sum(r['best']['selection_score']>=null['observed_best_selection'] for r in null['records']))/20
        assert expected==null['empirical_tail']
    receipt['phase_null_trials']=38
    # Recreate seeded transformations, verify exact phase inventories and
    # independently recompute the saved winning period's development score.
    rng=np.random.default_rng(331);nullchecks=0;station=np.array([g['stations_px'][o]%g['period_px'] for o in names])
    for null in data['nulls']:
        for r in null['records']:
            shifts=rng.integers(0,64,12)*13;cp=c.copy();wp=w.copy()
            if null['kind']=='phase_lane_rotation':
                for block in range(12):
                    for phase in range(13):
                        jj=np.flatnonzero((b==block)&(A%13==phase));jj=jj[np.argsort(station[jj])]
                        if len(jj):
                            offset=int(rng.integers(len(jj)));cp[jj]=np.roll(c[jj],offset);wp[jj]=np.roll(w[jj],offset)
                            assert sorted(zip(cp[jj],wp[jj]))==sorted(zip(c[jj],w[jj]))
            else:assert shifts.tolist()==r['section_offsets']
            best=r['best'];name,fam=best['map'].rsplit('-',1);coords=coordinates(states[name]);wt=[7,6] if fam=='A' else [6,7];present=np.array([o in coords for o in names]);k=np.array([np.dot(coords.get(o,(0,0)),wt) for o in names])
            if null['kind']=='section_translation13':k+=shifts[b]
            p=best['period'];dev=[0,1,3,4,6,7,9,10];gain=den=0.
            for testblocks in [dev[::2],dev[1::2]]:
                train=present&np.isin(b,[x for x in dev if x not in testblocks]);test=present&np.isin(b,testblocks);freq=np.ones(3);cc=np.zeros((p,3))
                for j in np.flatnonzero(train):freq[cp[j]]+=wp[j];cc[k[j]%p,cp[j]]+=wp[j]
                freq/=freq.sum();theta=(cc+3*freq)/(cc.sum(1)[:,None]+3)
                for j in np.flatnonzero(test):gain+=wp[j]*np.log(theta[k[j]%p,cp[j]]/freq[cp[j]]);den+=wp[j]
            score=gain/den-.1*p*np.log(3)/den;assert abs(score-best['selection_score'])<1e-11;nullchecks+=1
    receipt['independent_null_transform_and_winner_checks']=nullchecks
    # Proper geographic exclusion, including the optional adjacent-section guard.
    hierarchy=0
    for r in data['sensitivity']:
        if r['black_weight']!=.55 or r['robust']:continue
        gain,acc,_=independent(A if r['family']=='A' else B,c,w,b,r['period'],parent=r['parent'],guard=r['guard']);assert abs(gain-r['gain_nats'])<1e-11;hierarchy+=1
    receipt['independent_hierarchy_guard_checks']=hierarchy
    assert extra['partition_A306_B305']['max_prediction_difference']==0
    for pair in extra['pairs']:
        k=A if pair['family']=='A' else B;n=agree=0
        for i in range(len(k)):
            for j in range(i+1,len(k)):
                if abs(k[j]-k[i])==pair['period']:n+=1;agree+=int(c[i]==c[j])
        assert n==pair['n'] and agree==pair['agree']
    receipt['extra_pair_counts']=len(extra['pairs'])
    # Independently reconstruct metadata errors; no motif needed or credited.
    adj=defaultdict(list)
    for edge in g['graph']['edges']:
        a,z=edge['source'],edge['target'];adj[a].append(z);adj[z].append(a)
    metachecks=0
    for r in error['results']:
        if r['method']!='frozen_graph_metadata':continue
        k=(A if r['family']=='A' else B).copy();bad={names.index(o) for o in r['affected_ids']};perturbed=k.copy()
        if 'index' in r['kind']:
            for j in bad:perturbed[j]+=r['shift']
        offsets={}
        for j,o in enumerate(names):
            if b[j]!=r['section']:continue
            if r['kind']=='unobserved' and j in bad:offsets[j]=0;continue
            votes=Counter(int(perturbed[names.index(z)]+k[j]-k[names.index(z)]-perturbed[j]) for z in adj[o]);best=sorted(votes,key=lambda v:(-votes[v],v))[0];n=votes[best]
            offsets[j]=best if best in [-7,-6,-1,1,6,7] and n>=2 and n>=.75*sum(votes.values()) else 0
        exact=sum(offsets[j]==-r['shift'] for j in bad) if r['shift'] else 0;assert exact==r['exact_index_recovered'];assert sum(v!=0 for j,v in offsets.items() if j not in bad)==r['false_index'];metachecks+=1
    receipt['independent_graph_metadata_trials']=metachecks
    # Posterior state arithmetic is not a calibrated confidence measure. Verify
    # that every real index proposal would be refused if it breaks graph links.
    assert all(not r['adoptable'] for r in error['real_proposals'])
    # Independently form the nine-state posterior for saved real-data flags.
    audit={r['id']:r for r in read(ROOT/'photo2/r330/refinement/refinement.json.gz')['color_audit']};latentchecks=0
    for fam,k,p,parent in [('A',A,208,104),('B',B,207,None)]:
        # Complete real-data absence of index adoption is separately asserted.
        for r in error['real_proposals']:
            if r['family']!=fam:continue
            j=names.index(r['id']);q=np.maximum(np.array(audit[r['id']]['mean_votes']),.03);q/=q.sum();col=colors.index(r['proposed_color'])
            tr=b!=b[j];freq=np.ones(3);cc=np.zeros((p,3));pc=np.zeros((parent or 1,3))
            for i in np.flatnonzero(tr):freq[c[i]]+=w[i];cc[k[i]%p,c[i]]+=w[i];pc[k[i]%(parent or 1),c[i]]+=w[i]
            freq/=freq.sum()
            if parent:
                pp=(pc+3*freq)/(pc.sum(1)[:,None]+3);theta=(cc+pp[np.arange(p)%parent])/(cc.sum(1)[:,None]+1)
            else:theta=(cc+3*freq)/(cc.sum(1)[:,None]+3)
            scores=[.8*theta[k[j]%p,c[j]]*q[c[j]]]
            scores += [(.08/6)*theta[(k[j]+d)%p,c[j]]*q[c[j]] for d in [-7,-6,-1,1,6,7]]
            scores += [.06*theta[k[j]%p,(c[j]+d)%3]*q[(c[j]+d)%3] for d in [1,2]]
            mass=np.array(scores)/sum(scores);which=int(mass.argmax());assert which in [7,8];assert col==(c[j]+which-6)%3;assert abs(mass[which]-r['posterior'])<1e-12;latentchecks+=1
    receipt['independent_real_latent_posteriors']=latentchecks
    assert error['duplicates']['injected']==error['duplicates']['detected']==9
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');figures=read(root/'review/figures.json')
    for f in figures:assert np.array_equal(np.asarray(Image.open(root/'review'/f['file'])),np.asarray(photo.crop(f['bbox'])))
    receipt['literal_native_crops']=len(figures);receipt['unique_native_crop_files']=len({f['file'] for f in figures})
    receipt.update(passed=True,seconds=time.perf_counter()-start,base_commit=BASE,
        limitations='Independent code verifies numbers, exclusion, arithmetic, crops and preservation. No independent new photographic labels, true period or count were established.')
    Path(args.output).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
