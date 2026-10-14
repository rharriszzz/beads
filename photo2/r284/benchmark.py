"""Reuse certified POV appearance controls, with truth evaluator-only after inference.

These R283 frames are retrospective development controls, not fresh holdouts.
No geometric solver or renderer runs in R284A.
"""
from pathlib import Path
from PIL import Image
import numpy as np
from photo2.r282.common import ROOT,read,save,sha
from photo2.r282.phase1 import image_features
from photo2.r283.benchmark import evaluate
from .methods import cues,infer
from .run import OUT


def main():
    results=[]
    for i in range(16):
        folder=ROOT/'photo2/r283/results/confirmation'/f'scene-{i:02}'
        rgb=np.asarray(Image.open(folder/'photo.png').convert('RGB'));f=image_features(rgb);bank,ledger=cues(f)
        inference={m:infer(f,bank,m)[0] for m in 'ABC'}
        save(OUT/'synthetic'/f'scene-{i:02}.json.gz',dict(records=inference,cues=bank,photo_sha256=sha(folder/'photo.png')))
        truth=np.asarray(Image.open(folder/'identity.png'))[:,:,0].astype(int)-1;classes=read(folder/'truth.json')['classes']
        results.append(dict(scene=i,methods={m:evaluate(inference[m],truth,classes) for m in 'ABC'},identity_sha256=sha(folder/'identity.png')))
        print('control',i,{m:(results[-1]['methods'][m]['distinct_correct'],results[-1]['methods'][m]['false_or_wrong_body']) for m in 'ABC'},flush=True)
    summary={}
    for m in 'ABC':
        rr=[r['methods'][m] for r in results]
        totals={k:sum(r[k] for r in rr) for k in ('high','distinct_correct','duplicates','false_or_wrong_body','detected_eligible','mixed_body_support','background_majority')}
        totals['eligible']=sum(len(r['eligible']) for r in rr)
        totals['distinct_precision']=totals['distinct_correct']/max(1,totals['high'])
        totals['recall']=totals['detected_eligible']/totals['eligible']
        totals['colors']={c:dict(eligible=sum(r['eligible_colors'].get(c,0) for r in rr),detected=sum(len({h['owner'] for h in r['hits'] if h['correct_support'] and h['truth_color']==c and h['owner'] in r['eligible']}) for r in rr)) for c in ('red','yellow','black')}
        summary[m]=totals
    save(OUT/'synthetic-summary.json',dict(summary=summary,scenes=results,scope='Retrospective R283 POV confirmation frames. Now development controls, not fresh heldout validation. Real-photo comparisons take priority.'))
    print(summary,flush=True)

if __name__=='__main__':main()
