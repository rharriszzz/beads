"""Compact offline review using only original-photo crops and measured overlays."""
import argparse,csv,html,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import binary_erosion
from photo2.r329.common import ROOT,read,canonical
from photo2.r329.photographic_diagnostics.explore import OBS,CO,measure
from photo2.r329.photographic_diagnostics.continuity import CASES

COL={'red':'#e63f48','yellow':'#f6cb39','black':'#20232b','?':'#b5bac3'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(ROOT/'photo2/r330'));args=ap.parse_args();root=Path(args.root);out=root/'review';out.mkdir(exist_ok=True);assets=out/'assets';assets.mkdir(exist_ok=True)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');patterns=read(root/'results/patterns.json.gz');ref=read(root/'refinement/refinement.json.gz');diag=read(root/'photography/photography.json.gz');figures=[]
    def crop(key,bbox):
        photo.crop(bbox).save(assets/(key+'.png'));figures.append(dict(file='assets/'+key+'.png',bbox=list(bbox)));return 'assets/'+key+'.png'
    def svg(key,bbox,ids,state,rows=(),predictions=None,highlight=None,extra=''):
        name=crop(key,bbox);x0,y0,x1,y1=bbox;W=x1-x0;H=y1-y0;pts={o:(measure(OBS[o])[0] if OBS[o]['color']!='black' and measure(OBS[o]) is not None else np.array(OBS[o]['xy'])) for o in ids}
        def point(o):return pts[o]-[x0,y0]
        text=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{key}"><image href="{name}" width="{W}" height="{H}"/><g class="overlay">']
        for family,seq,steps in rows:
            for a,b,step in zip(seq,seq[1:],steps):
                if a not in pts or b not in pts:continue
                x,y=point(a);xx,yy=point(b);color=['#00dcff','#8aff58'][family];dash=' stroke-dasharray="3 2"' if step>1 else ''
                text.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="{color}" stroke-width="1.1"{dash}><title>{a} → {b}: family {family}, {step} steps</title></path>')
        if highlight:
            a,b=highlight[:2];color=highlight[2] if len(highlight)>2 else '#00dcff';x,y=point(a);xx,yy=point(b);text.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="#ff36db" stroke-width="3.2"/><path d="M{x},{y} L{xx},{yy}" stroke="{color}" stroke-width="1.2"/>')
        if predictions:
            for o,p in predictions.items():
                x,y=np.array(p['prediction'])-[x0,y0];xx,yy=np.array(p['observed'])-[x0,y0]
                text.append(f'<path d="M{x-3},{y-3} l6,6 m-6,0 l6,-6 M{x},{y} L{xx},{yy}" stroke="#ff4fdf" stroke-width="1.1" stroke-dasharray="2 1"><title>{o}: colored-target miss {p["error"]:.2f}px</title></path>')
        text.append(extra)
        for j,o in enumerate(ids):
            x,y=point(o);lx=x+7;ly=y-7
            text.append(f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="white" stroke-width=".7"/><path d="M{x},{y} L{lx},{ly}" stroke="white" stroke-width=".5"/><circle cx="{lx}" cy="{ly}" r="4.8" fill="#122039" stroke="white" stroke-width=".5"/><text x="{lx}" y="{ly+2}" text-anchor="middle" font-size="6" fill="white">{j+1}</text>')
        text.append('</g></svg>');return ''.join(text)
    def keytable(ids,states):
        rows=[]
        for j,o in enumerate(ids):
            vals=[]
            for st in states:
                co=CO[st];vals.append(str(int(np.dot(co[o],[7,6]))) if o in co else 'unindexed')
            rows.append(f'<tr><td>{j+1}</td><td>{o}</td><td>{OBS[o]["color"]}</td>'+''.join(f'<td>{v}</td>' for v in vals)+'</tr>')
        return '<div class="scroll"><table><tr><th>Label</th><th>Stable ID</th><th>Recorded color</th>'+''.join(f'<th>{s}: A index</th>' for s in states)+'</tr>'+''.join(rows)+'</table></div>'
    content=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R330 pattern recovery</title><style>body{max-width:1140px;margin:24px auto;padding:0 16px;font:16px/1.45 system-ui;color:#182438;background:#f7f9fc}a{color:#065a9d}h2{margin-top:36px}svg,img{max-width:100%;height:auto}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}figcaption{margin:8px 0}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px;width:100%}th,td{padding:6px;text-align:left;border-bottom:1px solid #ced6df}button{padding:10px}code{overflow-wrap:anywhere}.note{background:#e3edf8;padding:12px}.motif{overflow:auto}details{margin:12px 0}summary{cursor:pointer;font-weight:600}@media(max-width:700px){.pair{grid-template-columns:1fr}}</style><h1>A repeating motif, and where the observations disagree</h1><p class="note"><b>No human decision is required now.</b> The new evidence supports a partial 208-position motif and six provisional color corrections. G remains a conflict between local photographic geometry and broader pattern predictions. The working graph is preserved.</p><p><a href="../../R330_REPORT.md">Scientific report</a> · <a href="../../R330_REPRODUCE.md">Reproduction</a> · <a href="../verification.json">Verification</a> · <a href="motif.csv">Residue evidence</a> · <a href="suspects.csv">All suspected observations</a></p><p>All bead indices below use <b>A = 7a + 6b</b>, with C-1302-0316 at index zero. Cyan is [1,0]; green is [0,1]. Numbered circles identify measured supports or partial pigment, never black-bead centers. Every unobserved position still contains a physical bead.</p><button id="toggle">Hide / show photographic overlays</button><h2>Partial motif: 154 of 208 entries have repeated consensus</h2><p>Each known entry has ≥80% weighted agreement, at least three supporting observations and at least three photographic sections. “?” retains uncertainty. This exploratory full-data display is separate from the original held-out test. A complete exact period 208 would require a compatible count; 2704 = 13 × 208 is compatible but is not an adopted count.</p>']
    entries=ref['full208_entries'];motif=ref['vote208_motif'];tiles=['<svg viewBox="0 0 1040 360" role="img" aria-label="208 position partial color motif">']
    for i,ch in enumerate(motif):
        x=i%26*40;y=i//26*44;col=COL[{'R':'red','Y':'yellow','B':'black','?':'?'}[ch]]
        tiles.append(f'<g><title>Residue {i}; {entries[i]["supporting_observations"]} supporting observations; {len(entries[i]["supporting_sections"])} sections</title><rect x="{x+1}" y="{y+13}" width="37" height="26" fill="{col}"/><text x="{x+19}" y="{y+10}" text-anchor="middle" font-size="10">{i}</text><text x="{x+19}" y="{y+31}" text-anchor="middle" font-size="13" fill="{"white" if ch=="B" else "#182438"}">{ch}</text></g>')
    content.append(''.join(tiles)+'</svg><p>The initial, more conservative period-104 motif predicted 143/143 held-out colors at 48.3% held-out coverage. Follow-up 208-position prediction reaches 91.9% agreement across all 900 original labels with sections left out in turn; this latter evaluation is exploratory.</p>')
    with open(out/'motif.csv','w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['residue','proposed_color','plurality','supporting_observations','supporting_sections','observed_repeats','weighted_agreement'])
        for e,ch in zip(entries,motif):writer.writerow([e['residue'],ch,e['plurality'],e['supporting_observations'],len(e['supporting_sections']),e['observed_repeats'],e['weighted_agreement']])
    with open(out/'suspects.csv','w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['id','x','y','A_index','residue208','recorded','pattern_prediction','strong_repetition','appearance_suggestion','appearance_min_vote','provisional_correction'])
        for s in ref['suspects']:writer.writerow([s['id'],*s['xy'],s['index'],s['residue'],s['color'],s['prediction'],s['strong'],s['photographic_color_audit']['suggestion'],s['photographic_color_audit']['min_vote'],s['correction_candidate']])
    content.append('<h2>Six provisional red → black color corrections</h2><p>The pattern flags these sites; separate RGB appearance comparisons against distant observations support dark-bead interpretations. Every one favors black in all nine radius/neighbor controls. The strict 80%-in-every-control rule accepted none. These exploratory stable-majority proposals remain separate from the original labels.</p>')
    for s in ref['suspects']:
        if not s['correction_candidate']:continue
        o=s['id'];x,y=OBS[o]['xy'];bbox=[round(x)-55,round(y)-55,round(x)+55,round(y)+55]
        nearby=[q for q in CO['working'] if q!=o and np.linalg.norm(np.array(OBS[q]['xy'])-[x,y])<50];ids=[o]+sorted(nearby,key=lambda q:np.linalg.norm(np.array(OBS[q]['xy'])-[x,y]))[:7];rows=[]
        for a in ids:
            for b in ids:
                d=np.array(CO['working'][b])-CO['working'][a]
                if tuple(d) in [(1,0),(0,1)]:rows.append((int(d[1]),[a,b],[1]))
        evidence=s['photographic_color_audit'];prefix='color-'+o
        content.append(f'<details><summary>{o}: A index {s["index"]}; red → black candidate</summary><div class="pair"><figure>{svg(prefix+"-old",bbox,ids,"working",rows)}<figcaption>Original color label: red. Circle 1 marks the recorded bright support.</figcaption></figure><figure>{svg(prefix+"-new",bbox,ids,"working",rows)}<figcaption>Hypothesis: black; identical pixels, index and connections.</figcaption></figure></div><p>{len(s["support"])} distant supporting observations, {len(set(v["section"] for v in s["support"]))} sections; smallest black vote {evidence["min_vote"]:.1%}. Highlight color alone does not identify bead pigment.</p>{keytable(ids,["working"])}</details>')
    # G: display the actual multi-target prediction differences on matched crops.
    ids=['P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325','E5-1633-0278','E5-1607-0290','C-1582-0272','C-1608-0253','C-1559-0252','C-1659-0261','NEW-1621-315']
    rows=[(0,['C-1559-0252','C-1582-0272','E5-1607-0290'],[1,1]),(0,['C-1608-0253','E5-1633-0278'],[1]),(1,['C-1582-0272','C-1608-0253'],[1]),(1,['E5-1607-0290','E5-1633-0278','C-1659-0261'],[1,1])]
    content.append('<h2>G: local photographic improvement is feasible, but creates other conflicts</h2><p>Magenta crosses predict colored observations 1–4 from the same 11 reference observations (excluded targets). Dashed lines show the actual misses. The cyan connection with a magenta border changes incoming row. These are pigment predictions, not black-body positions.</p><div class="pair">')
    for st in ['working','early']:
        f=next(r for r in diag['G']['variants'] if r['margin']==0 and r['degree']==2 and r['radius']==18 and r['state']==st)
        content.append('<figure>'+svg('g-'+st,[1510,205,1730,370],ids,st,rows,f['targets'],('E5-1633-0278' if st=='working' else 'E5-1607-0290','P5-1645-0309'))+f'<figcaption>{st}: target misses '+', '.join(f'{t["error"]:.1f}px' for t in f['targets'].values())+'</figcaption></figure>')
    content.append('</div>'+keytable(ids,['working','early'])+'<p>Windows 10–14 suffice to incorporate the preferred local assignments and reconnect to the original suffix, yielding H=(214,200), not the historical H=(214,176). That best photographic-score candidate creates 394 substantial pattern likelihood losses. The best tested same-winding repair changes 60 observations and still loses pattern prediction. Neither has passed joint evidence checks.</p><p>The historical −175 difference is a staircase of 25 green-coordinate changes, not a single −7 error propagated unchanged. No winding vote is requested.</p>')
    ids=['C-1125-2900','C-1119-2879','C-1098-2901','NEW-1074-2896','C-1144-2947','E5-1151-2893','C-1209-2970','C-1198-2943','C-1189-2919','C-1095-2873','C-1085-2813','C-1064-2868','C-1058-2815']
    content.append('<h2>H: omitted red material and expanded reference tests</h2><p>Circle 5 is the visible red observation missing from the lower alternative. Both panels show it. Crosses predict targets from the same expanded reference cohort; the lower alternative has no assignment to predict target 5. Nearby shared directions are drawn; the complete 11-reference cohort is in the numerical ledger.</p><div class="pair">')
    for st in ['working','lower']:
        f=next(r for r in diag['H']['variants'] if r['margin']==120 and r['degree']==2 and r['radius']==18 and r['state']==st)
        content.append('<figure>'+svg('h-'+st,[1035,2785,1260,3010],ids,st,CASES['H']['rows'][:5],f['targets'],('C-1125-2900','E5-1151-2893','#8aff58' if st=='working' else '#ffb94b'))+f'<figcaption>{st}; target 1 miss {f["targets"][ids[0]]["error"]:.1f}px; circle 5 '+('indexed; highlighted 1→6: [0,−1]' if st=='working' else 'unindexed; highlighted 1→6: [1,−1]')+'</figcaption></figure>')
    content.append('</div>'+keytable(ids,['working','lower'])+'<p>All 73 single-patch reinsertion attempts fail attachment. Four-window replay finds 81 complete repairs, including two preserving the lower winding; these alter other assignments and are not automatic corrections. The original working assignment retains the stronger current support. Wider curved fits are sensitive, so the lower alternative remains archived.</p>')
    content.append('<h2>F: registration explains part of the colored-material mismatch</h2><p>A translation fitted only to the index-zero yellow region moves the frozen model raster +8 px horizontally and −4 px vertically. Its reference coverage rises from 59% to 99%; the two other colored regions still reach only about 49%. The translated raster is a registration diagnostic, not a newly fitted or certified physical reconstruction.</p>')
    m=np.load(ROOT/'photo2/r329/photographic_diagnostics/model-geometry.npz');owner=m['owner'].reshape(m['shape']);mbox=m['bbox'];step=float(m['step']);bbox=[1230,208,1510,365];ids=['C-1302-0316','C-1391-0312','C-1422-0264','C-1251-0290','C-1277-0302','C-1339-0277','P5-1364-0299','NEW-1442-248'];rows=[(0,ids[3:5]+ids[:1],[1,1]),(0,['C-1339-0277','P5-1364-0299','C-1391-0312'],[1,1]),(1,['C-1302-0316','C-1339-0277'],[2]),(1,['C-1391-0312','C-1422-0264','NEW-1442-248'],[2,1])];content.append('<div class="pair">')
    for name,dx,dy in [('frozen',0,0),('translated',8,-4)]:
        extra=[]
        for target in diag['F']['rows']:
            j=int(np.flatnonzero(m['indices']==target['address'])[0]);mask=owner==j;edge=mask&~binary_erosion(mask);yy,xx=np.nonzero(edge)
            for x,y in zip(xx[::2],yy[::2]):extra.append(f'<rect x="{x*step+mbox[0]+dx-bbox[0]}" y="{y*step+mbox[1]+dy-bbox[1]}" width=".6" height=".6" fill="#ff3de1"/>')
            for x,y in target['pixels']:
                xx=int(round((x-dx-mbox[0])/step));yy=int(round((y-dy-mbox[1])/step));inside=0<=xx<owner.shape[1] and 0<=yy<owner.shape[0] and owner[yy,xx]==j
                if not inside:extra.append(f'<rect x="{x-bbox[0]}" y="{y-bbox[1]}" width="1" height="1" fill="#ff9f16" opacity=".75"/>')
        content.append('<figure>'+svg('f-'+name,bbox,ids,'working',rows,extra=''.join(extra))+f'<figcaption>{name}: magenta = visible model boundaries; orange = measured colored pixels outside their assigned body.</figcaption></figure>')
    content.append('</div>'+keytable(ids,['working'])+'<p>No exact first physical error is established. A shared address change fitted at the reference provides no gain. Geometry, projection and correspondence remain separate unresolved causes.</p><h2>E: retained regression; broader screen remains diagnostic</h2><div class="pair"><figure><img src="../../r329/photographic_diagnostics/images/e-working.png" alt="Working same-family colored target prediction"><figcaption>Working: colored target reached within 0.55–9.08 px.</figcaption></figure><figure><img src="../../r329/photographic_diagnostics/images/e-alternative.png" alt="Alternative mixed-family prediction misses colored target"><figcaption>Closest alternative: colored target missed by 24.43–32.60 px.</figcaption></figure></div><p>These preserved R329 panels use B indices; their IDs and physical targets are unchanged. The E diagnostic passes unchanged. Automatic extension checks 155 other candidate bridges and finds preferences in both directions; it is not adopted as a universal filter.</p><h2>What remains unresolved</h2><p>There are no physical gaps or absent beads. Unknown motif entries, unseen positions, uncertain colors and missing indexed associations remain distinct. The evidence does not establish a final count, exact full motif, globally correct lattice or physical model. Current uncertainties need better automatic measurements and controlled reconstruction tests; no useful visual choice is being delegated to you.</p><script>document.querySelector("#toggle").onclick=()=>document.querySelectorAll(".overlay").forEach(e=>e.style.display=e.style.display==="none"?"":"none");</script></html>')
    # r329 links are relative to review, which is one directory deeper.
    document=''.join(content).replace('src="../../r329/','src="../../r329/')
    (out/'index.html').write_text(document);(out/'figures.json').write_text(json.dumps(figures,indent=2)+'\n');print('REVIEW',len(figures),'native crops')

if __name__=='__main__':main()
