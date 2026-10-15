"""Cached photograph sampling and discrete, many-to-one ownership hypotheses."""
import numpy as np
from scipy.spatial import cKDTree
from .common import *
from .geometry import Chain, FIELD_SIZE


def beam_assign(scene, rows, assignments, edges, width=12):
    """Beam over connected region graphs, with null and 1/6/7 index alternatives.

Multiple reflections and compatible material regions may share a physical owner.
Only measured color/valley cues penalize sharing. A beam is a conditional hypothesis,
not certified identity. Components factor exactly; pruning within one is approximate.
"""
    records={a['id']:a for a in assignments if a['kind']=='region'}
    sources={r['id']:r for r in rows};adj={k:set() for k in records};weights={}
    for e in edges:
        a,b=e['ids']
        if a in records and b in records:
            adj[a].add(b);adj[b].add(a);weights[tuple(sorted((a,b)))]=e['separation_weight']
    remaining=set(records);components=[]
    while remaining:
        queue=[min(remaining)];remaining.remove(queue[0]);component=[]
        while queue:
            a=queue.pop(0);component.append(a)
            for b in sorted(adj[a]&remaining):remaining.remove(b);queue.append(b)
        components.append(component)
    total=0.;chosen={};alternatives=[]
    for component in components:
        beams=[(0.,[])];seen=[]
        for key in component:
            r=records[key];opts={a['index']:a['fraction'] for a in r['alternatives']}
            if r['index'] is not None:
                for d in (-7,-6,-1,0,1,6,7):
                    k=r['index']+d
                    if scene.closed:k=int((k-scene.indices[0])%scene.n+scene.indices[0])
                    if scene.indices[0]<=k<=scene.indices[-1]:opts.setdefault(k,0.)
            options=[(None,.28)]+sorted(opts.items());new=[]
            for score,values in beams:
                for k,f in options:
                    penalty=0.
                    for previous,j in zip(seen,values):
                        if j is None or k is None or previous not in adj[key]:continue
                        if j==k:penalty+=weights[tuple(sorted((key,previous)))]
                        else:
                            predicted=scene.pc[k-scene.indices[0]]-scene.pc[j-scene.indices[0]]
                            measured=np.asarray(sources[key]['point'])-sources[previous]['point']
                            if predicted@measured<0:penalty+=.12
                    new.append((score+min(f,.9)/.9-penalty,values+[k]))
            beams=sorted(new,key=lambda a:-a[0])[:width];seen.append(key)
        total+=beams[0][0];chosen.update(zip(component,beams[0][1]))
        alternatives.append(dict(ids=component,hypotheses=[dict(score=float(s),indices=v) for s,v in beams[:3]]))
    return dict(score=float(total/max(1,len(records))),assignments=chosen,components=alternatives)

class Objective:
    def __init__(self,data,split='train',tier='fine',allow_reserved=False):
        if split=='reserved' and not allow_reserved:
            raise ValueError('Reserved outcomes require a sealed model')
        self.data=data;self.split=split;self.tier=tier
        self.rows=[r for r in data['rows'] if r['split']==split]
        groups=[];self.sizes=[]
        for r in self.rows:
            xy=pixels(r['pixels']);n=(3 if r['kind']=='patch' else 12) if tier=='coarse' else (10 if r['kind']=='patch' else 64)
            g=xy[np.linspace(0,len(xy)-1,min(n,len(xy))).astype(int)]
            groups.append(g);self.sizes.append(len(g))
        self.obs_xy=np.concatenate(groups) if groups else np.empty((0,2));self.bounds=np.r_[0,np.cumsum(self.sizes)]
        raw=np.load(EVIDENCE/'cues.npz');keep=raw['split']==split
        if tier=='coarse':keep&=np.all(raw['xy']%10==0,axis=1)
        self.cues={k:raw[k][keep] for k in ('xy','color','paper','lum','station','distance')}
        mapping=np.full(len(keep),-1,int);mapping[keep]=np.arange(keep.sum())
        if tier=='coarse':
            # Retain photographic 5px edges in coarse tier via deterministic subset;
            # otherwise a 10px grid has no original adjacent pairs.
            keep=raw['split']==split
            pp=raw['pairs'];good=keep[pp].all(1)&(np.arange(len(pp))%8==0)
            pairxy=raw['xy'][pp[good]].reshape(-1,2)
            self.edge_xy=pairxy;self.edge=raw['edge'][good];self.mid_lum=raw['mid_lum'][good]
            self.edge_color=raw['color'][pp[good]]
            self.pairs=np.arange(len(pairxy)).reshape(-1,2)
        else:
            pp=raw['pairs'];good=keep[pp].all(1)
            self.pairs=mapping[pp[good]];self.edge=raw['edge'][good];self.mid_lum=raw['mid_lum'][good]
            self.edge_color=self.cues['color'][self.pairs];self.edge_xy=np.empty((0,2))
        self.anchor=pixels(data['anchor']['measured_support'])[::8]
        self.xy=np.concatenate([self.obs_xy,self.cues['xy'],self.edge_xy,self.anchor])
        self.edges=[e for e in data['edges'] if e['split']==split]

    def assess(self,scene,discrete=True):
        trace=scene.trace(self.xy);o=trace['owner'];rows=[];assigned=[];fractions=[]
        for r,a,b in zip(self.rows,self.bounds[:-1],self.bounds[1:]):
            ids,counts=np.unique(o[a:b],return_counts=True)
            alternatives=sorted([dict(index=int(scene.indices[k]),fraction=float(v/(b-a))) for k,v in zip(ids,counts) if k>=0],key=lambda r:(-r['fraction'],r['index']))
            fraction=alternatives[0]['fraction'] if alternatives else 0.
            rival=alternatives[1]['fraction'] if len(alternatives)>1 else 0.
            index=alternatives[0]['index'] if fraction>=.3 else None
            rows.append(dict(id=r['id'],kind=r['kind'],index=index,containment=fraction,alternatives=alternatives,
                compatible=fraction>=.8 and fraction-rival>=.2,unmatched_fraction=float(np.mean(o[a:b]<0)),
                stratum=r['stratum'],station=r['station'],accepted=r['accepted'],reflection=r['reflection'],identity_verified=False))
            assigned.append(index);fractions.append(fraction)
        frac=np.array(fractions);region=np.array([r['kind']=='region' for r in rows]);patch=~region
        patchvals=[]
        owners=sorted(set(k for k,good in zip(assigned,patch) if good and k is not None))
        for k in owners:patchvals.append(np.mean([f for f,j,good in zip(frac,assigned,patch) if good and j==k]))
        patchvals.extend(f for f,k,good in zip(frac,assigned,patch) if good and k is None)
        patch_score=float(np.mean(patchvals)) if patchvals else 0.
        material=float(np.mean(np.minimum(frac[region],.9)/.9)) if region.any() else 0.
        graph=beam_assign(scene,self.rows,rows,self.edges) if discrete else dict(score=material,assignments={})
        go=o[len(self.obs_xy):len(self.obs_xy)+len(self.cues['xy'])];visible=go>=0
        paper=float(self.cues['paper'][visible].mean()) if visible.any() else 0.
        colored=self.cues['color']>0;coverage=float(visible[colored].mean()) if colored.any() else 0.
        count=np.zeros((scene.n,3));np.add.at(count,(go[visible],self.cues['color'][visible]),1)
        n=count[:,1:].sum(1);owned=n>=3
        conflict=float(np.mean(np.minimum(count[owned,1],count[owned,2])/n[owned])) if owned.any() else 0.
        if self.tier=='coarse':
            start=len(self.obs_xy)+len(self.cues['xy']);eo=o[start:start+len(self.edge_xy)]
        else:eo=go
        a,b=self.pairs.T;boundary=(eo[a]!=eo[b])&((eo[a]>=0)|(eo[b]>=0))
        continuous=(self.edge_color[:,0]>0)&(self.edge_color[:,0]==self.edge_color[:,1])&(self.mid_lum>.065)&(self.edge<.6)
        cut=float(np.sum(boundary&continuous)/max(1,continuous.sum()))
        edge=float(self.edge[boundary].mean()) if boundary.any() else 0.
        # One fixed bead-0 observation anchors the gauge in every score. Validation
        # metrics exclude anchor from their selection score to avoid pseudo-replication.
        anchor=float(np.mean(o[-len(self.anchor):]==np.flatnonzero(scene.indices==0)[0]))
        p=scene.p
        smooth=sum(float(np.mean(np.diff(np.r_[p[k],p[k][0]])**2))*w for k,w in [('local_phase',.04),('local_spacing',1.),('local_bend',.002)])
        reg=smooth+.001*np.mean(np.asarray(p['bend'])**2)+.2*np.mean(np.asarray(p['strain'])**2)
        score=.28*graph['score']+.10*patch_score+.12*coverage+.22*edge-.75*paper-.50*conflict-.50*cut-reg
        if self.split=='train':score+=.13*anchor-.8*max(0,.75-anchor)
        sections=[]
        for j in range(FIELD_SIZE):
            # Geographic diagnostics use observation position, not candidate successes.
            selected=[r for r in rows if int(r['station']/self.data['length']*FIELD_SIZE)%FIELD_SIZE==j]
            large=[r for r in selected if r['kind']=='region']
            score_j=np.mean([r['containment'] for r in large or selected]) if selected else None
            sections.append(dict(section=j,n=len(selected),regions=len(large),containment=float(score_j) if score_j is not None else None,
                failure=float(1-score_j) if score_j is not None else 0.))
        return dict(score=float(score),region_containment=float(frac[region].mean()) if region.any() else 0.,
            region_compatibility=sum(r['compatible'] for r in rows if r['kind']=='region'),patch_owner_balanced=patch_score,
            colored_coverage=coverage,paper=paper,color_conflict=conflict,bright_material_cuts=cut,edge_agreement=edge,
            anchor=anchor,regularization=float(reg),unknown_rays=int(trace['unknown'].sum()),rays=len(self.xy),
            assignments=rows,ownership=graph,sections=sections,
            strata={s:dict(n=sum(r['stratum']==s for r in rows),mean_containment=float(np.mean([r['containment'] for r in rows if r['stratum']==s])) if any(r['stratum']==s for r in rows) else None) for s in ('central','peripheral')})

def compact(metrics):
    return {k:v for k,v in metrics.items() if k not in ('assignments','ownership','sections')}


OriginalObjective = Objective


def balanced_material(rows,length):
    """Equal geographic mass; no large cluster of correlated patches can dominate."""
    values=[];sections=[]
    for j in range(FIELD_SIZE):
        region=[r['containment'] for r in rows if r['kind']=='region' and int(r['station']/length*FIELD_SIZE)%FIELD_SIZE==j]
        if region:
            # Every region has bounded weight; all regions retained, not pixel count.
            value=float(np.mean(region));values.append(value)
            sections.append(dict(section=j,n=len(region),mean=value,worst_quartile=float(np.mean(sorted(region)[:max(1,int(np.ceil(len(region)/4)))]))))
    if not values:return 0.,sections
    return .7*float(np.mean(values))+.3*float(np.mean(sorted(values)[:max(1,int(np.ceil(len(values)/4)))])),sections


class Objective(OriginalObjective):
    def __init__(self,*args,mode='balanced',**kwargs):
        super().__init__(*args,**kwargs);self.mode=mode

    def assess(self,scene,discrete=True):
        m=super().assess(scene,discrete);m['legacy_score']=m['score']
        material,sections=balanced_material(m['assignments'],self.data['length'])
        m['balanced_material']=material;m['material_sections']=sections;m['objective_mode']=self.mode
        if self.mode=='legacy':return m
        # Region extent is scored directly: a null beam choice must not hide loss.
        # Edge precision alone can reward arbitrary extra cuts; keep continuity.
        terms=dict(material=.48*material,ownership=.08*m['ownership']['score'],
            patches=.05*m['patch_owner_balanced'],coverage=.12*m['colored_coverage'],
            boundaries=.10*m['edge_agreement']-.65*m['bright_material_cuts'],
            paper=-.75*m['paper'],color=-.50*m['color_conflict'],regularity=-m['regularization'])
        if self.split=='train':terms['anchor']=.13*m['anchor']-.8*max(0,.75-m['anchor'])
        if self.mode=='no-patches':terms['patches']=0.
        if self.mode=='no-boundaries':terms['boundaries']=0.
        m['objective_terms']=terms;m['score']=float(sum(terms.values()))
        return m
