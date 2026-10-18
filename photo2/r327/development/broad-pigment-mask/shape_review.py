"""Supplementary native evidence for the reviewed shear correction."""
import html
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from .runner import ROOT,OUT,read,save

def main():
    g=read(OUT/'graph.json.gz');bad=read(ROOT/'photo2/r327/development/before-shape/graph.json.gz');shape=read(OUT/'shared-shape-evidence.json.gz');op={o['id']:o for o in g['observations']};native=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');cards=[];checks=[]
    for name,center in [('upper',[1660,285]),('lower',[1485,3010])]:
        x,y=center;box=[x-180,y-130,x+180,y+130];fn='shape-'+name+'-native.png';native.crop(box).save(OUT/fn);assert np.array_equal(np.array(Image.open(OUT/fn)),np.array(native)[box[1]:box[3],box[0]:box[2]])
        panels=[]
        for doc,title,color in [(None,'Original native pixels','#fff'),(bad,'Preserved first working choice','#ffae49'),(g,'Corrected working choice','#00e5ff')]:
            svg=f'<figure><svg viewBox="0 0 360 260"><image href="{fn}" width="360" height="260"/>'
            if doc:
                for e in doc['graph']['edges']:
                    a=np.array(op[e['source']]['xy'])-box[:2];b=np.array(op[e['target']]['xy'])-box[:2]
                    if np.any(a<0) or np.any(a>[360,260]) or np.any(b<0) or np.any(b>[360,260]):continue
                    svg+=f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="{color}" stroke-width="1.2"><title>{html.escape(e["source"])} / {html.escape(e["target"])}</title></path>'
            panels.append(svg+f'</svg><figcaption>{title}</figcaption></figure>')
        rows=[]
        for wi,w in enumerate(g['windows']):
            if np.linalg.norm(np.array(w['center'])-center)>130 or not bad['selected_window_states'][wi]:continue
            hi=bad['selected_window_states'][wi][0];h=w['hypotheses'][hi];ev=h['r327_shared_shape']
            if ev['penalty']<=1e-8:continue
            rows.append(f'<tr><td>{wi}/{hi}</td><td>{", ".join(f"{v:.2f}" for v in ev["declared_metric_lengths"])}</td><td>{ev["third_shortest_length"]:.2f}</td><td>{ev["penalty"]:.3f}</td><td>{html.escape(str([d["delta"] for d in ev["three_shortest_primitive_directions"]]))}</td></tr>')
            checks.append(dict(window=wi,hypothesis=hi,penalty=ev['penalty'],native_colored_anchors=shape['window_metrics'][wi]['colored_region_anchors']))
        cards.append(f'<h2>{name.title()} correction</h2><div class="panels">'+''.join(panels)+'</div><div class="scroll"><table><tr><th>Former window/state</th><th>Declared lengths in measured shape metric</th><th>Third shortest primitive length</th><th>Penalty</th><th>Shorter directions</th></tr>'+''.join(rows)+'</table></div>')
    # Independently check all component pixels, covariance arithmetic and local metrics.
    rgb=np.asarray(native,float)/255
    for r in shape['regions']:
        xy=np.array(r['pixels_xy']);colors=rgb[xy[:,1],xy[:,0]];assert np.all(colors[:,0]>1.5*colors[:,2]) and np.all(colors[:,0]>.16);delta=xy-np.rint(r['xy']);assert np.max(np.sum(delta*delta,axis=1))<=19**2;mean=xy.mean(0);cov=(xy-mean).T@(xy-mean)/(len(xy)-1);assert np.allclose(cov,r['covariance_px2'],atol=1e-10)
    for w,m in zip(g['windows'],shape['window_metrics']):
        rr=[r for r in shape['regions'] if np.linalg.norm(np.array(r['xy'])-w['center'])<100];assert [r['observation'] for r in rr]==m['colored_region_anchors'];cov=np.median([r['covariance_px2'] for r in rr],axis=0);ev,E=np.linalg.eigh(cov);assert np.allclose((E*np.clip(ev,16,100))@E.T,m['covariance_px2'],atol=1e-10)
    body='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R327 shared-shape correction</title><style>body{font:16px/1.5 system-ui;max-width:1160px;margin:24px auto;padding:0 16px}.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}figure{margin:0}svg{width:100%;height:auto}table{border-collapse:collapse;font-size:13px}td,th{border:1px solid #aaa;padding:5px}.scroll{overflow:auto}@media(max-width:750px){.panels{grid-template-columns:1fr}}</style><h1>R327 — correction from native shared bead geometry</h1><p>The first sequence-weighted result could choose a sheared lattice: coordinates fit the same observed supports while some declared neighbors follow longer directions. Visible colored pigment regions provide a common projected shape metric. The corrected score penalizes a declared direction only when a shorter primitive direction is available in that metric. All colors use the same metric; no bead count or exact angle is imposed.</p><p>The 623 measured colored regions are partial visible pigment, not complete contours. This is conditional photographic geometry evidence, not a proof of contact. Every old candidate and the complete earlier result remain available.</p><p><a href="index.html">Main review</a> · <a href="shared-shape-evidence.json.gz">Native pixels and shared metrics</a> · <a href="shared-shape-selection.json">Complete score comparison</a></p>'''
    (OUT/'shared-shape-review.html').write_text(body+''.join(cards));page=(OUT/'index.html').read_text();needle='<p><a href="../../R327_REPORT.md">Report</a>';addition='<p><a href="shared-shape-review.html">See the native shared-shape correction and preserved earlier working choice</a>. Shared colored-bead geometry resolves the sheared-neighbor preference found during review.</p>'
    if addition not in page:page=page.replace(needle,addition+needle)
    (OUT/'index.html').write_text(page);save(OUT/'shared-shape-verification.json',dict(passed=True,colored_regions=len(shape['regions']),native_pigment_pixels=sum(len(r['pixels_xy']) for r in shape['regions']),window_metrics=len(shape['window_metrics']),reviewed_penalized_states=checks,native_crops_exact=True))
if __name__=='__main__':main()
