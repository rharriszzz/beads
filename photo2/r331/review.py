"""Offline scientific review and printable four-problem presentation.

All photographic assets are literal native RGB crops. SVG lines/boxes annotate
conditional assignments or inspection areas, never measured black-body centers.
"""
import argparse,csv,html,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import binary_erosion
from photo2.r329.common import ROOT,read,canonical
from photo2.r330.pattern import dataset,COLORS

STYLE='''body{margin:24px auto;max-width:1200px;padding:0 20px;font:17px/1.45 system-ui;color:#15243a;background:#f5f7fb}h1{font-size:34px;line-height:1.13}h2{font-size:27px}h3{font-size:20px}a{color:#075f9e}svg,img{max-width:100%;height:auto}figure{margin:0}.pair,.three{display:grid;grid-template-columns:1fr 1fr;gap:18px}.three{grid-template-columns:1fr 1fr 1fr}figcaption{font-size:14px;margin:8px 0}.note{padding:14px;background:#e3edf8;border-left:4px solid #14719a}.help{padding:12px;background:#fff1cd}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;padding:5px;border-bottom:1px solid #cbd3de}code{overflow-wrap:anywhere}button{padding:10px;margin:8px 0}details{margin:18px 0}summary{font-weight:600;cursor:pointer}.slide{margin:38px 0;padding:22px;background:white;border:1px solid #d5dce5;border-radius:10px}.eyebrow{font-size:14px;color:#38607e;text-transform:uppercase;letter-spacing:1px}.small{font-size:13px}.bar{height:14px;background:#1a709c}.muted{color:#5a6778}@media(max-width:700px){.pair,.three{grid-template-columns:1fr}body{padding:0 12px}.slide{padding:12px}}@media print{@page{size:A4 landscape;margin:10mm}body{margin:0;padding:0;max-width:none;background:white;font-size:12px}.slide{height:174mm;break-after:page;margin:0;padding:0;border:0;border-radius:0;overflow:hidden}h1{font-size:25px}h2{font-size:22px;margin:8px 0}p{margin:7px 0}.slide svg{max-height:85mm;width:100%}table{font-size:9px}td,th{padding:2px}.note,.help{padding:8px}.noprint{display:none}.slide:last-child{break-after:auto}}
'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(ROOT/'photo2/r331/review'));args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True);(out/'assets').mkdir(exist_ok=True)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');g,states,ids,obs,station,blocks,c,w=dataset();co={name:canonical(state) for name,state in states.items()}
    data=read(ROOT/'photo2/r331/results-final/analysis.json.gz');extra=read(ROOT/'photo2/r331/followup-final/followup.json.gz');err=read(ROOT/'photo2/r331/errors-v2/errors.json.gz');diag=read(ROOT/'photo2/r330/photography/photography.json.gz');ref=read(ROOT/'photo2/r330/refinement/refinement.json.gz');figures=[]
    def crop(key,bbox):
        f='assets/'+key+'.png';photo.crop(bbox).save(out/f);figures.append(dict(file=f,bbox=bbox));return f
    def panel(key,bbox,which,selected,links=True,highlight=None,predictions=None,boxes=None,extra_svg=''):
        f=crop(key,bbox);x0,y0,x1,y1=bbox;W=x1-x0;H=y1-y0;coord=co[which]
        pts={o:np.array(obs[o]['xy'])-[x0,y0] for o in selected};s=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{key}: original photograph with labeled supports"><image href="{f}" width="{W}" height="{H}"/><g class="overlay">']
        if links:
            for a in selected:
                for z in selected:
                    if a not in coord or z not in coord:continue
                    d=tuple(np.array(coord[z])-coord[a])
                    if d not in [(1,0),(0,1)]:continue
                    x,y=pts[a];xx,yy=pts[z];color='#00d9ff' if d==(1,0) else '#8aff58'
                    s.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="{color}" stroke-width=".9" opacity=".9"><title>{html.escape(a)} to {html.escape(z)}, delta {d}</title></path>')
        if highlight:
            a,z=highlight;x,y=pts[a];xx,yy=pts[z];s.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="#ff39de" stroke-width="2.3"/>')
        if predictions:
            for o,r in predictions.items():
                x,y=np.array(r['prediction'])-[x0,y0];xx,yy=np.array(r['observed'])-[x0,y0]
                s.append(f'<path d="M{x-3},{y-3} l6,6 m-6,0 l6,-6 M{x},{y} L{xx},{yy}" stroke="#ff39de" stroke-width="1" stroke-dasharray="2 1"><title>{o}: colored-pigment prediction error {r["error"]:.2f}px</title></path>')
        if boxes:
            for box in boxes:
                x,y,ww,hh,label=box;s.append(f'<rect x="{x-x0}" y="{y-y0}" width="{ww}" height="{hh}" fill="none" stroke="#ffb332" stroke-width="1.2" stroke-dasharray="2 2"><title>{label}; inspection area only, not measured body boundary</title></rect>')
        s.append(extra_svg)
        for j,o in enumerate(selected):
            x,y=pts[o];lx=x+5;ly=y-7
            # Small support cross; label is displaced to avoid claiming a center.
            s.append(f'<path d="M{x-2},{y} h4 m-2,-2 v4" stroke="white" stroke-width=".7"/><path d="M{x},{y} L{lx},{ly}" stroke="white" stroke-width=".4"/><rect x="{lx-4}" y="{ly-4}" width="8" height="8" rx="2" fill="#10213a" stroke="white" stroke-width=".4"/><text x="{lx}" y="{ly+2}" text-anchor="middle" font-size="5.5" fill="white">{j+1}</text>')
        s.append('</g></svg>');return ''.join(s)
    def table(selected,which=('working',),proposal=None):
        txt='<div class="scroll"><table><tr><th># / original observation ID</th><th>Recorded color</th>'
        for st in which:txt+=f'<th>{st}: (a,b); A / B</th>'
        if proposal:txt+='<th>Color hypothesis</th>'
        txt+='</tr>'
        for j,o in enumerate(selected):
            txt+=f'<tr><td>{j+1}: {o}</td><td>{obs[o]["color"]}</td>'
            for st in which:
                ab=co[st].get(o);value=f'{ab}; {np.dot(ab,[7,6])} / {np.dot(ab,[6,7])}' if ab is not None else 'unindexed'
                txt+=f'<td>{value}</td>'
            if proposal:txt+=f'<td>{proposal.get(o,"unchanged")}</td>'
            txt+='</tr>'
        return txt+'</table></div>'
    def nearby(o,r=82):
        pt=np.array(obs[o]['xy']);near=[q for q in co['working'] if q!=o and np.linalg.norm(np.array(obs[q]['xy'])-pt)<r]
        return [o]+sorted(near,key=lambda q:np.linalg.norm(np.array(obs[q]['xy'])-pt))[:16]
    legend='<p class="small">Cyan: +a, A+7/B+6. Green: +b, A+6/B+7. Magenta: disputed connection or colored-target prediction. White crosses mark recorded supports, <b>not measured bead centers</b>. Amber dashed rectangles mark visible-material inspection areas; they are not measured boundaries. Overlays can be hidden to inspect the literal original crop.</p>'
    # Matched G context, expanded enough to expose both directions and dark material.
    gids=['P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325','E5-1633-0278','E5-1607-0290','C-1582-0272','C-1608-0253','C-1559-0252','C-1659-0261','NEW-1621-315','K-1695-0317','K-1721-0308']
    gbbox=[1510,205,1750,375];gpanels=[]
    for st in ['working','early']:
        v=next(x for x in diag['G']['variants'] if x['margin']==0 and x['degree']==2 and x['radius']==18 and x['state']==st)
        gpanels.append('<figure>'+panel('g-'+st,gbbox,st,gids,highlight=('E5-1633-0278' if st=='working' else 'E5-1607-0290','P5-1645-0309'),predictions=v['targets'],boxes=[[1609,300,21,28,'Dark material near NEW-1621 support']])+f'<figcaption>{st}: magenta crosses predict red targets 1–4 from the same 11 colored references. Misses: '+', '.join(f'{x["error"]:.1f}' for x in v['targets'].values())+' px. Dashed amber box: dark material near support 11.</figcaption></figure>')
    # Same-direction black and colored rows: explicit [0,1] family in upper crop.
    blackids=['NEW-1706-342','K-1695-0317','K-1721-0308','D40-K-1746-0312','P5-1645-0309','C-1669-0293','NEW-1697-280','C-1729-0337','E5-1757-0332']
    blackpanel=panel('black-direction',[1600,240,1785,390],'working',blackids,boxes=[[1698,329,17,25,'Dark material at red-labeled NEW-1706'],[1684,301,22,31,'Dark material at K-1695'],[1713,288,20,34,'Dark material at K-1721']])
    # Inward ambiguity: identical photographic context with each convention's indices.
    eids=['C-1721-1566','K-1740-1575','MAT25-K-1719-1592','C-1717-1540','K-1683-1538','E5-1694-1563','C-1770-1577','K-1750-1601','C-1777-1612','C-1705-1514']
    epanels=[]
    for st in ['working','closest']:
        epanels.append('<figure>'+panel('inward-'+st,[1640,1485,1810,1645],st,eids,highlight=(eids[0],eids[1]),boxes=[[1731,1561,19,25,'Dark material at K-1740 support'],[1709,1580,22,24,'Dark material at MAT25-K-1719 support']])+f'<figcaption>{st}: magenta joins supports 1→2. '+('Working delta (0,−1); A−6/B−7.' if st=='working' else 'Alternative delta (−1,0); A−7/B−6.')+' Amber boxes mark dark-material inspection areas. Nearby yellow supports carry the same cyan/green direction labels.</figcaption></figure>')
    # F reuses all-body visibility from R329, no new render or registration fit.
    m=np.load(ROOT/'photo2/r329/photographic_diagnostics/model-geometry.npz');owner=m['owner'].reshape(m['shape']);mbox=m['bbox'];step=float(m['step']);bbox=[1230,208,1510,365]
    fids=['C-1302-0316','C-1391-0312','C-1422-0264','C-1251-0290','C-1277-0302','C-1339-0277','P5-1364-0299','NEW-1442-248'];fpanels=[]
    for st,dx,dy in [('frozen',0,0),('translated',8,-4)]:
        overlay=[]
        for t in diag['F']['rows']:
            j=int(np.flatnonzero(m['indices']==t['address'])[0]);mask=owner==j;yy,xx=np.nonzero(mask&~binary_erosion(mask))
            for x,y in zip(xx[::2],yy[::2]):overlay.append(f'<rect x="{x*step+mbox[0]+dx-bbox[0]}" y="{y*step+mbox[1]+dy-bbox[1]}" width=".6" height=".6" fill="#ff39de"/>')
            for x,y in t['pixels']:
                xx=int(round((x-dx-mbox[0])/step));yy=int(round((y-dy-mbox[1])/step));inside=0<=xx<owner.shape[1] and 0<=yy<owner.shape[0] and owner[yy,xx]==j
                if not inside:overlay.append(f'<rect x="{x-bbox[0]}" y="{y-bbox[1]}" width="1" height="1" fill="#ffa71a" opacity=".75"/>')
        fpanels.append('<figure>'+panel('material-'+st,bbox,'working',fids,extra_svg=''.join(overlay))+f'<figcaption>{st}: magenta is the cached visible model-body boundary; orange marks measured yellow/red pixels outside their assigned model body. '+('No raster translation.' if st=='frozen' else 'Raster moved +8 px right / 4 px up; fitted only at yellow support 1.')+'</figcaption></figure>')
    # Quantitative figure uses exact computed summaries, never generated artwork.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels=['A/104 flat','A/208 hierarchical','B/207 flat','B/299 flat','A/306 flat','B/305 flat'];values=[]
    for fam,p,parent in [('A',104,None),('A',208,104),('B',207,None),('B',299,None),('A',306,None),('B',305,None)]:
        r=next(x for x in data['sensitivity'] if x['family']==fam and x['period']==p and x['parent']==parent and not x['robust'] and x['guard']==0 and x['black_weight']==.55);values.append(r['gain_nats'])
    fig,ax=plt.subplots(figsize=(9,3.3));ax.barh(labels[::-1],values[::-1],color=['#29779e' if v>=0 else '#a85349' for v in values[::-1]]);ax.axvline(0,color='#333',lw=.7);ax.set_xlabel('Exploratory held-section log gain (nats / weighted observation)');ax.set_xlim(-.2,.9);fig.tight_layout();fig.savefig(out/'assets/comparison.png',dpi=150);plt.close(fig)
    header=lambda title:f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{STYLE}</style>'
    toggle='<button class="noprint" id="toggle">Hide / show overlays</button>'
    script='<script>document.querySelector("#toggle").onclick=()=>document.querySelectorAll(".overlay").forEach(e=>e.style.display=e.style.display==="none"?"":"none");</script></html>'
    # A presentation with four concrete review problems, plus evidence and next step.
    slides=[]
    def slide(k,title,body):slides.append(f'<section class="slide"><div class="eyebrow">R331 · {k}</div><h2>{title}</h2>{body}</section>')
    slide('finding','A useful 208 prediction is not the recovered design', '<div class="pair"><div><p>The maker says the shortest repeat is about 200–399 and is not divisible by 13.</p><p><b>A: 2704 = 13 × 208.</b> Its only allowed-range divisors, 208/338, violate that constraint.</p><p><b>B: 2691 = 13 × 207 = 9 × 299.</b> Those lengths satisfy the maker constraint but predict poorly on this map.</p><p>None of the saved maps establishes a design-compatible exact repeat. The 104/208 structure survives phase-preserving controls.</p></div><figure><img src="assets/comparison.png" alt="Computed held-section comparison"><figcaption>Same 900 original observations; all results are exploratory reuse. Hierarchical A/208 has an explicitly different prior; flat comparisons are in the report.</figcaption></figure></div><p class="help">Four review problems follow. They ask for concrete observations in the photograph; they do not ask you to certify a model, count or pattern.</p>')
    slide('problem 1 of 4','G: which row reaches the first red sequence?', '<div class="pair">'+''.join(gpanels)+'</div><p><b>Help I would use:</b> compare the highlighted incoming link to red support 1 against the annotated yellow rows 6→5→10 and 7→6. Does the visible red-body sequence 1→2→3 continue that same diagonal, or bend into the adjacent row?</p><p>The local colored-target fit favors the alternative, but neither B/207 nor the weak 305/306 candidates resolves its downstream consequences. A/208 remains predictive evidence, not a design veto.</p>'+legend)
    slide('problem 1 · labels','G: the exact competing assignments',table(gids,('working','early'))+'<p class="help">The first three red target misses fall from 21.4/21.2/20.3 px to 9.1/9.5/10.0 px under the same 11-reference quadratic fit. These are partial-pigment extrapolations. The fourth target and wider reference fits remain sensitive. A concrete row identification here would justify a bounded replay; motif preference alone would not.</p>')
    slide('problem 2 of 4','Black material: color label or wrong observation?', '<div class="pair"><figure>'+blackpanel+'<figcaption>Same-direction comparison: green [0,+1] links dark supports 2→3→4 and red supports 5→6→7. The separate green link 1→8→9 shows the red-labeled site in its neighboring row. Amber boxes mark visible dark-material inspection areas.</figcaption></figure><div><p>Support 1, NEW-1706-342, was labeled red. Its appearance controls and A/208 favor black. Its B/207 prediction favors red.</p><p><b>Help I would use:</b> inspect the dark material in box 1, then compare its visible body with boxes 2/3 and the adjacent red row in the same green direction. A reflection supplies an observation location; it does not measure the body center or establish pigment.</p><p>All six R330 red→black hypotheses remain provisional. More pattern agreement is not new confirmation.</p></div></div>'+legend)
    slide('problem 2 · labels','Black comparison: IDs, indices and competing color readings',table(blackids,proposal={'NEW-1706-342':'red → black, provisional'})+'<p>The same image can support a dark-body reading while carrying a tinted bright patch. The review marks inspection areas rather than inferring complete black outlines. The full review includes matched contexts for all six hypotheses and three additional model flags; none changes the frozen labels.</p>')
    slide('problem 3 of 4','Inward bend: one diagonal changes the conditional count','<div class="pair">'+''.join(epanels)+'</div><p><b>Help I would use:</b> compare 1→2 with the green/cyan yellow continuations and the dark material in boxes 2/3. Which family is supported by the visible body arrangement? The current native prediction favors working; the competing family survives complete replay.</p><p>Working H=(214,201), A/B counts 2704/2691. Closest alternative H=(215,200), counts 2705/2690. Replacing windows 124–126 is sufficient to produce that change.</p>'+legend)
    slide('problem 3 · labels','Inward bend: exact labels and evidence',table(eids,('working','closest'))+'<p class="help">Cached target-excluded errors, working → alternative: C-1721 6.11→9.56 px; K-1740 5.38→8.51 px; MAT25-K-1719 5.22→12.59 px. Native-response ratios for K-1740: .691→.057. These measure response at predicted supports, not distances between measured body centers. Better local body correspondence would matter more than another pattern score.</p>')
    slide('problem 4 of 4','F: a common image shift still leaves material unexplained','<div class="pair">'+''.join(fpanels)+'</div><p><b>Help I would use:</b> compare the orange measured pigment at targets 2/3 with the magenta assigned-body borders after translation. Identify any visibly wrong body association before changing shape or lighting. A visual association can narrow correspondence; the crop alone cannot choose the physical parameter responsible.</p><p>Reference target 1 improves from about 59% to 99% coverage. Targets 2/3 remain near 49%. The frozen 3000-body model is incompatible with the photographic conditional count; this is a retained diagnostic, not a reconstruction proposal.</p>'+legend)
    slide('problem 4 · labels','F: what the crop can and cannot decide',table(fids)+'<p>Targets 1–3 use frozen model addresses −64/−38/−26. Orange pixels are actual measured colored regions; magenta borders come from the saved visibility raster. The source image and all 3000 model bodies are unchanged.</p><p class="help">A visible mistake in which body owns a colored region would redirect correspondence work. If the association is right, the residual belongs to projection/shape/trajectory diagnosis. No new fitting campaign was performed in R331.</p>')
    slide('next investigation','Resolve one row continuation before another global fit','<p><b>Most valuable next investigation:</b> a tightly bounded, color-independent body-correspondence audit at G, using the same visible diagonal in neighboring colored and black sequences, followed by replay of only the already implicated windows.</p><p>The new latent model separates color substitutions from shift proposals and abstains when several ±1/±6/±7 corrections explain the same color. It flags 52/144 injected isolated A-index errors but uniquely restores none from the motif alone. Frozen neighbor equations restore 138/144 bookkeeping errors; they cannot validate an internally consistent wrong row.</p><p>Unknown motif entries remain unknown. No winding, count, exact design or provisional color correction is adopted. Stop for review; no automatic R332.</p><p class="small">Report: photo2/R331_REPORT.md. Full offline review: index.html. Reproduction and machine-readable evidence are linked there. These four review tasks do not establish new photographic truth until a specific visible choice is recorded.</p>')
    (out/'presentation.html').write_text(header('R331 · four unresolved Phase 2 problems')+'<div class="noprint"><h1>Four problems to put behind us</h1><p><a href="index.html">Full evidence review</a> · <a href="presentation.pdf">Printable presentation</a></p>'+toggle+'</div>'+''.join(slides)+script)
    # Full review: all correction flags get original context, IDs and own indices.
    content=[header('R331 pattern and alias audit'),'<h1>The structure is predictive; the actual repeat remains unresolved</h1><p class="note">208 is a strong predictive lattice period that conflicts with the maker’s shortest-repeat restriction. B/207 is arithmetically allowed but poorly predictive. No new count, winding, exact motif or color label is adopted.</p><p><a href="../../R331_REPORT.md">Report</a> · <a href="../../R331_REPRODUCE.md">Reproduce</a> · <a href="presentation.html">Four-problem presentation</a> · <a href="presentation.pdf">Presentation PDF</a> · <a href="../results-final/periods.csv">Period scores</a> · <a href="../verification.json">Independent numerical checks</a></p>',toggle,legend,'<img src="assets/comparison.png" alt="Held-section model comparison"><h2>The alias relationship is measured, not assumed</h2><p>A−B=a−b and A+B=13(a+b). All 623 observed pairs separated by A+208 use (Δa,Δb)=(16,16), hence B+208, not B+207. They agree in recorded color 585/623 times. The 605 B+207 pairs instead use (17,15), and agree only 89/605 times. Each A+208 pair advances its B/207 residue by one. Thirteen such phase increments close arithmetically; they do not establish the physical design.</p><h2>Maker-compatible motifs retain uncertainty</h2>']
    for m0 in data['motifs']:
        fam,p=m0['family'],m0['period'];entries=m0['entries'];tiles=['<svg viewBox="0 0 1040 '+str(((p+25)//26)*29)+'" role="img" aria-label="Partial motif '+fam+'/'+str(p)+'">']
        for r,e in enumerate(entries):
            color={'red':'#d84948','yellow':'#f1cc4c','black':'#202632','?':'#d4d9e0'}[e['color']];x=r%26*40;y=r//26*29;letter={'red':'R','yellow':'Y','black':'B','?':'?'}[e['color']]
            tiles.append(f'<g><title>Residue {r}; {e["observations"]} observations; {len(e["sections"])} supporting sections</title><rect x="{x}" y="{y}" width="38" height="27" fill="{color}"/><text x="{x+19}" y="{y+10}" font-size="8" text-anchor="middle" fill="{"white" if letter=="B" else "#142139"}">{r}</text><text x="{x+19}" y="{y+23}" font-size="12" text-anchor="middle" fill="{"white" if letter=="B" else "#142139"}">{letter}</text></g>')
        content.append(f'<details><summary>{fam}/{p}: {m0["known"]} consensus entries, {p-m0["known"]} unknown; {m0["unobserved"]} wholly unobserved residues</summary>'+''.join(tiles)+'</svg><p>Consensus requires ≥80% weighted agreement, ≥3 supporting observations and ≥3 sections. These are full-data exploratory summaries, not certified motif entries.</p></details>')
        with (out/f'motif-{fam}-{p}.csv').open('w',newline='') as f:
            wr=csv.DictWriter(f,list(entries[0]),lineterminator='\n');wr.writeheader();wr.writerows(entries)
    content+=['<h2>G: matched original photographic contexts</h2><div class="pair">'+''.join(gpanels)+'</div>',table(gids,('working','early')),'<h2>Inward bend: conditional count sensitivity</h2><div class="pair">'+''.join(epanels)+'</div>',table(eids,('working','closest')),'<h2>All color hypotheses and additional model flags</h2><p>The six R330 hypotheses retain their original status. Three extra A/208 latent-model flags are shown for completeness, with weaker competing evidence; they are not promoted to recommended corrections. Every working/alternative pair below has identical image pixels, indices and graph directions. Only the color interpretation differs.</p>']
    proposed=dict(ref['color_candidates'])
    for r in err['real_proposals']:
        if r['family']=='A':proposed.setdefault(r['id'],r['proposed_color'])
    for o,color in proposed.items():
        x,y=map(round,obs[o]['xy']);bbox=[x-85,y-80,x+85,y+80];selected=nearby(o);audit=next(a for a in ref['color_audit'] if a['id']==o)
        panels=[]
        for st in ['working','hypothesis']:
            panels.append('<figure>'+panel('color-'+o+'-'+st,bbox,'working',selected,boxes=[[x-9,y-13,18,26,'Visible-material inspection at target support']])+f'<figcaption>{st}: support 1, {o}; color '+(obs[o]['color'] if st=='working' else color)+'. Identical crop, support positions, indices and links. Amber rectangle marks the material inspection area, not a complete body or measured center.</figcaption></figure>')
        checks=[r for r in data['color_checks'] if r['id']==o and r['period']==207]
        bprediction=checks[0]['prediction'] if checks else 'not a six-site control'
        status='Preserved R330 provisional hypothesis' if o in ref['color_candidates'] else 'Additional latent-model flag; unverified'
        content.append(f'<details><summary>{o}: {obs[o]["color"]} → {color} · {status}</summary><div class="pair">'+''.join(panels)+f'</div><p>Appearance majority: {audit["suggestion"]}; minimum control vote {audit["min_vote"]:.1%}; all controls agree: {audit["stable"]}. B/207 prediction: {bprediction}. Competing explanations: tinted reflection, wrong support/body association, index or motif error.</p>'+table(selected,proposal={o:color})+'</details>')
    content+=['<h2>Black sequences compared in the same direction</h2>',blackpanel,table(blackids,proposal={'NEW-1706-342':'black, provisional'}),'<p>Green [0,+1] chains are marked for dark supports 2→3→4 and red supports 5→6→7. Amber rectangles mark dark-material inspection areas. These are body-context comparisons, not spacing measured between reflection centers.</p>','<h2>Frozen material mismatch, without new fitting</h2><div class="pair">'+''.join(fpanels)+'</div>',table(fids),'<h2>What would resolve an unknown entry?</h2><p>A known original-photo body/color association at an indexed occurrence, supported across other geographic sections, or a verified continuation that changes the residue assignment. More fitted pixels from the same uncertain motif do not supply independent evidence. Unobserved positions remain occupied physical positions of unknown color.</p><p>All new scores reuse R330 observations. Numerical verification is independently coded; the photograph has no new independent truth labels. Stop for review.</p>',script]
    (out/'index.html').write_text(''.join(content));(out/'figures.json').write_text(json.dumps(figures,indent=2)+'\n');print('review native crops',len(figures),'slides',len(slides))

if __name__=='__main__':main()
