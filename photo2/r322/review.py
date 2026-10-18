"""Small static original-photo review; no detection or parameter fitting."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
from photo2.r322.tracker import ROOT,CROP

COLORS=['#00ecff','#96ff42'];SCALE=5;VIEW=(1180,215,1540,385)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
def text(draw,xy,s,color,size=20):draw.text(tuple(xy),s,fill=color,font=font(size),stroke_width=2,stroke_fill='#111111')
def xy(p):return tuple((np.array(p)-np.array(VIEW[:2]))*SCALE)
def base():
    raw=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB').crop(VIEW)
    return raw.resize((raw.width*SCALE,raw.height*SCALE),Image.Resampling.NEAREST)
def dashed(draw,points,color,width=3):
    for i in range(0,len(points)-1,6):draw.line(points[i:i+4],fill=color,width=width)
def generate(folder):
    folder=Path(folder);g=json.loads((folder/'graph.json').read_text());nodes={p['id']:p for p in g['intersections']}
    raw=base();raw.save(folder/'raw.png')
    clean=base();draw=ImageDraw.Draw(clean)
    for t in g['tracks']:
        pts=[xy(p) for p in t['points']];draw.line(pts,fill=COLORS[t['family']],width=3)
        # Each fragment has a unique integer display label; coordinate is separate.
        anchor=pts[len(pts)//2];text(draw,(anchor[0]+4,anchor[1]+3),t['id'],COLORS[t['family']],18)
    clean.save(folder/'diagonals-only.png')
    indexed=base();draw=ImageDraw.Draw(indexed)
    for e in g['graph']['edges']:
        if e['family']=='difference':continue
        p,q=nodes[e['source']],nodes[e['target']];pts=[xy(z) for z in np.linspace(p['xy'],q['xy'],30)]
        if e['status']!='accepted conditional' or e['priority']=='edge':dashed(draw,pts,'#ffa74a',2)
    for t in g['tracks']:
        pts=[xy(p) for p in t['points']];draw.line(pts,fill=COLORS[t['family']],width=2)
        text(draw,pts[len(pts)//2],t['id'],COLORS[t['family']],15)
    for n in nodes.values():
        x,y=xy(n['xy']);supported=n['status'] in ('confident bead','probable bead')
        c={'red':'#ff6868','yellow':'#ffff5a','black':'#ffffff'}.get(n['color'],'#ffa74a')
        if supported:
            draw.ellipse((x-7,y-7,x+7,y+7),outline=c,width=2)
            k=n['conditional_indices']['A'];label=f'{k:+d} {n["color"][0].upper()}'
            if n['status']!='confident bead':label+='?'
            text(draw,(x+8,y-22),label,c,18)
        else:
            draw.line((x-5,y-5,x+5,y+5),fill='#ffa74a',width=2);draw.line((x+5,y-5,x-5,y+5),fill='#ffa74a',width=2)
            text(draw,(x+6,y+5),'?', '#ffa74a',18)
    indexed.save(folder/'indexed.png')
    ev=base();draw=ImageDraw.Draw(ev)
    for o in g['observations']:
        x,y=xy(o['xy']);c={'red':'#ff6868','yellow':'#ffff5a','black':'#ffffff'}[o['color']]
        draw.ellipse((x-5,y-5,x+5,y+5),outline=c,width=2)
        text(draw,(x+6,y+5),o['id'],c,13)
    ev.save(folder/'observations.png')
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R322 photographic diagonals</title><style>body{font:16px system-ui;max-width:1800px;margin:24px auto;padding:0 16px;background:#181818;color:#eee}a{color:#80dfff}img{width:100%;height:auto}p{max-width:1000px}figure{margin:30px 0}figcaption{margin:8px 0}</style><h1>R322 — original-photograph diagonal experiment</h1><p>Image-derived candidate bands. Cyan F0 and green F1. Each fragment has its own integer label; these labels are not physical bead indices. Held-out result: 24/25 interior beads, 38/45 interior links, three wrong interior links. No expansion or pattern inference. Edges are lower priority.</p><p><a href="../../R322_REPORT.md">Scientific report</a> · <a href="graph.json">Graph, alternatives and timings</a> · <a href="observation-pixels.json">Native observation pixels</a> · <a href="validation.json">Held-out validation</a> · <a href="verification.json">Independent checks</a></p>'''
    for filename,caption in [('diagonals-only.png','Clean view: only the two sets of curved band fragments and unique labels.'),('indexed.png','Supported crossings: conditional A index (7a+6b) and R/Y/B. Orange × is an unsupported crossing, never a confirmed absence. ? marks uncertainty. B and global reversal alternatives are retained in graph.json. These provisional indices are not adopted.'),('heldout-validation.png','Post-freeze validation: white maker numbers, cyan automatic associations, orange wrong links. All 40 maker beads remain visible.'),('failure-and-recovery.png','First interior row switch, recovered 11–14–16 chain, and consistent interior examples. White dashed paths are held-out evidence, never tracker input.'),('raw.png','Unmarked original photographic crop, native coordinates x=1180…1540, y=215…385, enlarged 5× with nearest-neighbor sampling.'),('observations.png','Reused image-only R275 bright supports. These are evidence anchors, not bead centers; no angle gate joins them.')]:
        html+=f'<figure><figcaption>{caption}</figcaption><a href="{filename}"><img src="{filename}" alt="{caption}"></a></figure>'
    html+='</html>';(folder/'index.html').write_text(html)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/r322/results');args=ap.parse_args();generate(args.output)
