"""Curated known-N score checks; these points are synthetic, not maker marks."""
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-tangent-mpl')
import matplotlib.pyplot as plt
import numpy as np

from center_marks import score_counts
from tangent_viewer import ViewerStore, ROOT
from tangent_circles import sha
from label_beads import atomic_json


def main():
    output=ROOT/'photo2/review/r184';output.mkdir(parents=True,exist_ok=True)
    records=[]
    with tempfile.TemporaryDirectory() as folder:
        store=ViewerStore(Path(folder)/'choice.json')
        for hand in [-1,1]:
            frame=store.frame(2698,hand)
            xy=np.array(frame['circles'])[np.linspace(0,len(frame['circles'])-1,12,dtype=int),:2]
            points=[dict(id=f'synthetic-{i}',number=i+1,x=float(x),y=float(y)) for i,(x,y) in enumerate(xy)]
            document=dict(schema_version=1,kind='synthetic_outward_points',source=store.source,points=points,revision=1)
            result=score_counts(document,list(range(2618,2779)),hand,store.frame)
            assert result['best']['count']==2698 and result['best']['sse']==0
            records.append(dict(result=result,model_reference=store.configuration(2698,hand)))
    fig,axes=plt.subplots(2,1,figsize=(10,7),layout='constrained')
    for ax,record in zip(axes,records):
        result=record['result'];rows=result['rows']
        ax.plot([r['count'] for r in rows],[r['sse'] for r in rows],'.-',color='#008c9e')
        ax.scatter([2698],[0],color='#bd6010',label='Known synthetic count 2698',zorder=4)
        ax.set(title=f"Independent synthetic test: 12 outward points, hand {result['hand']:+d}",
               xlabel='Total model bead count',ylabel='Sum of squared distances (pixels²)')
        ax.grid(alpha=.25);ax.legend()
    fig.suptitle('Score verification only — no maker centers or recovered photo count',fontsize=13)
    fig.savefig(output/'synthetic-score-check.png',dpi=150);plt.close(fig)
    files=['beads-photo-2.jpg','beads.pov','photo2/center_marks.py','photo2/tangent_viewer.py',
           'photo2/tangent_circles.py','photo2/bead_placement.py','photo2/curved_surface_fit.py',
           'photo2/local_surface_fit.py','photo2/spline-seed-r175.json','photo2/review_center_scores.py',
           'photo2/test_center_marks.py','photo2/test_tangent_viewer.py',
           'photo2/tangent_viewer/app.mjs','photo2/tangent_viewer/marks.mjs',
           'photo2/tangent_viewer/marks.test.mjs','photo2/tangent_viewer/viewport.mjs',
           'photo2/tangent_viewer/index.html','photo2/tangent_viewer/style.css']
    atomic_json(output/'validation.json',dict(
        request='R184–R185',status='Synthetic score checks only; no maker center marks exist yet.',
        records=records,source_sha256={p:sha(ROOT/p) for p in files},
        figure_sha256=sha(output/'synthetic-score-check.png'),
        checks='13 Python tests; 7 JavaScript named checks; syntax checks. No browser, server or launcher interaction test.',
        reproduction=['.venv/bin/python photo2/review_center_scores.py',
                      '.venv/bin/python -m unittest discover -s photo2 -p test_center_marks.py',
                      '.venv/bin/python -m unittest discover -s photo2 -p test_tangent_viewer.py',
                      'node photo2/tangent_viewer/marks.test.mjs','node photo2/tangent_viewer/viewport.test.mjs']))
    print(json.dumps(dict(figure=str(output/'synthetic-score-check.png'),best_counts=[r['result']['best']['count'] for r in records])))


if __name__=='__main__':main()
