"""Apply exactly two explicit pigments; preserve every old record field."""
from common import *
import subprocess


def main():
    old, obs, co = load_graph(ROOT/'photo2/r343/graph.json.gz')
    graph = copy.deepcopy(old)
    fo = {r['id']: r for r in graph['observations']}
    ledger = copy.deepcopy(read(ROOT/'photo2/r343/maker-decisions.json')['authoritative_labels'])
    changes = []
    for o in CORRECTIONS:
        assert obs[o]['color'] == 'red'
        record = dict(id=o, photograph='R343 P29' if o == CORRECTIONS[0] else 'R343 P127', local_feature=1,
                      before_color='red', color='yellow', category='explicit_individual_pigment',
                      source='R344 explicit individual maker pigment judgment',
                      prior_observation=copy.deepcopy(obs[o]), prior_authority=copy.deepcopy(ledger.get(o)),
                      geometry_or_identity_change=False,
                      explanation='Yellow throughout nearly all visible glass, except very edge.' if o == CORRECTIONS[0] else 'Yellow glass in shadow.')
        changes.append(record)
        fo[o]['color'] = 'yellow'
        fo[o]['r344_pigment_authority'] = dict(category=record['category'], color='yellow', source=record['source'], photograph=record['photograph'], local_feature=1,
                                             supersedes=('Software red and prior general illustration approval; all prior statements retained' if o == CORRECTIONS[0] else 'Software red; no prior individual pigment authority; original statements retained'), protected_from_automatic_recoloring=True)
        ledger[o] = dict(color='yellow', source=record['source'], category=record['category'])
    graph['indexed_colors'] = dict(Counter(fo[o]['color'] for o in co))
    graph.update(r344_policy='Only two explicit maker pigment overlays; all existing record fields/provenance except current color retained. No identities, XY, AB, links, roles or winding changed.', previous_graph='photo2/r343/graph.json.gz')
    save(OUT/'graph.json.gz', graph)
    save(OUT/'corrections.json', dict(decisions=changes, authoritative_labels=ledger, old_authority_statements_retained=True, automatic_color_changes=[]))
    paths = subprocess.check_output(['git', 'ls-files', 'beads-photo-2.jpg', 'beads.pov'] + [f'photo2/r{n}' for n in range(336,344)] + [f'photo2/R{n}_REPORT.md' for n in range(336,344)], cwd=ROOT, text=True).splitlines()
    save(OUT/'input-seal.json', {p:sha(ROOT/p) for p in paths})
    save(OUT/'freeze.json', dict(base_commit=BASE, changed_ids=CORRECTIONS, graph_sha256=sha(OUT/'graph.json.gz'), corrections_sha256=sha(OUT/'corrections.json'),
                                identities_coordinates_links_winding_unchanged=True, pattern_used_for_pigment=False, black_detector_sha256=sha(ROOT/'photo2/r342/recognize.py'), historical_files=len(paths)))
    print('FROZEN', len(obs), len(co), len(graph['edges']), graph['indexed_colors'])


if __name__ == '__main__':
    main()
