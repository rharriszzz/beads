"""Complete offline canvas viewer and matched, fully enumerated photo tiles."""
import argparse,ast,csv,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
from .common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);args=ap.parse_args();run=Path(args.run);out=Path(args.output);out.mkdir(parents=True,exist_ok=True);assets=out/'assets';assets.mkdir(exist_ok=True)
    r=read(run/'graph.json.gz');g,base,H=baseline();co={x['id']:x['ab'] for x in r['coordinates']};obs={x['id']:x for x in r['observations']};accepted={x['id']:x for x in r['accepted_additions']};pending={x['id']:x for x in r['provisional_observations']};ref=read(ROOT/'photo2/r328/results/established-subset.json');confirmed={o for x in ref['links']+ref['peripheral_links'] for o in [x['source'],x['target']]};nodes=[]
    for o in obs.values():
        oid=o['id'];status='confirmed' if oid in confirmed else 'working' if oid in co else 'unresolved'
        if 'provisional' in str(o).lower():status='provisional'
        nodes.append(dict(id=oid,xy=o['xy'],color=o['color'],status=status,ab=co.get(oid),new=oid in accepted and not accepted[oid]['known'],
            newly_indexed=oid in accepted and accepted[oid]['known'],source_id=o.get('source_id',oid),source=o.get('source'),
            evidence=accepted.get(oid,pending.get(oid)),proposed_ab=pending[oid].get('cell') if oid in pending else None,kind=o.get('kind'),note='Confirmed = historical R161 association, not new blind truth.' if status=='confirmed' else 'Working photographic assignment; no physical-center measurement.'))
    # Group provisional alternatives for display; all source alternatives remain
    # accessible in the full scientific ledger and on each group record.
    groups={}
    for p in r['provisional_observations']:
        if p['id'] in co:continue
        key=tuple(p.get('cell',[])) if p.get('cell') else tuple(np.rint(np.array(p['xy'])/10).astype(int));groups.setdefault(key,[]).append(p)
    for key,rows in groups.items():
        p=min(rows,key=lambda x:(len(x.get('reasons',[])),x.get('error',999),x['id']))
        if p['id'] in obs:continue
        nodes.append(dict(id=p['id'],xy=p['xy'],color=p.get('color','?'),status='provisional',ab=None,proposed_ab=p.get('cell'),new=True,
            evidence=p,alternatives=[x['id'] for x in rows],source=p.get('source'),note='Native-material candidate; proposed coordinates do not occupy the accepted lattice.'))
    # Pure predictions have no observed point. They deliberately use a separate
    # marker and switch; their coordinates are never counted as observations.
    for p in r.get('predictions',[]):nodes.append(dict(id=p['id'],xy=p['prediction'],color='?',status='predicted',ab=None,proposed_ab=p['cell'],new=True,evidence=p,note='Geometric vacancy prediction only; no physical missing bead is inferred.'))
    for p in r.get('unrepresented_candidates',[]):
        if p['id'] in {x['id'] for x in nodes}:continue
        nodes.append(dict(id=p['id'],xy=p['xy'],color=p.get('color','?'),status='candidate',ab=None,new=True,evidence=p,note='Retained pixel candidate not associated to the working lattice; may be duplicate, shadow or occluded material.'))
    index={x['id']:j for j,x in enumerate(nodes)}
    for j,n in enumerate(nodes):n['number']=j+1
    edges=[dict(e,kind='new' if e.get('origin')=='R332' else 'baseline') for e in r['edges']]
    for e in r['link_candidates']:
        if e['status']!='accepted working addition':edges.append(dict(e,kind='unresolved'))
    for e in r.get('coordinate_only_edges',[]):edges.append(dict(e,kind='coordinate'))
    accepted_pairs={edgekey(e['source'],e['target']) for e in r['edges']}
    alternatives=read(ROOT/'photo2/r332/audit/cached-edge-alternatives.json.gz')['edges']
    for e in alternatives:
        if e['source'] not in index or e['target'] not in index:continue
        if edgekey(e['source'],e['target']) in accepted_pairs:continue
        d=tuple(e['delta_ab']);a,z=e['source'],e['target']
        if d not in STEPS:a,z=z,a;d=tuple(-np.array(d))
        edges.append(dict(e,source=a,target=z,delta_ab=[int(v) for v in d],family=FAMILY[d],kind='alternative',status='cached competing local assignment; not accepted'))
    # Explicit same-family colored comparisons for difficult black observations.
    for node in nodes:
        if node['color']!='black' or not node.get('new') or not node.get('evidence'):continue
        comparisons=[]
        for family in ['F0','F1','difference']:
            options=[]
            for e in r['edges']:
                if e['family']!=family:continue
                a,z=obs[e['source']],obs[e['target']]
                if a['color']=='black' or z['color']=='black':continue
                midpoint=(np.array(a['xy'])+z['xy'])/2;distance=np.linalg.norm(midpoint-node['xy'])
                if distance<180:options.append((distance,e['source'],e['target']))
            if options:
                distance,a,z=min(options);comparisons.append(dict(family=family,source=a,target=z,context_distance_px=float(distance),note='Actual accepted colored-neighbor link in the same lattice family; compare the visible bodies, not black highlight centers.'))
        node['same_direction_colored_comparisons']=comparisons
    data=dict(nodes=nodes,edges=edges,regions=[dict(name=n,bbox=b) for n,b in REGIONS],summary=r['summary'],baseline=dict(recorded=len(g['observations']),indexed=len(base),links=len(g['graph']['edges'])),image=dict(width=2540,height=3182,src='../../../beads-photo-2.jpg'))
    (out/'data.js').write_text('window.R332='+json.dumps(data,separators=(',',':'))+';\n')
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font=ImageFont.truetype(fontpath,15);small=ImageFont.truetype(fontpath,12);figures=[];regional=[]
    colors={'F0':'#00c9fa','F1':'#5ee84b','difference':'#ffaf35'};nodecolors={'red':'#ff4949','yellow':'#ffed39','black':'#ffffff','?':'#bec6d3'}
    oldlists={}
    for node in ast.walk(ast.parse((ROOT/'photo2/r331/review.py').read_text())):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ['gids','eids','fids','blackids']:oldlists[target.id]=set(ast.literal_eval(node.value))
    oldpanels={'G':oldlists['gids'],'upper-F':oldlists['fids'],'inward':oldlists['eids']}
    for name,bbox in REGIONS:
        local=[n for n in nodes if inside(n['xy'],bbox) and n['status'] not in ['predicted','candidate']];local.sort(key=lambda n:(n['xy'][1],n['xy'][0]));lookup={n['id']:j+1 for j,n in enumerate(local)};counts={}
        native=assets/(name+'-native.png');photo.crop(bbox).save(native);figures.append(dict(file='assets/'+native.name,bbox=bbox))
        for version in ['before','after']:
            scale=3;W=(bbox[2]-bbox[0])*scale;HH=(bbox[3]-bbox[1])*scale;canvas=photo.crop(bbox).resize((W,HH),Image.Resampling.NEAREST);draw=ImageDraw.Draw(canvas)
            shown={n['id'] for n in local if version=='after' or n['id'] in {o['id'] for o in g['observations']}}
            ee=[e for e in edges if e['kind'] in (['baseline','new'] if version=='after' else ['baseline']) and e['source'] in shown and e['target'] in shown]
            for e in ee:
                a,z=[nodes[index[e[k]]]['xy'] for k in ['source','target']];xy=[((p[0]-bbox[0])*scale,(p[1]-bbox[1])*scale) for p in [a,z]];draw.line(xy,fill=colors[e['family']],width=3 if e['kind']=='new' else 2)
            # Numbered labels use four staggered positions and a halo, while a
            # separate complete CSV key preserves every full stable ID.
            occupied=[]
            for n in local:
                if n['id'] not in shown:continue
                x,y=(np.array(n['xy'])-bbox[:2])*scale;col=nodecolors.get(n['color'],'white');rad=5
                if n['status']=='provisional':draw.polygon([(x,y-rad-2),(x-rad-2,y+rad),(x+rad+2,y+rad)],outline='#ff54e0',width=2)
                elif n['id'] in base and name in oldpanels and n['id'] not in oldpanels[name]:draw.rectangle((x-rad,y-rad,x+rad,y+rad),outline='#ffb54d',width=2)
                else:draw.ellipse((x-rad,y-rad,x+rad,y+rad),outline='#46ffff' if n['new'] else col,width=2)
                label=str(lookup[n['id']]);tw=draw.textbbox((0,0),label,font=font)[2]+5;th=20;choices=[(x+6,y-23),(x+6,y+5),(x-tw-6,y-23),(x-tw-6,y+5),(x-tw/2,y-34)]
                def overlap(b):return sum(max(0,min(b[2],a[2])-max(b[0],a[0]))*max(0,min(b[3],a[3])-max(b[1],a[1])) for a in occupied)
                lx,ly=min(choices,key=lambda p:overlap((p[0],p[1],p[0]+tw,p[1]+th)));lx=max(0,min(W-tw,lx));ly=max(0,min(HH-th,ly));occupied.append((lx,ly,lx+tw,ly+th));draw.line((x,y,lx+tw/2,ly+th/2),fill='white',width=1);draw.rounded_rectangle((lx,ly,lx+tw,ly+th),radius=3,fill='#142138');draw.text((lx+2,ly),label,font=font,fill='white')
            canvas.save(assets/(name+'-'+version+'.png'));counts[version]=dict(observations=len(shown),links=len(ee),provisional=sum(n['id'] in shown and n['status']=='provisional' for n in local))
        with (assets/(name+'-labels.csv')).open('w',newline='') as f:
            fields=['label','id','color','status','new','newly_indexed','ab','proposed_ab','source_id','shown_in_R331_named_panel'];writer=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(dict(n,label=lookup[n['id']],shown_in_R331_named_panel=n['id'] in oldpanels[name] if name in oldpanels else 'no corresponding named panel') for n in local)
        rr=dict(region=name,bbox=bbox,**counts,newly_recovered=sum(n['new'] and n['status'] not in ['provisional','predicted','candidate'] for n in local),newly_indexed=sum(n['newly_indexed'] for n in local if 'newly_indexed' in n),unindexed_known=sum(n['id'] in obs and n['ab'] is None for n in local),unresolved_native_candidate_groups=sum(n['status']=='candidate' and inside(n['xy'],bbox) for n in nodes));regional.append(rr)
    save(out/'native-crops.json',figures);save(out/'regional-counts.json',regional)
    beforeafter=[]
    for rr in regional:
        name=rr['region'];beforeafter.append(f'<section><h2>{name}</h2><p>Before: {rr["before"]["observations"]} baseline recorded observations, {rr["before"]["links"]} actual working links. After: {rr["after"]["observations"]} shown observations/candidates, {rr["after"]["links"]} accepted links; {rr["newly_recovered"]} accepted new observations. Provisional triangles: {rr["after"]["provisional"]}. <a href="assets/{name}-labels.csv">Every numbered ID/status</a>.</p><div class="pair"><figure><img src="assets/{name}-before.png" alt="Complete baseline labels and working links in {name}"><figcaption>All baseline records, all three working directions. Amber observation squares in G/F/inward mark indexed records omitted from that R331 named panel.</figcaption></figure><figure><img src="assets/{name}-after.png" alt="Additive completion and provisional candidates in {name}"><figcaption>Same original pixels. Cyan/green/amber lines: F0/F1/difference accepted links. Bright cyan observation rings are new; magenta triangles are provisional.</figcaption></figure></div></section>')
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R332 complete photographic lattice</title><style>body{margin:0;font:15px/1.4 system-ui;background:#101924;color:#e9eff6}a{color:#81d8ff}header,main{padding:14px 20px}h1{margin:5px 0;font-size:26px}.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:10px;background:#1c2b3e}.toolbar label{white-space:nowrap}button,input,select{font:inherit}button,select{padding:5px}#stage{display:grid;grid-template-columns:minmax(0,1fr) 320px;height:73vh;min-height:480px}#view{width:100%;height:100%;background:#050a11;touch-action:none}#info{padding:12px;overflow:auto;background:#19273a;overflow-wrap:anywhere}#info pre{white-space:pre-wrap;font-size:12px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:15px}img{max-width:100%;height:auto}figure{margin:0}section{margin:30px 0}table{font-size:12px;border-collapse:collapse}td,th{padding:4px;border-bottom:1px solid #567}#selection{width:240px}#legend{font-size:13px;color:#c6d4e4}details{margin:8px 0}.notice{padding:10px;background:#253a50}@media(max-width:760px){#stage{grid-template-columns:1fr;height:auto}#view{height:65vh}#info{max-height:300px}.pair{grid-template-columns:1fr}header,main{padding:10px}.toolbar{gap:6px}}</style><header><h1>Every recorded observation and every working link</h1><p id="summary"></p><p><a href="../../R332_REPORT.md">Report</a> · <a href="../../R332_REPRODUCE.md">Reproduce</a> · <a href="../verification.json">Independent verification</a> · <a href="../results/omissions.json.gz">Omission/candidate ledger</a> · <a href="#tiles">Complete before/after tiles</a></p><p class="notice">The user found no incorrect labels or links in R331's displayed assignments. That supports those particular illustrations. The baseline remains a conditional working graph; the new additions are submitted for photographic review. Observation markers identify measured pigment/reflection/dark-material supports, never measured physical centers.</p></header><div class="toolbar"><button id="fit">Whole photo</button><button id="zin">+</button><button id="zout">−</button><button id="native">Native 1:1</button><select id="region"><option value="">Review region…</option></select><select id="labels"><option value="numbers">Number labels at magnification</option><option value="ids">Full IDs (use high magnification)</option><option value="none">No labels</option></select><input id="selection" list="beads" placeholder="Select stable ID"><datalist id="beads"></datalist><button id="recenter">Recenter selected bead</button><span id="zoom"></span></div><div class="toolbar" id="layers"><label><input type="checkbox" data-status="confirmed" checked> Historical reference</label><label><input type="checkbox" data-status="working" checked> Accepted working</label><label><input type="checkbox" data-status="provisional" checked> Provisional</label><label><input type="checkbox" data-status="unresolved" checked> Unindexed recorded</label><label><input type="checkbox" data-status="predicted"> Pure predictions</label><label><input type="checkbox" data-status="candidate"> Unassociated pixel candidates</label><label><input type="checkbox" data-kind="baseline" checked> Baseline working links</label><label><input type="checkbox" data-kind="new" checked> New accepted links</label><label><input type="checkbox" data-kind="unresolved"> Unresolved links</label><label><input type="checkbox" data-kind="coordinate"> Coordinate-only neighbors</label></div><div class="toolbar"><label><input type="checkbox" data-family="F0" checked> Cyan F0 (+a)</label><label><input type="checkbox" data-family="F1" checked> Green F1 (+b)</label><label><input type="checkbox" data-family="difference" checked> Amber difference (+a,−b)</label><label><input type="checkbox" id="pixels"> Selected native material pixels</label><label><input type="checkbox" id="predictions"> Selected geometry prediction</label><button id="raw">Toggle all overlays</button></div><div id="stage"><canvas id="view" aria-label="Native photograph; pan, zoom and click any recorded bead"></canvas><aside id="info">Click a bead, choose a region, or enter a stable observation ID.</aside></div><main><p id="legend">Drag to pan. Wheel/pinch or +/− to magnify. At high zoom every visible observation can carry its full ID; numbered tiles below retain readable complete keys. New observations have cyan outer rings; magenta triangles are provisional. Hollow squares are geometric predictions only. Dashed gray lines are coordinate-only relationships, never accepted photographic links. The original photograph is loaded at its full native resolution.</p><h2 id="tiles">Complete matched before/after images</h2>'''+''.join(beforeafter)+'''<p>No percentage of all physical beads recovered is claimed. Unobserved positions are not physically missing beads. Provisional alternatives do not propagate into accepted coordinates.</p></main><script src="data.js"></script><script src="viewer.js"></script></html>'''
    html=html.replace('<label><input type="checkbox" data-kind="coordinate"> Coordinate-only neighbors</label>','<label><input type="checkbox" data-kind="coordinate"> Coordinate-only neighbors</label><label><input type="checkbox" data-kind="alternative"> Cached competing row/direction links</label>')
    (out/'index.html').write_text(html)
    js=Path(__file__).with_name('viewer.js').read_text();(out/'viewer.js').write_text(js);print('VIEW',len(nodes),'nodes',len(edges),'edges',len(regional),'complete tiles')

if __name__=='__main__':main()
