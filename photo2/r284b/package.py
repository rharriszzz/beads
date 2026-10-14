"""Small review entry page with explicit human photographic assessments.

Captions are evaluation-only. Neither this module nor its text enters inference.
"""
import html
from photo2.r282.common import read
from .run import OUT
from .review import REVIEW,LABELS
CAPTIONS={
 'two-sided':'T removes the two lower-left tails while retaining all three reviewed observations. I/J remove the yellow tail but truncate the red interior. E/W/L preserve or enlarge unwanted material. The red remains crossing; both yellows remain near.',
 'duplicate':'R1 and R4 preserve the elongated upper reflection at essentially the same location. R2 measures a smaller bright core; R3 contracts too far. The lower feature is retained as a secondary reflection with unresolved physical ownership. See the red neighbor and secondary detail below.',
 'abstention':'J follows the lower intensity profile and removes the left branch most convincingly here. I stops at its 18px search radius. E is still clipped; W branches into the neighbor; L retains a notch. J is a domain ablation, not a new independent algorithm, and fails elsewhere.',
 'auto-red':'T keeps a substantial red interior with a small centroid shift. I/J cut a crescent around the highlight despite stronger boundary gradients; that is truncation, not improved ownership. E/W/L expand the lower rim.',
 'auto-yellow':'T remains compact. E/W visibly extend into the adjacent yellow bead. I/J remain confined in this example; L adds a small upper protrusion. A large connected region is not evidence of a single bead.',
 'auto-black':'The strong reflection is much smaller than its historical dark collar. R1/R4 follow the bright footprint; R2 contracts further. A small centroid shift does not imply recovery of the physical bead center.',
 'auto-opposite':'Opposite-side colored observations remain eligible under T. E/W/L enlarge interfaces and conflicts. I/J shrink red interiors toward highlights. R1/R4 measure black reflections separately; whole black-body crossing remains unknown.',
 'auto-three':'The selected two yellow observations and black reflection remain separate under T plus R1/R4. The full cue overview also exposes inherited paper-facing and wrong-material proposals; none are promoted. A black candidate elsewhere in this crop has an ineligible peak and remains unresolved.',
 'auto-weak':'Critical failure: R1 merges the weak feature with a brighter neighboring highlight (5.43px shift); R3 inherits it. R4 separates the intensity basins (22px, 2.53px shift); R2 retains a 25px core. R4 may clip at its basin boundary. Physical ownership is unresolved.',
 'auto-same-color':'Selection intentionally preserves an imperfect same-color cue pair. The first red support stays compact under T. The second cue lies near a reflection/material interface: I/J wander across neighboring material; J exceeds the 870px ceiling. Its color/ownership is not established.'}
METHOD_TEXT={
'A':'Historical compact support; tails, collars and inherited ownership errors remain.',
'T':'Native thickness opening; subset of A, no restored rim. Can remove valid narrow material.',
'E':'Connected brightness-barrier flood; can bypass a valley and leak through another route.',
'W':'Competing intensity basins; marker multiplicity flags possible false partitions, not bead counts.',
'L':'Gradient level set with curvature smoothing; may expand, notch or stop at material bounds.',
'I':'Local isophote, 18px domain; can isolate yellow interiors but truncate red shading.',
'J':'Same isophote, 24px domain ablation; tests clipping, increases leakage risk.',
'R283':'Historical comparison only; its dark collar is not a reflection measurement.',
'R1':'Smoothed-field isophote plus separate native threshold support; may join weak/strong highlights.',
'R2':'Adaptive local intensity threshold; smaller core, occasional loss or neighbor substitution.',
'R3':'Gradient snake; contraction and instability remain; rejected moves fall back to the isophote.',
'R4':'Competing-highlight isophote; preserves separate features, with possible basin clipping.'}

def metric_table(rows):
    s='<table><tr><th>Feature / method</th><th>Area</th><th>Removed / added</th><th>Centroid shift</th><th>Evidence / limitation</th></tr>'
    for r in rows:
        shift='empty' if r['centroid_shift'] is None else f"{r['centroid_shift']:.2f}px"
        s+=f'<tr><td>{html.escape(r["feature"])} / {r["method"]}</td><td>{r["area"]}</td><td>{r["removed"]} / {r["added"]}</td><td>{shift}</td><td>{METHOD_TEXT[r["method"]]}</td></tr>'
    return s+'</table>'

def main():
    cases=read(OUT/'cases.json');focus=read(OUT/'focus-metrics.json');validation=read(OUT/'validation.json')
    s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R284B — photographic measurements</title><style>body{font:17px system-ui;margin:24px;max-width:1700px;background:#17191c;color:#eee}a{color:#83caff}img{max-width:100%;height:auto}img.native{width:128px;height:128px;image-rendering:pixelated}section{border-top:1px solid #555;margin-top:32px}summary{cursor:pointer;padding:12px}table{border-collapse:collapse;font-size:14px}td,th{border:1px solid #666;padding:7px}details{overflow:auto}p{max-width:1100px}.callout{background:#293239;padding:15px}</style><h1>R284B — photographic interiors and specular reflections</h1><p class="callout">For review: prefer T for the two colored tails. Compare R1 with R4 for reflection measurements: R4 repairs a weak/strong highlight merger that R1 misses. J improves the wandering yellow example but fails as a universal colored rule. No method has been adopted.</p><p><a href="../../R284B_REPORT.md">Full scientific report</a> · <a href="../../R284B_SPECIFICATION.md">Complete requirements</a> · <a href="../../R284B_ALGORITHM_EXPLANATION.md">Existing algorithm explained</a> · <a href="../../r284b/results/validation.json">Numerical validation</a></p><p>White + = native support centroid; orange × = initial photographic cue; green dot = measured intensity peak; dashed blue = image-derived centerline. Filled cells are exact native support; cyan curves are native boundaries for colored material and separate subpixel contours for R1–R4. Black-body centers and crossing remain unknown. Click panels for full resolution.</p><p>249 fixed image-only cues in ten crops, including unresolved and incorrect proposals. These are not 249 verified beads. Importance is high; reliability is unrated. Counts and boundary gradients do not certify ownership.</p>'''
    for i,c in enumerate(cases):
        n=c['name'];s+=f'<section id="{n}"><h2>{n}</h2><p>{CAPTIONS[n]}</p><p>{html.escape(c["selection_rule"])}</p><img class="native" alt="Unmodified native crop" src="{n}-native.png">'
        if i<3:
            s+=f'<a class="principal" href="{n}-focus.png"><img alt="{n} method comparison" src="{n}-focus.png"></a><details><summary>Exact principal metrics and method captions</summary>'+metric_table(focus[n])+'</details>'
        for a in validation['anchors']:
            if a['case']==n:
                s+=f'<details><summary>Selected anchor: {a["source_id"]} — native support, contours and brightness profiles</summary><p>Matched image cue distance {a["seed_distance"]:.2f}px; this is not a physical correspondence.</p><a href="{a["figure"]}"><img alt="Automatic anchor comparison" src="{a["figure"]}"></a>'+metric_table(a['metrics'])+'</details>'
        if n=='duplicate':
            s+='<details><summary>Lower secondary reflection and red neighbor</summary><p>Secondary status is user review evidence. Same-bead ownership is not established and the observation is never deleted.</p><img src="secondary-focus.png" alt="Secondary reflection">'+metric_table(focus['secondary'])+'<img src="red-neighbor-focus.png" alt="Red neighbor">'+metric_table(focus['red-neighbor'])+'</details>'
        s+=f'<details><summary>All cues in this crop, including unresolved and failed proposals</summary><a href="{n}-overview.png"><img alt="All cue comparison" src="{n}-overview.png"></a><p>Oversized and conflicting masks are diagnostics, not accepted measurements. Empty outputs are retained in the data.</p></details><p><a href="../../r284b/results/{n}.json.gz">Exact native runs, intensity arrays, contours, provenance and pair diagnostics</a></p></section>'
    s+='<p>Stopped for method selection. Proposed next step after review: test the chosen colored-tail and reflection rules with explicit clipping, merge and ownership abstention gates; preserve all independent observations.</p></html>'
    (REVIEW/'index.html').write_text(s)
    from photo2.r282.common import save
    save(OUT/'visual-assessment.json',dict(case_captions=CAPTIONS,method_captions=METHOD_TEXT,role='Human visual evaluation only; never algorithm input. Real leakage counts and precision remain uncalibrated.'))

if __name__=='__main__':main()
