"""Curated comparison and captions; evaluation-only judgments never enter detector."""
import html
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from photo2.r282.common import ROOT,read,save,photo,pixels
from photo2.r284.assess import TARGETS
from .select import OUT
from .review import REVIEW,plt,COLORS
from .run import local_mask
from .assess import PERIPHERAL
CAPTIONS={
'e01':'Lower yellow: J removes the lower-left lobe. D crosses the dark saddle into the adjacent yellow. S separates those regions while preserving more diffuse material; no thickness pruning. The remaining rim is a photographic proposal, not a full body.',
'e02':'Left red crossing the centerline: J keeps only 200px around the highlight. S restores the diffuse red to 495px and retains measured crossing. Its lower edge follows darker red material; exact physical extent remains unknown.',
'e03':'Right yellow: J is already plausible. S adds a darker photographic rim with little centroid movement; extra area alone is not improvement. All three two-sided observations remain separately represented.',
'e04':'User-approved yellow brightness-profile case: J remains the reference. S gives a similar intensity-shaped region with a modest additional rim. D joins the neighboring yellow; G truncates to the bright center.',
'e05':'Strong red truncation flag: J loses diffuse material beyond a bright peak. S restores much of it and rejects A’s leftward neighboring lobe. S also retains a narrow dark lower extension; this is unresolved stopping evidence, not a reason to impose thickness pruning.',
'e06':'Peripheral shadow/background cue. A already measures questionable material; J’s large displacement is not established red-bead regression. Retained for audit, deprioritized under the user’s edge/shadow instruction.',
'e07':'Visible yellow pair at necklace edge: J crosses the dark connection and includes part of the upper bead. S separates the upper contribution while retaining the lower photographic interior. Edge location alone does not invalidate this clear seam example.',
'e08':'The overlap flag is not automatically leakage: A extends toward a lower neighbor, while J better isolates the upper yellow. S expands its diffuse interior; old-mask agreement is not ground truth.',
'e09':'Peripheral shadowed-paper cue misclassified as red. Large connected regions are a material/eligibility failure in both old and new methods. Do not optimize the clear-bead rule to rescue this excluded area.',
'e10':'Peripheral edge/shadow case; oversized red proposals follow poorly supported dark material. All numerical failures are retained, but this is not a central J regression.',
'e11':'Peripheral shadow cue with artificial J radius contact. D/S demonstrate that enlarging the window alone does not establish ownership. Domain sensitivity is a warning, not a bead boundary.',
'e12':'Lost-bright-material ranking selected a misleading old mask: A includes neighboring yellow. J removes much of that contribution. S adds diffuse material to the lower target. A’s lost pixels are not all legitimate target material.',
'e13':'Wrong-material/black-reflection interface cue. Large centroid disagreement does not mean the physical bead center moved. Peripheral uncertain observation, not a clear red truncation.',
'e14':'Edge/material-interface cue with unreliable old ownership. Both centroid and color assignment are doubtful; retain unresolved, deprioritize this example.',
'e15':'J improvement candidate: adds photographed yellow material with a small shift. S adds a dimmer rim. Prefer the brightness evidence over compactness; added area is not automatically better.',
'e16':'J recovers lower yellow material omitted by A’s clipped support. S extends farther into the dimmer rim; D connects another yellow. No physical identity or silhouette is certified.',
'v01':'Unseen clear red: S restores diffuse interior lost by J, with a small shift from A. D crosses to the adjacent red; G concentrates on the highlight.',
'v02':'Unseen clear red: S restores area lost by J, but pigment/neutral-highlight eligibility produces a left notch and small projections. This is a remaining material-gate defect, not corrected by smoothing the drawing.',
'v03':'Unseen clear yellow: J is plausible; S adds diffuse rim while stopping before the lower neighbor. D joins the two.',
'v04':'Important clear-material failure: S merges several yellow neighbors, exceeds870px and changes with domain size. J isolates the target better. This failure is NOT covered by the edge/shadow exception.',
'v05':'Unresolved red confirmation: S separates a red neighbor but follows a yellow rim and black reflection at its margins. J is more confined. Material ownership remains inadequate; preserve failure.',
'v06':'Unresolved yellow: S still includes the lateral same-color feature, while separating the lower one. J is more confined. A stable domain alone does not establish correct ownership.',
'v07':'Fresh image-only red cue: S expands real red but retains a dark lower tendril. J is the more conservative interior. New cue does not establish a newly discovered physical bead.',
'v08':'Fresh yellow cue: J includes a lower-neighbor contribution; S separates it and retains the broad target. G almost vanishes. Candidate supports cross the image centerline, but completeness is unproven.',
'red-neighbor':'Red neighboring comparison to the reviewed upper black reflection. Colored supports remain separate from reflection measurements; no physical ownership is inferred from proximity.'}

def compact(o,name,native):
    x,y=o['origin'];im=native[y:y+97,x:x+97];Image.fromarray(im).save(REVIEW/(name+'-native97.png'));origin=np.array([x,y]);lum=np.array(o['native_Y']);fig,axs=plt.subplots(1,4,figsize=(12,3.5))
    for ax in axs:ax.imshow(im,interpolation='nearest');ax.set_xlim(12,84);ax.set_ylim(84,12);ax.set_xticks([]);ax.set_yticks([])
    axs[0].set_title('Unmodified photo enlarged')
    for ax,m in zip(axs[1:3],('J','S')):
        r=o['variants'][m];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
        if len(c):ax.plot(c[:,0],c[:,1],lw=1,color=COLORS[m])
        if r['measured_photo_location']:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white')
        ax.set_title(m+f": {r['metrics']['area']} native pixels")
    j=local_mask(o['variants']['J']['measured_support'],origin,(97,97));s=local_mask(o['variants']['S']['measured_support'],origin,(97,97))
    rgba=np.zeros((97,97,4));rgba[j&~s]=[1,0,0,.65];rgba[s&~j]=[0,1,0,.65];axs[3].imshow(rgba,interpolation='nearest');axs[3].set_title('S vs J: lost red / gained green')
    fig.suptitle(name+' / '+o['color']+' — photographic centroids, not physical centers');fig.tight_layout();fig.savefig(REVIEW/(name+'-choice.png'),dpi=135);plt.close(fig)
    edges=o['variants']['S']['method_evidence'].get('saddles',[])
    if edges:
        edges=sorted(edges,key=lambda e:(not e['separate_after_merging'],min(np.linalg.norm(np.array(p)-[48,48]) for p in e['peaks'])))
        e=edges[0];a,b=np.array(e['peaks']);route=np.linspace(a,b,max(2,int(np.linalg.norm(b-a)*4)));values=ndi.map_coordinates(lum,route[:,::-1].T,order=1)
        fig,axs=plt.subplots(1,2,figsize=(9,3.5));axs[0].imshow(im,interpolation='nearest');axs[0].plot(route[:,0],route[:,1],color='lime');axs[0].set_title('Photographic sampling route');axs[1].plot(np.linspace(0,np.linalg.norm(b-a),len(values)),values,label='Native Y, interpolated route');axs[1].axhline(e['saddle_Y'],label='Highest basin connection',color='orange');axs[1].axhline(.65*min(e['diffuse_references']),ls='--',label='Contextual separation limit',color='red');axs[1].set_xlabel('Native pixel distance');axs[1].legend(fontsize=7);axs[1].set_title(f"saddle/reference={e['saddle_ratio']:.2f}; separated={e['separate_after_merging']}");fig.tight_layout();fig.savefig(REVIEW/(name+'-saddle.png'),dpi=125);plt.close(fig)

def image_link(name):return f'<a href="{name}"><img loading="lazy" src="{name}"></a>'
def table(o):
    rows=[]
    for m,r in o['variants'].items():
        v=r['metrics'];cl=r['centerline'];info=r['method_evidence'];rows.append(f"<tr><td>{m}</td><td>{v['area']}</td><td>−{v['removed']} / +{v['added']}</td><td>{v['centroid_shift'] or 0:.2f}</td><td>{v['boundary_gradient'] or 0:.4f}</td><td>{cl['side']}; near={cl['near']}</td><td>{info.get('domain_iou','old fixed domain')}</td></tr>")
    return '<div class="scroll"><table><tr><th>Method</th><th>Area px</th><th>Change vs A</th><th>Centroid shift px</th><th>Boundary gradient</th><th>Support / line</th><th>32/48 IoU</th></tr>'+''.join(rows)+'</table></div>'

def main():
    native,_,_=photo();dev=read(OUT/'development.json.gz')['observations'];obs={o['id']:o for o in dev};selection=read(OUT/'selection.json');confirm=read(OUT/'confirmation.json.gz')['observations'];entries=[(q['example'],obs[q['observation_id']],q['selection_reason']) for q in selection['development']]+[(f'v{i+1:02}',o,'Frozen SHA256 photograph-only confirmation; >180px from development crops.') for i,o in enumerate(confirm)]
    xy=TARGETS['duplicate'][2][1];red=min([o for o in dev if o['color']=='red'],key=lambda o:np.linalg.norm(np.array(o['seed'])-xy));entries.append(('red-neighbor',red,'User-reviewed neighboring comparison; evaluation only.'))
    sections={};manifest=[]
    for name,o,reason in entries:
        compact(o,name,native);caption=CAPTIONS[name];manifest.append(dict(name=name,id=o['id'],caption=caption,selection_reason=reason,peripheral=name in PERIPHERAL))
        body=f'<section id="{name}"><h2>{name} — {o["color"]}</h2><p>{html.escape(caption)}</p>'+image_link(name+'-choice.png')+f'<details><summary>Native pixels, original A, all alternatives, exact supports and profiles</summary><p>{html.escape(reason)}</p><img class="native" src="{name}-native97.png">'
        if (REVIEW/(name+'-methods.png')).exists():body+=image_link(name+'-methods.png')+image_link(name+'-profiles.png')
        if (REVIEW/(name+'-saddle.png')).exists():body+=image_link(name+'-saddle.png')
        body+=table(o)+'</details></section>';sections[name]=body
    black=read(OUT/'reflections.json.gz');save(OUT/'review-manifest.json',manifest)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R285 — J and brightness-driven boundaries</title><style>body{font:17px system-ui;background:#181b20;color:#eee;margin:24px;max-width:1600px}a{color:#86caff}img{max-width:100%;height:auto}img.native{width:97px;image-rendering:pixelated}section{border-top:1px solid #667;margin:28px 0}summary{cursor:pointer;padding:12px}table{border-collapse:collapse;font-size:14px}td,th{border:1px solid #667;padding:7px}.scroll{overflow-x:auto}</style><h1>R285: brightness governs photographic support</h1><p>J remains the primary candidate. S adds diffuse-intensity measurement and dark-saddle separation. Review the gains and the clear-material failure before choosing. No production inventory changed.</p><p><a href="../../R285_REPORT.md">Scientific report</a> · <a href="../../R285_SPECIFICATION.md">Requirements</a> · <a href="../../R285_DIAGNOSIS.md">Why dark stopping weakened</a> · <a href="../../r285/README.md">Reproduce</a> · <a href="../../r285/results/diagnostics.json.gz">Full measurements</a></p><p>Start with e01–e05, e07 and unseen v04. Cyan/blue S versus green J; white + means measured photographic centroid. Native masks, original A and failed D/G alternatives are expandable. An old mask is not truth. The user permits disregarding edge/shadow areas; those controls are retained separately below.</p>'''
    page+=''.join(sections[n] for n,_,_ in entries if n.startswith('e') and n not in PERIPHERAL)
    page+='<details><summary>Six peripheral edge/shadow/material-interface disagreements — preserved, lower priority</summary>'+''.join(sections[n] for n in sorted(PERIPHERAL))+'</details>'
    page+='<h2>Unseen photographic confirmation — methods frozen before opening</h2>'+''.join(sections[n] for n,_,_ in entries if n.startswith('v'))
    page+='<h2>Black reflections: R2 default candidate, R1/R4 retained</h2><p>All are reflection regions only. Lower secondary remains measured; physical ownership stays unknown. Smoothness alone never sets reliability.</p>'
    for q in black['selected']:page+=f'<section id="{q["name"]}"><h2>{q["name"]}</h2>'+image_link(q['name']+'.png')+'</section>'
    page+=sections['red-neighbor']+'<p><a href="../../r285/results/reflections.json.gz">Native reflection supports, contours and stability</a> · <a href="../../r285/results/synthetic-summary.json">Independent rendered confirmation</a> · <a href="../../r285/results/mechanisms.json">Bright-neck / dark-seam / ambiguous texture controls</a></p><p>Stop for method review. No global Phase2 fitting or Phase3 search.</p></html>'
    (REVIEW/'index.html').write_text(page)
    print('review package',len(entries),'colored comparisons and',len(black['selected']),'reflection panels')
if __name__=='__main__':main()
