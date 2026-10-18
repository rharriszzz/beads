"""Static original-RGB photographic evidence; never feeds the detector."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np
from photo2.r323.tracker import ROOT,CROP,save
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COLORS=['#00edff','#a2ff40']
def text(d,p,s,c='white',size=18):d.text(tuple(p),s,fill=c,font=ImageFont.truetype(FONT,size),stroke_width=2,stroke_fill='#111')
def canvas(im,crop,scale):return im.crop(crop).resize(((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale),Image.Resampling.NEAREST)
def point(p,crop,scale):return tuple((np.array(p)-crop[:2])*scale)
def dash(d,a,b,c,width=2):
    a,b=np.array(a),np.array(b)
    for t in np.arange(0,1,.12):d.line([tuple(a+t*(b-a)),tuple(a+min(1,t+.06)*(b-a))],fill=c,width=width)
def draw_graph(im,g,crop,scale,indices=False,labels=False,uncertain=False):
    out=canvas(im,crop,scale);d=ImageDraw.Draw(out);nodes={n['id']:n for n in g['intersections']}
    for e in g['graph']['edges']:
        if e['family']=='difference':continue
        a,b=[point(nodes[e[k]]['xy'],crop,scale) for k in ('source','target')]
        d.line([a,b],fill=COLORS[int(e['family'][-1])],width=max(1,scale))
    if uncertain:
        for e in g['graph']['unresolved_edges']:
            if e['family']=='difference':continue
            a,b=[point(nodes[e[k]]['xy'],crop,scale) for k in ('source','target')];dash(d,a,b,'#ffae45',max(1,scale))
    if labels:
        for t in g['tracks']:
            p=t['points'][len(t['points'])//2];text(d,point(p,crop,scale),t['id'],COLORS[t['family']],max(12,scale*6))
    if indices:
        for n in nodes.values():
            if not(crop[0]<=n['xy'][0]<crop[2] and crop[1]<=n['xy'][1]<crop[3]):continue
            p=point(n['xy'],crop,scale);c={'red':'#ff9494','yellow':'#ffff70','black':'white'}.get(n['color'],'#aaa')
            if n['status']=='confident bead':
                k=n['conditional_indices']['A'];s=f'{n["component"]}:{k:+d}{n["color"][0].upper()}'
                text(d,(p[0]+4,p[1]-16),s,c,max(12,scale*6))
                d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),outline=c)
            else:text(d,p,'?', '#ffae45',max(12,scale*6))
    return out

def generate(folder):
    folder=Path(folder);g=json.loads((folder/'graph.json').read_text());im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    canvas(im,CROP,1).save(folder/'raw.png')
    draw_graph(im,g,CROP,2,labels=True,uncertain=True).save(folder/'full-overlay.png')
    draw_graph(im,g,CROP,2).save(folder/'diagonals-only.png')
    draw_graph(im,g,CROP,2,indices=True).save(folder/'indexed.png')
    nodes={n['id']:n for n in g['intersections']}
    # Automatically select spatially distinct competing-row / skipped-observation cases.
    unresolved=sorted(g['graph']['unresolved_edges'],key=lambda e:(-e['competing_windows'],-len(e['intervening_observations']),-e['supporting_windows']))
    examples=[]
    for e in unresolved:
        p=np.mean([nodes[e[k]]['xy'] for k in ('source','target')],axis=0)
        if any(np.linalg.norm(p-np.array(x['center']))<85 for x in examples):continue
        examples.append(dict(center=p.tolist(),edge=e))
        if len(examples)==4:break
    rows=[]
    for j,x in enumerate(examples):
        px,py=map(int,x['center']);crop=(max(CROP[0],px-75),max(CROP[1],py-65),min(CROP[2],px+75),min(CROP[3],py+65));s=4
        raw=canvas(im,crop,s);annot=draw_graph(im,g,crop,s,uncertain=True)
        row=Image.new('RGB',(raw.width*2,raw.height+95),'#181818');row.paste(raw,(0,95));row.paste(annot,(raw.width,95));d=ImageDraw.Draw(row)
        e=x['edge'];text(d,(8,8),f'{j+1}: {e["source"]} → {e["target"]}',size=17)
        text(d,(8,33),f'{e["supporting_windows"]} supporting / {e["competing_windows"]} competing windows; '+', '.join(e['reasons']),size=14)
        text(d,(8,58),'Raw RGB | solid accepted; orange dashed unresolved (anchors are bright supports)',size=14)
        rows.append(row)
    if rows:
        result=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)),'#181818');y=0
        for r in rows:result.paste(r,(0,y));y+=r.height
        result.save(folder/'uncertainty.png')
    save(folder/'uncertainty-examples.json',examples)
    # Known failure geography is for requested review only, not inference.
    old=json.loads((ROOT/'photo2/r322/results/graph.json').read_text());crop=(1180,235,1350,365);s=5
    raw=canvas(im,crop,s);oldim=canvas(im,crop,s);d=ImageDraw.Draw(oldim)
    for t in old['tracks']:d.line([point(p,crop,s) for p in t['points']],fill=COLORS[t['family']],width=2)
    new=draw_graph(im,g,crop,s,uncertain=True)
    result=Image.new('RGB',(raw.width*3,raw.height+70),'#181818')
    for i,(r,title) in enumerate([(raw,'Original photograph'),(oldim,'R322 phase bands'),(new,'R323 joint proposals')]):result.paste(r,(i*raw.width,70));text(ImageDraw.Draw(result),(i*raw.width+10,20),title,size=23)
    result.save(folder/'failure-comparison.png')
    captions=[('full-overlay.png','Larger region: cyan F0, green F1, orange dashed unresolved; track IDs are fragment names.'),('diagonals-only.png','Clean view: accepted conditional diagonal chains only. Lines join evidence anchors, not bead centers.'),('indexed.png','Interior conditional A indices: component:index and color. B/reversals are in graph.json; ? remains unresolved or edge.'),('failure-comparison.png','Original photo / frozen R322 bands / R323 proposals. Requested failure and black-reflection geography; no maker links enter inference.'),('uncertainty.png','Automatically selected competing continuations, with original pixels alongside.'),('raw.png','Unmarked original RGB crop x900…1900, y0…700.')]
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R323 photographic tracking</title><style>body{font:16px system-ui;background:#181818;color:#eee;max-width:1800px;margin:20px auto;padding:0 14px}img{width:100%;height:auto}a{color:#80dfff}figure{margin:25px 0}p{max-width:1100px}</style><h1>R323 — joint photographic diagonal tracking</h1><p>Conditional image-supported topology, with local abstentions. Smooth lines and closed cycles do not certify correct bead identities. Overlapping observations are correlated. See held-out evaluation for measured errors.</p><p><a href="../../R323_REPORT.md">Report</a> · <a href="graph.json">Graph and all hypotheses</a> · <a href="validation.json">Held-out evaluation</a> · <a href="verification.json">Verification</a> · <a href="observation-pixels.json">Native supports</a></p>'''
    for file,caption in captions:
        if (folder/file).exists():html+=f'<figure><figcaption>{caption}</figcaption><a href="{file}"><img src="{file}" alt="{caption}"></a></figure>'
    html+='</html>';(folder/'index.html').write_text(html)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/r323/results');generate(ap.parse_args().output)
