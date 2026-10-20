"""Publication pattern figure and self-contained offline photographic review."""
from common import *
from PIL import Image, ImageOps
import html
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'beads-r344'
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

PALETTE = {'red':'#d43b42','yellow':'#dfb915','black':'#252a31','?':'#eeeeee'}


def main():
    g,obs,co=load_graph(OUT/'graph.json.gz')
    p=read(OUT/'pattern208.json'); ev=read(OUT/'evaluation.json'); tr=read(OUT/'training-agreement.json')
    ledger=read(OUT/'corrections.json')['authoritative_labels']; blocks=ev['geographic_blocks']
    fig,axs=plt.subplots(1,2,figsize=(16,10))
    for ax,kind,title in zip(axs,['strict','provisional'],['Strict: 199 supported, 9 unresolved','Provisional: all 208, 9 tentative assignments']):
        for e in p['entries']:
            k=e['residue'];x=k%16;y=12-k//16;c=e[kind+'_color']; tentative=kind=='provisional' and e['tentative']
            ax.add_patch(Circle((x,y),.33,facecolor=PALETTE[c],edgecolor='#185da8' if tentative else '#888',linewidth=2 if tentative else .6,linestyle='--' if tentative else '-'))
            if c=='?':ax.text(x,y,'?',ha='center',va='center',fontsize=11)
            ax.text(x,y-.52,str(k),ha='center',va='center',fontsize=8)
        ax.set(xlim=(-.6,15.6),ylim=(-.9,12.7),aspect='equal',title=title);ax.axis('off')
    fig.suptitle('Conditional A string order: read left to right, then next row. Origin is conventional.',fontsize=13)
    fig.text(.5,.02,'Red / yellow / black are bead colors. ? = strict unknown. Blue dashed border = provisional only. No photographic labels are changed by completion.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.04,1,.96));fig.savefig(OUT/'patterns.png',dpi=160);fig.savefig(OUT/'patterns.svg',metadata={'Date':None});plt.close(fig)
    svg=OUT/'patterns.svg';svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n')
    out=OUT/'review';out.mkdir(exist_ok=True)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    fig,ax=plt.subplots(figsize=(7,10));ax.imshow(photo)
    cm=matplotlib.colormaps['tab20']
    for region in range(12):
        xy=np.array([obs[o]['xy'] for o in co if blocks[o]==region]);ax.scatter(xy[:,0],xy[:,1],s=8,color=cm(region/12),alpha=.7)
        cx,cy=xy.mean(0);ax.text(cx,cy,str(region),fontsize=12,ha='center',bbox=dict(facecolor='white',alpha=.9,edgecolor='black'))
    ax.set_title('Frozen photographic geographic blocks 0–11\nOverlay colors identify blocks, not bead pigments');ax.axis('off');fig.tight_layout();fig.savefig(OUT/'geography.png',dpi=130);plt.close(fig)
    # Literal crops of the two solved bodies and three surviving mismatches.
    ids=CORRECTIONS+[r['id'] for r in tr['current1041']['mismatches']]
    panels=[]
    for o in ids:
        x,y=np.rint(obs[o]['xy']).astype(int);box=[int(x-60),int(y-60),int(x+61),int(y+61)]
        key=[o]+sorted([z for z in obs if z!=o and np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy'])<55],key=lambda z:(float(np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy'])),z))
        filename=o+'-native.png';photo.crop(box).save(out/filename)
        panels.append(dict(id=o,key=key,crop_box=box,filename=filename))
    save(out/'panels.json',panels)
    meta=[]
    for o,r in obs.items():
        k=index(co[o]) if o in co else None
        meta.append(dict(id=o,xy=r['xy'],color=r['color'],ab=co.get(o),k=k,position=k%208 if k is not None else None,occurrence=k//208 if k is not None else None,
                         region=blocks.get(o),authority=authority(o,ledger),authority_source=ledger.get(o,{}).get('source',r.get('source','Historical native label'))))
    paper=read(OUT/'graph-paper-layout.json')
    data=dict(observations=meta,edges=g['edges'],pattern=p,evaluation=ev,training=tr,panels=panels,paper=paper)
    (out/'data.js').write_text('const DATA='+json.dumps(data,separators=(',',':'))+';\n')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R344 — graph-paper bead pattern and accuracy</title><link rel="stylesheet" href="style.css">
<h1>R344 — the graph-paper bead pattern</h1>
<p><b>199 supported / 2 conflicting / 7 insufficient.</b> Two explicit maker-yellow corrections resolve positions 29 and 127. Geometry and bead identities are unchanged. A=7a+6b, N=2704 and 13 repeats are conditional. The displayed cyclic origin and forward direction are conventions.</p>
<p><a href="../../R344_REPORT.md">Report and recommendation</a> · <a href="../../R344_REPRODUCE.md">Reproduce</a> · <a href="../strict-pattern.csv">Strict CSV</a> · <a href="../provisional-pattern.csv">Provisional CSV</a> · <a href="../pattern208.json">Every position’s evidence/confidence</a> · <a href="../../../beads-photo-2.jpg">Original photograph</a></p>
<h2>The original graph-paper arrangement</h2>
<p>Rows contain alternately <b>6 and 7 identical ellipses</b>. Right is string +1, up-left +6, up-right +7. The thin teal START and purple END lines mark one block, positions0–207 exactly once in each central strip. Eight continuation rows appear before and after it; all copies retain their original pattern-position color and identity. Reading proceeds upward. White is the chosen interval; gray background is continuation. Strict unknowns stay gray ?. Provisional inferred colors have dashed blue outlines.</p>
<div class="paper-controls"><label>Show <select id="paper-kind" onchange="paperDraw()"><option value="both">Strict and provisional</option><option value="strict">Strict only</option><option value="provisional">Provisional only</option></select></label><button onclick="paperZoom(1.5)">Zoom +</button><button onclick="paperZoom(1/1.5)">Zoom −</button><button onclick="paperFit()">Fit</button><button onclick="paperLocate()">Center selected position</button><label><input type="checkbox" id="paper-indices" onchange="paperDraw()"> Position numbers</label><label><input type="checkbox" id="paper-grid" checked onchange="paperDraw()"> Graph paper</label><label><input type="checkbox" id="paper-guides" onchange="paperDraw()"> Primitive diagonal guides</label><label><input type="checkbox" id="paper-seam" onchange="paperDraw()"> Lateral seam copies</label></div>
<p>Drag to pan; use the wheel or buttons to zoom. Click an ellipse or a string-order bead below: every display of that position is highlighted, and its photographed sources appear below. Optional lateral copies have the <em>same k</em> as their central original; they are outside the selected central interval and add no observations.</p><div class="paper-frame"><svg id="graph-paper" role="img" aria-label="Alternating six and seven bead graph-paper pattern, zoomable"></svg></div><p id="paper-status"></p>
<p><a href="../graph-paper.pdf">Print A4 PDF</a> · <a href="../graph-paper.png">High-resolution PNG</a> · <a href="../graph-paper.svg">Vector SVG</a> · <a href="../graph-paper-numbered.pdf">Print with indices</a> · <a href="../../GRAPH_PAPER_6_5_BEADS.md">General 6.5-bead presentation method</a> · <a href="../graph-paper-verification.json">Algebra, seam and general-boundary verification</a></p>
<h2>The same block in one-dimensional string order, positions 0–207</h2>
<p>Read left to right, then down. Each circle is one string position, not a physical crochet row. Red, yellow and black denote pigment. Gray <b>?</b> means unresolved under the unchanged strict rule. <b>Blue dashed</b> circles in the provisional block are predictions, never new photographic colors. Click any position.</p>
<div class="two"><section><h3>Authoritative strict sequence</h3><div id="strict" class="block"></div></section><section><h3>Best provisional completion</h3><div id="provisional" class="block"></div></section></div>
<p><a href="../patterns.png">Export graphic</a> · <a href="../patterns.svg">Vector graphic</a></p><pre id="sequence"></pre>
<h2>Thirteen proposed repeats: photographed occurrences versus predictions</h2>
<p>Rows are proposed occurrences 0–12; columns are positions 0–207. <b>Solid circles are recorded photographic colors.</b> Faint circles are predictions at addresses without indexed photographic observations. Blue dashed borders denote tentative motif entries. Magenta borders identify the three recorded mismatches. Gray ? is a strict unknown. Scroll horizontally; click a circle to open its original photographed occurrence if one exists. Only 1,041 of the 2,704 conditional addresses are indexed photographically. Cyclic closure returns address 2703 (q12, position207) to address0 (q0, position0).</p>
<label><input type="checkbox" id="complete" checked onchange="matrix()"> Show provisional predictions where no indexed observation exists</label><div class="scroll"><svg id="matrix" role="img" aria-label="13 repeats linked to photographed occurrences"></svg></div>
<h2>Selected position and photographic provenance</h2><label>Position <input id="position-input" type="number" min="0" max="207" value="29"></label><button onclick="selectPosition(+document.querySelector('#position-input').value)">Open</button><button onclick="selectPosition((selected+207)%208)">Previous</button><button onclick="selectPosition((selected+1)%208)">Next</button>
<div id="position-detail"></div><div class="scroll"><table id="occurrences"></table></div>
<section id="inspector"><h3 id="photo-title"></h3><p>Target is feature 1. Numbers belong only to this photograph and its matching current adjacency diagram. Native support locations are not asserted bead centers.</p><label><input type="checkbox" id="numbers" checked onchange="drawPhoto()"> Local numbers</label> <label><input type="checkbox" id="old-color" onchange="drawPhoto()"> Before R344 colors in diagram</label><div class="two"><canvas id="native" width="484" height="484"></canvas><canvas id="diagram" width="484" height="484"></canvas></div><div id="key"></div><p id="source-detail"></p></section>
<h2>Training fit and held-out prediction are different</h2><p>The provisional completion matches <b>1,038/1,041</b> recorded colors. The strict pattern matches <b>1,011/1,011</b> evaluable observations and abstains on 30. These are fitted-label comparisons. Guarded geographic held-out A208 predicts <b>1,024/1,041</b>; whole-occurrence held-out predicts <b>1,038/1,041</b>. They reuse one photograph and a previously selected hypothesis, so they are not independent physical validation.</p><p><a href="../geography.png">Native photograph showing the twelve frozen geographic blocks</a></p><div id="summary-tables"></div>
<h2>Nine tentative entries</h2><p>Seven are unanimously recorded black but lack three geographic blocks/observations. Positions 83 and 189 tentatively use yellow plurality while contrary red records remain. Prediction scores are fixed-shrinkage descriptive quantities, not calibrated confidence in physical truth. Every source can be inspected above.</p><div id="tentative"></div>
<h2>Three surviving mismatches</h2><p>These edge/thin-body sources have no safely delimited material core in R343. No new pigment judgment is invented here. Click an ID to examine its native body, stable key and existing links. The report recommends targeted independent reobservation of these three bodies, rather than another classifier campaign.</p><div id="mismatches"></div>
<details><summary>Literal native crops of the two solved corrections and three remaining mismatches</summary>NATIVE_CROPS</details>
<h2>Conditional shortest-repeat test</h2><p>All proper divisors of 208 are contradicted by pairs of strict colors. Therefore every completion of this strict 208-block has minimal cyclic period 208 <em>under this indexing and closure</em>. This does not establish that the photographic indexing or physical total is correct. B207/B299/A338 fit the same recorded cohort poorly. No broad winding search ran.</p><div id="divisors"></div>
<script src="data.js"></script><script src="viewer.js"></script><script src="paper.js"></script></html>'''
    crops=''.join(f'<figure><figcaption>{html.escape(r["id"])} — original pixels, no resampling</figcaption><img src="{r["filename"]}" width="363" alt="Native crop {r["id"]}"></figure>' for r in panels)
    (out/'index.html').write_text(page.replace('NATIVE_CROPS',crops))
    for name in ['viewer.js','style.css','paper.js']:(out/name).write_text((ROOT/'photo2/r344'/name).read_text())
    print('PRESENT',len(panels),'literal native crops and interactive 208 x13 review')


if __name__=='__main__':
    main()
