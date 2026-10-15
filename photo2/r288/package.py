"""Small front-page review with complete expandable scientific evidence."""
from html import escape
from .common import *
CAPTIONS={
'N07':'W preserves the fuller 515-pixel red interior. Minimum perturbation IoU improves from M 0.389 to W 0.968. The old large change came from a two-pair dark connector being merged. J remains undersized.',
'N11':'W removes the abrupt merger instability, but its nominal 694-pixel support is identical to M, including the questionable upper extension. That extension remains unresolved. H rejects the whole feature; trimming it is not a demonstrated success.',
'N06':'W separates the two yellows: 1148 → 576 pixels. The original two-pair interface was dark, but M treated its short length as permission to merge.',
'P2':'The good broad red interior remains exactly 495 pixels in M and W. This preserves S/M’s success; it is not a new improvement over that nominal measurement.',
'P5':'Nominal W=M=664 pixels; the original repaired-M measurement remains. W stays much more stable under the small changes that remerged M. The user’s good J alternative is preserved.',
'C05':'M and W retain the same acceptable-but-imperfect 527-pixel red interior. No claim that its full boundary is now correct.',
'Q01':'The anchor retains broad diffuse red and a small side extension. The atlas shows real-looking red/yellow merger corrections, but also a poor preference on a rejected tinted-dark cue.',
'Q02':'W preserves the nominal yellow interior while improving perturbation behavior. A new construction need not change its baseline pixels.',
'Q03':'Broad diffuse red survives. Nearby weak/uncertain cues remain in the atlas, including abstention.',
'Q04':'Clear yellow anchor is preserved; a neighboring red merger is removed. Weak peripheral cues still produce questionable colored supports. These failures remain visible.',
'Q05':'Fuller diffuse red remains separated from its nearby red neighbor. W and M agree nominally.',
'Q06':'Independent success: M visibly joins two yellows; W retains the target (1151 → 588 pixels). The second yellow remains a separate photographic observation.',
'Q07':'W preserves diffuse red while reducing instability. This is not a new physical bead identity.',
'Q08':'J includes upper-neighbor material. The smaller M/W measurement is better confined; area maximization would choose badly.',
'Q09':'The anchor retains diffuse red. Another red cue loses a neighboring merger, but a tiny tinted reflection is still interpreted as red; see the full atlas.',
'Q10':'M/W avoid J’s upper yellow contribution. Nearby feature/color ambiguity remains unresolved.',
'Q11':'Broad red is retained beyond J’s highlight core. Ownership and full-body extent remain unknown.',
'Q12':'The same nominal yellow support is retained with a more stable construction. Native alternatives are kept independently.',
'Q13':'Yellow anchor remains. A weak nearby feature is reduced to a tiny uncertain region and abstains; this is not certified recovery.',
'Q14':'SELECTOR FAILURE: J123 is preferred even though all 392 additional M/W pixels pass direct continuation. W becomes1321 under contrast+10%; the adequacy rule still requires a stable alternative before counting that evidence against J. No confirmation retuning.',
'Q15':'The anchor and nearby clear yellow remain. A high-source 426-pixel yellow still abstains, and a weak colored interstice is rejected. Inspect the remaining material uncertainty.',
'Q01-merge':'Independent neighboring red: M1181 → W593 removes an upper bead contribution while retaining a broad target interior. The cue was frozen with its entire neighborhood before results.',
'Q01-weak':'PRESERVED FAILURE: a previously rejected cue still receives a preference for M644 on tinted dark/reflection material. Stable watershed support does not certify a colored bead.',
'Q09-weak':'PRESERVED FAILURE: a tiny 90-pixel red interpretation on a dark-bead reflection survives. Upstream cue/color identity is not repaired by better basin merging.'}

def img(name,alt):return f'<a href="{name}.png"><img loading="lazy" src="{name}.png" alt="{escape(alt)}"></a>'
def table(o):
    s='<table><tr><th>Method</th><th>Pixels</th><th>Minimum perturbation IoU</th><th>Domain IoU</th><th>Seam conflicts</th><th>Near / crossing</th></tr>'
    for m,r in o['variants'].items():
        e=o['evidence']['candidates'][m];s+=f'<tr><td>{m}</td><td>{r["metrics"]["area"]}</td><td>{e["stability"]["minimum_iou"]:.3f}</td><td>{e["stability"]["domain_minimum_iou"]:.3f}</td><td>{e["coherent_seam_conflicts"]}</td><td>{r["centerline"]["near"]} / {r["centerline"]["crosses"]}</td></tr>'
    s+='</table><p>R287: '+escape(o['r287_selector']['decision'])+'. R288: '+escape(o['selector']['status'])+' '+escape(','.join(o['selector']['selection']['alternatives']))+'.</p><p>'+escape(o['selector']['selection']['reasons'][0])+'</p>'
    for m,reasons in o['selector']['selection']['candidate_objections'].items():
        if reasons:s+='<p>'+m+': '+escape('; '.join(reasons))+'.</p>'
    return s

def main():
    dev=read(OUT/'development.json.gz')['cases'];conf=read(OUT/'confirmation.json.gz')['cases'];allobs={o['id']:o for q in dev+conf for o in q['observations']};extra=read(OUT/'additional-review-manifest.json');manifest=read(OUT/'development-review-manifest.json')+read(OUT/'confirmation-review-manifest.json')+extra
    html=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R288 — understand J/M and repair dark-interface merging</title><style>body{font:17px/1.5 system-ui,sans-serif;max-width:1350px;margin:auto;padding:24px;background:#f5f4ef;color:#242424}section{background:white;padding:20px;margin:20px 0;border:1px solid #ddd;border-radius:8px}img{width:100%;height:auto}table{display:block;overflow:auto;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:7px;border-bottom:1px solid #ddd}details{margin:15px 0}summary{cursor:pointer;font-weight:600}a{color:#064e84}.failure{border-left:5px solid #ad4134}h1,h2{line-height:1.2}</style><h1>R288 — understand J and M, then improve their measurements</h1><p><strong>W’s dark-interface repair is promising; ownership and the selector remain incomplete.</strong> Original M merges a dark interface when it has only two pixel pairs. Requiring positive evidence to merge preserves broader red material and separates new yellow neighbors. N11’s upper extension and Q14’s undersized-J fallback remain unresolved.</p><p>Start with the <a href="../../J_AND_M_EXPLAINED.md">standalone J/M explanation</a> (completed before segmentation changes), <a href="../../R288_DIAGNOSIS.md">causal diagnosis</a>, <a href="../../R288_REPORT.md">full report</a>, <a href="../../R288_REPRODUCE.md">reproduction</a>, or <a href="../../r288/results/evaluation.json">numerical evidence</a>.</p><p>J green · M cyan · W magenta · E gold · H blue. White + is a photographic centroid, not a physical bead center. “New interior W” may reproduce nominal M pixels through a more stable construction. All results remain unrated; no production inventory is changed.</p>''']
    order=['N07','N11','N06','P2','P5','C05','Q06','Q01-merge','Q14','Q01-weak','Q09-weak']+[q['name'] for q in conf if q['name'] not in ('Q06','Q14')]
    shown={'N07','N11','N06','P2','P5','Q06','Q01-merge','Q14','Q01-weak'}
    for name in order:
        item=next(r for r in manifest if r['name']==name);o=allobs[item['id']];cls=' class="failure"' if name in ('N11','Q14','Q01-weak','Q09-weak') else '';html.append(f'<section id="{name}"{cls}><h2>{name}</h2><p>{CAPTIONS[name]}</p>')
        if name in shown:html.append(img(name+'-choice',name+' original J M W comparison'))
        html.append('<details><summary>Exact supports, all methods, intensity profiles and decision evidence</summary>'+img(name+'-evidence',name+' complete photographic evidence')+table(o)+f'<p><a href="{name}-native.png">Exact native 97-pixel crop</a></p>')
        if (REVIEW/(name+'-diagnosis.png')).exists():html.append(img(name+'-diagnosis',name+' original M interface cause'))
        if (REVIEW/(name+'-group.png')).exists():html.append(img(name+'-group',name+' nearby observations')+img(name+'-atlas',name+' every cue including failures')+f'<p><a href="{name}-group-native.png">Exact native 145-pixel neighborhood</a></p>')
        html.append('</details></section>')
    ev=read(OUT/'evaluation.json')['confirmation'];html.append('<section id="comparison"><h2>Frozen confirmation and coverage</h2><p>Fifteen new regions, 69 cues, no confirmation retuning. Decisions: 18 new constructions, 39 M, 3 both, 2 J, 7 abstentions. Weak cues can still receive poor preferences; these are not certified detections.</p><table><tr><th>Evidence</th><th>J</th><th>M</th><th>W</th><th>R287</th><th>R288</th></tr>')
    for k,label in [('nonempty','Retained observations'),('near_robust','Support-near'),('crossing_robust','Measured crossings'),('overlap_pairs','Overlap pairs'),('flanking_pairs','Opposite-side pairs')]:html.append('<tr><th>'+label+'</th>'+''.join('<td>'+str(ev['coverage'][m]['total'][k])+'</td>' for m in ('J','M','W','R287','selector'))+'</tr>')
    html.append('</table><p>Raw methods include defective proposals; selectors exclude abstentions. W’s instability flags fall from M’s 20 to 6. Native near coverage stays 45; crossing count falls 26→24 at corrected merger regions. No new distinct bead or complete centerline recovery is certified.</p></section>')
    html.append('<section id="mechanisms"><h2>Preserved failure and correction</h2><p>First W split shallow shading and a narrow bright connection because lateral paths were dark. Final W requires a dark central route too. This correction preceded confirmation. E still inherits correlated M instability; H’s local-color model can reject the entire red feature.</p>'+img('mechanisms','Preserved initial W false split and revised controls')+'<p>Black R2/R1/R4 measurements remain unchanged and reflection-only, with unknown physical ownership.</p></section><section id="stop"><h2>Recommendation and stop</h2><p>Review W’s affirmative-merge repair as the strongest component. Do not adopt E, H or the five-way selector as a production default. N11 extension ownership and Q14 adequacy remain unresolved. The next bounded proposal is independent adequacy and cue-quality evidence with the seam repair held fixed, only after user assessment. No R289, global physical fit or pattern search has begun.</p></section></html>')
    (REVIEW/'index.html').write_text('\n'.join(html))
if __name__=='__main__':main()
