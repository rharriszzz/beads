"""Paired, scene-cluster comparison of the two pre-frozen methods."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .common import OUT, ROOT, read, save
from .detector import decide


def compare(split, level):
    rules = read(OUT / 'confirmation-freeze.json')['rules']
    all_rows = read(OUT / (split + '-evaluation.json.gz'))
    rows = [{**r, 'accepted': decide(r, rules, r['method'])['status'] == 'supported'}
            for r in all_rows if r['method'] in ('material', 'combined')
            and r['kind'] in ('present', 'removed') and r['level'] == level]
    scenes = sorted({r['scene'] for r in rows})
    methods = ('material', 'combined')
    # Rows are whole scenes; all correlated targets and paired negatives stay together.
    counts = np.zeros((len(scenes), 2, 5))
    for i, scene in enumerate(scenes):
        for j, method in enumerate(methods):
            rr = [r for r in rows if r['scene'] == scene and r['method'] == method]
            counts[i, j] = [sum(not r['negative'] for r in rr),
                            sum(r['accepted'] and r['correct'] for r in rr),
                            sum(r['accepted'] and r['negative'] for r in rr),
                            sum(r['accepted'] and not r['negative'] and not r['correct'] for r in rr),
                            sum(r['accepted'] for r in rr)]
    rng = np.random.default_rng(281404)
    draws = counts[rng.integers(0, len(scenes), (2000, len(scenes)))].sum(axis=1)
    recall_delta = (draws[:, 0, 1] - draws[:, 1, 1]) / draws[:, 0, 0]
    false_delta = (draws[:, 0, 2] - draws[:, 1, 2]) / draws[:, 0, 0]
    positive = {m: {(r['scene'], r['target']) for r in rows if r['method'] == m
                    and r['accepted'] and r['correct']} for m in methods}
    gained = sorted(positive['material'] - positive['combined'])
    lost = sorted(positive['combined'] - positive['material'])
    return dict(populated_scenes=len(scenes), level=level,
                material_only_correct=gained, combined_only_correct=lost,
                recall_difference95=np.quantile(recall_delta, [.025, .975]).tolist(),
                false_absent_difference95=np.quantile(false_delta, [.025, .975]).tolist(),
                note='Material minus combined; 2000 paired scene bootstrap draws. '
                     'Zero errors cannot establish a zero population rate.')


def main():
    fresh = read(OUT / 'confirmation-frozen-summary.json')
    paired = {split: [compare(split, level) for level in (0., .05, .1)]
              for split in ('heldout', 'confirmation')}
    rules = read(OUT / 'confirmation-freeze.json')['rules']
    real = [dict(id=r['id'], kind=r['kind'], combined=r['result']['status'],
                 material=decide(r['result'], rules, 'material')['status'])
            for r in read(OUT / 'real/measurements.json')['rows']]
    save(OUT / 'confirmation-comparison.json', dict(
        fixed_rule_comparisons=paired,
        fresh_summary=fresh,
        real_decision_comparison=real,
        limitation='Follow-up same-family evidence; original held-out results were known. '
                   'No rules, model selection or production behavior changed.'))
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for method in ('R280', 'material', 'combined'):
        values = [fresh[method][f'paired:{level}'] for level in (0., .05, .1)]
        axes[0].plot([0., .05, .1], [s['recall'] for s in values], 'o-', label=method)
        axes[1].plot([0., .05, .1], [s['false_rate'] for s in values], 'o-', label=method)
    for ax, title in zip(axes[:2], ('Correct present targets', 'False absent confirmations')):
        ax.set(xlabel='Position error / diameter', ylabel='Fraction', title=title, ylim=(-.03, 1.03))
        ax.legend(fontsize=8)
    kinds = ('paper', 'neighbor', 'identity', 'phase', 'duplicate')
    x = np.arange(len(kinds))
    for j, method in enumerate(('R280', 'material', 'combined')):
        axes[2].bar(x + (j - 1) * .25,
                    [fresh[method][f'{kind}:d0.0:r0.0']['false_rate'] for kind in kinds],
                    .25, label=method)
    axes[2].set(xticks=x, xticklabels=kinds, ylabel='False confirmation fraction',
                title='Incorrect controls', ylim=(0, 1.03))
    axes[2].tick_params(axis='x', rotation=25)
    axes[2].legend(fontsize=8)
    fig.suptitle('Fresh seed281403 confirmation — unchanged rules')
    fig.tight_layout()
    fig.savefig(ROOT / 'photo2/review/r281/confirmation.png', dpi=170)
    plt.close(fig)
    print(paired['confirmation'])


if __name__ == '__main__':
    main()
