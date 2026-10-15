"""Bounded training-only alternating visible ownership and physical geometry search."""
import argparse,time,datetime
from copy import deepcopy
import numpy as np
from .common import *
from .geometry import Chain,extend,R

class Objective:
    def __init__(self,split='train',window=None,version=1):
        self.data=read(EVIDENCE/'inputs.json.gz');self.inputs=self.data['r294'];self.version=version;self.calls=0;self.history=[]
        self.rows=[r for r in self.data['rows'] if r['split']==split and (window is None or window[0]<=r['along_px']<=window[1])]
        groups=[];self.sizes=[]
        for r in self.rows:
            xy=pixels(r['pixels']);n=8 if r['kind']=='patch' else 48
            g=xy[np.linspace(0,len(xy)-1,min(n,len(xy))).astype(int)];groups.append(g);self.sizes.append(len(g))
        self.obs_xy=np.concatenate(groups) if groups else np.empty((0,2));self.bounds=np.r_[0,np.cumsum(self.sizes)]
        raw=np.load(EVIDENCE/'photographic-cues.npz');keep=raw['split']==split
        if window is not None:keep&=(raw['station']>=window[0])&(raw['station']<=window[1])
        self.cues={k:raw[k][keep] for k in ('xy','color','paper','lum')};mapping=np.full(len(keep),-1,int);mapping[keep]=np.arange(keep.sum())
        pp=raw['pairs'];good=keep[pp].all(1);self.pairs=mapping[pp[good]];self.edge=raw['edge'][good];self.mid_lum=raw['mid_lum'][good]
        self.anchor=pixels(self.inputs['anchor']['measured_support'])[::8]
        self.xy=np.concatenate([self.obs_xy,self.cues['xy'],self.anchor])

    def assess(self,p,physical=True,details=False):
        self.calls+=1;s=Chain(p,self.inputs);cert=s.certify(iterations=60,witnesses=False)
        # Every proposal is audited before photographic scoring. Failed plane tests
        # remain unresolved, not mislabeled collisions. Diagnostic unresolved candidates
        # are retained separately and never accepted as the certified primary.
        if physical and not cert['certified']:
            return dict(score=-10.,feasible=False,contact=cert)
        d=s.trace(self.xy);o=d['owner'];hist=[];assign=[];frac=[]
        for a,b in zip(self.bounds[:-1],self.bounds[1:]):
            counts=np.bincount(o[a:b][o[a:b]>=0],minlength=s.n)/(b-a);hist.append(counts)
            j=int(counts.argmax());assign.append(j if counts[j]>=.3 else -1);frac.append(float(counts[j]))
        assign=np.array(assign);frac=np.array(frac);regions=np.array([r['kind']=='region' for r in self.rows]);patch=~regions
        # Cap correlated highlight leverage by current physical owner. Keep their
        # native measurements independent in outputs; this is only objective weighting.
        patch_values=[]
        for j in set(assign[patch]):
            vals=frac[patch&(assign==j)];patch_values.extend(vals.tolist() if j<0 else [float(vals.mean())])
        patch_score=float(np.mean(patch_values)) if patch_values else 0.
        material=float(np.mean(frac[regions])) if regions.any() else 0.
        anchor=float(np.mean(o[-len(self.anchor):]==np.flatnonzero(s.indices==0)[0]))
        go=o[len(self.obs_xy):len(self.obs_xy)+len(self.cues['xy'])];visible=go>=0
        paper=float(np.sum(self.cues['paper']&visible)/max(1,visible.sum()))
        colored=(self.cues['color']>0);coverage=float(np.mean(visible[colored])) if colored.any() else 0.
        # Infer each owner's observed material locally, with no sequence/pattern prior.
        count=np.zeros((s.n,3))
        np.add.at(count,(go[visible],self.cues['color'][visible]),1)
        colored_count=count[:,1:].sum(1);owned=colored_count>=3
        conflict=float(np.mean(np.minimum(count[owned,1],count[owned,2])/colored_count[owned])) if owned.any() else 0.
        a,b=self.pairs.T;boundary=(go[a]!=go[b])&((go[a]>=0)|(go[b]>=0))
        # Bright same-material continuity is affirmative evidence against a modeled
        # cut; dark pixels alone never assert background or a missing bead.
        continuous=(self.cues['color'][a]>0)&(self.cues['color'][a]==self.cues['color'][b])&(self.mid_lum>.065)&(self.edge<.6)
        cut=float(np.sum(boundary&continuous)/max(1,continuous.sum()))
        edge_agreement=float(np.mean(self.edge[boundary])) if boundary.any() else 0.
        incompatible=float(np.mean(self.cues['paper'][visible])) if visible.any() else 0.
        reg=.001*np.mean(np.array(p['bend'])**2)+.2*np.mean(np.array(p['strain'])**2)+.006*np.mean(np.array(p.get('phase_knots',[0]*5))**2)
        score=.42*material+.12*patch_score+.13*anchor+.10*coverage+.13*edge_agreement-.6*paper-.30*conflict-.30*cut-reg
        if self.version==2:
            # Stage 2 balances robust region fitting with photometric ownership;
            # no single dubious automatic support can dictate an arbitrary lattice.
            robust=float(np.mean(np.minimum(frac[regions],.9)/.9)) if regions.any() else 0.
            score=.28*robust+.10*patch_score+.13*anchor+.12*coverage+.22*edge_agreement-.75*paper-.50*conflict-.50*cut-reg
        if anchor<.75:score-=.8*(.75-anchor)
        out=dict(score=float(score),feasible=cert['certified'],contact=cert,region_containment=material,patch_owner_balanced=patch_score,anchor=anchor,
            colored_coverage=coverage,paper=paper,color_conflict=conflict,bright_material_cuts=cut,edge_agreement=edge_agreement,regularization=reg,unknown_rays=int(d['unknown'].sum()))
        if details:out['assignments']=[dict(id=r['id'],kind=r['kind'],index=int(s.indices[j]) if j>=0 else None,containment=f,alternatives=[dict(index=int(s.indices[k]),fraction=float(h[k])) for k in np.argsort(h)[-4:][::-1] if h[k]>0]) for r,j,f,h in zip(self.rows,assign,frac,hist)]
        return out

def valid(p):
    return (6.6<=p['scale']<=10.5 and 1.02<=p['pitch']<=1.65 and 48<=p['elevation']<=88 and abs(p['phase'])<=1.8 and abs(p['s0'])<=18
        and 1.6<=p['radius']<=2.12 and .72<=p['axial']<=1.18 and 6.35<=p['turn']<=6.65 and 3.7<=p['minor']<=4.3
        and abs(p['yaw'])<=22 and 0<=p['perspective']<=.0025 and max(abs(np.array(p['strain'])))<=.12 and max(abs(np.array(p['bend'])))<=8 and max(abs(np.array(p['phase_knots'])))<=.5)

def perturb(p,key,delta):
    q=deepcopy(p)
    if ':' in key:
        key,j=key.split(':');q[key][int(j)]+=delta
    else:q[key]+=delta
    return q

def refine(obj,p,keys,steps=(1.,.5),rounds=1):
    p=extend(p);start=obj.assess(p);best=start;history=[];trials=[]
    for step in steps:
        for iteration in range(rounds):
            changed=False
            for key,delta in keys:
                options=[]
                for sign in (-1,1):
                    q=perturb(p,key,sign*step*delta)
                    if valid(q):
                        m=obj.assess(q);trials.append(dict(parameters=q,metrics=m));options.append((m,q))
                if options:
                    m,q=max(options,key=lambda z:z[0]['score'])
                    if m['score']>best['score']+1e-9:p=q;best=m;changed=True
            history.append(dict(step=step,iteration=iteration,parameters=deepcopy(p),metrics=best))
            if not changed:break
    return dict(parameters=p,train=obj.assess(p,details=True),initial=start,history=history,trials=trials)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['screen','local','global','revision']);args=parser.parse_args();stage=args.stage
    data=read(EVIDENCE/'inputs.json.gz');base=extend(read(ROOT/'photo2/r294/results/revised.json')['selected']['parameters'])
    obj=Objective(window=(50,290) if stage in ('screen','local') else None,version=2 if stage=='revision' else 1)
    if stage=='screen':
        candidates=[]
        # Controlled factors: fixed camera/shape, paired radius/spacing, thickness,
        # progression, camera elevation; both hands and phase basins get equal grids.
        shapes=[('intended',R,1.,1.26),('legacy',2.1109157489,1.,1.50),('legacy_thin',2.1109157489,.80,1.26),('thin',R,.85,1.12),('thick',R,1.10,1.40)]
        for hand in (-1,1):
            for label,radius,axial,pitch in shapes:
                for phase in (-.30,.15,.55,.95):
                    for elev in (60.,76.):
                        p=extend(base);p.update(hand=hand,radius=radius,axial=axial,pitch=pitch,phase=phase,elevation=elev)
                        # Preserve mean longitudinal image spacing in paired shape trials.
                        if label in ('legacy','thick'):p['scale']=base['scale']*base['pitch']/pitch
                        m=obj.assess(p);candidates.append(dict(family=label,parameters=p,train=m))
            print('screen hand',hand,'calls',obj.calls,flush=True)
        save(OUT/'screen.json',dict(candidates=candidates,window=[50,290],source_hashes=source_hashes()))
    else:
        if stage=='local':
            pool=read(OUT/'screen.json')['candidates'];starts=[]
            for hand in (-1,1):
                for family in ('intended','legacy','legacy_thin','thin','thick'):
                    pp=[r for r in pool if r['parameters']['hand']==hand and r['family']==family and r['train']['feasible']]
                    if pp:starts.append(max(pp,key=lambda r:r['train']['score']))
            keys=[('s0',2.),('phase',.12),('scale',.15),('pitch',.025),('elevation',4.)]
        elif stage=='global':
            pool=read(OUT/'local.json')['candidates'];starts=sorted(pool,key=lambda r:r['train']['score'],reverse=True)[:3]
            starts.append(dict(parameters=base,family='R294-control'))
            keys=[('s0',1.5),('phase',.08),('scale',.12),('pitch',.02)]+[(f'strain:{j}',.018) for j in range(5)]+[(f'bend:{j}',1.5) for j in range(5)]
        else:
            pool=read(OUT/'global.json')['candidates'];starts=sorted(pool,key=lambda r:r['train']['score'],reverse=True)[:2]
            starts.append(dict(parameters=base,family='R294-control'))
            keys=[('s0',1.25),('phase',.08),('axial',.04),('turn',.015),('elevation',3.),('yaw',5.),('perspective',.0005)]+[(f'phase_knots:{j}',.08) for j in range(5)]+[(f'strain:{j}',.0125) for j in range(5)]+[(f'bend:{j}',1.) for j in range(5)]
        candidates=[]
        for i,r in enumerate(starts):
            result=refine(obj,r['parameters'],keys);result['family']=r.get('family','inherited');candidates.append(result)
            save(OUT/(stage+'-partial.json'),dict(candidates=candidates))
            print(stage,i,result['family'],{k:round(v,4) for k,v in result['train'].items() if isinstance(v,float)},flush=True)
        chosen=max(candidates,key=lambda r:r['train']['score']);save(OUT/(stage+'.json'),dict(candidates=candidates,selected=chosen,source_hashes=source_hashes(),objective_version=obj.version,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),training_only=True))
if __name__=='__main__':main()
