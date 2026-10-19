"""Offline synchronized photograph, unwrapped graph paper and annotated cases."""
import argparse,json,html,time
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from .common import *
from photo2.r330.pattern import dataset as old_dataset
from photo2.r329.common import canonical
C={'red':'#df393d','yellow':'#f4d548','black':'#242933','?':'#afbbc9'}
LINE={'BR':'#12b9dc','BY':'#a546e4'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);assets=out/'assets';assets.mkdir();t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=dataset();sp=read(artifact('spirals/spirals.json.gz'));st=read(artifact('staircases/staircases.json.gz'));di=read(artifact('diagnosis/diagnosis.json.gz'));period=read(artifact('periods-selected/periods.json.gz'));photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');breakby={r['id']:r for r in di['breaks']};crops=[];cases=[]
    # Separate literal native crops from annotated overlays. Black examples get
    # all same-direction colored references via the six measured neighbors.
    chosen=di['breaks'][:6]
    for row in di['breaks']:
        if not row['photographic_support'] and all(np.linalg.norm(np.array(row['xy'])-x['xy'])>150 for x in chosen):chosen.append(row)
        if len(chosen)>=10:break
    for target in ['NEW-1927-2829','REC266-P146299']:
        row=next((r for r in di['breaks'] if r['id']==target),None)
        if row and row not in chosen:chosen.append(row)
    chosen+=di['gaps'][:4]
    def crop(row,name):
        x,y=row['xy'];box=[max(0,int(x)-145),max(0,int(y)-130),min(photo.width,int(x)+146),min(photo.height,int(y)+131)];raw=photo.crop(box);raw.save(assets/f'{name}-native.png');crops.append(dict(file=f'assets/{name}-native.png',bbox=box));annot=raw.resize((raw.width*3,raw.height*3));draw=ImageDraw.Draw(annot);font=ImageFont.truetype(FONT,18)
        local=[o for o in ids if box[0]<=obs[o]['xy'][0]<box[2] and box[1]<=obs[o]['xy'][1]<box[3]];number={o:j+1 for j,o in enumerate(local)}
        def p(xy):return tuple((xy[j]-box[j])*3 for j in range(2))
        for e in g['edges']:
            if e['source'] in number and e['target'] in number:draw.line([p(obs[e['source']]['xy']),p(obs[e['target']]['xy'])],fill='#80a0ad',width=1)
        for trace in st['traces']:
            for a,z in zip(trace['ids'],trace['ids'][1:]):
                if a in number and z in number:draw.line([p(obs[a]['xy']),p(obs[z]['xy'])],fill=LINE['BR' if trace['palette'][1]=='red' else 'BY'],width=3)
        for o in local:
            xx,yy=p(obs[o]['xy']);draw.ellipse((xx-7,yy-7,xx+7,yy+7),outline=C[obs[o]['color']],width=3);draw.text((xx+8,yy-22),str(number[o]),font=font,fill='white',stroke_width=2,stroke_fill='#162234')
        xx,yy=p(row['xy']);draw.rectangle((xx-16,yy-16,xx+16,yy+16),outline='#ff35d7',width=4);draw.text((8,8),row['id'],font=font,fill='white',stroke_width=2,stroke_fill='black')
        if 'prediction' in row:
            draw.text((8,32),f"recorded {row.get('original','?')} / expected {row['prediction']} (hypothesis)",font=font,fill='white',stroke_width=2,stroke_fill='black')
            for nr in row.get('neighbors',[]):
                if nr['id'] not in number or tuple(nr['delta_ab']) not in [(1,0),(0,1),(-1,0),(0,-1)]:continue
                q=np.array(p(obs[nr['id']]['xy']));origin=np.array([xx,yy]);delta=q-origin
                for tt in np.arange(0,1,.18):draw.line([tuple(origin+delta*tt),tuple(origin+delta*min(1,tt+.09))],fill='#ff45d5',width=3)
        annot.save(assets/f'{name}-annotated.png')
        return box,local,number
    def lattice_svg(rows,traces,path,title,mark=None,local=False):
        aa=np.array([co[o] for o in rows]);s=aa.sum(1);d=aa[:,0]-aa[:,1];s0=int(s.min())-2;s1=int(s.max())+2;d0=int(d.min())-2;d1=int(d.max())+2;unit=32;W=(s1-s0+1)*unit;hh=(d1-d0+1)*unit
        def xy(o):a,bb=co[o];return ((a+bb-s0)*unit+16,(d1-(a-bb))*unit+35)
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{hh+70}" viewBox="0 0 {W} {hh+70}"><rect width="100%" height="100%" fill="#f3f6fa"/><text x="10" y="20" font-family="sans-serif" font-size="15">{html.escape(title)}</text>'];present={tuple(co[o]) for o in rows}
        for ss in range(s0,s1+1):
            svg.append(f'<path d="M{(ss-s0)*unit+16} 28V{hh+50}" stroke="#d4e0ee"/>')
            for dd in range(d0,d1+1):
                if (ss+dd)%2:continue
                if ((ss+dd)//2,(ss-dd)//2) not in present:svg.append(f'<text x="{(ss-s0)*unit+12}" y="{(d1-dd)*unit+40}" fill="#abb7c7" font-size="12">?</text>')
        for dd in range(d0,d1+1):svg.append(f'<path d="M0 {(d1-dd)*unit+35}H{W}" stroke="#d4e0ee"/>')
        for tr in traces:
            for a,z in zip(tr['ids'],tr['ids'][1:]):
                if a in rows and z in rows:
                    x,y=xy(a);u,v=xy(z);svg.append(f'<path d="M{x} {y}L{u} {v}" stroke="{LINE["BR" if tr["palette"][1]=="red" else "BY"]}" stroke-width="2"/>')
        for o in rows:
            x,y=xy(o);svg.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{C[obs[o]["color"]]}" stroke="#526171"><title>{html.escape(o)} {co[o]}</title></circle>')
            if local:svg.append(f'<text x="{x+9}" y="{y-9}" font-size="10" font-family="sans-serif">{rows.index(o)+1}</text>')
            if o==mark:svg.append(f'<rect x="{x-14}" y="{y-14}" width="28" height="28" fill="none" stroke="#ec27be" stroke-width="3"/>')
        gap=next((g for g in di['gaps'] if g['id']==mark),None)
        if gap:
            cell=np.array(gap['ab']);hh=np.array(g['H']);cell-=round(float((cell-aa.mean(0))@hh/(hh@hh)))*hh
            x=(int(cell.sum())-s0)*unit+16;y=(d1-int(cell[0]-cell[1]))*unit+35
            for nr in gap['neighbors']:
                if nr['id'] not in rows:continue
                u,v=xy(nr['id']);svg.append(f'<path d="M{x} {y}L{u} {v}" fill="none" stroke="#e927c2" stroke-width="2" stroke-dasharray="5 4"/>')
            svg.append(f'<path d="M{x} {y-14}L{x+14} {y}L{x} {y+14}L{x-14} {y}Z" fill="white" stroke="#e927c2" stroke-width="3"/><text x="{x-4}" y="{y+4}" font-size="13">?</text><text x="{x+17}" y="{y-17}" font-size="11" fill="#b91d9b">expected {gap["prediction"]}; unconfirmed</text>')
        svg.append('</svg>');path.write_text(''.join(svg))
    for j,row in enumerate(chosen):
        name=f'case-{j+1:02}';box,local,number=crop(row,name);lattice_svg(local,st['traces'],assets/f'{name}-lattice.svg',f'{row["id"]}: recorded colors; ? = unobserved site',row['id'],True);examples=[]
        for k,ex in enumerate(row.get('comparisons',row.get('examples',[]))[:2]):
            exrow=dict(id=ex['id'],xy=ex['xy']);ebox,elocal,enumbers=crop(exrow,f'{name}-example-{k+1}');lattice_svg(elocal,st['traces'],assets/f'{name}-example-{k+1}-lattice.svg',f'Comparison {ex["id"]}',ex['id'],True);examples.append(dict(**ex,asset=f'{name}-example-{k+1}',key=[dict(number=v,id=o,color=obs[o]['color'],xy=obs[o]['xy'],ab=co[o]) for o,v in enumbers.items()]))
        cases.append(dict(id=row['id'],name=name,bbox=box,classification=row['classification'],original=row['original'],prediction=row['prediction'],proposed=row['proposed'],key=[dict(number=v,id=o,color=obs[o]['color'],xy=obs[o]['xy'],ab=co[o]) for o,v in number.items()],examples=examples,alternatives=row['alternatives'],proposals=row.get('proposals',[])))
    # A standalone graph-paper SVG in short panels is readable at native scale.
    for section in range(8):
        rows=[o for o in ids if section*52-16<=sum(co[o])<(section+1)*52-16];lattice_svg(rows,st['traces'],assets/f'unwrapped-{section+1}.svg',f'Section {section+1}: s=a+b, d=a-b; colors recorded, ? unknown')
    _,states,*_=old_dataset();maps={name:dict(H=state['H'],coordinates=canonical(state),cohort='original saved observations only; R332 additions unavailable') for name,state in states.items()};maps={'R332':dict(H=g['H'],coordinates=co,cohort='1041 R332 indexed observations'),**maps}
    nodes=[dict(id=o,xy=obs[o]['xy'],color=obs[o]['color'],ab=co.get(o),status='working' if o in co else 'unindexed',number=j+1,source=obs[o].get('source'),location_kind=obs[o].get('location_kind'),hypothesis=di['color_hypotheses'].get(o),break_info=breakby.get(o)) for j,o in enumerate(sorted(obs))]
    nodemap={n['id']:n for n in nodes}
    for r in g['provisional_observations']:
        if r['id'] in nodemap:nodemap[r['id']].update(proposed_ab=r['cell'],reasons=r['reasons'])
        else:nodes.append(dict(id=r['id'],xy=r['xy'],color=r['color'],proposed_ab=r['cell'],status='provisional',reasons=r['reasons']))
    data=dict(image=dict(src='../../../beads-photo-2.jpg',width=photo.width,height=photo.height),nodes=nodes,edges=g['edges'],greedy=sp['segments'],traces=st['traces'],maps=maps,gaps=di['gaps'],cases=cases,endpoints=di['path_endpoints'],summary=di['counts'],spatial_coverage=st['coverage'])
    (out/'data.js').write_text('window.R333='+json.dumps(data,separators=(',',':'))+';\n');save(out/'cases.json',cases);save(out/'native-crops.json',crops)
    sections=[]
    for case in cases:
        name=case['name'];keys=' · '.join(f'{r["number"]}: {r["id"]} ({r["color"]}, {r["ab"]})' for r in case['key']);examplehtml=''
        for ex in case['examples']:examplehtml+=f'<figure><img src="assets/{ex["asset"]}-annotated.png" alt="Comparable native context for {ex["id"]}"><img src="assets/{ex["asset"]}-lattice.svg" alt="Comparable lattice"><figcaption>{ex["id"]}, translation {ex.get("translation")}; <a href="assets/{ex["asset"]}-native.png">literal native crop</a><details><summary>Every comparison marker</summary>{html.escape(str(ex["key"]))}</details></figcaption></figure>'
        sections.append(f'<section id="{name}"><h2>{case["id"]}</h2><p>{case["classification"]}. Recorded {case["original"]}; repeated-feature expectation {case["prediction"]}. Hypothesis: {html.escape(str(case["proposed"]))}. <button class="jump" data-id="{case["id"]}">Inspect both views</button></p><div class="pair"><figure><img src="assets/{name}-annotated.png" alt="Measured photograph and numbered observations"><figcaption>Magenta box = target support/site; thin cyan = black–red, purple = black–yellow. <a href="assets/{name}-native.png">Original native crop</a></figcaption></figure><figure><img src="assets/{name}-lattice.svg" alt="Matched lattice with recorded colors"><figcaption>Same numbered observations; unknown sites remain ?. Path lines have measured support; expectation is separate from color.</figcaption></figure></div><p>Competing explanations: {html.escape(" / ".join(case["alternatives"]))}</p><p>{html.escape(str(case["proposals"])) if case["proposals"] else "Color-only hypothesis preserves all neighbor equations. Local index changes require the complete boundary-link audit in the ledger."}</p><details><summary>Every numbered ID, color and lattice coordinate</summary>{html.escape(keys)}</details><h3>Comparable repeated structures</h3><div class="pair">{examplehtml}</div></section>')
    strip=''.join(f'<figure><img src="assets/unwrapped-{j}.svg" alt="Unwrapped lattice section {j}"><figcaption>Section {j}; <a href="assets/unwrapped-{j}.svg">standalone SVG</a></figcaption></figure>' for j in range(1,9))
    (out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R333 | Spirals on graph paper</title><link rel="stylesheet" href="style.css"><header><p class="eyebrow">PHOTO 2 / R333</p><h1>Spirals on graph paper</h1><p>Measured colors and links, repeated staircase structures, reversible error hypotheses.</p><p><a href="../../R333_REPORT.md">Scientific report</a> · <a href="../../R333_REPRODUCE.md">Reproduce</a> · <a href="../diagnosis/ledger.csv">Ranked error / gap ledger</a> · <a href="../periods-selected/motifs.html">Partial motifs</a> · <a href="../verification.json">Independent checks</a> · <a href="#cases">Detailed problems</a> · <a href="#unwrapped">Full unwrapped diagram</a></p><p class="notice">Cyan: black–red. Purple: black–yellow. Lines follow measured working links. Magenta: interruption or unconfirmed hypothesis. Markers locate pigment/reflection/material supports; they are never measured bead centers. Unknown sites retain ?. R332 additions await review.</p></header><div class="toolbar"><button id="fit">Whole circuit</button><button id="zoom-in">+</button><button id="zoom-out">−</button><button id="native">Photo 1:1</button><button id="raw">Raw photo</button><select id="section"><option value="">Full photo / lattice panel 1</option><option value="all">Whole circuit in both views</option></select><input id="selection" list="ids" placeholder="Observation ID"><datalist id="ids"></datalist><button id="recenter">Find</button></div><div class="toolbar"><label><input id="links" type="checkbox" checked>Working links</label><label><input id="br" type="checkbox" checked>Black–red</label><label><input id="by" type="checkbox" checked>Black–yellow</label><label><input id="repeat-only" type="checkbox">Repeated subset</label><label><input id="breaks" type="checkbox" checked>Interruptions / gaps</label><label><input id="provisional" type="checkbox">R332 provisional</label><label><input id="hypotheses" type="checkbox">Color hypotheses (rings)</label><label><input id="labels" type="checkbox">IDs at zoom</label><label><input type="checkbox" data-family="F0" checked>F0</label><label><input type="checkbox" data-family="F1" checked>F1</label><label><input type="checkbox" data-family="difference" checked>Difference</label></div><div class="toolbar"><label>Map <select id="map"></select></label><label>Index <select id="convention"><option>A</option><option>B</option></select></label><label><input type="checkbox" id="reverse">Reverse</label><label>Unwrap <select id="axes"><option value="strip">s=a+b, d=a−b</option><option value="paper">Graph paper a,b</option></select></label><label>Trace <select id="trace"><option value="regular">Learned regular staircases</option><option value="greedy">Flexible palette paths</option></select></label><span id="map-note"></span></div><main><div id="views"><div><h2>Original photograph</h2><canvas id="photo"></canvas></div><div><h2>Unwrapped lattice <span id="axis-label"></span></h2><canvas id="lattice"></canvas></div></div><p id="status"></p><aside id="info">Select a marker or a problem to compare its native photograph, original index and repeated examples. Drag either view to pan; wheel to zoom.</aside><section id="cases"><h2>Interruptions with matched evidence</h2><p>Numbers identify all working observations in each literal photographic context. For black targets, inspect neighboring colored bodies along the same drawn lattice directions; the marker is a support, not a center. Comparisons use matching directions and recorded colors. Provisional candidate locations and pure predictions remain distinct.</p>'''+''.join(sections)+'''</section><section id="unwrapped"><h2>Whole-circuit graph paper</h2><p>Eight overlapping views of the recorded lattice. The vertical strip coordinate d changes around the uncertain winding. Unknown graph-paper sites are unobserved, not absent physical beads. Use the interactive map selector to compare saved windings on their original observation cohorts.</p>'''+strip+'''</section></main><script src="data.js"></script><script src="viewer.js"></script></html>''')
    (out/'style.css').write_text(Path(__file__).with_name('review-style.css').read_text());(out/'viewer.js').write_text(Path(__file__).with_name('review-viewer.js').read_text())
    save(out/'generation.json',dict(seconds=time.perf_counter()-t,cases=len(cases),literal_crops=len(crops),standalone_lattice_panels=8));print('VIEWER',len(cases),len(crops),'seconds',time.perf_counter()-t,flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
