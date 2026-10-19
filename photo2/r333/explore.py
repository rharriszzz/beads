"""Preserved first exploration: directional palette paths on measured links."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r333-mpl')
from collections import Counter,defaultdict
import numpy as np
from photo2.r332.common import ROOT,read,save
D=np.array([(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)])
E=D@np.array([[1.,0.],[.5,.866025403784]])

def paths(g,palette,cone,colors=None,minlen=6):
    co={r['id']:np.array(r['ab']) for r in g['coordinates']};obs={o['id']:o for o in g['observations']};names=sorted(co)
    col={o:obs[o]['color'] for o in names} if colors is None else colors
    steps=[tuple(D[cone]),tuple(D[(cone+1)%6])];heading=E[cone]+E[(cone+1)%6];proj={o:float(co[o]@np.array([[1.,0.],[.5,.866025403784]])@heading) for o in names};adj=defaultdict(list)
    for e in g['edges']:
        a,z=e['source'],e['target'];v=tuple(e['delta_ab'])
        if v in steps:adj[a].append((z,steps.index(v)))
        if tuple(-np.array(v)) in steps:adj[z].append((a,steps.index(tuple(-np.array(v)))))
    # Canonical cut prevents a false DAG through the necklace seam; cut paths
    # end at the cut, which is explicitly marked instead of called an error.
    for a in adj:adj[a]=[(z,j) for z,j in adj[a] if proj[z]>proj[a]]
    unused={o for o in names if col[o] in palette};answer=[]
    order=sorted(names,key=lambda o:proj[o])
    while unused:
        score={};back={}
        for a in order:
            if a not in unused:continue
            for last in range(2):
                score.setdefault((a,last),1.)
                for z,j in adj[a]:
                    if z not in unused:continue
                    val=score[a,last]+1+.25*(col[a]!=col[z])-.15*(last!=j)
                    if val>score.get((z,j),0):score[z,j]=val;back[z,j]=(a,last)
        if not score:break
        end=max(score,key=score.get);chain=[];state=end
        while state:
            chain.append(state[0]);state=back.get(state)
        chain=chain[::-1];unused-=set(chain)
        if len(chain)<minlen:break
        if min(Counter(col[o] for o in chain)[p] for p in palette)<2:continue
        word=[list((co[z]-co[a]).astype(int)) for a,z in zip(chain,chain[1:])]
        answer.append(dict(ids=chain,length=len(chain),score=score[end],word=word,counts=dict(Counter(col[o] for o in chain))))
    return answer

def main():
    g=read(ROOT/'photo2/r332/results/graph.json.gz');rows=[]
    for p in [('black','red'),('black','yellow')]:
        for cone in range(6):
            pp=paths(g,p,cone);r=dict(palette=p,cone=cone,segments=pp,coverage=sum(x['length'] for x in pp));rows.append(r)
            print(p,cone,len(pp),r['coverage'],[x['length'] for x in pp[:10]],flush=True)
    save(ROOT/'photo2/r333/development/first-paths.json.gz',rows)
if __name__=='__main__':main()
