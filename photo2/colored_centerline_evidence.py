"""R187: colored rim/diagonal proposals before fitting a replacement centerline.

The image alone supplies detection and side/chain proposals. Historical curves,
maker centers and confirmed interiors are never detector or selection inputs.
The learned search-strip axis is only an ordering device, not a centerline fit.
"""
import argparse
from copy import deepcopy
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

import auto_label_beads as auto
from label_beads import atomic_json


def colored_subset(result, graph):
    indices = [i for i,p in enumerate(result['points']) if p['kind']=='chromatic']
    remap = {old:new for new,old in enumerate(indices)}
    points = [dict(deepcopy(result['points'][i]), original_proposal_number=i+1,
                   observation_number=new+1) for new,i in enumerate(indices)]
    edges = [dict(deepcopy(e),start=remap[e['start']],end=remap[e['end']])
             for e in graph['edges'] if e['start'] in remap and e['end'] in remap]
    return points, dict(edges=edges)


def rim_candidates(points, axis_length, diameter):
    """Local cross-position tails, not established edge/outline measurements."""
    station=np.array([p['station'] for p in points]);cross=np.array([p['cross'] for p in points])
    output=[]
    for i,p in enumerate(points):
        distance=(station-p['station']+axis_length/2)%axis_length-axis_length/2
        local=abs(distance)<=diameter*4
        if local.sum()<8:continue
        low,high=np.quantile(cross[local],[.15,.85])
        # A locally collapsed distribution does not support two envelope sides.
        if high-low<diameter*.5:continue
        side='outer-side' if cross[i]<=low else 'inner-side' if cross[i]>=high else None
        if side:
            output.append(dict(observation_number=p['observation_number'],side=side,
                               source_xy=p['source_xy'],support_area=p['support_area'],
                               local_support=int(local.sum()),cross_limits=[float(low),float(high)],
                               status='Colored interior near local proposal envelope; edge exposure/ownership unverified.'))
    return output


def diagonal_chains(points, edges):
    chains=[]
    for direction in ['d2','d3']:
        subset=[e for e in edges if e['direction']==direction]
        following={e['start']:e['end'] for e in subset}
        if len(following)!=len(subset):raise ValueError('Competing outgoing neighbors must be retained, not collapsed.')
        previous={e['end'] for e in subset};visited=set()
        for start in sorted(following):
            if start in previous:continue
            path=[start]
            while path[-1] in following and following[path[-1]] not in path:
                path.append(following[path[-1]])
            visited.update(path)
            if len(path)>=3:
                chains.append(dict(direction=direction,observation_numbers=[i+1 for i in path],
                                   source_xy=[points[i]['source_xy'] for i in path],
                                   status='Tentative direction and consecutive neighbors; skipped/missing beads unverified.'))
        # Cycles are retained as uncertainty, never converted to bead closure.
        remaining=sorted(set(following)-visited)
        if remaining:chains.append(dict(direction=direction,unresolved_component_numbers=[i+1 for i in remaining],
                                       status='Cyclic/unsupported chain component; no inferred closure.'))
    return chains


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,default=auto.ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output',type=Path,default=auto.ROOT/'photo2/output/r187/colored')
    args=parser.parse_args()
    # Existing maker/edited proposals cannot be replaced by this pilot.
    auto.check_output(args.output)
    args.output.mkdir(parents=True,exist_ok=True)
    with Image.open(args.image) as im:image=ImageOps.exif_transpose(im).convert('RGB')
    result=auto.detect(np.array(image));full_graph=auto.adjacency(result)
    points,graph=colored_subset(result,full_graph)
    rims=rim_candidates(points,len(result['axis']['xy']),result['diameter'])
    chains=diagonal_chains(points,graph['edges'])
    doc=auto.export(dict(points=points),graph,args.image,image.size,args.output)
    doc['annotation_kind']='Unreviewed colored interior/neighbor proposals for centerline evidence; no measured bead centers or physical edges.'
    doc['automatic_origin'].update(proposal_script_sha256=auto.sha(Path(__file__)),
                                   point_role='Conservative colored-surface interior, not full visible-area center or edge/outward point.')
    atomic_json(args.output/'annotations.json',doc)
    report=dict(request='R187',image_sha256=auto.sha(args.image),parameters=result['parameters'],
                source_sha256={str(p.relative_to(auto.ROOT)):auto.sha(p) for p in [Path(__file__),auto.ROOT/'photo2/auto_label_beads.py']},
                points=points,rim_candidates=rims,diagonal_chains=chains,adjacency=graph,
                automatic_annotation_sha256=auto.sha(args.output/'annotations.json'),
                roles='Candidate colored-body interiors and provisional side/diagonal constraints. No replacement centerline fitted.',
                excluded_colored_near_band_edge=sum(p['kind']=='chromatic' for p in result['excluded']),
                unresolved_dark_bodies=sum(p['kind']=='dark-reflection' for p in result['points']),
                missing_slots='Black/undetected bodies and uncertain unit steps are retained conceptually; colored-only observations are not compressed string indices.')
    atomic_json(args.output/'report.json',report)
    print(dict(colored_interiors=len(points),rim_candidates=len(rims),
               diagonal_chains=sum('observation_numbers' in c for c in chains),tentative_links=len(graph['edges'])))


if __name__=='__main__':main()
