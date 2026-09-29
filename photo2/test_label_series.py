import copy
import json
from pathlib import Path
import unittest

from analyze_label_series import analyze, consistent_chart, edges_from_document, minimal_omissions


ROOT = Path(__file__).resolve().parents[1]


def synthetic_grid(size=4):
    number=lambda u,v:1+v*size+u
    annotations=[dict(id=f'point-{u}-{v}',number=number(u,v),x=10+5*u,y=10+5*v)
                 for v in range(size) for u in range(size)]
    ids={a['number']:a['id']for a in annotations}
    series=[]
    def add(direction,numbers):
        series.append(dict(id=f'series-{len(series)}',direction=direction,status='complete',bead_ids=[ids[n]for n in numbers]))
    for v in range(size):add('d1',[number(u,v)for u in range(size)])
    for u in range(size):add('d2',[number(u,v)for v in range(size)])
    for diagonal in range(1,2*size-2):
        cells=[(u,diagonal-u)for u in range(size-1,-1,-1)if 0<=diagonal-u<size]
        if len(cells)>1:add('d3',[number(u,v)for u,v in cells])
    return dict(schema_version=2,source=dict(oriented_size=[100,100]),revision=1,annotations=annotations,series=series)


class LabelSeriesTests(unittest.TestCase):
    def test_known_grid_recovers_true_coordinates_and_all_sign_candidates(self):
        d=synthetic_grid();r=analyze(d);self.assertEqual(r['search'][0]['solutions'],1)
        c=r['conditional_charts'][0]
        expected={str(1+v*4+u):[u,v]for v in range(4)for u in range(4)}
        self.assertEqual(c['coordinates'],expected)
        self.assertEqual(c['coordinate_collisions'],0)
        self.assertEqual(c['proposed_jumps'],[])
        candidates={tuple(s['weights'][k]for k in ['d1','d2','d3'])for s in c['relative_index_candidates']}
        self.assertEqual(candidates,{(1,7,6),(-1,6,7),(-1,-7,-6),(1,-6,-7)})
        for s in c['relative_index_candidates']:
            w=s['weights'];offsets=s['offsets']
            for e in r['edges']:self.assertEqual(offsets[str(e['end'])]-offsets[str(e['start'])],w[e['direction']])

    def test_two_skipped_clicks_recovered_without_modifying_input(self):
        d=synthetic_grid();d['series'][1]['bead_ids'].pop(1);d['series'][6]['bead_ids'].pop(1)
        before=copy.deepcopy(d);r=analyze(d);self.assertEqual(d,before)
        self.assertEqual(r['search'][-1]['omission_count'],2)
        matches=[c for c in r['conditional_charts']if {(j['start'],j['end'])for j in c['proposed_jumps']}=={(5,7),(3,11)}]
        self.assertEqual(len(matches),1)
        self.assertEqual({j['proposed_steps']for j in matches[0]['proposed_jumps']},{2})
        self.assertEqual({tuple(j['intermediate_beads'])for j in matches[0]['proposed_jumps']},{(6,),(7,)})

    def test_contradiction_and_isolation_are_not_silently_accepted(self):
        d=synthetic_grid();edges=edges_from_document(d);numbers=[a['number']for a in d['annotations']]
        bad=copy.deepcopy(d);bad['series'][0]['direction']='d2'
        self.assertIsNone(consistent_chart(numbers,edges_from_document(bad)))
        self.assertIsNone(consistent_chart(numbers+[99],edges))
        with self.assertRaises(ValueError):minimal_omissions(numbers,edges,3)

    def test_original_and_corrected_maker_saves_preserve_provenance_and_coverage(self):
        before=json.loads((ROOT/'photo2/manual-labels-r144.json').read_text())
        after=json.loads((ROOT/'photo2/manual-labels-r146.json').read_text())
        r=analyze(before);self.assertEqual(r['search'][-1]['solutions'],1)
        self.assertEqual(r['search'][-1]['checked'],1326)
        c=r['conditional_charts'][0]
        self.assertEqual({(j['start'],j['end'],j['proposed_steps'],tuple(j['intermediate_beads']))for j in c['proposed_jumps']},{(10,12,2,(11,)),(2,9,2,(5,))})
        fixed=analyze(after);self.assertEqual(fixed['bead_count'],27);self.assertEqual(fixed['recorded_link_count'],54)
        self.assertEqual(fixed['cycle_rank'],28);self.assertEqual(len(fixed['triangles']),28)
        self.assertEqual({tuple(t['signed_direction_counts'])for t in fixed['triangles']},{(1,-1,1)})
        self.assertEqual(fixed['conditional_charts'][0]['coordinates'],c['coordinates'])
        self.assertEqual(fixed['conditional_charts'][0]['proposed_jumps'],[])
        self.assertEqual(fixed['six_recorded_neighbors'],[5,8,11,14,17,20])
        self.assertEqual(fixed['recorded_direction_neighbors']['20'],
                         {'+d1':[21],'-d1':[19],'+d2':[23],'-d2':[16],'+d3':[22],'-d3':[17]})
        self.assertEqual({(e['start'],e['end'],e['direction']) for e in fixed['conditional_charts'][0]['implied_unrecorded_links']},
                         {(3,6,'d2'),(25,26,'d3')})
        self.assertEqual(after['annotations'],before['annotations'])
        self.assertEqual(after['source'],before['source'])


if __name__=='__main__':unittest.main()
