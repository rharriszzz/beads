"""Additive, cached-candidate and native-body lattice completion.

Baseline coordinates/links are immutable. No motif, physical model, winding
search or strong-highlight requirement is used. New measurements retain their
native pixels separately from geometric predictions and body-center inference.
"""
import argparse,time
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from .common import *

def pixels(runs):return np.array([(x,y) for y,a,z in runs for x in range(a,z+1)],int).reshape(-1,2)
def runs(points):
    output=[]
    if len(points):
        for y in sorted(set(points[:,1])):
            xx=sorted(set(points[points[:,1]==y,0]));a=z=xx[0]
            for x in xx[1:]:
                if x==z+1:z=x
                else:output.append([int(y),int(a),int(z)]);a=z=x
            output.append([int(y),int(a),int(z)])
    return output

class Completion:
    def __init__(self,g,co,H):
        self.g=g;self.original=set(co);self.co=dict(co);self.H=np.array(H);self.obs={o['id']:dict(o) for o in g['observations']};self.links={edgekey(e['source'],e['target']):dict(e,origin='baseline') for e in g['graph']['edges']}
        self.photo=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));self.rgb=self.photo.astype(np.float32)/255
        from photo2.r325.tracker import preprocess
        self.fg=preprocess(Image.fromarray(self.photo))['fg'].astype(np.float32)
        r,gg,b=self.rgb.transpose(2,0,1);v=self.rgb.max(2);chroma=v-self.rgb.min(2)
        self.masks={'red':(r>1.8*gg)&(r>2.5*b)&(r>.16),'yellow':(gg>.35*r)&(gg>1.8*b)&(r>.9*gg)&(r>.16),
            'black':(v<.36)&(chroma<.13)&(v>.012)}
        # Appearance is learned from recorded bodies, independently of their
        # lattice indices. Multiple extraction scales expose ambiguous colors.
        self.color_names=['red','yellow','black'];self.appearance={}
        for radius in [8,12,16]:
            features=np.array([self.feature(o['xy'],radius) for o in self.obs.values()]);scale=np.maximum(np.percentile(features,75,axis=0)-np.percentile(features,25,axis=0),.04)
            self.appearance[radius]=(cKDTree(features/scale),scale,np.array([self.color_names.index(o['color']) for o in self.obs.values()]))
        self.occupied={representative(v,H):o for o,v in co.items()};self.proposals=[];self.history=[];self.cache_votes=self.cached_assignments();self.measure_cache={};self.rebuild()
    def feature(self,xy,radius):
        x,y=np.rint(xy).astype(int);p=self.rgb[max(0,y-radius):y+radius+1,max(0,x-radius):x+radius+1]
        return np.quantile(p.reshape(-1,3),[.1,.3,.5,.7,.9],axis=0).ravel()
    def classify(self,point):
        votes=[]
        for radius,(tree,scale,labels) in self.appearance.items():
            distances,idx=tree.query(self.feature(point,radius)/scale,k=25);wt=1/np.maximum(distances,.3)
            votes.append(np.bincount(labels[idx],weights=wt,minlength=3)/wt.sum())
        values=np.array(votes);winner=int(values.mean(0).argmax())
        return self.color_names[winner],dict(probabilities=values.mean(0).tolist(),scale_votes=values.tolist(),stable=bool(np.all(values.argmax(1)==winner)),minimum_vote=float(values[:,winner].min()))
    def rebuild(self):
        self.names=sorted(self.co);self.xy=np.array([self.obs[o]['xy'] for o in self.names]);self.ab=np.array([self.co[o] for o in self.names]);self.tree=cKDTree(self.xy)
        self.allnames=sorted(self.obs);self.allxy=np.array([self.obs[o]['xy'] for o in self.allnames]);self.alltree=cKDTree(self.allxy)
    def cached_assignments(self):
        bank=read(ROOT/'photo2/r327/results/graph.json.gz');votes=defaultdict(lambda:defaultdict(list))
        for wi,window in enumerate(bank['windows']):
            for hi,h in enumerate(window['hypotheses']):
                aa=h['assignments'];shared=sorted(self.co.keys()&aa.keys())
                if len(shared)<5:continue
                root=np.array(self.co[shared[0]]);offsets=[]
                for o in shared:
                    v=np.array(self.co[o]);v-=round(float((v-root)@self.H/(self.H@self.H)))*self.H
                    offsets.append(tuple(v-np.array(aa[o]['ab'])))
                offset,n=Counter(offsets).most_common(1)[0]
                if n<len(shared)*.9:continue
                for o in aa.keys()-self.co.keys():
                    cell=tuple(np.array(aa[o]['ab'])+offset);votes[o][representative(cell,self.H)].append(dict(window=wi,hypothesis=hi,aligned=n,shared=len(shared),residual=aa[o]['residual_px']))
        return {o:[dict(cell=cell,witnesses=rows,windows=len({x['window'] for x in rows})) for cell,rows in vv.items()] for o,vv in votes.items()}
    def model(self,point,exclude=None,colored=False):
        dist,idx=self.tree.query(point,k=min(32,len(self.names)));use=[i for d,i in zip(np.atleast_1d(dist),np.atleast_1d(idx)) if d<135 and self.names[i]!=exclude and (not colored or self.obs[self.names[i]]['color']!='black')]
        if len(use)<6:return None
        root=self.ab[use[0]];ab=self.ab[use].copy();delta=ab-root;ab-=np.rint(delta@self.H/(self.H@self.H)).astype(int)[:,None]*self.H
        keep=np.linalg.norm(ab-root,axis=1)<7.5;use=np.array(use)[keep][:20];ab=ab[keep][:20]
        if len(use)<6:return None
        u=(ab-root)/3.;X=np.c_[u[:,0]*0+1,u,u[:,0]**2,u[:,0]*u[:,1],u[:,1]**2];xy=self.xy[use];wt=np.exp(-np.sum((xy-point)**2,axis=1)/10000)
        if np.linalg.matrix_rank(X[:,:3])<3:return None
        for iteration in range(3):
            coef=np.linalg.lstsq(X.T@(wt[:,None]*X)+np.diag([0,0,0,.35,.35,.35]),X.T@(wt[:,None]*xy),rcond=None)[0]
            residual=np.linalg.norm(X@coef-xy,axis=1);wt*=np.minimum(1,6/np.maximum(residual,1e-6))
        return dict(root=root,coef=coef,anchors=[self.names[i] for i in use],rms=float(np.sqrt(np.average(residual**2,weights=wt))))
    @staticmethod
    def predict(model,cell):
        u=(np.array(cell)-model['root'])/3.;return np.array([1,*u,u[0]**2,u[0]*u[1],u[1]**2])@model['coef']
    def infer(self,point,exclude=None):
        model=self.model(point,exclude)
        if model is None:return None
        grid=np.array([model['root']+[a,b] for a in range(-5,6) for b in range(-5,6)]);pred=np.array([self.predict(model,c) for c in grid]);err=np.linalg.norm(pred-point,axis=1);order=err.argsort();j=order[0]
        return dict(cell=tuple(grid[j]),prediction=pred[j],error=float(err[j]),margin=float(err[order[1]]-err[j]),model=model)
    def neighbors(self,cell):
        found=[]
        for d in DIRECTIONS:
            o=self.occupied.get(representative(np.array(cell)+d,self.H))
            if o:found.append((o,d))
        return found
    def evidence(self,point,color=None):
        x,y=np.rint(point).astype(int);key=(int(x),int(y),color)
        if key in self.measure_cache:return self.measure_cache[key]
        radius=12;x0=max(0,x-radius);y0=max(0,y-radius);x1=min(self.photo.shape[1],x+radius+1);y1=min(self.photo.shape[0],y+radius+1)
        yy,xx=np.mgrid[y0:y1,x0:x1];disk=(xx-x)**2+(yy-y)**2<=radius**2;result={}
        for col in ['red','yellow','black']:
            mask=self.masks[col][y0:y1,x0:x1]&disk;lab,n=ndi.label(mask,np.ones((3,3)));size=np.bincount(lab.ravel());size[0]=0
            if n:
                label=int(size.argmax());pts=np.c_[xx[lab==label],yy[lab==label]]
            else:pts=np.empty((0,2),int)
            result[col]=dict(n=len(pts),pixels=pts,centroid=pts.mean(0).tolist() if len(pts) else None)
        colored=max(['red','yellow'],key=lambda c:result[c]['n']);cn=result[colored]['n'];bn=result['black']['n']
        # A color region is not borrowed from an adjacent site: its centroid must
        # remain near the inspected location, with enough native body evidence.
        guess,appearance=self.classify(point)
        if color is not None:guess=color
        chosen=result[guess];fg=float(self.fg[y0:y1,x0:x1][disk].mean());span=np.ptp(chosen['pixels'],axis=0).tolist() if chosen['n'] else [0,0]
        patch=self.rgb[y0:y1,x0:x1];v=patch.max(2);ch=patch.max(2)-patch.min(2)
        # Visible boundary/texture signal in eight sectors; not a silhouette fit.
        grad=np.hypot(ndi.sobel(v,0),ndi.sobel(v,1))/8;rr=(xx-x)**2+(yy-y)**2;ann=(rr>=64)&(rr<=144);sectors=((np.arctan2(yy-y,xx-x)+np.pi)*4/np.pi).astype(int)%8
        boundaries=[float(np.percentile(grad[ann&(sectors==k)],75)) if np.any(ann&(sectors==k)) else 0 for k in range(8)]
        record=dict(color=guess,pixel_count=chosen['n'],pixels_xy=chosen['pixels'],centroid=chosen['centroid'],span=span,
            foreground_fraction=fg,dark_pixels=bn,colored_pixels=cn,black_fraction=float(self.masks['black'][y0:y1,x0:x1][disk].mean()),
            boundary_sectors=sum(v>.045 for v in boundaries),sector_gradient=boundaries,
            peak_value=float(v[disk].max()),median_value=float(np.median(v[disk])),
            appearance=appearance,
            location_kind='native material support; geometric prediction is separate; no measured physical center')
        self.measure_cache[key]=record;return record
    def link_check(self,a,pa,z,pz):
        p,q=np.array(pa),np.array(pz);v=q-p;dist=float(v@v);near=[]
        if dist<1:return dict(allowed=False,foreground_fraction=0,intervening_observations=[])
        for j in self.alltree.query_ball_point((p+q)/2,np.sqrt(dist)/2+7):
            o=self.allnames[j]
            if o in [a,z]:continue
            delta=self.allxy[j]-p;t=float(delta@v/dist)
            if .2<t<.8 and np.linalg.norm(delta-t*v)<7:near.append(o)
        pts=np.linspace(p,q,31);fg=float(ndi.map_coordinates(self.fg,[pts[:,1],pts[:,0]],order=1,mode='nearest').mean())
        return dict(allowed=not near and fg>.95,foreground_fraction=fg,intervening_observations=near)
    def assess(self,candidate,known=False,body_only=False):
        oid=candidate['id'];point=np.array(candidate['xy']);source_point=point.copy();relocalized=False
        if not known and not body_only:
            material=self.evidence(point,'black' if candidate.get('source_kind')=='cached-black' else None);pp=material['pixels_xy']
            if len(pp)>=25 and float(np.min(np.linalg.norm(pp-point,axis=1)))>1.5:
                centroid=pp.mean(0);representative_point=pp[np.argmin(np.linalg.norm(pp-centroid,axis=1))]
                if np.linalg.norm(representative_point-point)<=8:point=representative_point.astype(float);relocalized=True
        inference=self.infer(point,oid if known else None)
        if inference is None:return dict(id=oid,status='unresolved',reason='insufficient local anchors',xy=point.tolist())
        cell=inference['cell'];owner=self.occupied.get(representative(cell,self.H));ev=self.evidence(point,candidate.get('color') if known else None);color=candidate.get('color',ev['color']) if known else ev['color']
        if not known and candidate.get('source_kind')=='cached-black':color='black';ev=self.evidence(point,'black')
        neighbors=self.neighbors(cell);directions={tuple(d) if tuple(d) in STEPS else tuple(-np.array(d)) for _,d in neighbors};incident=[]
        for z,d in neighbors:incident.append(dict(source=oid,target=z,delta_ab=list(d),**self.link_check(oid,point,z,self.obs[z]['xy'])))
        good=[e for e in incident if e['allowed']];families={tuple(e['delta_ab']) if tuple(e['delta_ab']) in STEPS else tuple(-np.array(e['delta_ab'])) for e in good}
        triangles=sum(edgekey(a['target'],z['target']) in self.links for j,a in enumerate(good) for z in good[j+1:])
        competing=self.cache_votes.get(oid,[]);matching=[r for r in competing if tuple(r['cell'])==representative(cell,self.H)];cache_windows=max([r['windows'] for r in matching],default=0)
        color_model=self.model(point,oid if known else None,colored=True);color_prediction=self.predict(color_model,cell) if color_model else None
        spread=float(np.linalg.norm(color_prediction-inference['prediction'])) if color_model else None
        reasons=[]
        if owner and owner!=oid:reasons.append('occupied lattice site; possible duplicate or wrong association')
        limit=8 if color=='black' else 6.5
        if inference['error']>limit:reasons.append('native support too far from local prediction')
        if inference['margin']<5:reasons.append('competing lattice site too close')
        if inference['model']['rms']>8:reasons.append('local fit unstable')
        if len(good)<2 or len(families)<2:reasons.append('fewer than two image-supported directions')
        if triangles<1:reasons.append('no supported shared-neighbor triangle')
        if ev['pixel_count']<(35 if color=='black' else 25) or min(ev['span'])<4:reasons.append('insufficient separate native material')
        if ev['foreground_fraction']<.8:reasons.append('material near background boundary')
        if spread is not None and spread>8:reasons.append('colored-only/all-support predictions disagree')
        nearest_dist,nearidx=self.alltree.query(point)
        if not known and nearest_dist<13:reasons.append('close recorded support; possible duplicate')
        if not known and ev['centroid'] is not None and np.linalg.norm(np.array(ev['centroid'])-point)>8:reasons.append('native component displaced toward neighbor')
        if not known and (not ev['appearance']['stable'] or ev['appearance']['minimum_vote']<.6):reasons.append('color appearance not stable across scales')
        if not known:
            # An addition must not invalidate an original native link corridor.
            # A genuine new body there would require reconsidering that old edge,
            # which this additive pass explicitly defers rather than hiding.
            blocking=[]
            for edge in self.links.values():
                if edge.get('origin')!='baseline':continue
                p=np.array(self.obs[edge['source']]['xy']);q=np.array(self.obs[edge['target']]['xy']);v=q-p;t=float((point-p)@v/(v@v))
                if .2<t<.8 and np.linalg.norm(point-p-t*v)<7:blocking.append([edge['source'],edge['target']])
            if blocking:reasons.append('would intervene in an existing working link')
        else:blocking=[]
        status='accepted' if not reasons else 'unresolved'
        if body_only and status=='accepted':
            # No isolated reflection required. More demanding geometry and actual
            # boundary sectors protect dark cast-shadow/occlusion predictions.
            goodsteps={tuple(e['delta_ab']) for e in good};opposed=any(tuple(-np.array(d)) in goodsteps for d in goodsteps)
            body_geometry=len(good)>=3 and len(families)>=2 and (opposed or ev['boundary_sectors']>=5)
            body_pixels=ev['boundary_sectors']>=3 and ev['black_fraction']>=.35 and ev['foreground_fraction']>=.95
            if color=='black' and not(body_geometry and body_pixels):status='provisional'
        if reasons and not owner and inference['error']<11 and len(neighbors)>=2 and ev['pixel_count']>=25 and ev['foreground_fraction']>.65:status='provisional'
        return dict(id=oid,xy=point.tolist(),color=color,status=status,reasons=reasons,cell=list(cell),prediction=inference['prediction'].tolist(),
            error=inference['error'],site_margin=inference['margin'],anchor_ids=inference['model']['anchors'],fit_rms=inference['model']['rms'],
            colored_anchor_ids=color_model['anchors'] if color_model else [],colored_prediction=color_prediction.tolist() if color_model else None,
            prediction_spread=spread,neighbors=[dict(id=o,delta=d) for o,d in neighbors],incident_links=incident,triangles=triangles,
            cache_windows=cache_windows,blocked_baseline_links=blocking,native=dict(ev,pixels_xy=ev['pixels_xy'].tolist()),source=candidate.get('source'),
            source_kind=candidate.get('source_kind','known'),source_id=candidate.get('source_id',oid),body_only=body_only,known=known,
            cached_support_xy=source_point.tolist() if not known and not body_only else None,relocalized_to_native_material=relocalized)
    def accept(self,record,iteration):
        o=record['id'];self.co[o]=tuple(record['cell']);self.occupied[representative(record['cell'],self.H)]=o
        if o not in self.obs:
            self.obs[o]=dict(id=o,xy=record['xy'],color=record['color'],kind='native-dark-body' if record['body_only'] and record['color']=='black' else 'recovered native material support',
                location_kind=record['native']['location_kind'],source=record['source'],source_id=record['source_id'],r332_status='accepted',r332_iteration=iteration)
        for e in record['incident_links']:
            if not e['allowed']:continue
            d=tuple(e['delta_ab']);a,z=e['source'],e['target']
            if d not in STEPS:a,z=z,a;d=tuple(-np.array(d))
            self.links[edgekey(a,z)]=dict(source=a,target=z,delta_ab=list(d),family=FAMILY[d],origin='R332',status='accepted working addition',
                foreground_fraction=e['foreground_fraction'],intervening_observations=e['intervening_observations'],iteration=iteration,
                photographic_evidence=record['id'],admission='two image-supported families plus shared-neighbor triangle; no window-count gate')
    def pool(self):
        pool=[];catalog=read(ROOT/'photo2/review/r275/inventory.json');old=set(self.obs)
        for row in catalog['locations']:
            if row['id'] not in old and row.get('bright_patch',{}).get('centroid'):
                pool.append(dict(id='REC275-'+row['id'],xy=row['bright_patch']['centroid'],color=row['color'],source_kind='cached-black' if row['color']=='black' else 'cached-colored',source_id=row['id'],source='photo2/review/r275/inventory.json'))
        represented=set()
        for threshold in [12,6]:
            source=f'photo2/review/r266/straight-0-selected{threshold}/regions.json.gz';records=read(ROOT/source)['regions']
            for r in records:
                if r['id'] in represented:continue
                represented.add(r['id']);xy=r['bright_patch']['patch_centroid'];pool.append(dict(id='REC266-'+r['id'],xy=xy,source_kind='cached-support',source_id=r['id'],source=source,
                    source_pixel_count=r['pixel_count'],source_support=r['pixel_runs']))
        for r in read(ROOT/'photo2/review/r275/band-edge-candidates.json'):
            pool.append(dict(id='EDGE275-'+r['id'],xy=[r['point']['x'],r['point']['y']],color=r['color'],source_kind='cached-black' if r['color']=='black' else 'cached-colored',source_id=r['id'],source='photo2/review/r275/band-edge-candidates.json'))
        # Deterministic location-level screening only; accepted measurements and
        # all aliases remain in the proposal ledger, never silently merged.
        return pool
    def empty_sites(self):
        sites={}
        for o,ab in self.co.items():
            for d in DIRECTIONS:
                v=tuple(np.array(ab)+d);key=representative(v,self.H)
                if key not in self.occupied:sites.setdefault(key,v)
        return [v for v in sites.values() if len(self.neighbors(v))>=2]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--passes',type=int,default=3);ap.add_argument('--budget',type=float,default=180);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();g,co,H=baseline();engine=Completion(g,co,H);pool=engine.pool();save(out/'candidate-pool.json.gz',pool);accepted=[];allproposals=[];calibration=[]
    # Retrospective held-observation checks use every eighth baseline observation,
    # not new labels. They calibrate coordinate association, not color truth.
    for o in sorted(co)[::8]:
        inferred=engine.infer(np.array(engine.obs[o]['xy']),o)
        if inferred:calibration.append(dict(id=o,color=engine.obs[o]['color'],correct=representative(inferred['cell'],H)==representative(co[o],H),error=inferred['error'],margin=inferred['margin']))
    known=[dict(o,source_kind='known') for o in g['observations'] if o['id'] not in co];remaining=known+pool;history=[]
    for iteration in range(args.passes):
        began=time.perf_counter();batch=[]
        for candidate in remaining:
            if candidate['id'] in engine.co:continue
            result=engine.assess(candidate,candidate['source_kind']=='known');result['iteration']=iteration;batch.append(result)
        # Highest support first; each acceptance rechecks site occupancy and
        # duplicate distance, without changing any established coordinates.
        added=[]
        for record in sorted(batch,key=lambda r:(r['status']!='accepted',-r.get('triangles',0),r.get('error',999),r['id'])):
            if record['status']!='accepted':continue
            if representative(record['cell'],H) in engine.occupied:record['status']='rejected duplicate';record['reasons'].append('site occupied by earlier stronger candidate');continue
            if not record['known'] and min(np.linalg.norm(np.array(record['xy'])-np.array(engine.obs[o]['xy'])) for o in engine.obs)<13:record['status']='rejected duplicate';record['reasons'].append('stronger nearby observation accepted first');continue
            engine.accept(record,iteration);added.append(record);accepted.append(record)
        engine.rebuild();allproposals.extend(batch)
        # Search only vacancies predicted by multiple existing native neighbors.
        body=[]
        for cell in engine.empty_sites():
            neighbors=engine.neighbors(cell);point=np.mean([engine.obs[o]['xy'] for o,d in neighbors],axis=0);model=engine.model(point)
            if not model:continue
            target=np.array(cell);target-=round(float((target-model['root'])@engine.H/(engine.H@engine.H)))*engine.H
            prediction=engine.predict(model,target)
            if np.any(prediction<15) or prediction[0]>=engine.photo.shape[1]-15 or prediction[1]>=engine.photo.shape[0]-15:continue
            if engine.alltree.query(prediction)[0]<14:continue
            ev=engine.evidence(prediction);color=ev['color'];pixels0=ev['pixels_xy']
            if len(pixels0)<25:continue
            # Color centroid is observed pigment. A dark body's core centroid is
            # likewise measured material, never claimed to be its physical center.
            point=np.array(ev['centroid']);key=representative(target,H);oid=f'R332-{color[0].upper()}-{key[0]:04d}-{key[1]:04d}'
            cand=dict(id=oid,xy=point.tolist(),color=color,source='original RGB, multiply predicted vacant cell',source_kind='new-native-body',source_id=oid)
            record=engine.assess(cand,body_only=True);record['iteration']=iteration;record['initial_prediction']=prediction.tolist();record['initial_cell']=target.tolist()
            if record.get('cell') and representative(record['cell'],H)!=key:record['status']='unresolved';record['reasons'].append('native component associates with a different cell')
            if record['status']=='accepted' and key not in engine.occupied:
                if min(np.linalg.norm(np.array(record['xy'])-np.array(engine.obs[o]['xy'])) for o in engine.obs)>=13:
                    engine.accept(record,iteration);accepted.append(record);added.append(record)
            body.append(record)
        allproposals.extend(body);engine.rebuild()
        history.append(dict(iteration=iteration,added=len(added),newly_indexed_known=sum(r['known'] for r in added),colors=dict(Counter(r['color'] for r in added)),indexed=len(engine.co),links=len(engine.links),seconds=time.perf_counter()-began,total_seconds=time.perf_counter()-start))
        print(history[-1],flush=True)
        if not added or time.perf_counter()-start>args.budget:break
    # Reconsider the six existing-coordinate gaps using exactly the native gates.
    link_candidates=[]
    for a,ab in list(engine.co.items()):
        for d in STEPS:
            z=engine.occupied.get(representative(np.array(ab)+d,H))
            if not z or edgekey(a,z) in engine.links:continue
            ck=engine.link_check(a,engine.obs[a]['xy'],z,engine.obs[z]['xy']);row=dict(source=a,target=z,delta_ab=d,family=FAMILY[d],origin='R332',**ck)
            row['status']='accepted working addition' if ck['allowed'] else 'blocked or ambiguous';link_candidates.append(row)
            if ck['allowed']:engine.links[edgekey(a,z)]=dict(row,admission='original native foreground/intervening-observation gates; existing coordinate relation')
    # Keep latest nonaccepted native proposals visible, not only successful ones.
    latest={r['id']:r for r in allproposals};provisional=[r for o,r in latest.items() if o not in engine.co and r['status']=='provisional'];unresolved=[r for o,r in latest.items() if o not in engine.co and r['status'] not in ['accepted','provisional']]
    # Distinct provisional candidates can claim the same predicted site; retain
    # as alternatives with an explicit shared-group identifier, never occupancy.
    accepted_ids={r['id'] for r in accepted};addobs=[engine.obs[o] for o in sorted(set(engine.obs)-{o['id'] for o in g['observations']})]
    result=dict(schema='r332-additive-native-lattice-v1',H=list(H),reference='C-1302-0316',baseline_commit=BASE,
        observations=list(engine.obs.values()),coordinates=[dict(id=o,ab=v) for o,v in sorted(engine.co.items())],edges=list(engine.links.values()),
        accepted_additions=accepted,provisional_observations=provisional,remaining_candidates=unresolved,link_candidates=link_candidates,
        history=history,calibration=calibration,seconds=time.perf_counter()-start,
        summary=dict(baseline_recorded=len(g['observations']),recorded_accepted=len(engine.obs),indexed=len(engine.co),
            newly_indexed_known=sum(r['known'] for r in accepted),newly_associated_cached= sum(not r['known'] and not r['body_only'] for r in accepted),
            newly_measured_native=sum(r['body_only'] for r in accepted),new_colors=dict(Counter(r['color'] for r in accepted if not r['known'])),
            links=len(engine.links),families=dict(Counter(e['family'] for e in engine.links.values())),
            unindexed=len(engine.obs)-len(engine.co),provisional=len(provisional),unresolved_candidates=len(unresolved),
            new_links_existing=sum(e['origin']=='R332' and e['source'] not in accepted_ids and e['target'] not in accepted_ids for e in engine.links.values()),
            new_links_total=sum(e['origin']=='R332' for e in engine.links.values())),
        policy='All original observations/coordinates/links preserved. New working additions are native-supported conditional assignments, not independently confirmed physical identities. Provisional candidates never propagate. No color motif/physical model or count inference.')
    save(out/'graph.json.gz',result);save(out/'proposal-ledger.json.gz',allproposals);save(out/'summary.json',result['summary']);print('FINAL',result['summary'],flush=True)

if __name__=='__main__':main()
