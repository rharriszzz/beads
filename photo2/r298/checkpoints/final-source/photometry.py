"""Preserved material and independent separator diagnostics; no patch reward."""
import numpy as np
from scipy.ndimage import map_coordinates
from .calibrate import BASE,measurements
from photo2.r297.common import ROOT,read,save,sha,photo,pixels,load_evidence

def freeze():
    data,_=load_evidence();rgb,_,_=photo();sources={r['id']:r for r in data['rows']};pairs=[]
    for e in data['edges']:
        a,b=[sources.get(i) for i in e['ids']]
        if a is None or b is None or a['kind']!='region' or b['kind']!='region' or a['reflection'] or b['reflection']:continue
        delta=np.array(b['point'])-a['point'];distance=np.linalg.norm(delta)
        if not 20<distance<48 or e['valley']<.65:continue
        section=int(a['station']/data['length']*32)
        if any(p['section']==section for p in pairs):continue
        xy=np.array(a['point'])+np.linspace(0,1,97)[:,None]*delta
        ij=np.rint(xy).astype(int);color=rgb[ij[:,1],ij[:,0]];v=color@np.array([.299,.587,.114])/255
        mid=np.arange(29,68);trough=int(mid[np.argmin(v[mid])]);level=v[trough]+.25*(min(v[:16].max(),v[-16:].max())-v[trough]);lo=hi=trough
        while lo>0 and v[lo-1]<level:lo-=1
        while hi<96 and v[hi+1]<level:hi+=1
        pairs.append(dict(id=f'S{section:02}',section=section,source_ids=e['ids'],xy=xy.tolist(),rgb=color.tolist(),luminance=v.tolist(),valley_sample=trough,dark_interval=[lo,hi],dark_interval_px=float((hi-lo)*distance/96),representative_displacement=delta.tolist(),representative_distance=float(distance),source_edge=e,split='comparison' if section%4==3 else 'development',meaning='Observed surface-representative displacement and dark interval, NOT physical center spacing or an empty gap. Neighbor family unknown.'))
    save(BASE/'evidence/separators.json',dict(records=pairs,source_sha256=sha(ROOT/'photo2/r296/evidence/inputs.json.gz'),photo_sha256=sha(ROOT/'beads-photo-2.jpg')))
    print('Frozen photographic separators',len(pairs))

class PhotoScore:
    def __init__(self,data,split='development'):
        self.separators=[r for r in read(BASE/'evidence/separators.json')['records'] if r['split']==split]
        raw=np.load(ROOT/'photo2/r296/evidence/cues.npz');sections=(raw['station']/data['length']*32).astype(int)%32
        keep=((sections%4==3) if split=='comparison' else (sections%4!=3))&(np.arange(len(sections))%5==0)
        self.cues={k:raw[k][keep] for k in ['xy','color','paper','lum']}
        self.rows=[r for r in data['rows'] if r['kind']=='region' and ((int(r['station']/data['length']*32)%4==3)==(split=='comparison'))]
        parts=[];self.bounds=[0]
        for r in self.rows:
            xy=pixels(r['pixels']);part=xy[np.linspace(0,len(xy)-1,min(24,len(xy))).astype(int)];parts.append(part);self.bounds.append(self.bounds[-1]+len(part))
        self.obs=np.concatenate(parts);self.xy=np.concatenate([self.cues['xy'],self.obs]+[np.array(r['xy']) for r in self.separators])
    def assess(self,scene):
        tr=scene.trace(self.xy);o=tr['owner'];n=len(self.cues['xy']);go=o[:n];visible=go>=0;c=self.cues;colored=c['color']>0
        paper=float(visible[c['paper']].mean()) if c['paper'].any() else 0
        missing=float((~visible[colored]).mean()) if colored.any() else 0
        count=np.zeros((scene.n,3));np.add.at(count,(go[visible],c['color'][visible]),1);nn=count[:,1:].sum(1);use=nn>=3
        conflict=float(np.mean(np.minimum(count[use,1],count[use,2])/nn[use])) if use.any() else 0
        fractions=[];assignments=[]
        for row,a,b in zip(self.rows,self.bounds[:-1],self.bounds[1:]):
            ids,counts=np.unique(o[n+a:n+b],return_counts=True);ok=ids>=0;ids,counts=ids[ok],counts[ok];j=int(np.argmax(counts)) if len(ids) else None
            frac=float(counts[j]/(b-a)) if j is not None else 0;fractions.append(frac);assignments.append(dict(id=row['id'],fraction=frac,index=int(scene.indices[ids[j]]) if j is not None else None))
        seps=[];start=n+len(self.obs)
        for r in self.separators:
            owners=o[start:start+97];start+=97;changes=np.flatnonzero(owners[:-1]!=owners[1:])+.5
            dist=float(min(abs(changes-r['valley_sample']))*r['representative_distance']/96) if len(changes) else 24.
            a,b=owners[16],owners[80];diff=int(scene.indices[b]-scene.indices[a]) if a>=0 and b>=0 else None
            if diff is not None and scene.closed:diff=int((diff+scene.n//2)%scene.n-scene.n//2)
            seps.append(dict(id=r['id'],boundary_error_px=dist,conditional_index_difference=diff,bank_owners=[int(scene.indices[x]) if x>=0 else None for x in [a,b]],unknown_rays=int(tr['unknown'][start-97:start].sum()),profile_owners=[int(scene.indices[x]) if x>=0 else None for x in owners]))
        error=float(np.mean([min(12,r['boundary_error_px']) for r in seps])) if seps else 0
        return dict(paper_occupied=paper,colored_missing=missing,color_conflict=conflict,region_containment=float(np.mean(fractions)),separator_error_px=error,separators=seps,assignments=assignments,unknown_rays=int(tr['unknown'].sum()),rays=len(o))
if __name__=='__main__':freeze()
