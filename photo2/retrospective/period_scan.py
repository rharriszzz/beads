"""Finite descriptive period scan on the frozen R347 color assessment.

Run .venv/bin/python photo2/retrospective/period_scan.py from the repo root.
No graph, observation, pattern, renderer or historical output is changed.
"""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import json
import os

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-period-scan-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def read(path):
    with gzip.open(path, 'rt') if path.suffix == '.gz' else path.open() as f:
        return json.load(f)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths = [ROOT/'photo2/r344/graph.json.gz', ROOT/'photo2/r344/pattern208.json',
             ROOT/'photo2/r347/answers/assessment.json']
    seal = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    graph, pattern, assessment = map(read, paths)
    coords = {r['id']: r['ab'] for r in graph['coordinates']}
    raw = {r['id']: r['color'] for r in graph['observations']}
    ids = sorted(set(coords)-set(assessment['excluded_from_color_evidence']))
    colors = {o: ('yellow' if o in assessment['maker_photo_yellow_corrections'] else raw[o]) for o in ids}
    assert len(ids) == 1040
    palette = ['red', 'yellow', 'black']
    labels = np.array([palette.index(colors[o]) for o in ids])
    rows = []
    for family, count, weights in [('A', 2704, (7, 6)), ('B', 2691, (6, 7))]:
        indices = np.array([(weights[0]*coords[o][0]+weights[1]*coords[o][1]) % count for o in ids])
        for length in range(1, 416):
            residues = indices % length
            histogram = np.bincount(residues*3+labels, minlength=length*3).reshape(length, 3)
            agreements = int(histogram.max(axis=1).sum())
            observed = int(np.count_nonzero(histogram.sum(axis=1)))
            # Independent dictionary computation of the same optimum.
            groups = defaultdict(Counter)
            for o, r in zip(ids, residues):
                groups[int(r)][colors[o]] += 1
            assert agreements == sum(max(c.values()) for c in groups.values())
            row = dict(family=family, conditional_total=count, length=length,
                       observations=len(ids), minimum_disagreements=len(ids)-agreements,
                       best_agreements=agreements, best_agreement_percent=100*agreements/len(ids),
                       observed_residues=observed, unobserved_residues=length-observed,
                       conflicting_residues=int(np.count_nonzero(np.count_nonzero(histogram, axis=1)>1)),
                       complete_repeat_closure_eligible=count % length == 0)
            rows.append(row)
            if family == 'A' and length == 208:
                fitted = ''.join(palette[i][0].upper() for i in histogram.argmax(axis=1))
                assert fitted == pattern['provisional_sequence']
    a = [r for r in rows if r['family']=='A']
    b = [r for r in rows if r['family']=='B']
    assert [r['length'] for r in a if r['minimum_disagreements']==0] == [208]
    assert not any(r['minimum_disagreements']==0 for r in b)
    for old in assessment['epochs']['maker_assessment']['trials']:
        row = next(r for r in rows if r['family']==old['family'] and r['length']==old['period'])
        assert row['complete_repeat_closure_eligible']
        assert (row['minimum_disagreements']==0) == old['compatible']
        assert row['observed_residues'] == old['observed_residues']
    with (OUT/'pattern-length-match.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

    plt.rcParams.update({'font.size':11, 'axes.titlesize':17, 'axes.labelsize':12,
                         'font.family':'DejaVu Sans', 'svg.fonttype':'none'})
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.plot([r['length'] for r in a], [r['best_agreement_percent'] for r in a],
            color='#276b99', linewidth=1.15, marker='.', markersize=2.4,
            label='Best-fitting word at each length (current A indexing)')
    closing = [r for r in a if r['complete_repeat_closure_eligible']]
    ax.scatter([r['length'] for r in closing], [r['best_agreement_percent'] for r in closing],
               s=47, facecolors='none', edgecolors='#cf6a27', linewidths=1.5, zorder=4,
               label='Length divides the assumed 2,704-bead total')
    for length, offset in [(104,(-20,-57)), (208,(10,-30)), (312,(10,9))]:
        r=a[length-1]
        suffix='\nDoes not divide 2,704' if length==312 else ''
        ax.annotate(f'{length}: {r["best_agreement_percent"]:.2f}%\n{r["minimum_disagreements"]} disagreements'+suffix,
                    (length,r['best_agreement_percent']), xytext=offset, textcoords='offset points',
                    fontsize=10, ha='left', va='center', arrowprops=dict(arrowstyle='-',color='#536878'),
                    bbox=dict(boxstyle='round,pad=.35',facecolor='white',edgecolor='#cad5dc',alpha=.97))
    ax.set(xlim=(0,416), ylim=(30,104), xlabel='Candidate repeat length (beads)',
           ylabel='Retained color observations matched (%)',
           title='Only length 208 matches every retained color observation')
    ax.set_xticks([1,52,104,156,208,260,312,364,415])
    ax.grid(alpha=.2)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='lower right', fontsize=9)
    fig.text(.5,.025,'1,040 observations · lengths 1–415 · best fitted agreement, not held-out accuracy\nFixed saved indexing and seam; ambiguous Q1 withheld; two maker photo-based yellow corrections applied.',
             ha='center', fontsize=9, color='#52616c')
    fig.tight_layout(rect=(0,.08,1,1))
    fig.savefig(OUT/'pattern-length-match.png', dpi=180)
    fig.savefig(OUT/'pattern-length-match.svg')
    svg = OUT/'pattern-length-match.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
    assert seal == {str(p.relative_to(ROOT)): sha(p) for p in paths}
    summary = dict(input_sha256=seal, minimum_length=1, maximum_length=415, observations=len(ids),
                   metric='Sum over residues of (total observed colors minus largest color count). This is the minimum disagreement count over all words of the candidate length.',
                   fixed_seam_warning='Non-closing lengths use the saved k in [0,N) cut; their fitted score need not be invariant to the choice of cut.',
                   exact_A_lengths=[r['length'] for r in a if r['minimum_disagreements']==0],
                   exact_B_lengths=[r['length'] for r in b if r['minimum_disagreements']==0],
                   best_A=sorted(a,key=lambda r:(r['minimum_disagreements'],r['length']))[:10],
                   best_B=sorted(b,key=lambda r:(r['minimum_disagreements'],r['length']))[:3],
                   checked_cases=len(rows), independent_counting_check=True,
                   historical_R347_closure_cases_reproduced=True, scientific_inputs_unchanged=True)
    (OUT/'pattern-length-match.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
