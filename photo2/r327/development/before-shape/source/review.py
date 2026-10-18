"""Native-pixel before/working/alternative comparisons and decision evidence."""
import html
from collections import Counter,defaultdict
import numpy as np
from PIL import Image,ImageOps
from .runner import ROOT,OUT,OLD,read,save
from photo2.r326.runner import key
from .analyze import metrics

def main():
    g=read(OUT/'graph.json.gz');old=read(OLD/'graph.json');alts=read(OUT/'lower-bend-alternatives.json.gz');reference=read(OUT/'reference.json');op={o['id']:o for o in g['observations']};image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');receipts=[];cards=[];pm=metrics(g,g['selected_window_states']);om=metrics(g,old['selected_window_states']);oldkeys={key(e) for e in old['graph']['edges']};newkeys={key(e) for e in g['graph']['edges']}
    def crop(name,center):
        x,y=map(int,center);box=[x-180,y-130,x+180,y+130];fn=name+'-native.png';image.crop(box).save(OUT/fn);assert np.array_equal(np.array(Image.open(OUT/fn)),np.array(image)[box[1]:box[3],box[0]:box[2]]);receipts.append(dict(file=fn,box=box,native_exact=True));return box,fn
    def panel(box,fn,graph,label,compare=False):
        parts=[f'<figure><svg viewBox="0 0 360 260" role="img" aria-label="{html.escape(label)}"><image href="{fn}" width="360" height="260"/>']
        if graph:
            for e in graph['edges']:
                a=np.array(op[e['source']]['xy'])-box[:2];b=np.array(op[e['target']]['xy'])-box[:2]
                if np.any(a<0) or np.any(a>[360,260]) or np.any(b<0) or np.any(b>[360,260]):continue
                k=key(e);color='#51ffaf' if compare and k not in oldkeys else '#00e5ff';title=f'{e["source"]} → {e["target"]}; delta {e["delta_ab"]}; working hypothesis'
                parts.append(f'<path d="M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f}" stroke="{color}" stroke-width="1.1"><title>{html.escape(title)}</title></path>')
            if compare:
                for e in old['graph']['edges']:
                    if key(e) in newkeys:continue
                    a=np.array(op[e['source']]['xy'])-box[:2];b=np.array(op[e['target']]['xy'])-box[:2]
                    if np.any(a<0) or np.any(a>[360,260]) or np.any(b<0) or np.any(b>[360,260]):continue
                    parts.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#ffae49" stroke-width="1.6" stroke-dasharray="4 3"><title>Withdrawn, rollback retained: {html.escape(e["source"])} / {html.escape(e["target"])}</title></path>')
            for o in g['observations']:
                p=np.array(o['xy'])-box[:2]
                if np.any(p<0) or np.any(p>[360,260]):continue
                c='#ff66ee' if o.get('provisional') else '#fff';parts.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="2" fill="none" stroke="{c}" stroke-width=".7"><title>{html.escape(o["id"])}</title></circle>')
        return ''.join(parts)+f'</svg><figcaption>{label}</figcaption></figure>'
    cases=[('upper','Upper bridge',[1660,285]),('inward','Inward bend',[1750,1625]),('black','Faint black reflection',[290,1410]),('closure','Lower bend',[1485,3010])]
    decisions=read(OUT/'final-changes.json.gz');classified=[];regional={}
    for wi,(before,after) in enumerate(zip(old['selected_window_states'],g['selected_window_states'])):
        if before==after:continue
        bh=g['windows'][wi]['hypotheses'][before[0]] if before else None;ah=g['windows'][wi]['hypotheses'][after[0]] if after else None
        br={r['observation']:r for r in bh['r327_evidence']['rows']} if bh else {};ar={r['observation']:r for r in ah['r327_evidence']['rows']} if ah else {};comparisons=[]
        for oid in br.keys()&ar.keys():comparisons.append(dict(observation=oid,utility_gain=ar[oid]['utility']-br[oid]['utility'],before=br[oid],after=ar[oid]))
        comparisons.sort(key=lambda r:-r['utility_gain'])
        regional[wi]=dict(window=wi,before=before,after=after,photo_score_before=bh['score'] if bh else None,photo_score_after=ah['score'] if ah else None,strongest_support_for_change=comparisons[:6],strongest_evidence_against_change=comparisons[-6:],new_supported_observations=sorted(ar.keys()-br.keys()),lost_supported_observations=sorted(br.keys()-ar.keys()),policy='These named native-support predictions explain the regional tradeoff. They are conditional evidence; compatibility can still select a local loss.')
    for r in decisions:
        ids=r['edge'][:2];common=[o for o in ids if o in pm and o in om];old_error=float(np.mean([om[o][0] for o in common])) if common else None;new_error=float(np.mean([pm[o][0] for o in common])) if common else None
        reason='missing comparable target predictions' if not common else ('selected configuration predicts these observed supports more closely' if new_error<old_error-.25 else ('selected configuration trades worse local prediction for other supports/global compatibility' if new_error>old_error+.25 else 'little local prediction separation; global compatibility/other supports decide'))
        affected={v['window'] for v in r['previous_witnesses']+r['current_witnesses']};details=[regional[wi] for wi in sorted(affected) if wi in regional]
        classified.append(dict(**r,regional_tradeoffs=details,old_endpoint_prediction_error_px=old_error,new_endpoint_prediction_error_px=new_error,photographic_comparison=reason,evidence_type='working inference, not an established image contradiction'))
    save(OUT/'decision-ledger.json.gz',classified)
    for name,title,center in cases:
        box,fn=crop(name,center);local=[r for r in classified if any(np.linalg.norm(np.array(op[o]['xy'])-center)<160 for o in r['edge'][:2])];table=''
        for r in local[:20]:
            a=r['old_endpoint_prediction_error_px'];b=r['new_endpoint_prediction_error_px'];errs='unavailable' if a is None else f'{a:.2f} → {b:.2f} px'
            table+=f'<tr><td>{r["action"]}</td><td>{html.escape(str(r["edge"]))}</td><td>{errs}</td><td>{r["photographic_comparison"]}</td></tr>'
        cards.append(f'<article><h2>{title}</h2><div class="panels">'+panel(box,fn,None,'Original native pixels')+panel(box,fn,old['graph'],'R326 working candidate')+panel(box,fn,g['graph'],'R327 working choice; green added, orange dashed withdrawn',True)+f'</div><details><summary>{len(local)} changed decisions near this crop; endpoint prediction evidence</summary><div class="scroll"><table><tr><th>Decision</th><th>Link / delta</th><th>R326 → R327 prediction error</th><th>Interpretation</th></tr>{table}</table></div><p>Showing up to 20 decisions. Errors are medians over correlated selected windows, averaged over available endpoints. Complete predictions and anchors are in the decision ledger. A lower error is conditional evidence, not proof of body identity.</p></details></article>')
    altcards=[]
    for i,a in enumerate(alts['alternatives']):
        box,fn=crop(f'lower-alt-{i}',[1485,3010]);h=a['compatibility']['cycle_audit']['possible_holonomies'];table=''.join(f'<tr><td>{r["observation"]}</td><td>{r["primary_error_pixel_utility"][0]:.2f}</td><td>{r["alternative_error_pixel_utility"][0]:.2f}</td></tr>' for r in a['photographic_consequences'][:8]);altcards.append(f'<details><summary>Alternative {i+1}: H={h}, cyclic gap {a["cyclic_gap"]:.3f}, {len(a["added_links"])} added / {len(a["withdrawn_links"])} withdrawn links</summary><div class="panels">'+panel(box,fn,None,'Original native pixels')+panel(box,fn,g['graph'],'Working primary')+panel(box,fn,a['graph'],f'Alternative {i+1}')+f'</div><p>Common supports: {a["common_supports"]}; mean cross-prediction error {a["mean_error_primary"]:.3f} → {a["mean_error_alternative"]:.3f} px. Conditional counts: {html.escape(str(a["conditional_counts"]))}. No count adopted.</p><table><tr><th>Largest changed prediction</th><th>Primary px</th><th>Alternative px</th></tr>{table}</table></details>')
    stats=dict(working_links=len(newkeys),indexed=sum(n['component'] is not None for n in g['intersections']),components=len(g['graph']['components']),added=len(newkeys-oldkeys),withdrawn=len(oldkeys-newkeys),decision_reasons=dict(Counter(r['photographic_comparison'] for r in classified)),independent_reference=reference['summary'],primary_holonomies=g['compatibility']['cycle_audit']['possible_holonomies'])
    historic=read(ROOT/'photo2/r326/results/historical-contested.json')['links'];stats['historical174_retained_working']=sum(key(dict(source=e['source'],target=e['target'],delta_ab=e['original_delta'])) in newkeys for e in historic);stats['indexed_black']=sum(n['color']=='black' and n['component'] is not None for n in g['intersections']);stats['provisional_links']=[list(key(e)) for e in g['graph']['edges'] if any(op[o].get('provisional') for o in (e['source'],e['target']))];stats['working_objective']=g['incumbent_selection']
    classes=dict(actual_new_established_image_contradictions=[],model_disagreement='Archived alternate contexts/affine assignments remain available; no penalty or veto.',conditional_prediction_mismatches='Target-excluded coordinate/native-response comparisons in graph evidence and decision ledger; not independent contradictions.',potential_direct_counterevidence=[dict(edge=list(key(e)),intervening_observations=e['intervening_observations'],foreground_fraction=e['foreground_fraction']) for e in g['graph']['unresolved_edges'] if e['intervening_observations'] or e['foreground_fraction']<=.95],missing_support=[dict(edge=list(key(e)),reasons=e['reasons']) for e in g['graph']['unresolved_edges'] if e['supporting_windows']<2],policy='Visible intermediate supports and foreground/background samples are image evidence with uncertain body identity; darkness and absent observations are never proof of absence.')
    save(OUT/'evidence-classes.json',classes);save(OUT/'summary.json',stats);save(OUT/'native-crops.json',receipts)
    head='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R327 working reconstruction</title><style>body{font:16px/1.5 system-ui;max-width:1160px;margin:24px auto;padding:0 16px;color:#222;background:#fafafa}h1{font-size:27px}article{border-top:1px solid #aaa;margin-top:24px;padding-top:8px}.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}figure{margin:0}svg{width:100%;height:auto}figcaption{font-size:13px}table{border-collapse:collapse;font-size:13px}td,th{padding:6px;border:1px solid #ccc;text-align:left}details{margin:16px 0}summary{cursor:pointer}.scroll{overflow:auto}a{color:#165797}@media(max-width:750px){.panels{grid-template-columns:1fr}} </style>'''
    body=f'<h1>R327 — reversible photographic working decisions</h1><p><b>{stats["indexed"]} indexed supports, {stats["working_links"]} working links, {stats["components"]} components.</b> {stats["added"]} links added and {stats["withdrawn"]} withdrawn relative to R326. These are selected working hypotheses, not a certified physical lattice. Independent historical reference recovery: {reference["summary"]["recovered"]}/86 links, {reference["summary"]["interior_recovered"]}/45 interior; {reference["summary"]["wrong_automatic_edges"]} wrong reference links. No new independent truth is claimed.</p><p>White circles mark measured supports, not bead centers. Magenta marks the provisional faint black site. Cyan/green links are reversible working choices. Orange dashed links remain available for rollback. Alternative affine fits are model disagreement, never automatically image contradiction.</p><p>Original pixels, target-excluded geometry predictions, native response, and supported sequences determine the new objective. Shared geometry applies to every color; black targets use colored anchors where possible. Low predicted brightness is missing support, not proof of absence. This is cross-prediction within a previously discovered candidate bank, not independent validation.</p><p><a href="../../R327_REPORT.md">Report</a> · <a href="../../R327_REPRODUCE.md">Reproduce</a> · <a href="summary.json">Summary</a> · <a href="graph.json.gz">Working graph</a> · <a href="established-subset.json">Independent reference subset</a> · <a href="decision-ledger.json.gz">Reversible decision ledger</a> · <a href="verification.json">Verification</a></p>'
    (OUT/'index.html').write_text(head+body+''.join(cards)+'<article><h2>Actively tested lower-bend alternatives</h2><p>Each alternative forces a different lower-bend hypothesis, then constructs one compatible whole-window witness. Forcing bonuses are removed from reported cyclic scores. Different abstentions mean these are not equal-coverage accuracy experiments.</p>'+''.join(altcards)+'</article></html>')
if __name__=='__main__':main()
