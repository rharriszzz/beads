"""Reproducible stage driver. Inference never reads synthetic truth."""
import argparse,gzip,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from .photographic import detect,select,neighbors,PARAMETERS
from .predict import predict_pair,score_prediction,refit_ABC

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'photo2/review/r279'

def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if path.suffix=='.gz':path.write_bytes(gzip.compress(raw,mtime=0))
    else:path.write_bytes(raw)

def read(path):
    path=Path(path);return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def tangent(a,state):
    x,y=map(int,a['point']);mask=~state['known_background'];y0=max(0,y-75);x0=max(0,x-75);yy,xx=np.where(mask[y0:y+76,x0:x+76])
    if len(xx)<10:return None
    _,v=np.linalg.eigh(np.cov(np.c_[xx,yy].T));return float(np.arctan2(v[1,-1],v[0,-1]))

def gallery(rgb,obs,cases,folder,predictions=None):
    by={o['id']:o for o in obs};im=Image.fromarray(rgb);overview=im.copy();d=ImageDraw.Draw(overview)
    for j,case in enumerate(cases):
        a=by[case['anchor']];x,y=a['point'];d.ellipse((x-9,y-9,x+9,y+9),outline='cyan',width=3);d.text((x+10,y),str(j+1),fill='white')
        box=(x-55,y-55,x+55,y+55);raw=im.crop(box).resize((440,440));ann=raw.copy();draw=ImageDraw.Draw(ann)
        def pos(p):return ((p[0]-box[0])*4,(p[1]-box[1])*4)
        ids=[a['id']]+list(dict.fromkeys(r['id'] for m in case['methods'].values() for r in m['ranking'][:3]))
        for k,oid in enumerate(ids):
            o=by[oid];pt=pos(o['centroid']);col='cyan' if k==0 else 'lime';draw.ellipse((pt[0]-5,pt[1]-5,pt[0]+5,pt[1]+5),outline=col,width=2)
            for p in o['pixels'][::3]:
                px,py=pos(p);draw.point((px,py),fill=col)
            draw.text((pt[0]+5,pt[1]),'A' if k==0 else str(k),fill='white')
        panel=Image.new('RGB',(890,590),'white');panel.paste(raw,(0,25));panel.paste(ann,(450,25));dd=ImageDraw.Draw(panel);dd.text((5,5),f'{j+1:02d} {a["id"]} ({a["color"]}) RAW / interior proposals; not verified identities',fill='black')
        for k,method in enumerate('ABC'):
            m=case['methods'][method];top=m['ranking'][0];dd.text((5,470+18*k),f'{method}: {m["top"]} {m["status"]}, d={top["distance_px"]:.1f}px; interval={np.round(top["interval_px"],1)}; same-body? {top["cues"]["possible_same_body"]}',fill='black')
        for row in range((len(ids)-1+3)//4):
            names=[f'{k}={ids[k]}' for k in range(1+4*row,min(len(ids),5+4*row))]
            dd.text((5,528+16*row),'  '.join(names),fill='black')
        panel.save(folder/f'anchor-{j+1:02d}.jpg',quality=92)
    overview.thumbnail((800,1000));overview.save(folder/'anchors-overview.jpg',quality=92)

def process(name,path,oracle=None,limit=6):
    folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(path)).convert('RGB'));obs,state=detect(rgb);anchors=select(obs,21 if name=='real' else 6)
    save(folder/'observations.json.gz',obs);save(folder/'frozen-sample.json',dict(anchors=anchors,parameters=PARAMETERS,photo_sha256=sha(path),selection='quality, appearance cycle, geographic farthest points before predictions'))
    cases=neighbors(obs,anchors,state);save(folder/'test1.json',cases);gallery(rgb,obs,cases,folder)
    by={o['id']:o for o in obs};pairs=[]
    for case in cases[:limit]:
        bid=case['methods']['C']['top']
        if bid:pairs.append(('end-to-end',by[case['anchor']],by[bid]))
    if oracle is not None:
        a,b=read(oracle);pairs.append(('oracle',a,b))
    manifests=[]
    for number,(mode,a,b) in enumerate(pairs):
        label=f'pair-{number:02d}-{mode}';frozen=predict_pair(a,b,tangent(a,state))
        v=np.array(b['centroid'])-a['centroid'];baseline=[(np.array(b['centroid'])+z).tolist() for z in (v,np.array([-v[1],v[0]]),np.array([v[1],-v[0]]))]
        frozen['photographic_baseline_C_regions']=dict(centers=baseline,radius_px=a['uncertainty']+b['uncertainty'],rule='continue AB vector or turn +/-90 degrees; no C evidence')
        save(folder/(label+'-before-C.json.gz'),frozen);digest=sha(folder/(label+'-before-C.json.gz'))
        # First access to held-out detection coordinates for scoring is here.
        scored=[];excluded=[a['id'],b['id']]
        # Oracle A/B memberships excluded from automatic candidate pool via positive pixels.
        candidates=obs
        if mode=='oracle':
            occupied=set(map(tuple,a['pixels']+b['pixels']));candidates=[o for o in obs if np.mean([tuple(p) in occupied for p in o['pixels']])<.5]
        for h in frozen['hypotheses']:scored.append(score_prediction(h,candidates,excluded,state))
        save(folder/(label+'-after-C.json'),dict(frozen_sha256=digest,scores=scored))
        ds=[]
        # Matched-budget first qualifying alternative per hand; never revise original C.
        for hand in (-1,1):
            hits=[(h,s) for h,s in zip(frozen['hypotheses'],scored) if h['hand']==hand and s['match']]
            if not hits:continue
            h,s=hits[0];c=by[s['match']];fourth=refit_ABC(h,a,b,c)
            df=folder/(label+f'-h{hand:+d}-before-D.json.gz');save(df,fourth)
            dscore=score_prediction(fourth,candidates,excluded+[c['id']],state,'D');save(folder/(label+f'-h{hand:+d}-after-D.json'),dict(frozen_sha256=sha(df),score=dscore));ds.append(df.name)
        manifests.append(dict(mode=mode,A=a,B=b,before_C=label+'-before-C.json.gz',after_C=label+'-after-C.json',before_D=ds))
        # Review image shows frozen surfaces for one alternative from each hand.
        x,y=a['point'];box=(x-65,y-65,x+65,y+65);raw=Image.fromarray(rgb).crop(box).resize((390,390));panel=Image.new('RGB',(1180,425),'white');panel.paste(raw,(0,25));dr=ImageDraw.Draw(panel);dr.text((0,5),label+' raw / frozen C surfaces (physically rejected)',fill='black')
        for z,hand in enumerate((-1,1)):
            ann=raw.copy();d=ImageDraw.Draw(ann);hs=[h for h in frozen['hypotheses'] if h['hand']==hand]
            if hs:
                h=min(hs,key=lambda h:h['AB_loss'])
                for px,py in h['C_visible_pixels']:d.point(((px-box[0])*3,(py-box[1])*3),fill='lime')
                for o,text in ((a,'A'),(b,'B')):d.text(((o['centroid'][0]-box[0])*3,(o['centroid'][1]-box[1])*3),text,fill='cyan')
                dr.text((395*(z+1),5),f'h={hand:+d} AB={h["delta"]:+d} C={h["target"]:+d}',fill='black')
            panel.paste(ann,(395*(z+1),25))
        panel.save(folder/(label+'.jpg'),quality=92)
        print(name,label,'frozen',len(frozen['hypotheses']),'C conditional',sum(s['match'] is not None for s in scored),flush=True)
    save(folder/'pairs.json.gz',manifests)
    save(folder/'summary.json',dict(observations=len(obs),anchors=len(anchors),color_counts={c:sum(o['color']==c for o in obs) for c in ('red','yellow','black')},anchor_colors={c:sum(by[x]['color']==c for x in anchors) for c in ('red','yellow','black')},background_hue=state['background_hue']))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['generate','real','synthetic','evaluate','manifest']);args=parser.parse_args()
    if args.stage=='generate':
        from .synthetic import generate
        generate(OUT/'synthetic-scenes')
    elif args.stage=='real':process('real',ROOT/'beads-photo-2.jpg')
    elif args.stage=='synthetic':
        for f in sorted((OUT/'synthetic-scenes').glob('scene-*')):process(f.name,f/'photo.png',f/'oracle-pair.json',1)
    elif args.stage=='evaluate':
        from .evaluate import evaluate
        evaluate(OUT)
    else:
        sources=[ROOT/'beads-photo-2.jpg',ROOT/'beads.pov',ROOT/'photo2/bead_placement.py']+sorted((ROOT/'photo2/r279').glob('*.py'))+[ROOT/'photo2/r279/PROTOCOL.md']
        save(OUT/'source-manifest.json',{str(p.relative_to(ROOT)):sha(p) for p in sources})
        save(OUT/'evidence-manifest.json',{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='evidence-manifest.json' and '__pycache__' not in p.parts})
if __name__=='__main__':main()
