"""Repeated-patch breaks, independent appearance audit, coherent patch alternatives.

No pattern-derived color becomes a truth label. Every proposed edit is a layer.
"""
import argparse,time,csv
from pathlib import Path
from PIL import Image,ImageOps
from scipy.spatial import cKDTree
from .common import *
from .explore import paths
STEPS=[(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)]

def appearance(obs,ids,blocks,c):
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo.astype(float)/255;variants=[]
    for radius in [8,12,16]:
        feats=[]
        for o in ids:
            x,y=np.rint(obs[o]['xy']).astype(int);p=rgb[y-radius:y+radius+1,x-radius:x+radius+1];yy,xx=np.indices(p.shape[:2]);px=p[(xx-radius)**2+(yy-radius)**2<=radius**2];feats.append(np.quantile(px,[.1,.3,.5,.7,.9],axis=0).ravel())
        feats=np.array(feats);pr=np.zeros((len(ids),3,3))
        for block in range(12):
            tr=np.flatnonzero(blocks!=block);te=np.flatnonzero(blocks==block);scale=np.maximum(np.percentile(feats[tr],75,axis=0)-np.percentile(feats[tr],25,axis=0),.05);dist=np.sum(((feats[te,None]-feats[None,tr])/scale)**2,axis=2);near=np.argsort(dist,axis=1)[:,:51]
            for j,kn in enumerate([15,31,51]):pr[te,j]=np.stack([(c[tr[near[:,:kn]]]==a).mean(1) for a in range(3)],axis=1)
        variants.append(pr)
    vv=np.stack(variants,axis=1).reshape(len(ids),9,3);result={}
    for i,o in enumerate(ids):
        win=int(vv[i].mean(0).argmax());x,y=np.rint(obs[o]['xy']).astype(int);p=rgb[y-12:y+13,x-12:x+13];r,gg,bb=p.transpose(2,0,1);v=p.max(2);dark=(v<.36)&(v-p.min(2)<.13)&(v>.012)
        result[o]=dict(suggestion=COLORS[win],stable=bool(np.all(vv[i].argmax(1)==win)),minimum_vote=float(vv[i,:,win].min()),mean_votes=vv[i].mean(0).tolist(),variants=vv[i].tolist(),native_context=dict(radius=12,red_pixels=int(((r>1.8*gg)&(r>2.5*bb)&(r>.16)).sum()),yellow_pixels=int(((gg>.35*r)&(gg>1.8*bb)&(r>.9*gg)&(r>.16)).sum()),dark_pixels=int(dark.sum()),maxV=float(v.max()),medianV=float(np.median(v))),policy='Photo quantiles at recorded support; votes use other geographic sections. Neither calibrated probabilities nor physical body centers; dark patches may contain seams/shadows.')
    return result

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=dataset();ix={o:i for i,o in enumerate(ids)};H=g['H'];occ={tuple(v):o for o,v in co.items()};quot={representative(v,H):o for o,v in co.items()};audit=appearance(obs,ids,b,c);spirals=read(artifact('spirals/spirals.json.gz'));periods=read(artifact('periods-selected/periods.json.gz'));membership=defaultdict(list)
    for p in spirals['segments']:
        for o in p['ids']:membership[o].append(p['id'])
    def copies(cell,exclude_blocks):
        result=[]
        for mul in range(-15,16):
            if mul==0:continue
            oid=occ.get(tuple(np.array(cell)+mul*np.array([16,16])))
            if oid and b[ix[oid]] not in exclude_blocks:result.append(dict(id=oid,xy=obs[oid]['xy'],ab=co[oid],color=obs[oid]['color'],section=int(b[ix[oid]]),translation=[mul*16,mul*16]))
        return result
    def context(o,z):
        # Parallel directions and complete visible neighborhoods, not highlight
        # center matching. Agreement is independently serialized per neighbor.
        rows=[];shift=np.array(co[z])-co[o]
        for d in STEPS:
            a=occ.get(tuple(np.array(co[o])+d));other=occ.get(tuple(np.array(co[z])+d))
            rows.append(dict(delta_ab=d,target_neighbor=a,example_neighbor=other,colors=[obs[a]['color'] if a else '?',obs[other]['color'] if other else '?'],same=bool(a and other and obs[a]['color']==obs[other]['color'])))
        return rows
    breaks=[];allpred=[]
    for i,o in enumerate(ids):
        examples=copies(co[o],{(b[i]-1)%12,int(b[i]),(b[i]+1)%12});counts=Counter(e['color'] for e in examples);winner,n=counts.most_common(1)[0] if counts else ('?',0);sections={e['section'] for e in examples if e['color']==winner};strong=n>=3 and len(sections)>=3 and n/max(len(examples),1)>=.8
        row=dict(id=o,xy=obs[o]['xy'],ab=co[o],indexA=int(ab[i]@[7,6]),indexB=int(ab[i]@[6,7]),original=obs[o]['color'],prediction=winner if strong else '?',plurality=winner,support=n,total=len(examples),supporting_sections=sorted(sections),strong=strong,examples=examples,disagreement=bool(winner!=obs[o]['color']))
        allpred.append(row)
        if not strong or winner==obs[o]['color']:continue
        a=audit[o];photo_support=a['suggestion']==winner and a['stable'] and a['minimum_vote']>=.55 and max(a['mean_votes'])>=.75
        same=[e for e in examples if e['color']==winner];comparisons=[]
        for e in same:
            ctx=context(o,e['id']);comparisons.append(dict(**e,context=ctx,matching_neighbor_colors=sum(r['same'] for r in ctx),comparable_neighbor_pairs=sum(bool(r['target_neighbor'] and r['example_neighbor']) for r in ctx)))
        comparisons.sort(key=lambda e:(-e['matching_neighbor_colors'],-e['comparable_neighbor_pairs']))
        neighbors=[dict(id=z,delta_ab=d,color=obs[z]['color']) for d in STEPS if (z:=occ.get(tuple(ab[i]+d)))]
        mechanism='likely recorded-color error' if photo_support else 'unresolved color / association / design-model break'
        breaks.append(dict(**row,kind='observed-color-rule-break',rank_score=float(n/max(len(examples),1)+.1*n+.1*max((e['matching_neighbor_colors'] for e in comparisons),default=0)+2*photo_support),proposed=dict(color=winner if photo_support else None,index=None,association=None,links=[]),appearance=a,classification=mechanism,photographic_support=bool(photo_support),segments=membership[o],neighbors=neighbors,comparisons=comparisons[:4],alternatives=['Recorded color is correct; repeated spatial rule has a genuine exception or a longer motif.','Wrong body association or coherent local row assignment; test patch and all boundary links.'],neighbor_equations_preserved=True,color_edit_changes_link_equations=0))
    # Coherent local translations; translate complete connected 1/2-hop patches,
    # preserving INTERNAL edges. Never recommend independent integer edits.
    edges=g['edges'];adj=defaultdict(set)
    for e in edges:adj[e['source']].add(e['target']);adj[e['target']].add(e['source'])
    mismatch={r['id'] for r in breaks};patches=[]
    for root in sorted(mismatch):
        patch={root}
        for _ in range(2):patch|={z for a in list(patch) for z in adj[a] if np.linalg.norm(np.array(obs[z]['xy'])-obs[root]['xy'])<100}
        if sum(o in mismatch for o in patch)<2:continue
        if any(patch==set(r['ids']) for r in patches):continue
        boundary=[e for e in edges if (e['source'] in patch)!=(e['target'] in patch)];internal=[e for e in edges if e['source'] in patch and e['target'] in patch];ranks=[]
        block=int(b[ix[root]]);tr=~np.isin(b,[(block-1)%12,block,(block+1)%12]);keys,_=spatial_keys(ab);th,ba,cc=fit_keys(keys,c,w,tr);prior={tuple((v-(v[0]//16)*np.array([16,16])).tolist()):th[keys[j]] for j,v in enumerate(ab)}
        def cost(d):
            total=0
            for o in sorted(patch):
                cell=np.array(co[o])+d;key=tuple(cell-(cell[0]//16)*np.array([16,16]));pr=prior.get(key,ba);total-=w[ix[o]]*np.log(pr[COLORS.index(obs[o]['color'])])
            return total
        baseline=cost(np.array([0,0]))
        for d in STEPS+[(1,1),(-1,-1),(2,0),(0,2)]:
            collisions=[o for o in sorted(patch) if (other:=quot.get(representative(np.array(co[o])+d,H))) and other not in patch]
            ranks.append(dict(delta_ab=d,likelihood_gain=baseline-cost(np.array(d)),internal_edges_preserved=len(internal),boundary_edges_violated=len(boundary),occupied_site_collisions=collisions,admissible=False))
        patches.append(dict(root=root,ids=sorted(patch),break_ids=sorted(patch&mismatch),boundary_links=boundary,alternatives=sorted(ranks,key=lambda r:-r['likelihood_gain'])))
    # Gaps inside the measured neighborhood, with native-cache evidence kept
    # separate from pure predictions. Unknown site color is never filled in viewer.
    groups=defaultdict(list)
    for key,kind in [('provisional_observations','provisional'),('predictions','prediction-only')]:
        for r in g[key]:
            if representative(r['cell'],H) not in quot:groups[representative(r['cell'],H)].append(dict(r,layer=kind))
    gaps=[]
    for cell,proposals in groups.items():
        neigh=[dict(id=z,delta_ab=d,color=obs[z]['color']) for d in STEPS if (z:=quot.get(representative(np.array(cell)+d,H)))]
        if len(neigh)<3:continue
        block=int(b[ix[neigh[0]['id']]]);examples=copies(cell,{(block-1)%12,block,(block+1)%12});counts=Counter(e['color'] for e in examples);winner,n=counts.most_common(1)[0] if counts else ('?',0)
        if n<3 or n/max(len(examples),1)<.8 or len({e['section'] for e in examples if e['color']==winner})<3:continue
        native=[p for p in proposals if p['layer']=='provisional'];matching=[p for p in native if p['color']==winner];xy=proposals[0].get('xy',proposals[0].get('prediction'))
        gaps.append(dict(id=f'GAP-{cell[0]}-{cell[1]}',kind='unobserved-working-site',ab=cell,xy=xy,original='?',prediction=winner,support=n,total=len(examples),examples=examples,neighbors=neigh,proposals=[dict(id=p['id'],xy=p.get('xy'),prediction=p.get('prediction'),color=p.get('color','?'),layer=p['layer'],reasons=p.get('reasons',[]),native_pixel_count=p.get('native',{}).get('pixel_count',p.get('native_pixel_count',0))) for p in proposals],classification='known unindexed observation candidate' if any(p['id'] in obs for p in native) else 'native provisional candidate matches repeated feature' if matching else 'competing-color native candidate' if native else 'no recorded native body; hidden or missed unresolved',rank_score=.2*n+len(neigh)*.1+bool(matching),proposed=dict(color=None,index=None,association=[p['id'] for p in matching],links=[]),photographic_support=False,alternatives=['Existing native proposal may be an adjacent body or seam; R332 rejection reasons remain.','Physical site may be occluded; no claim that a visible or physical bead is missing.']))
    # Every selected measured path endpoint has explicit continuation alternatives.
    endpoints=[]
    breakset={r['id'] for r in breaks};gapby={tuple(r['ab']):r['id'] for r in gaps}
    for p in spirals['segments']:
        for which,sgn in [('start',-1),('end',1)]:
            oid=p['ids'][0 if sgn<0 else -1];options=[]
            for step in [(sgn,0),(0,sgn)]:
                cell=np.array(co[oid])+step;other=quot.get(representative(cell,H));gap=gapby.get(representative(cell,H));linked=other in adj[oid] if other else False
                reason='measured same-palette continuation; path cover choice/branch' if other and obs[other]['color'] in p['palette'] and linked else 'observed competing palette; design boundary unless repeated rule conflicts' if other else 'unknown site; visibility/inventory unresolved'
                options.append(dict(delta_ab=step,id=other,ab=cell.tolist(),color=obs[other]['color'] if other else '?',actual_working_link=linked,break_id=other if other in breakset else gap,reason=reason))
            endpoints.append(dict(segment=p['id'],endpoint=which,id=oid,options=options))
    breaks.sort(key=lambda r:-r['rank_score']);gaps.sort(key=lambda r:-r['rank_score']);hypotheses={r['id']:r['proposed']['color'] for r in breaks if r['proposed']['color']};corrected=c.copy()
    for o,col in hypotheses.items():corrected[ix[o]]=COLORS.index(col)
    feedback=[]
    # No labels corrected in the evaluation reference. Hypothesis sites excluded
    # from targets; only training emission is changed by the reversible layer.
    targetmask=np.array([o not in hypotheses for o in ids]);keys,_=spatial_keys(ab)
    for fam,p,parent in [('A',104,None),('A',208,None),('A',208,104),('A',306,None),('B',207,None),('B',305,None)]:
        k=ab@([7,6] if fam=='A' else [6,7]);before=np.zeros((len(ids),3));after=np.zeros_like(before);base=np.zeros_like(before)
        for block in range(12):
            tr=b!=block;te=(b==block)&targetmask
            for cc,output in [(c,before),(corrected,after)]:
                th,ba,cnt=fit_keys(k%p,cc,w,tr)
                if parent:
                    par,_,_=fit_keys(k%parent,cc,w,tr);prior=par[np.arange(len(th))%parent];th=(cnt+prior)/(cnt.sum(1)[:,None]+1)
                output[te]=th[k[te]%p]
            base[te]=ba
        j=np.flatnonzero(targetmask);delta=np.log(after[j,c[j]]/before[j,c[j]])
        feedback.append(dict(family=fam,period=p,parent=parent,unchanged_targets=len(j),gain_from_hypothesis_training=float(np.average(delta,weights=w[j])),scope='Exploratory re-use; hypothesis colors never used as validation truth.'))
    beforepaths=sum(len(p['ids']) for p in spirals['segments']);cg=dict(g,observations=[dict(o,color=hypotheses.get(o['id'],o['color'])) for o in g['observations']]);afterpaths=[]
    for palette in [('black','red'),('black','yellow')]:
        ps=paths(cg,palette,0);afterpaths.append(dict(palette=palette,segments=len(ps),lengths=[p['length'] for p in ps],nodes=sum(p['length'] for p in ps)))
    # Second iteration uses frozen out-of-section rules and independent appearance.
    # Those inputs don't change after applying an unconfirmed layer: no new truth
    # to propagate. Stop instead of recursively converting motif agreement to labels.
    result=dict(breaks=breaks,gaps=gaps,all_predictions=allpred,appearance=audit,coherent_patches=patches,path_endpoints=endpoints,color_hypotheses=hypotheses,feedback=feedback,hypothesis_path_cover=afterpaths,iterations=[dict(iteration=0,observed_breaks=len(breaks),candidate_gaps=len(gaps)),dict(iteration=1,reversible_color_hypotheses=len(hypotheses),coherent_index_changes_admitted=0),dict(iteration=2,new_independently_supported_changes=0,stop='Frozen independent evidence unchanged; no self-confirming propagation.')],counts=dict(observed_significant_breaks=len(breaks),likely_color_errors=len(hypotheses),likely_index_errors=0,unresolved_observed_breaks=len(breaks)-len(hypotheses),gap_classification=dict(Counter(r['classification'] for r in gaps)),confirmed_missing_visible_observations=0,confirmed_physical_absences=0),seconds=time.perf_counter()-t)
    save(out/'diagnosis.json.gz',result);save(out/'summary.json',dict(counts=result['counts'],color_hypotheses=hypotheses,feedback=feedback,iterations=result['iterations'],seconds=result['seconds']))
    with (out/'ledger.csv').open('w',newline='') as f:
        fields=['id','kind','xy','ab','indexA','indexB','original','prediction','classification','photographic_support','rank_score'];wr=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');wr.writeheader();wr.writerows(breaks+gaps)
    print('DIAGNOSIS',result['counts'],hypotheses,'seconds',result['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
