"""Curate R160 numerical comparisons; keep exhaustive ray samples ignored.

Run after refit_interior_poses.py and before check_interior_refit.py.
The displayed A1/B1 use original start ranks, never held-out selection.
"""
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_placement import ROOT,sha
from score_interior_poses import photo_samples,plot


def main():
    out=ROOT/'photo2/review/r160';path=out/'report.json'
    report=json.loads(path.read_text())
    if 'full_sample_details' in report:
        report=json.loads((ROOT/report['full_sample_details']['path']).read_text())
    assert len(report['cases'])==26,'Wait for all retained starts to finish'
    detail=ROOT/'photo2/output/r160/full-refits.json'
    detail.write_text(json.dumps(report,indent=2)+'\n')
    curated=json.loads(json.dumps(report))
    for c in curated['cases']:
        if c['case_index'] in [4,7]:continue
        for stage in ['before','after']:
            for bead in c[stage]['interiors']['beads']:
                for kind in ['core','route']:
                    missed=bead[kind].pop('missed_xy')
                    bead[kind]['missed_count']=len(missed)
                    bead[kind]['first_miss_xy']=missed[0] if missed else None
    curated['full_sample_details']=dict(path=str(detail.relative_to(ROOT)),sha256=sha(detail),
        reproduction='Run refit_interior_poses.py then summarize_interior_refit.py; exhaustive coordinates remain ignored here.')
    curated['curator_sha256']=sha(Path(__file__))
    curated['source_sha256']=sha(ROOT/'beads.pov')
    curated['image_sha256']=sha(ROOT/'beads-photo-2.jpg')
    curated['annotations_sha256']=sha(ROOT/'photo2/manual-labels-r146.json')
    path.write_text(json.dumps(curated,indent=2)+'\n')
    loops=json.loads((ROOT/'photo2/review/r157/report.json').read_text())
    samples=photo_samples(loops)
    a=next(c for c in report['cases'] if (c['case_index'],c['start_rank'])==(4,0))
    b=next(c for c in report['cases'] if (c['case_index'],c['start_rank'])==(7,0))
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    fig,axs=plt.subplots(5,4,figsize=(12,13),constrained_layout=True)
    for row,(n,s) in enumerate(samples.items()):
        plot(axs[row,0],rgb,s,f'Raw bead {n}')
        for col,(label,result) in enumerate([('A1 before',a['before']),('A1 refit',a['after']),('B1 unchanged',b['after'])],1):
            metric=next(m for m in result['interiors']['beads'] if m['number']==n)
            plot(axs[row,col],rgb,s,f'{label}: core {metric["core"]["passed"]}/{metric["core"]["total"]}',metric)
    fig.suptitle('Green: maker-confirmed interior loop. Orange / red x: model misowns an interior sample.\nA1 refit and B1 cover every loop/core; A1 still misses one withheld mark. No bead boundary is drawn.',fontsize=11)
    fig.savefig(out/'interior-refit.png',dpi=150);plt.close(fig)
    print(json.dumps(dict(full_bytes=detail.stat().st_size,curated_bytes=path.stat().st_size,
        fits=len(report['cases']),figure=str(out/'interior-refit.png')),indent=2))


if __name__=='__main__':main()
