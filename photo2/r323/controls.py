"""Predeclared overlap ablations, fixed before R161 evaluation."""
import json,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r323 import tracker as t

def main(folder):
    folder=Path(folder);g=json.loads((folder/'graph.json').read_text());im=ImageOps.exif_transpose(Image.open(t.ROOT/'beads-photo-2.jpg')).convert('RGB');data=t.base.preprocess(im,t.CROP)
    controls={}
    for name,windows,beam in [('local_winners_without_joint_selection',g['windows'],[dict(score=0.,choices=[0 if w['hypotheses'] else None for w in g['windows']])])]:
        start=time.perf_counter();nodes,graph,tracks,selected=t.infer_graph(g['observations'],windows,beam,data)
        controls[name]=dict(intersections=nodes,graph=graph,tracks=tracks,selected=selected,seconds=time.perf_counter()-start)
    chosen=g['joint_beam'][0]['choices'];comparisons=[]
    for wi,hi in enumerate(chosen):
        if hi is None:continue
        w=g['windows'][wi];best=w['hypotheses'][0];h=w['hypotheses'][hi]
        comparisons.append(dict(window=wi,crop=w['crop'],local_rank=hi,local_best_score=best['score'],selected_score=h['score'],
            overlap_with_local_winner=t.overlap(best,h),selected_observations=len(h['assignments'])))
    controls['joint_decisions']=comparisons
    controls['note']='Same frozen photographic candidates. Local-only control removes the joint beam, retaining the same edge consensus checks. Not a statistically independent image dataset.'
    t.save(folder/'controls.json',controls)
if __name__=='__main__':main(t.ROOT/'photo2/r323/results')
