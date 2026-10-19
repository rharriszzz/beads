"""Joint exact-divisor search (non13 is a preference) on complete cached paths, with R336 extension gates."""
import argparse,time,csv,resource,copy,os
from .common import *
from photo2.r329.common import canonical,inputs,replay,REF,serialize

def states():
    ss=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'];out=[('R328-'+str(i),s) for i,s in enumerate(ss)]
    out += [('R329-'+str(i),r['state']) for i,r in enumerate(read(ROOT/'photo2/r329/results/novel-windings.json.gz')['alternatives'])]
    out += [('G-'+str(i),r['state']) for i,r in enumerate(read(ROOT/'photo2/r330/photography/g-replays.json.gz')[-1]['candidates'])]
    out += [('H-'+str(i),r['state']) for i,r in enumerate(read(ROOT/'photo2/r330/checks/h-bundle-repair.json.gz')['candidates'])]
    extra=Path(os.environ.get('R337_EXTRA_STATES',ROOT/'photo2/r337/bounded/states.json.gz'))
    if extra.exists():out += [('J-'+str(i),r['state']) for i,r in enumerate(read(extra)['candidates'])]
    return out

def normalized(s,n):
    by={r['window']:r for r in s['path'][:-1]}
    return [by[j] for j in range(n)]+[by[0]]

def extension(g,co,alt,H,core,protected):
    # Anchor the entire saved alternative, propagate R332-only nodes through
    # retained R336 equations, then check ALL old/new boundary equations.
    bad=[];missing=[];edges=g['edges'];coord=dict(alt);adj=defaultdict(list)
    for e in edges:
        a,z=e['source'],e['target'];d=tuple(e['delta_ab']);adj[a].append((z,d));adj[z].append((a,tuple(-v for v in d)))
    todo=deque(sorted(coord));assigned=[]
    while todo:
        a=todo.popleft()
        for z,d in adj[a]:
            if z in coord:continue
            coord[z]=tuple(coord[a][j]+d[j] for j in range(2));assigned.append(z);todo.append(z)
    for e in edges:
        a,z=e['source'],e['target']
        if a not in coord or z not in coord:missing.append(e);continue
        residual=[coord[z][j]-coord[a][j]-e['delta_ab'][j] for j in range(2)]
        if quotient(residual,H)!=(0,0):bad.append(dict(e,residual=residual,both_legacy=a in alt and z in alt,both_core=a in core and z in core,maker_protected=frozenset((a,z)) in protected))
    occ=defaultdict(list)
    for o,v in coord.items():occ[quotient(v,H)].append(o)
    duplicates=[v for v in occ.values() if len(v)>1]
    return dict(indexed=len(coord),propagated=assigned,missing_edges=missing,violated_edges=bad,core_violations=sum(r['both_core'] for r in bad),maker_violations=sum(r['maker_protected'] for r in bad),new_support_boundary_violations=sum(not r['both_legacy'] for r in bad),duplicate_sites=duplicates),coord

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.perf_counter();g,obs,co,ids,ab,c,b,core=data();index={o:i for i,o in enumerate(ids)};bankg,bank,prep,oldstates=inputs();s0,primary_receipt,cps=replay(bank,prep,oldstates[0]['path']);primary=oldstates[0];protected=maker_constraints(g,co);ss=states()
    common=sorted(set.intersection(set(ids),*[set(canonical(s)) for _,s in ss]));ii=np.array([index[o] for o in common]);comparisons=[];evaluations=[];replays=[];records={};mapkeys={};countreuse=read(ROOT/'photo2/r329/results/coverage-summary.json');csvcounts=list(csv.DictReader(open(ROOT/'photo2/r329/results/count-coverage.csv')))
    save(out/'scope.json',dict(paths=len(ss),common_ids=common,protected_pairs=[dict(ids=sorted(v),authority=protected[v]) for v in sorted(protected,key=lambda v:sorted(v))],count_exploration=countreuse,previous_count_rows=len(csvcounts),policy='No new detector/model/beam search. Joint search only on own-count exact divisors of independently saved paths. All current active IDs retained in deterministic extension; conflicts reject an extension, never silently delete links. Physical count exploration supplies provenance, not fit truth.'))
    def scoremap(name,alt,H,ext):
        aa=np.array([alt[o] for o in common]);rows=[]
        for fam,w in [('A',[7,6]),('B',[6,7])]:
            N=abs(int(np.dot(H,w)));k=aa@w
            lengths=[L for L in range(200,400) if N%L==0]
            for L in lengths:
                key=(tuple(map(tuple,aa)),tuple(H),fam,L)
                sc,pr,sp=predict(k%L,c[ii],b[ii]); coremask=np.array([o in core for o in common]); core_score,_,_=predict((k%L)[coremask],c[ii][coremask],b[ii][coremask]);occsc,_,_=predict(k%L,c[ii],b[ii],occ=(k%N)//L)
                spkey=spatial(aa);spatialsc,prior,ba=predict(spkey,c[ii],b[ii]);currentkey=ab[ii]@[7,6]%208;current_sc,current_pr,_=predict(currentkey,c[ii],b[ii],parent=ab[ii]@[7,6]%104)
                # Period adds counts to target-excluded spatial probabilities.
                joint=np.zeros_like(pr);joint_current=np.zeros_like(pr)
                for block in range(12):
                    tr=~np.isin(b[ii],[(block-1)%12,block,(block+1)%12]);te=b[ii]==block;ct=np.bincount((k[tr]%L)*3+c[ii][tr],minlength=L*3).reshape(L,3);z=ct[k[te]%L];joint[te]=(z+3*prior[te])/(z.sum(1)[:,None]+3);joint_current[te]=(z+3*current_pr[te])/(z.sum(1)[:,None]+3)
                increment=float(np.log(joint[np.arange(len(ii)),c[ii]]/prior[np.arange(len(ii)),c[ii]]).mean())
                row=dict(map=name,H=H,family=fam,N=N,L=L,repeat_count=N//L,preferred_non13=bool(L%13),score=sc,core_score=core_score,occurrence_score=occsc,increment_over_current208=float(np.log(joint_current[np.arange(len(ii)),c[ii]]/current_pr[np.arange(len(ii)),c[ii]]).mean()),current208_common=current_sc,candidate_spatial=spatialsc,increment_over_candidate_spatial=increment,**conflicts(k%L,c[ii],common),coherent_R336=not ext['violated_edges'] and not ext['duplicate_sites'] and not ext['missing_edges'],core_link_changes=ext['core_violations'],maker_link_changes=ext['maker_violations'],total_link_changes=len(ext['violated_edges']),new_boundary_changes=ext['new_support_boundary_violations'],motif=motif(k%L,c[ii],b[ii],common,L),coverage=len(common),count_previous_trials=next((int(z["physical_trials"]) for z in csvcounts if int(z["N"])==N),0))
                evaluations.append(row);rows.append(dict(family=fam,N=N,L=L,gain=sc['gain_nats']))
        return rows
    # Current map comparison uses the SAME common cohort as every saved path.
    ext0,cc0=extension(g,co,{o:co[o] for o in common},g['H'],core,protected);scoremap('R336',co,g['H'],ext0)
    for name,s in ss:
        alt0=canonical(s);alt={o:tuple(np.array(v)+co[REF]) for o,v in alt0.items() if o in co};H=s['H'];path=normalized(s,len(bank['windows']));diff=[j for j,(a,z) in enumerate(zip(primary['path'],path)) if (a.get('patch'),a.get('skipped'))!=(z.get('patch'),z.get('skipped'))]
        first=min(diff) if diff else 0;last=max(diff) if diff else 0
        # Execute the substitution into the primary checkpoint and its full
        # downstream suffix, including return. No newly optimized paths.
        full,receipt,_=replay(bank,prep,path,checkpoint=cps[first],start=first)
        one=copy.deepcopy(primary['path'])
        if diff:one[first]=path[first]
        _,single,_=replay(bank,prep,one,checkpoint=cps[first],start=first)
        fullco=canonical(serialize(full)) if full else {}; exact=bool(full and all(o in fullco and quotient(np.array(v)-fullco[o],H)==(0,0) for o,v in alt0.items()))
        ext,complete=extension(g,co,alt,H,core,protected);rows=scoremap(name,alt,H,ext)
        selectededges={}
        for r in path:
            if r.get('skipped'):continue
            for a,z,d in prep['patches'][r['window']][r['patch']]['edges']:
                if a not in co or z not in co:continue
                if a>z:a,z,d=z,a,[-v for v in d]
                selectededges[a,z,tuple(d)]=dict(source=a,target=z,delta_ab=list(d),window=r['window'],hypothesis=r['hypothesis'])
        introduced=[e for e in selectededges.values() if quotient(np.array(co[e['target']])-co[e['source']]-e['delta_ab'],g['H'])!=(0,0)]
        rec=dict(map=name,H=H,source_path=s['path'],changed_windows=[path[j]['window'] for j in diff],first_replaced=first,last_replaced=last,full_replay=receipt,single_patch_replay=single,reproduces_saved_map=exact,extension=ext,proposed_changed_links=introduced,periods=rows,source_score=s['score'],changed_current_coordinates=sum(quotient(np.array(alt[o])-co[o],H)!=(0,0) for o in alt),missing_current_anchors=sorted(set(co)-set(alt)),conclusion='Rejected as unchanged-R336 reconstruction' if ext['violated_edges'] or ext['duplicate_sites'] else 'Retains R336 constraints; exact repeat still tested separately')
        comparisons.append({k:v for k,v in rec.items() if k not in ['source_path','extension','proposed_changed_links','missing_current_anchors']}|dict(violated_links=len(ext['violated_edges']),core_violations=ext['core_violations'],maker_violations=ext['maker_violations'],new_boundary_violations=ext['new_support_boundary_violations'],duplicate_sites=len(ext['duplicate_sites'])))
        rec['extension_coordinates']={o:list(v) for o,v in complete.items()};records[name]=rec
        if len(records)%25==0:print("replayed",len(records),"paths",round(time.perf_counter()-started,2),flush=True)
    evaluations.sort(key=lambda r:-r['score']['gain_nats']);save(out/'candidates.json.gz',evaluations);save(out/'replays.json.gz',records);save(out/'comparisons.json',comparisons)
    # Explicit forbidden compression control is unnecessary: every link is
    # checked on actual alternatives. No arbitrary stripe intervention is run.
    save(out/'summary.json',dict(paths=len(ss),evaluations=len(evaluations),common_observations=len(common),successful_replays=sum(r['full_replay']['completed'] if 'completed' in r['full_replay'] else False for r in comparisons),R336_preserving_maps=sum(not r['violated_links'] and not r['duplicate_sites'] for r in comparisons),maker_preserving_maps=sum(not r['maker_violations'] for r in comparisons),best=[{k:v for k,v in r.items() if k not in ['motif','witnesses']} for r in evaluations[:8]],seconds=time.perf_counter()-started,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,policy='Scores exploratory, equal record weights and identical smoothing across candidates. Geographic guard excludes target and adjacent sections; leave-occurrence-out also reported. Exposed historical colors are not fresh blind validation. No candidate adopted.'))
    print('SEARCH',len(ss),'paths',len(evaluations),'exact-divisor fits, multiples13 included','common',len(common),'best',[(r['map'],r['family'],r['N'],r['L'],r['score']['gain_nats'],r['total_link_changes']) for r in evaluations[:5]],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
