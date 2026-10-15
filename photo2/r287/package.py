"""Compact photographic review with complete expandable evidence and failures."""
from html import escape
from .common import *
CAPTIONS={
'P5':'User: J and B good, S bad. M equals B nominally here. Prefer J because M merges under small smoothing/background/seed changes; the nominal M boundary is not declared wrong.',
'P2':'User: J too small, S good, B equally good. Prefer M: all 295 added pigment pixels follow continuous diffuse routes. M/B reproduce S; this is not a B improvement over S.',
'C05':'User: S/M/B acceptable but imperfect, others very bad. Prefer M for 279 supported diffuse pixels; remaining boundary/ownership uncertainty is retained.',
'C02-edge':'User: all bad, peripheral edge, no substantial further effort. The reviewed weak-edge cue abstains due seam, area, domain and instability evidence. No tuning to rescue it.',
'C02':'Other anchor/context in the C02 crop: selector prefers M. This does not satisfy the user’s broad negative assessment of the edge example. Retained as a limitation, not a success.',
'P1':'Both remain supported. The user’s earlier J preference remains review evidence; this does not force a larger mask.',
'P3':'Prefer M because J changes greatly with background perturbation. The user previously preferred nominal J: stability does not settle every boundary preference.',
'C04':'Anchor both; the unresolved fresh 885px merger abstains in the atlas. Nearby dark/tinted cues remain uncertain. No new bead is certified.',
'C07':'Anchor prefers M, but nearby cue overlap and differing selected supports remain. Do not count every cue as a distinct bead.',
'N01':'Prefer M: photographed diffuse red extends well beyond J’s highlight core, without a detected seam conflict. New independent example.',
'N02':'Both: two plausible interior extents survive checks; neither is a physical silhouette.',
'N03':'Prefer M: broader diffuse red survives the direct route and stability tests.',
'N04':'Prefer M for a yellow bead: continuous pigment supports the extra material. The rule is not color-only.',
'N05':'Prefer M: J keeps a small bright patch; M better represents diffuse red. Physical identity remains unverified.',
'N06':'Prefer J: M visibly joins two yellows, with multi-path seam and instability evidence. The atlas also exposes a doubtful 52px red preference on a tinted dark-bead highlight.',
'N07':'FAILURE: prefer J merely because M is unstable. Nominal M retains 227 supported diffuse pixels that J omits. The selected J is still visibly too small; no retuning after confirmation.',
'N08':'Prefer J avoids M’s two-yellow merger, but the selected J excludes substantial visible material. Avoiding a merger alone does not prove an adequate interior.',
'N09':'Prefer M: clear diffuse red beyond J’s small peak core. This supports the continuity idea beyond P2.',
'N10':'Prefer M even though it is smaller: J reaches a lower neighboring region and is domain-sensitive. This is not area maximization.',
'N11':'FAILURE: M has a questionable extension and is unstable; automatic fallback chooses a very small J core despite 525 supported added pigment pixels. Preserve uncertainty instead of declaring success.',
'N12':'Both is questionable: M retains a lower appendage that may belong elsewhere. No detected seam plus moderate IoU does not establish equal quality.',
'N13':'Prefer J avoids an obvious red-neighbor merger in M. J still looks substantially truncated; this is a conservative measurement, not demonstrated full recovery.',
'N14':'Prefer M for continuous diffuse yellow material. The larger support needs photographic review, not approval from area alone.',
'N15':'Prefer M: broader diffuse red stays separate in this anchor. A nearby high-source cue still abstains.',
'N16':'Both: J and M give plausible nested yellow interiors. Both are retained independently, never unioned.'}

def image(name,alt):return f'<a href="{name}.png"><img loading="lazy" src="{name}.png" alt="{escape(alt)}"></a>'
def table(o):
    e=o['evidence'];s='<table><tr><th>Candidate</th><th>Pixels</th><th>Min perturbation IoU</th><th>Domain IoU</th><th>Seam conflicts</th><th>Near / crossing</th></tr>'
    for m in ('J','M','B'):
        c=e['candidates'][m];r=o['variants'][m];s+=f'<tr><td>{m}</td><td>{c["area"]}</td><td>{c["stability"]["minimum_iou"]:.3f}</td><td>{c["stability"]["domain_minimum_iou"]:.3f}</td><td>{c["coherent_seam_conflicts"]}</td><td>{r["centerline"]["near"]} / {r["centerline"]["crosses"]}</td></tr>'
    s+='</table><p>'+escape(o['selector']['selection']['reasons'][0])+'</p>'
    for m,why in o['selector']['selection']['candidate_objections'].items():
        if why:s+='<p>'+m+': '+escape('; '.join(why))+'.</p>'
    return s

def main():
    dev=read(OUT/'development.json.gz')['cases'];conf=read(OUT/'confirmation.json.gz')['cases'];obs={o['id']:o for q in dev+conf for o in q['observations']};man=read(OUT/'development-review-manifest.json');ev=read(OUT/'evaluation.json');html=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R287 photographic J/M selection</title><style>body{font:17px/1.5 system-ui,sans-serif;max-width:1350px;margin:auto;padding:24px;background:#f6f5f1;color:#242424}section{background:white;padding:20px;margin:20px 0;border:1px solid #ddd;border-radius:8px}img{width:100%;height:auto}table{display:block;overflow:auto;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:7px;border-bottom:1px solid #ddd}details{margin:15px 0}summary{cursor:pointer;font-weight:600}a{color:#064e84}.failure{border-left:5px solid #ad4134}h1,h2{line-height:1.2}</style><h1>R287 — choosing J or M from photographic evidence</h1><p><strong>The evidence helps, but this selector should not be adopted unchanged.</strong> Direct diffuse-material routes improve several J/M choices. Multi-path seams expose M mergers. However, an unstable M does not make an undersized J adequate: N07/N11 show this failure on independent central photographs.</p><p>J green, M cyan, B orange. White + is a photographic centroid. Both keeps two alternatives; abstain keeps the observation unresolved. No physical identities, color-only rule, hybrid union or production adoption.</p><p><a href="../../R287_REPORT.md">Full report</a> · <a href="../../R287_SPECIFICATION.md">Requirements</a> · <a href="../../R287_REPRODUCE.md">Reproduction</a> · <a href="../../r287/results/evaluation.json">All numerical evidence</a></p>''']
    for name in ('P2','P5','C05','C02-edge','P1','P3','C04','C07','C02'):
        q=next(q for q in man if q['name']==name);o=obs[q['id']];html.append(f'<section id="{name}"><h2>{name} — reviewed development</h2><p>{CAPTIONS[name]}</p>')
        if name in ('P2','P5','C05','C02-edge'):html.append(image(name+'-choice',name+' raw J M selector'))
        html.append('<details><summary>Native evidence, alternatives, profiles and decision reasons</summary>'+image(name+'-evidence',name+' native evidence')+table(o)+f'<a href="{name}-native.png">Exact native97 crop</a>')
        if (REVIEW/(name+'-stability.png')).exists():html.append(image(name+'-stability',name+' perturbation failure'))
        if (REVIEW/(name+'-group.png')).exists():html.append(image(name+'-group',name+' all nearby observations')+image(name+'-atlas',name+' every cue')+f'<a href="{name}-group-native.png">Exact native145 context</a>')
        if name in ('P2','P5'):html.append(f'<p><a href="../r286/{name}-all.png">Unchanged original J/S/M/B comparison from R286</a></p>')
        html.append('</details></section>')
    html.append('<section id="confirmation"><h2>Frozen independent confirmation</h2><p>Sixteen new regions, 63 cues: 29 prefer M, 18 prefer J, 6 both, 10 abstain. Anchors: 8 M, 5 J, 3 both. All rules and parameters frozen before these outputs; no confirmation retuning. Dark-seam and material counts are evidence proxies, not real precision.</p><table><tr><th>Coverage</th><th>Always J</th><th>Always M</th><th>B</th><th>Selector</th></tr>')
    for k,label in [('nonempty','Retained observations'),('near_robust','Support-near'),('crossing_robust','Measured crossing'),('near_overlap_groups','Near overlap groups'),('near_duplicate_pairs','Near-duplicate pairs'),('flanking_pairs','Opposite-side pairs')]:html.append('<tr><th>'+label+'</th>'+''.join('<td>'+str(ev['confirmation_coverage'][m][k])+'</td>' for m in ('J','M','B','selector'))+'</tr>')
    html.append('</table><p>Always-method counts include flagged proposals. Selector coverage excludes abstentions and requires all alternatives to agree for robust geometry. No new distinct bead is certified. Coverage falls despite fewer merger warnings.</p></section>')
    for case in conf:
        name=case['name'];o=min(case['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-case['seed']));cls=' class="failure"' if name in ('N07','N11','N12') else '';html.append(f'<section id="{name}"{cls}><h2>{name} — {o["color"]}, {case["stratum"]}</h2><p>{CAPTIONS[name]}</p>')
        if name in ('N01','N06','N07','N10','N11','N12'):html.append(image(name+'-choice',name+' independent review'))
        html.append('<details><summary>Original pixels, full evidence and all neighboring cues</summary>'+image(name+'-evidence',name+' full evidence')+table(o)+image(name+'-group',name+' neighborhood coverage')+image(name+'-atlas',name+' all cue results')+f'<a href="{name}-native.png">Exact native97 crop</a> · <a href="{name}-group-native.png">Exact native145 context</a>')
        if (REVIEW/(name+'-stability.png')).exists():html.append(image(name+'-stability',name+' stability counterexample'))
        html.append('</details></section>')
    html.append('<section id="mechanisms"><h2>Why brightness ratio alone failed</h2><p>The preserved first policy abstained on P2 because diffuse red was darker than its highlight. The revised direct-route test allows decreasing brightness while rejecting a valley followed by a renewed bright surface. Identical seam/internal-texture pixels remain physically ambiguous. Narrow bright material is not removed merely for width.</p>'+image('mechanisms','Controlled route mechanisms')+'<p>Black remains unchanged R2 reflection-only measurement, with R1/R4 alternatives and unknown physical ownership. No dark-body inference or new reflection tuning.</p></section><section id="stop"><h2>Recommendation and stop</h2><p>Keep the direct diffuse-continuation and multi-path seam diagnostics for further review. Do not adopt the frozen selector unchanged: “M unstable” is not proof that “J adequate.” No hybrid was justified. Await user assessment before another bounded experiment or adoption; no R288, global physical fitting or pattern search has begun.</p></section></html>')
    (REVIEW/'index.html').write_text('\n'.join(html))
if __name__=='__main__':main()
