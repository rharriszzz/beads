"""Plot the frozen R186 maker score without rescanning or changing live files."""
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-tangent-mpl')
import matplotlib.pyplot as plt

from tangent_circles import ROOT, sha
from label_beads import atomic_json


def main():
    output=ROOT/'photo2/review/r186'
    centers=json.loads((output/'centers.json').read_text())
    score=json.loads((output/'centers-score.json').read_text())
    assert centers['source']==score['source']
    assert centers['points']==score['centers']['points']
    rows=score['rows'];best=score['best']
    lo=max(rows[0]['count'],best['count']-60);hi=min(rows[-1]['count'],best['count']+60)
    near=[r for r in rows if lo<=r['count']<=hi]
    fig,axes=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    for ax,subset,title in zip(axes,[rows,near],['Saved full scan','Detail near the lowest sampled score']):
        ax.plot([r['count'] for r in subset],[r['sse'] for r in subset],'.-',markersize=2,color='#008c9e')
        ax.scatter([best['count']],[best['sse']],color='#bd6010',zorder=5,label=f"Lowest sampled: {best['count']}, SSE {best['sse']:.3f}")
        ax.set(title=title,xlabel='Total model bead count',ylabel='Sum of squared distances (pixels²)')
        ax.grid(alpha=.25);ax.legend()
    fig.suptitle(f"{len(centers['points'])} saved maker centers · hand {score['hand']:+d} · fixed-model proxy score",fontsize=14)
    fig.savefig(output/'saved-score-graph.png',dpi=150);plt.close(fig)
    files=['photo2/center_marks.py','photo2/tangent_viewer.py','photo2/test_center_marks.py',
           'photo2/tangent_viewer/app.mjs','photo2/tangent_viewer/index.html','photo2/tangent_viewer/style.css',
           'photo2/tangent_viewer/score_view.mjs','photo2/tangent_viewer/score_view.test.mjs','photo2/review_saved_scores.py']
    atomic_json(output/'summary.json',dict(request='R186',
        inputs={str(p.relative_to(ROOT)):sha(p) for p in [output/'centers.json',output/'centers-score.json']},
        maker_centers= len(centers['points']),center_revision=centers['revision'],score_center_revision=score['centers']['revision'],
        matching_points=True,hand=score['hand'],samples=len(rows),range=[rows[0]['count'],rows[-1]['count']],
        best={k:v for k,v in best.items() if k!='matches'},
        limitation='Lowest score is near the upper scan boundary; this fixed-phase, imperfect-centerline, visible-center/outward-point proxy does not establish N.',
        source_sha256={p:sha(ROOT/p) for p in files},figure_sha256=sha(output/'saved-score-graph.png'),
        checks='14 Python / 10 named JS checks and syntax checks. No browser/server/launcher interaction test.',
        reproduction=['.venv/bin/python photo2/review_saved_scores.py',
                      '.venv/bin/python -m unittest discover -s photo2 -p test_center_marks.py',
                      '.venv/bin/python -m unittest discover -s photo2 -p test_tangent_viewer.py',
                      'node photo2/tangent_viewer/score_view.test.mjs',
                      'node photo2/tangent_viewer/marks.test.mjs','node photo2/tangent_viewer/viewport.test.mjs']))
    print(json.dumps(dict(figure=str(output/'saved-score-graph.png'),centers=len(centers['points']),best_sampled_count=best['count'])))


if __name__=='__main__':main()
