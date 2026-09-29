"""R123 signed construction-direction coordinates, separate from image geometry.

This checks supplied neighbor labels; it does not identify neighbors in an image.
Triples record path steps, not unique bead identities. Observation IDs stay stable.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class DirectionCoordinates:
    n1: int = 0
    n6: int = 0
    n7: int = 0

    def step(self, delta):
        if delta not in (-7,-6,-1,1,6,7):
            raise ValueError('A supported immediate neighbor must be +/-1, +/-6 or +/-7')
        values=asdict(self);key={1:'n1',6:'n6',7:'n7'}[abs(delta)]
        values[key]+=1 if delta>0 else -1
        return DirectionCoordinates(**values)

    def bead_index(self, origin=0):
        return origin+self.n1+6*self.n6+7*self.n7


def resolve_local(nodes, edges, seed, origin=0):
    """Assign a first-path triple and check every supplied local edge.

    Different triples with the same weighted sum can describe the same bead.
    A full-necklace winding cycle is outside this local, unwrapped check; use a
    documented cut or a verified N before interpreting such a cycle modulo N.
    """
    nodes=list(nodes);edges=list(edges)
    if seed not in nodes or len(set(nodes))!=len(nodes):
        raise ValueError('Unique observation IDs and a listed seed are required')
    for u,v,d in edges:
        if u not in nodes or v not in nodes:
            raise ValueError('Every edge endpoint must be an observation ID')
        DirectionCoordinates().step(d)
    coords={seed:DirectionCoordinates()}
    for _ in nodes:
        for u,v,d in edges:
            if u in coords and v not in coords:coords[v]=coords[u].step(d)
            if v in coords and u not in coords:coords[u]=coords[v].step(-d)
    alternate_paths=[];conflicts=[]
    for u,v,d in edges:
        if u not in coords or v not in coords:continue
        alternative=coords[u].step(d)
        error=alternative.bead_index()-coords[v].bead_index()
        if error:
            conflicts.append(dict(u=u,v=v,delta=d,index_disagreement=error))
        elif alternative!=coords[v]:
            alternate_paths.append(dict(observation_id=v,via=u,delta=d,
                                        alternative=asdict(alternative)))
    indices={n:c.bead_index(origin) for n,c in coords.items()}
    duplicates=[(u,v) for j,u in enumerate(coords) for v in list(coords)[j+1:]
                if indices[u]==indices[v]]
    return dict(coordinates={n:asdict(c) for n,c in coords.items()},
                derived_component_indices=indices,consistent_alternate_paths=alternate_paths,
                conflicts=conflicts,distinct_observation_index_collisions=duplicates,
                unresolved=[n for n in nodes if n not in coords])
