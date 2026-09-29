"""Audit manual direction series; infer conditional local coordinates, never full indices."""
from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import asdict, dataclass
import hashlib
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path

from label_beads import validate_annotations, validate_series

ROOT = Path(__file__).resolve().parents[1]
STEPS = {'d1': (1, 0), 'd2': (0, 1), 'd3': (-1, 1)}


@dataclass(frozen=True)
class Edge:
    start: int
    end: int
    direction: str
    series_id: str
    position: int


def edges_from_document(doc):
    names = {a['id']: a['number'] for a in doc['annotations']}
    return [Edge(names[a], names[b], s['direction'], s['id'], pos)
            for s in doc['series'] if s['status'] == 'complete'
            for pos, (a, b) in enumerate(zip(s['bead_ids'], s['bead_ids'][1:]))]


def components(numbers, edges):
    adj = {n: [] for n in numbers}
    for e in edges:
        adj[e.start].append(e.end); adj[e.end].append(e.start)
    remaining, groups = set(numbers), []
    while remaining:
        root = min(remaining); reached = {root}; queue = [root]
        for a in queue:
            for b in adj[a]:
                if b not in reached:
                    reached.add(b); queue.append(b)
        remaining -= reached; groups.append(sorted(reached))
    return groups


def consistent_chart(numbers, edges, omitted=()):
    """Exact integer propagation; reject any conflicting cycle or disconnected chart."""
    if not numbers:
        return None
    adj = {n: [] for n in numbers}
    skipped = set(omitted)
    for i, e in enumerate(edges):
        if i in skipped:
            continue
        u, v = STEPS[e.direction]
        adj[e.start].append((e.end, (u, v)))
        adj[e.end].append((e.start, (-u, -v)))
    root = min(numbers); chart = {root: (0, 0)}; queue = [root]
    for a in queue:
        for b, (u, v) in adj[a]:
            wanted = chart[a][0] + u, chart[a][1] + v
            if b in chart and chart[b] != wanted:
                return None
            if b not in chart:
                chart[b] = wanted; queue.append(b)
    return chart if len(chart) == len(numbers) else None


def minimal_omissions(numbers, edges, max_omissions=2):
    """Exhaustively check all exclusions through the first consistent cardinality."""
    if max_omissions not in (0, 1, 2):
        raise ValueError('This bounded patch audit supports zero to two exclusions.')
    if len(edges) > 200:
        raise ValueError('Exhaustive audit is limited to patches of at most 200 links.')
    counts = []
    for count in range(max_omissions + 1):
        found, checked = [], 0
        for omitted in combinations(range(len(edges)), count):
            checked += 1
            chart = consistent_chart(numbers, edges, omitted)
            if chart is not None:
                found.append((omitted, chart))
        counts.append(dict(omission_count=count, checked=checked, solutions=len(found)))
        if found:
            return found, counts
    return [], counts


def triangles(numbers, edges):
    # Preserve multi-labelled pairs instead of choosing one label silently.
    labels = {}
    for e in edges:
        labels.setdefault((e.start, e.end), set()).add((e.direction, 1))
        labels.setdefault((e.end, e.start), set()).add((e.direction, -1))
    result = []
    for a, b, c in combinations(sorted(numbers), 3):
        pairs = [(a, b), (b, c), (c, a)]
        if not all(p in labels for p in pairs):
            continue
        for choices in product(*(sorted(labels[p]) for p in pairs)):
            counts = [0, 0, 0]
            for direction, sign in choices:
                counts[int(direction[1]) - 1] += sign
            result.append(dict(beads=[a, b, c], signed_direction_counts=counts))
    return result


def witness_path(edges, start, end, excluded):
    adj = {}
    for i, e in enumerate(edges):
        if i in excluded:
            continue
        adj.setdefault(e.start, []).append((e.end, i, 1))
        adj.setdefault(e.end, []).append((e.start, i, -1))
    queue = deque([start]); parents = {start: None}
    while queue and end not in parents:
        a = queue.popleft()
        for b, i, sign in adj.get(a, []):
            if b not in parents:
                parents[b] = (a, i, sign); queue.append(b)
    if end not in parents:
        return []
    steps, node = [], end
    while node != start:
        a, i, sign = parents[node]
        steps.append(dict(start=a, end=node, direction=edges[i].direction,
                          sign=sign, recorded_edge=i))
        node = a
    return steps[::-1]


def weight_candidates(chart):
    # d1 has magnitude 1; d2/d3 have magnitudes 6/7 in either order.
    # The triangle gives d1 - d2 + d3 = 0. Global reversal remains ambiguous.
    result = []
    for a in (-1, 1):
        for bmag, cmag in permutations((6, 7)):
            for bsign, csign in product((-1, 1), repeat=2):
                b, c = bsign * bmag, csign * cmag
                if a - b + c != 0:
                    continue
                result.append(dict(weights=dict(d1=a, d2=b, d3=c),
                                   offsets={str(n): a * u + b * v for n, (u, v) in sorted(chart.items())},
                                   status='Conditional relative offsets; origin and whole-string orientation unknown'))
    return result


def analyze(doc, max_omissions=2):
    if doc.get('schema_version') != 2:
        raise ValueError('Expected labeler schema 2.')
    points = validate_annotations(doc['annotations'], doc['source']['oriented_size'])
    validate_series(doc['series'], points)
    numbers = sorted(a['number'] for a in points)
    edges = edges_from_document(doc)
    neighbors = {n: {} for n in numbers}
    for e in edges:
        neighbors[e.start].setdefault('+' + e.direction, set()).add(e.end)
        neighbors[e.end].setdefault('-' + e.direction, set()).add(e.start)
    groups = components(numbers, edges)
    found, searches = minimal_omissions(numbers, edges, max_omissions)
    result = dict(assumptions=[
        'Completed click order supplies directed relations, not measured step counts.',
        'Trial chart assumes each retained link is one neighbor step.',
        'd3=d2-d1 is a proposed local relation supported by the recorded triangles.',
        'Skipped steps inferred from other paths remain proposals until maker confirmation.',
        'Maker numbers, stable IDs, discussion coordinates and full-string indices stay distinct.'],
        revision=doc['revision'], bead_count=len(numbers),
        completed_series=Counter(s['direction'] for s in doc['series'] if s['status'] == 'complete'),
        active_series=sum(s['status'] == 'active' for s in doc['series']),
        recorded_link_count=len(edges), components=groups,
        cycle_rank=len(edges)-len(numbers)+len(groups),
        recorded_direction_neighbors={str(n): {d: sorted(v) for d,v in sorted(adj.items())}
                                      for n,adj in neighbors.items()},
        six_recorded_neighbors=[n for n,adj in neighbors.items()
                                if len(adj)==6 and all(len(v)==1 for v in adj.values())],
        edges=[asdict(e) for e in edges], triangles=triangles(numbers, edges),
        search=searches, conditional_charts=[])
    for omitted, chart in found:
        inverse = {p: n for n, p in chart.items()}
        recorded = {(e.start,e.end,e.direction) for e in edges}
        implied = []
        for n,(u,v) in sorted(chart.items()):
            for direction,(du,dv) in STEPS.items():
                other = inverse.get((u+du,v+dv))
                if other is not None and (n,other,direction) not in recorded and (other,n,direction) not in recorded:
                    implied.append(dict(start=n,end=other,direction=direction,
                                        status='Graph-implied unit relation; not recorded or maker-confirmed'))
        jumps = []
        for i in omitted:
            e = edges[i]; delta = (chart[e.end][0]-chart[e.start][0], chart[e.end][1]-chart[e.start][1])
            step = STEPS[e.direction]
            factor = next((delta[k] // step[k] for k in range(2) if step[k]), None)
            valid_multiple = factor is not None and factor > 0 and delta == (factor*step[0], factor*step[1])
            intermediate = [inverse.get((chart[e.start][0]+k*step[0], chart[e.start][1]+k*step[1]))
                            for k in range(1, factor)] if valid_multiple else []
            jumps.append(dict(recorded_edge=i, **asdict(e), chart_delta=list(delta),
                              proposed_steps=factor if valid_multiple else None,
                              intermediate_beads=intermediate,
                              independent_recorded_path=witness_path(edges, e.start, e.end, set(omitted)),
                              status='Unconfirmed interpretation; original series preserved'))
        result['conditional_charts'].append(dict(
            origin_bead=min(numbers), direction_steps=STEPS,
            coordinates={str(n): list(p) for n,p in sorted(chart.items())},
            unit_link_count=len(edges)-len(omitted),
            independent_unit_cycles=len(edges)-len(omitted)-len(numbers)+1,
            coordinate_collisions=len(chart)-len(set(chart.values())),
            implied_unrecorded_links=implied,
            proposed_jumps=jumps, relative_index_candidates=weight_candidates(chart)))
    return result


def render_review(doc, report, image_path, directory):
    # Computational evidence plots; no generated/retouched source image.
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-r144-mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.path import Path as Polygon
    from PIL import Image, ImageOps
    directory.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(image_path)).convert('RGB')
    markers={a['number']:a for a in doc['annotations']}
    x0,y0,x1,y1=doc['view_crop']; chart=report['conditional_charts'][0]
    coords={int(n):p for n,p in chart['coordinates'].items()}
    omitted={j['recorded_edge'] for j in chart['proposed_jumps']}
    colors={'d1':'#b96800','d2':'#007f9e','d3':'#8e55b1'}
    fig,axes=plt.subplots(1,2,figsize=(13,8),layout='constrained')
    axes[0].imshow(im.crop(doc['view_crop']),extent=[x0,x1,y1,y0])
    axes[0].set_title('Maker-selected locations and unique numbers')
    for n,a in markers.items():
        axes[0].plot(a['x'],a['y'],'o',color='cyan',ms=2.8)
        axes[0].annotate(str(n),(a['x'],a['y']),xytext=(4,-4),textcoords='offset points',fontsize=8,color='white',bbox=dict(facecolor='black',alpha=.75,pad=1))
    axes[0].set_xlabel('Source x');axes[0].set_ylabel('Source y')
    for i,e in enumerate(report['edges']):
        axes[1].annotate('',coords[e['end']],coords[e['start']],arrowprops=dict(arrowstyle='->',color=colors[e['direction']],lw=1.3,linestyle='--' if i in omitted else '-',shrinkA=10,shrinkB=10))
    for n,p in coords.items():
        axes[1].text(*p,str(n),ha='center',va='center',fontsize=9,bbox=dict(boxstyle='circle',facecolor='white',edgecolor='#536675',pad=.25))
    us,vs=zip(*coords.values());axes[1].set_xlim(min(us)-.8,max(us)+.8);axes[1].set_ylim(min(vs)-.7,max(vs)+.7)
    axes[1].set_title('Conditional integer chart: d1=(1,0), d2=(0,1), d3=(-1,1)')
    axes[1].set_aspect('equal');axes[1].set_xlabel('d1 count u');axes[1].set_ylabel('d2 count v');axes[1].grid(alpha=.25)
    axes[1].legend(handles=[Line2D([0],[0],color=c,label=d)for d,c in colors.items()]+[Line2D([0],[0],color='gray',ls='--',label='Proposed multistep jump')],loc='upper right')
    fig.savefig(directory/'labeled-chart.png',dpi=150);plt.close(fig)
    jumps=sorted(chart['proposed_jumps'],key=lambda j:j['direction'])
    if jumps:
        fig,axes=plt.subplots(1,len(jumps)+1,figsize=(15,6),layout='constrained',squeeze=False)
        ax=axes[0,0];ax.imshow(im.crop(doc['view_crop']),extent=[x0,x1,y1,y0]);ax.set_title('Raw context')
        for ax,j in zip(axes[0,1:],jumps):
            nums=[j['start'], *[n for n in j['intermediate_beads'] if n is not None], j['end']]
            points=[markers[n]for n in nums];margin=20
            bx0=max(0,int(min(p['x']for p in points))-margin);by0=max(0,int(min(p['y']for p in points))-margin)
            bx1=min(im.width,int(max(p['x']for p in points))+margin);by1=min(im.height,int(max(p['y']for p in points))+margin)
            ax.imshow(im.crop((bx0,by0,bx1,by1)),extent=[bx0,bx1,by1,by0]);ax.set_title(f"{j['direction']}: {j['start']} → {j['end']}; proposed via {j['intermediate_beads']}")
            for n in nums:
                a=markers[n];ax.plot(a['x'],a['y'],'o',color='cyan',ms=4);ax.annotate(str(n),(a['x'],a['y']),xytext=(5,-8),textcoords='offset points',color='white',weight='bold',bbox=dict(facecolor='black',alpha=.8,pad=2))
            for a,b in zip(points,points[1:]):
                ax.annotate('',(b['x'],b['y']),(a['x'],a['y']),arrowprops=dict(arrowstyle='->',color='cyan',lw=1.6,linestyle='--'))
        for ax in axes[0]:ax.set_xlabel('Source x');ax.set_ylabel('Source y')
        fig.suptitle('Recorded endpoint jumps; dashed arrows propose intermediate beads (not yet maker-confirmed)')
        fig.savefig(directory/'step-question.png',dpi=150);plt.close(fig)
    old_path=ROOT/'photo2/local-fit-r126.json'
    old=json.loads(old_path.read_text())
    matches={name:[n for n,a in markers.items() if Polygon(poly).contains_point((a['x'],a['y']))]for name,poly in old['observations'].items()}
    report['historical_polygon_matches']=dict(source_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest(),matches=matches,
        status='Spatial containment in assistant rough polygons; tentative ID reconciliation, not maker confirmation')
    names=['B','C','G'];polys=[old['observations'][name]for name in names]
    xs=[x for poly in polys for x,y in poly];ys=[y for poly in polys for x,y in poly]
    bounds=(max(0,min(xs)-20),max(0,min(ys)-20),min(im.width,max(xs)+20),min(im.height,max(ys)+20))
    lx0,ly0,lx1,ly1=bounds
    fig,axes=plt.subplots(1,3,figsize=(11,5),layout='constrained')
    for ax in axes:
        ax.imshow(im.crop(bounds),extent=[lx0,lx1,ly1,ly0]);ax.set_xlabel('Source x');ax.set_ylabel('Source y')
    axes[0].set_title('Raw B/C/G context')
    axes[1].set_title('Maker numbers: tentative old-ID match')
    axes[2].set_title('Historical assistant polygons (dashed)')
    for name,color in zip(names,['cyan','yellow','lime']):
        poly=old['observations'][name]
        axes[2].plot([p[0]for p in poly]+[poly[0][0]],[p[1]for p in poly]+[poly[0][1]],'--',color=color,lw=1)
        for n in matches[name]:
            a=markers[n]
            for ax in axes[1:]:
                ax.plot(a['x'],a['y'],'o',color=color,ms=4)
                ax.annotate(f'{n} / {name}?',(a['x'],a['y']),xytext=(5,-8),textcoords='offset points',color='white',bbox=dict(facecolor='black',alpha=.8,pad=2))
    fig.savefig(directory/'id-question.png',dpi=150);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations',type=Path,default=ROOT/'photo2/manual-labels-r144.json')
    parser.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/label-series-audit/report.json')
    parser.add_argument('--review-dir',type=Path)
    args=parser.parse_args()
    raw=args.annotations.read_bytes();doc=json.loads(raw)
    if hashlib.sha256(args.image.read_bytes()).hexdigest()!=doc['source']['sha256']:
        parser.error('Annotation source hash differs from supplied image.')
    result=analyze(doc)
    result['provenance']=dict(annotation_sha256=hashlib.sha256(raw).hexdigest(),source_sha256=doc['source']['sha256'],
                              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if args.review_dir and len(result['conditional_charts'])==1:
        render_review(doc,result,args.image,args.review_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['revision','bead_count','recorded_link_count','cycle_rank','search']},indent=2))


if __name__=='__main__':main()
