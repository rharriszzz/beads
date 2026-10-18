"""Export frozen single-component growth, photographic witnesses and review."""
import argparse, collections, gzip, json, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from .grow import ROOT,BANK,SEED,read,save,sha,STEPS

def key(a,b,d):return (a,b,*d) if a<b else (b,a,*[-v for v in d])
def build(bank,prepared,state):
    op={o['id']:o for o in bank['observations']};checks={(e['source'],e['target']):e for e in prepared['checks']};patches=prepared['patches'];edges={};selected=[[] for _ in bank['windows']];birth={SEED:0};growth=[]
    for step,r in enumerate(state['path']):
        if r.get('skipped'):growth.append(r);continue
        wi=r['window'];p=patches[wi][r['patch']];hi=r['hypothesis'];selected[wi]=[hi]
        for oid in p['assignments']:birth.setdefault(oid,step)
        new=[]
        for a,b,d in p['edges']:
            k=key(a,b,d)
            if k not in edges:
                checksrow=checks[tuple(sorted((a,b)))];e=dict(source=a,target=b,delta_ab=d,family=STEPS[tuple(d)],first_growth_step=step,witnesses=[],foreground_fraction=checksrow['foreground_fraction'],intervening_observations=checksrow['intervening_observations'],status='provisional working link',independently_established=False)
                edges[k]=e;new.append(list(k))
            if [wi,hi] not in edges[k]['witnesses']:edges[k]['witnesses'].append([wi,hi])
        growth.append(dict(r,new_edges=new,patch_supports=sorted(p['assignments']),parent_omitted=p['parent_omitted'],families=sorted({STEPS[tuple(e[2])] for e in p['edges']}),score_terms=p['score_terms']))
    for e in edges.values():e['supporting_windows']=len({w for w,h in e['witnesses']})
    H=state['H'];coords={}
    for c in state['coords']:
        ab=[c['ab'][d]-c['turn']*H[d] for d in range(2)] if H is not None else c['ab']
        if c['observation'] in coords:assert coords[c['observation']]==ab
        coords[c['observation']]=ab
    nodes=[]
    for o in bank['observations']:
        ab=coords.get(o['id']);nodes.append(dict(id=o['id'],xy=o['xy'],color=o['color'],component=0 if ab is not None else None,relative_ab=ab,status='working indexed support' if ab is not None else 'unindexed observed support',first_growth_step=birth.get(o['id']),conditional_indices=None if ab is None else dict(A=7*ab[0]+6*ab[1],B=6*ab[0]+7*ab[1])))
    before={key(e['source'],e['target'],e['delta_ab']):e for e in bank['graph']['edges']};changes=[]
    for action,keys in [('added',edges.keys()-before.keys()),('withdrawn',before.keys()-edges.keys())]:
        for k in sorted(keys):
            witnesses=[]
            for step,r in enumerate(state['path']):
                if r.get('skipped'):continue
                p=patches[r['window']][r['patch']];aa=p['assignments']
                if k[0] not in aa or k[1] not in aa:continue
                h=bank['windows'][r['window']]['hypotheses'][r['hypothesis']];rows=[rr for rr in h['r327_evidence']['rows'] if rr['observation'] in k[:2]]
                witnesses.append(dict(window=r['window'],hypothesis=r['hypothesis'],delta_ab=[aa[k[1]][d]-aa[k[0]][d] for d in range(2)],target_predictions=rows))
            old=[]
            for wi,sels in enumerate(bank['selected_window_states']):
                for hi in sels:
                    h=bank['windows'][wi]['hypotheses'][hi];aa=h['assignments']
                    if k[0] in aa and k[1] in aa:old.append(dict(window=wi,hypothesis=hi,delta_ab=[aa[k[1]]['ab'][d]-aa[k[0]]['ab'][d] for d in range(2)],target_predictions=[rr for rr in h['r327_evidence']['rows'] if rr['observation'] in k[:2]]))
            changes.append(dict(action=action,edge=list(k),previous_witnesses=old,current_witnesses=witnesses,photographic_contradiction=False,explanation='Selected continuation based on the local photographic score and its subsequent compatible growth; alternative model assignments are retained.'))
    result=dict(schema='r328-single-seed-growth-v1',seed=SEED,observations=bank['observations'],intersections=nodes,graph=dict(edges=list(edges.values()),components=[dict(id=0,origin=SEED,nodes=sorted(coords))],closure=dict(identified=bool(H is not None and len(state['returns'])>=3),holonomy_ab=H,return_observations=state['returns'],policy='Conditional return of the same observed supports, not independent photographic certification')),growth=growth,selected_window_states=selected,unwrapped_coordinates=state['coords'],score=state['score'],stations_px=bank['stations_px'],period_px=bank['period_px'],source_bank_sha256=sha(BANK),image_sha256=sha(ROOT/'beads-photo-2.jpg'))
    summary=dict(seed=SEED,indexed=len(coords),unindexed=len(nodes)-len(coords),links=len(edges),components=1,selected_patches=sum(not r.get('skipped',False) for r in state['path']),skipped_windows=[r['window'] for r in state['path'] if r.get('skipped')],return_observations=len(state['returns']),H=H,score=state['score'],added_links=sum(c['action']=='added' for c in changes),withdrawn_links=sum(c['action']=='withdrawn' for c in changes),single_window_links=sum(e['supporting_windows']==1 for e in edges.values()),minimum_patch_direction_families=min(len(r['families']) for r in growth if not r.get('skipped')),provisional_black_links=sum('PROV326-290-1410' in (e['source'],e['target']) for e in edges.values()))
    return result,summary,changes

def review(out,g,old,summary):
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');op={o['id']:o for o in g['observations']};newset={key(e['source'],e['target'],e['delta_ab']) for e in g['graph']['edges']};oldset={key(e['source'],e['target'],e['delta_ab']) for e in old['graph']['edges']};cases=[('upper',(1480,155,1840,425)),('inward',(1570,1450,1940,1820)),('lower',(1230,2860,1650,3160)),('black',(175,1295,405,1525))];html=[]
    colors={'F0':'#00d9ff','F1':'#7dff62','difference':'#ffb441'}
    def lines(edges,box,highlight):
        x0,y0,x1,y1=box;ss=[]
        for e in edges:
            a,b=[op[e[k]]['xy'] for k in ('source','target')]
            if not all(x0<=p[0]<=x1 and y0<=p[1]<=y1 for p in [a,b]):continue
            changed=key(e['source'],e['target'],e['delta_ab']) in highlight
            ss.append(f'<line x1="{a[0]-x0}" y1="{a[1]-y0}" x2="{b[0]-x0}" y2="{b[1]-y0}" stroke="{colors[e["family"]]}" stroke-width="{2.3 if changed else 1}" opacity="{1 if changed else .6}"><title>{e["source"]} → {e["target"]} {e["delta_ab"]}</title></line>')
        return ''.join(ss)
    for name,box in cases:
        im.crop(box).save(out/f'{name}-native.png');w,h=box[2]-box[0],box[3]-box[1]
        panels=[]
        for label,edges,highlight in [('Original photograph',[],set()),('R327',old['graph']['edges'],oldset-newset),('R328 grown from one seed',g['graph']['edges'],newset-oldset)]:
            panels.append(f'<figure><figcaption>{label}</figcaption><svg viewBox="0 0 {w} {h}" role="img" aria-label="{name}: {label}"><image href="{name}-native.png" width="{w}" height="{h}"/>{lines(edges,box,highlight)}</svg></figure>')
        html.append(f'<h2>{name.title()}</h2><div class="panels">'+''.join(panels)+'</div>')
    all_lines=[]
    seed_xy=op[SEED]['xy']
    for e in g['graph']['edges']:
        a,b=[op[e[k]]['xy'] for k in ('source','target')];all_lines.append(f'<line data-step="{e["first_growth_step"]}" x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{colors[e["family"]]}" stroke-width="3"/>')
    steps=[dict(step=i,window=r['window'],nodes=len({c['id'] for c in g['intersections'] if c['first_growth_step'] is not None and c['first_growth_step']<=i}),skipped=r.get('skipped',False)) for i,r in enumerate(g['growth'])]
    index=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R328 — one seed around the circuit</title><style>body{{font:16px system-ui;margin:24px auto;padding:0 16px;max-width:1250px;background:#111;color:#eee}}a{{color:#86d9ff}}svg{{width:100%;height:auto}}.panels{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}figure{{margin:0}}figcaption{{margin-bottom:8px}}.overview{{max-width:500px}}input{{width:100%}}button{{padding:8px;margin:5px}}@media(max-width:700px){{.panels{{grid-template-columns:1fr}}}}</style><h1>One seed, one growing component</h1><p>{summary['indexed']} observed supports · {summary['links']} working links · {summary['return_observations']} observed return matches · conditional H={summary['H']}.</p><p>Each step attaches a connected local patch spanning neighboring diagonal lines. The search keeps alternative histories and checks the return to the original supports. Every displayed link is provisional unless separately supported by the historical reference.</p><p><a href="../../../R328_REPORT.md">Report</a> · <a href="graph.json.gz">Working reconstruction</a> · <a href="changes.json.gz">Changed-link photographic evidence</a> · <a href="established-subset.json">Independent subset</a> · <a href="alternatives.json.gz">Growth alternatives</a> · <a href="verification.json">Verification</a></p><label for="step">Growth step</label><input id="step" type="range" min="-1" max="{len(steps)-1}" value="{len(steps)-1}"><button id="play">Play growth</button><button id="raw">Toggle overlays</button><p id="status"></p><div class="overview"><svg viewBox="0 0 {im.width} {im.height}" role="img" aria-label="Connected growth around the original photograph"><image href="../../../beads-photo-2.jpg" width="{im.width}" height="{im.height}"/><circle cx="{seed_xy[0]}" cy="{seed_xy[1]}" r="8" fill="none" stroke="white" stroke-width="3"/><g id="growth">{''.join(all_lines)}</g></svg></div><p>Cyan: F0 · green: F1 · amber: difference direction. Thick crop lines mark changes against R327. Lines join measured reflection/pigment supports, not inferred bead centers.</p>{''.join(html)}<script>const steps={json.dumps(steps)}, slider=document.querySelector('#step');let timer=null;function show(){{let i=+slider.value;document.querySelectorAll('[data-step]').forEach(e=>e.style.display=+e.dataset.step<=i?'':'none');document.querySelector('#status').textContent=i<0?'Seed: one observed support, one component':`Step ${{i}}: window ${{steps[i].window}}, ${{steps[i].nodes}} observed supports, one component${{i===steps.length-1?', return checked':''}}`;}}slider.oninput=show;document.querySelector('#play').onclick=()=>{{if(timer){{clearInterval(timer);timer=null;return}}slider.value=-1;show();timer=setInterval(()=>{{slider.value=+slider.value+1;show();if(+slider.value===steps.length-1){{clearInterval(timer);timer=null}}}},80)}};document.querySelector('#raw').onclick=()=>document.querySelectorAll('svg line').forEach(e=>e.style.visibility=e.style.visibility==='hidden'?'':'hidden');show();</script></html>'''
    # Report is two levels above results, not three.
    index=index.replace('../../../R328_REPORT.md','../../R328_REPORT.md')
    (out/'index.html').write_text(index)
    save(out/'native-crops.json',dict(image_sha256=g['image_sha256'],crops=[dict(name=n,box=list(b)) for n,b in cases]))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output)
    if out.exists():raise RuntimeError('Preserve existing export')
    out.mkdir(parents=True);bank=read(BANK);prep=read(Path(args.run)/'prepared.json.gz');search=read(Path(args.run)/'search.json.gz');state=search['states'][0]
    assert search['completed'] and state['H'] is not None
    g,s,c=build(bank,prep,state);save(out/'graph.json.gz',g);save(out/'summary.json',s);save(out/'changes.json.gz',c);save(out/'alternatives.json.gz',dict(states=search['states'][1:],source=args.run,policy='Bounded search alternatives, never pooled into one graph.'))
    save(out/'growth-search.json.gz',dict(search,states=[]));review(out,g,bank,s)
    save(out/'scientific-seal.json',dict(graph_sha256=sha(out/'graph.json.gz'),bank_sha256=sha(BANK),run=args.run,sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r328').glob('*.py'))},policy='Frozen before retrospective reference evaluation; R161 is previously exposed development evidence.'))
    print(json.dumps(s),flush=True)
if __name__=='__main__':main()
