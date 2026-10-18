"""Small static scientific review: exact native crops plus vector overlays."""
import json,html,re,gzip
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r323.tracker import save
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def read(p):
    p=Path(p)
    return json.loads(p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()))
def main():
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');g=read(OUT/'full/graph.json');stages=[read(OUT/f'full/iteration-{i}.json') for i in range(4)];op={o['id']:o for o in g['observations']};black=read(OUT/'full/black-evidence.json');closure=read(OUT/'closure-investigation.json');cards=[];receipts=[]
    cases=[dict(name='upper',title='Upper bridge: a new context-derived hypothesis',center=[1660,285],before=0,after=1,caption='Window13 selects hypothesis10, generated from the160px context at window15. Two links to C-1659-0261 become eligible. Competing contexts still prevent calling this a resolved photographic identity.'),dict(name='inward',title='Inward bend: previously selected links are withdrawn',center=[1750,1625],before=2,after=3,caption='After further context-derived candidates compete, two links through K-1740-1575 are removed; new neighboring links appear. Window121 selects hypothesis19 from context118-240-0. This is a revised decision, not proof the removed links were wrong.'),dict(name='black',title='Native faint reflection enters the next inference pass',center=[290,1410],before=0,after=1,caption='The22 native pixels at(290.374,1410.186) are corroborated by colored-only fits with three distinct colored anchors across five overlapping parent windows. Three provisional links disappear in the no-provisional-state ablation. Distinct-body identity remains unconfirmed.'),dict(name='closure',title='Lower bend: winding is still conditional',center=[1485,3010],before=0,after=3,caption='Magenta dashed links are the four historical closure pairs. The compatible whole-hypothesis proposal changes from H=(213,201) in passes1–2 to(214,201) in pass3. The accepted two-window link graph has no winding cycle; changed contexts still disagree.')]
    for case in cases:
        x,y=case['center'];box=[x-180,y-130,x+180,y+130];crop=image.crop(box);fn=case['name']+'-native.png';crop.save(OUT/fn);assert np.array_equal(np.array(Image.open(OUT/fn)),np.array(image)[box[1]:box[3],box[0]:box[2]])
        receipts.append(dict(file=fn,crop_box=box,native_pixels_exact=True))
        def panel(stage,label):
            parts=[f'<svg viewBox="0 0 360 260" role="img" aria-label="{html.escape(label)}"><image href="{fn}" width="360" height="260"/>']
            if stage is not None:
                for e in stages[stage]['graph']['edges']:
                    a=np.array(op[e['source']]['xy'])-box[:2];b=np.array(op[e['target']]['xy'])-box[:2]
                    if np.any(a<0) or np.any(a>[360,260]) or np.any(b<0) or np.any(b>[360,260]):continue
                    parts.append(f'<path d="M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f}" stroke="#00e5ff" stroke-width="1.3" fill="none"/>')
                for o in g['observations']:
                    a=np.array(o['xy'])-box[:2]
                    if np.any(a<0) or np.any(a>[360,260]):continue
                    color='#ff55dd' if o.get('provisional') else '#fff';parts.append(f'<circle cx="{a[0]:.3f}" cy="{a[1]:.3f}" r="2.3" fill="none" stroke="{color}" stroke-width=".8"><title>{html.escape(o["id"])}</title></circle>')
                if case['name']=='closure':
                    for r in closure['old_four_pairs']:
                        a=np.array(op[r['source']]['xy'])-box[:2];b=np.array(op[r['target']]['xy'])-box[:2];parts.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#ff55dd" stroke-width="2" stroke-dasharray="4 3"/>')
                if case['name']=='black':
                    row=next(r for r in black['sites'] if r['admitted']);E=np.array(row['ellipse']['axes']);radii=np.array(row['ellipse']['radii_2sigma_px']);center=np.array(row['ellipse']['center_proxy_xy'])-box[:2];theta=np.linspace(0,2*np.pi,80);pts=(np.column_stack([np.cos(theta),np.sin(theta)])*radii)@E.T+center
                    parts.append('<polyline points="'+' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in pts)+'" stroke="#ffd760" fill="none" stroke-dasharray="3 3" stroke-width="1"/>')
            parts.append('</svg>');return '<figure>'+''.join(parts)+f'<figcaption>{label}</figcaption></figure>'
        cards.append(f'<article><h2>{case["title"]}</h2><p>{case["caption"]}</p><div class="panels">'+panel(None,'Original native pixels')+panel(case['before'],f'Before: pass{case["before"]}')+panel(case['after'],f'After: pass{case["after"]}')+'</div></article>')
    body='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R326 photographic review</title><style>body{font:16px/1.5 system-ui;max-width:1160px;margin:28px auto;padding:0 16px;color:#20252b;background:#fafafa}h1{font-size:27px}h2{font-size:21px}article{margin:28px 0;padding-top:12px;border-top:1px solid #bbb}.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}figure{margin:0}svg{display:block;width:100%;height:auto;background:#ddd}figcaption{font-size:13px}a{color:#15589c}p{max-width:95ch}@media(max-width:750px){.panels{grid-template-columns:1fr}}</style><h1>R326 — iterative feedback, unresolved photographic truth</h1><p><b>No reconstruction or pattern is adopted.</b> Three refinement passes retain937 original observations plus one provisional native site,1,833 candidate links and three components. R161 remains25/25 interior beads and45/45 links, zero wrong. All174 historical disagreements remain unresolved. The strict model interface has only17 links; broader candidates remain available.</p><p>Cyan: selected conditional links. White circles: measured bright supports, not bead centers. Magenta: provisional or unresolved relationships. Dashed yellow: exploratory same-shape visible-region envelope, not a measured body contour. Each left panel is an unchanged native crop.</p><p><a href="../../R326_REPORT.md">Report</a> · <a href="../../R326_REPRODUCE.md">Reproduce</a> · <a href="full/graph.json">Full candidate graph</a> · <a href="model-input.json">Strict model input and alternatives</a> · <a href="historical-contested.json">174-link diagnostic</a> · <a href="candidate-recall.json">R161 candidate recall</a> · <a href="verification.json">Verification</a></p>'''
    page=body+''.join(cards);chunks=re.split(r'(<[^>]*>)',page);in_style=False
    for i,chunk in enumerate(chunks):
        if chunk.startswith('<style'):in_style=True
        elif chunk.startswith('</style'):in_style=False
        elif not chunk.startswith('<') and not in_style:
            chunks[i]=re.sub(r'(?<=[a-z])(?=\d)',' ',chunk)
    (OUT/'index.html').write_text(''.join(chunks));save(OUT/'native-crop-verification.json',receipts)
if __name__=='__main__':main()
