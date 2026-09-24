#!/usr/bin/env python3
"""Blind neighbor/period attempt on the generated-JPEG observation records.

Uses existing image-only neighbor proposals, with both conventions preserved.
Does not load POV-Ray source/patterns, source indices, geometry, or truth masks.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

from blind_generated import ROOT, digest, write_json
from infer_neighbors import infer
from neighbor_graph import propagate, reciprocal


def periods(indexed):
    """Strong periods of arbitrary color names; absent indices stay absent."""
    if not indexed:
        return []
    low, high = min(indexed), max(indexed)
    candidates = []
    for period in range(1, (high-low+1)//2+1):
        slots = [None]*period
        support = [[] for _ in range(period)]
        for index, color in sorted(indexed.items()):
            if color == 'unknown':
                continue
            slot = (index-low) % period
            if slots[slot] not in (None, color):
                break
            slots[slot] = color
            support[slot].append(index)
        else:
            candidates.append(dict(period=period, slot_colors=slots,
                                   support_indices=support,
                                   missing_slots=[s for s in range(period) if slots[s] is None],
                                   multiply_observed_slots=sum(len(s) >= 2 for s in support)))
    return candidates


def attempt(observations, position):
    retained = [r for r in observations if not r['flags']]
    xy = np.array([r[position] for r in retained])
    if len(xy) < 4:
        return dict(position=position,status='insufficient_candidates',variants=[])
    proposals = infer(xy)
    # Open the annulus once; no true total count is available for modular indexing.
    angle = np.arctan2(xy[:, 1]-xy[:, 1].mean(), xy[:, 0]-xy[:, 0].mean())
    variants = []
    for variant in proposals['variants']:
        edges = [e for e in variant['edges'] if abs(angle[e[0]]-angle[e[1]]) <= np.pi]
        cut = [e for e in variant['edges'] if abs(angle[e[0]]-angle[e[1]]) > np.pi]
        result = propagate(list(range(len(xy))), reciprocal(edges))
        local = []
        for component in result['components']:
            vertices = component['vertices']
            local_edges = [e for e in edges if e[0] in vertices and e[1] in vertices]
            check = propagate(vertices, reciprocal(local_edges))
            if not check['consistent'] or len(vertices) < 12:
                continue
            indexed = {check['labels'][v]: retained[v]['color'] for v in vertices}
            local.append(dict(observation_ids=[retained[v]['observation_id'] for v in vertices],
                              relative_indices={str(retained[v]['observation_id']):check['labels'][v] for v in vertices},
                              unknown_component_offset=True,
                              compatible_local_periods=periods(indexed)))
        variants.append(dict(convention=variant['convention'],edges=edges,cut_edges=cut,
                             reciprocal_edges=len(edges),components=len(result['components']),
                             component_sizes=sorted([len(c['vertices']) for c in result['components']],reverse=True),
                             conflicting_directed_edges=len(result['conflicts']),
                             duplicate_index_groups=len(result['duplicate_indices']),
                             consistent=result['consistent'],graph=result,
                             consistent_local_groups=local,
                             ambiguous=variant['ambiguous'],nonreciprocal=variant['nonreciprocal']))
    return dict(position=position, anonymous_to_observation_id=[r['observation_id'] for r in retained],
                input_candidates=len(retained),neighbor_parameters=proposals['parameters'],variants=variants)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observations',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    rows=[]
    inputs={}
    for case in range(1,8):
        path=args.observations/f'beads{case}-observations.json'
        record=json.loads(path.read_text());inputs[str(path)]=digest(path)
        if digest(ROOT/record['input']) != record['input_sha256']:
            raise ValueError('JPEG no longer matches observations')
        attempts=[attempt(record['observations'],p) for p in ['marker_xy','visible_centroid_xy']]
        row=dict(image=record['input'],input_sha256=record['input_sha256'],attempts=attempts,
                 pattern_status='unresolved',recovered_repeat=None,
                 reason='No independently verified complete visible-bead map or reliable full indexing; local period compatibility is not recovery.')
        rows.append(row);write_json(args.output/f'beads{case}-index-attempt.json',row)
        print(record['input'],[(a['position'],[(v['convention'],v['conflicting_directed_edges'],v['duplicate_index_groups'],len(v['consistent_local_groups'])) for v in a['variants']]) for a in attempts],flush=True)
    sources=['photo2/blind_generated.py','photo2/blind_generated_index.py','photo2/infer_neighbors.py','photo2/neighbor_graph.py']
    report=dict(command=[sys.executable,*sys.argv],inputs=inputs,
                sources={p:digest(ROOT/p) for p in sources},
                method='Unflagged image candidates; marker/region-centroid alternatives, reciprocal signed sectors, both conventions, one image-angle seam cut, exact propagation; periods only for internally consistent groups >=12 candidates.',
                all_seven_patterns_identified=False,results=rows,
                limitations=['No exact total N or source order supplied.',
                             'Both sign conventions retained; no color-guided edge correction.',
                             'Cycle consistency is necessary but does not verify an edge.',
                             'Disconnected group offsets and every missing index remain unknown.',
                             'No period test on inconsistent index assignments.'])
    write_json(args.output/'report.json',report)


if __name__=='__main__':
    main()
