"""Original pixels beside measured/predicted overlays and substantial bottom keys."""
import html,textwrap
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from .common import OUT,OLD,ROOT,REVIEW,photo,read,save,pixels

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(size=17):return ImageFont.truetype(FONT,size)
def text(draw,xy,s,width=118,size=17,fill='white'):
    y=xy[1]
    for paragraph in s.split('\n'):
        for line in textwrap.wrap(paragraph,width=width) or ['']:
            draw.text((xy[0],y),line,font=font(size),fill=fill);y+=size+7
    return y

def panel(path,title,images,caption):
    width=1200;pad=16;cell=(width-pad*(len(images)+1))//len(images);height=max(int(im.height*cell/im.width) for _,im in images)
    # Explicit paragraph wrapping determines the footer height, so text cannot clip.
    lines=sum(max(1,len(textwrap.wrap(p,118))) for p in caption.split('\n'))
    out=Image.new('RGB',(width,70+height+32+lines*24+20),(24,29,36));d=ImageDraw.Draw(out)
    text(d,(16,10),title,95,22)
    for j,(label,im) in enumerate(images):
        x=pad+(cell+pad)*j;d.text((x,45),label,font=font(16),fill='white')
        resized=im.resize((cell,int(im.height*cell/im.width)),Image.Resampling.NEAREST);out.paste(resized,(x,70))
    text(d,(16,90+height),caption)
    out.save(path)

def overlay(raw,origin,rows,curve=None,model=None,anchors=None):
    im=raw.copy();d=ImageDraw.Draw(im);origin=np.array(origin);w,h=im.size
    if model is not None:
        boundary=np.zeros(model.shape,bool)
        for delta in ((0,1),(0,-1),(1,0),(-1,0)):boundary|=(model!=np.roll(model,delta,axis=(0,1)))&(model!=-999)
        yy,xx=np.where(boundary)
        for x,y in zip(xx,yy):
            if (x+y)%4<2:d.point((int(x),int(y)),fill='#ff9d32')
    if curve is not None:
        xy=np.asarray(curve)-origin;inside=(xy[:,0]>=0)&(xy[:,0]<w)&(xy[:,1]>=0)&(xy[:,1]<h)
        ids=np.flatnonzero(inside)
        for a,b in zip(ids[:-1],ids[1:]):
            if b-a==1:d.line([tuple(xy[a]),tuple(xy[b])],fill='white',width=1)
    for r in rows:
        p=pixels(r['measured_support'])-origin
        if not len(p):continue
        valid=(p[:,0]>=0)&(p[:,0]<w)&(p[:,1]>=0)&(p[:,1]<h);p=p[valid]
        if not len(p):continue
        mask=np.zeros((h,w),bool);mask[p[:,1],p[:,0]]=True;edge=mask&~ndi.binary_erosion(mask)
        color='#39ff68' if anchors and r['record_id'] in anchors else {'high':'#20ffff','medium':'#ffe875','unresolved':'#fa76ff','rejected':'#999999'}[r['status']]
        yy,xx=np.where(edge)
        for x,y in zip(xx,yy):d.point((int(x),int(y)),fill=color)
        x,y=np.array(r['measured_photo_location'])-origin
        d.line((x-2,y,x+2,y),fill='white');d.line((x,y-2,x,y+2),fill='white')
    return im

KEY='Overlay key: cyan = accepted measured interior edge; magenta = unresolved measured support; yellow = medium; gray = rejected. White crosses mark measured interior centroids, not physical centers. The white curve is the image-derived centerline, not a chain of bead centers. No colored edge is a complete bead silhouette.'
IDS='Record codes such as C-, K-, E5- and R282- are stable photographic proposal IDs. Their numbers refer to original proposal locations, not string indices. Color reliability, photographic ownership and physical identity are separate.'

def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,_,_=photo();im=Image.fromarray(native);p1=read(OUT/'phase1.json.gz');rows=p1['records'];by={r['record_id']:r for r in rows};curve=np.array(read(OLD/'centerline.json')['points']);coverage=read(OUT/'coverage.json');items=[]
    def crop_case(name,title,center,selected,caption,size=128):
        origin=np.rint(np.array(center)-size/2).astype(int);raw=im.crop((*origin,*(origin+size)))
        panel(REVIEW/(name+'.png'),title,[('Original photograph',raw),('Photographic measurements',overlay(raw,origin,selected,curve))],caption+'\n'+KEY+'\n'+IDS)
        raw.save(REVIEW/(name+'-raw.png'));items.append(dict(file=name+'.png',title=title,caption=caption))
    for g in coverage['gaps']:
        nearby=[by[r['id']] for r in g['nearby']];caption=f"R282 sector {g['sector']+1}: old nearest-high centroid distance {g['nearest_high_distance']:.1f} native pixels. "+' '.join(g['explanations'])+' '+g['curve_problem']
        crop_case(f"gap-{g['sector']+1}",f"Former gap picture {g['sector']+1}: proximity is not a missing-bead diagnosis",g['center'],nearby,caption)
    flank=coverage['flanking_pairs'][0];rr=[by[k] for k in flank['ids']]
    crop_case('two-sided','Two separate accepted interiors flank the reference curve',np.mean([r['measured_photo_location'] for r in rr],axis=0),rr,
        'Both observations count once. Neither centroid must lie on the curve, and another bead is not excluded by this pair. IDs: '+', '.join(flank['ids'])+'. Disjoint measured interiors support a two-body interpretation; real physical identities remain unverified.')
    crossing=max([r for r in rows if r['status']=='high' and r['centerline']['crosses']],key=lambda r:r['metrics']['area'])
    crop_case('crossing','A measured interior crosses the centerline',crossing['measured_photo_location'],[crossing],
        crossing['record_id']+': native support occurs on both signed sides and reaches the curve. It is one observation, not a separate bead for every nearby station.')
    pairs=read(OUT/'ownership.json')['pairs'];pp=[p for p in pairs if p['relation']=='shared-dark-envelope-alternative']
    pair=max(pp,key=lambda p:p['broad_dark_envelope_overlap']) if pp else pairs[0];rr=[by[k] for k in pair['ids']]
    crop_case('duplicate','Possible multiple reflections: ownership is unresolved',np.mean([r['measured_photo_location'] for r in rr],axis=0),rr,
        'IDs '+', '.join(pair['ids'])+'. The compact reflections may be separate features of one body, or neighboring bodies. Broader dark regions overlap. The algorithm retains both alternatives and abstains; dark connectivity does not prove a merge.')
    for color in ('yellow','red','black'):
        chosen=max([r for r in rows if r['color']==color and r['status']=='high' and r['centerline']['near']],key=lambda r:r['metrics']['solidity']*min(r['metrics']['area'],400))
        crop_case('good-'+color,'Accepted '+color+' photographic interior',chosen['measured_photo_location'],[chosen],
            chosen['record_id']+'. Attempt C is retained. '+('Black uses a coherent reflection plus measured dark collar, not a complete dark-body outline.' if color=='black' else 'This is a compact measured material region; the physical center and full silhouette remain unknown.')+' High is a descriptive class, not a numerical correctness probability.')
    conflict=max([p for p in pairs if p['relation']=='shared-material-conflict'],key=lambda p:p['shared_pixels']);rr=[by[k] for k in conflict['ids']]
    crop_case('abstention','Shared material: symmetric ownership abstention',np.mean([r['measured_photo_location'] for r in rr],axis=0),rr,
        f"These measurements share {conflict['shared_pixels']} native pixels. Both are questioned; record ordering cannot silently establish an owner. IDs: "+', '.join(conflict['ids'])+'. All original supports remain available.')
    folder=OUT/'local';raw=Image.open(folder/'raw.png').convert('RGB');anchors=read(folder/'anchors.json')['anchors'];held=read(folder/'withheld.json')['records'];ev={r['model']:r for r in read(folder/'evaluation.json')['results']}
    for m in read(folder/'prediction-freeze.json')['models']:
        owner=np.load(folder/(m['id']+'-prediction.npz'))['owner'];r=ev[m['id']]
        caption=f"Hand {m['parameters']['hand']:+}, {m['mode']} fit: {r['compatible']}/{r['withheld_count']} withheld interiors pass the compatibility gate; mean containment {r['mean_withheld_containment']:.3f}. Full anchor fractions: "+', '.join(f'{x:.2f}' for x in r['anchor_full_containment'])+'. '
        caption+='Green = four fitting interiors; cyan = withheld measured interiors; white crosses = measured centroids. Dashed orange = predicted first-hit model edges, NOT measured bead boundaries. All predictions were frozen before evaluation. Local model indices are conditional, not global string identities. Same-color overlap is not proof of identity.'
        pictures=[('Original photograph',raw),('Measured supports + predicted edges',overlay(raw,[0,0],anchors+held,model=owner,anchors={a['record_id'] for a in anchors}))]
        if (folder/(m['id']+'-pov.png')).exists():pictures.append(('POV model; one shared light',Image.open(folder/(m['id']+'-pov.png')).convert('RGB')))
        caption+=' Model render colors are conditional photo samples; gray means unknown. Its material is fixed. Compare packing and shape with the original photo. No model has accepted physical identities.'
        name=m['id']+'.png';panel(REVIEW/name,m['id']+': physical fit and supports withheld from fitting',pictures,caption);items.append(dict(file=name,title=m['id']+' physical comparison',caption=caption))
        ann=overlay(raw,[0,0],anchors+held);d=ImageDraw.Draw(ann)
        for row in anchors+held:
            if row.get('highlight'):
                x,y=row['highlight']['point'];cx,cy=row['measured_photo_location'];d.line((cx,cy,x,y),fill='#ff9d32');d.ellipse((x-2,y-2,x+2,y+2),outline='#ff9d32')
        stats='; '.join(f"{e['id']}: "+(f"{e['angle']:.1f} degrees" if e['usable'] else 'wrong or missing model owner') for e in r['light'])
        caption=f"One distant light is estimated from {m['light']['yellow_count']} usable yellow fitting highlights. At least two are required to constrain cross-bead consistency. Held-out yellow median angular disagreement: {r['yellow_median_angle']}. "+stats+'. '
        caption+='Orange circles mark measured bright/desaturated regions, not physical centers. Short orange segments run from interior centroid to highlight; these are photographic offsets, not recovered light rays. Surface normals and the shared-light test use the frozen annular model. Missing or wrong-owner highlights remain failures. Green/cyan/magenta and white crosses retain the photographic meanings above.'
        name=m['id']+'-light.png';panel(REVIEW/name,m['id']+': reflection evidence and shared-light disagreement',[('Original photograph',raw),('Measured highlight offsets',ann)],caption);items.append(dict(file=name,title=m['id']+' reflection test',caption=caption))
    folder=OUT/'local-confirmation';raw=Image.open(folder/'raw.png').convert('RGB');anchors=read(folder/'anchors.json')['anchors'];held=read(folder/'withheld.json')['records'];ev={r['model']:r for r in read(folder/'evaluation.json')['results']}
    for m in read(folder/'prediction-freeze.json')['models']:
        if m['mode']!='support':continue
        r=ev[m['id']];owner=np.load(folder/(m['id']+'-prediction.npz'))['owner']
        caption=f"Independent second region, chosen automatically at least 250 pixels from the development region. The method was fixed before this fit. Hand {m['parameters']['hand']:+}: {r['compatible']}/4 withheld interiors compatible; mean containment {r['mean_withheld_containment']:.3f}; held-out yellow light error {r['yellow_median_angle']:.1f} degrees. This is weaker than the development region and does not confirm reliable physical correspondence. "
        caption+='Green = fitting measured interiors; cyan = withheld measured interiors; white crosses = measured centroids. Dashed orange = predicted first-hit model boundaries, never photographic measurements. The render uses one shared yellow-trained light and conditional photo-derived colors; gray means unknown. All model identities remain unresolved.'
        name='confirmation-'+m['id']+'.png';panel(REVIEW/name,'Second region: fixed-method local correspondence test',[('Original photograph',raw),('Measurements and predictions',overlay(raw,[0,0],anchors+held,model=owner,anchors={a['record_id'] for a in anchors})),('Conditional POV model',Image.open(folder/(m['id']+'-pov.png')).convert('RGB'))],caption);items.append(dict(file=name,title='Second region '+m['id'],caption=caption))
    # Readable overview of all phases; pattern colors are explicitly conditional.
    info=Image.new('RGB',(1168,400),(24,29,36));d=ImageDraw.Draw(info)
    text(d,(12,12),'Phase 1: 561 high, 30 medium, 484 unresolved, 17 rejected observations. All 1092 retained.\n323 high support-near observations: 169 crossing / 80 negative side / 74 positive side.\nFresh synthetic: 148 distinct pure supports / 151 high; recall 148 / 389. Real accuracy uncalibrated.\nPhase 2: development best 3 / 4 withheld; second-region best 2 / 4. No physical identity accepted.\nPhase 3: conditional exact-divisor alternatives only; at least four full repeats. No pattern accepted.',105,19)
    p3=read(OUT/'integrated/phase3.json')
    caption='Full integrated regression retains all measurements and separates photographic color from conditional model indices. '+ '; '.join(f"{m['id']} leading periods "+','.join(map(str,m['leading_periods'][:3])) for m in p3['models'])+'. Period 1 or other short leaders with unknown slots mean abstention, not a discovered uniform-color pattern. Strict evidence is empty after identity uncertainty is propagated. All phase3 colors remain separate from measured colors. The maker rule excludes periods divisible by 13; total count need not satisfy that rule.'
    panel(REVIEW/'three-phase-status.png','R283 three-phase status',[('Evidence and limitations',info)],caption);items.append(dict(file='three-phase-status.png',title='Three-phase status',caption=caption))
    # Every false support and duplicate on fresh synthetic confirmation is visible.
    bench=read(OUT/'confirmation-results.json')
    for s in bench['scenes']:
        failures=[h for h in s['after']['hits'] if not h['correct_support']]
        if not failures:continue
        f=OUT/'confirmation'/f"scene-{s['scene']:02}";raw=Image.open(f/'photo.png').convert('RGB');rr=[r for r in read(f/'inference.json.gz')['after'] if r['record_id'] in {h['id'] for h in failures}]
        caption='This is a labeled SYNTHETIC control, not the real photograph. The detector did not receive the identity raster. These high-class supports fail the >=95% single-body purity criterion: '+', '.join(f"{h['id']} purity {h['purity']:.3f}" for h in failures)+'. The failures prevent a perfect-precision claim. Cyan edges and white centroids are measured from rendered appearance; known identities are used only afterward for evaluation.'
        name=f"synthetic-failure-{s['scene']:02}.png";panel(REVIEW/name,'Fresh held-out synthetic failure retained',[('Synthetic appearance input',raw),('Incorrect high-class support',overlay(raw,[0,0],rr))],caption);items.append(dict(file=name,title='Fresh synthetic failure '+str(s['scene']),caption=caption))
    save(REVIEW/'panels.json',items)
    body=''.join(f'<section><h2>{html.escape(a["title"])}</h2><a href="{a["file"]}"><img loading="lazy" src="{a["file"]}" alt="{html.escape(a["title"])}"></a><p>{html.escape(a["caption"])}</p></section>' for a in items)
    (REVIEW/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R283 evidence review</title><style>body{background:#181d24;color:white;font:18px sans-serif;max-width:1200px;margin:24px auto}img{width:100%}section{margin:45px 0}a{color:cyan}</style><h1>R283: photographic ownership → physical correspondence → conditional pattern</h1><p>High is an uncalibrated class. No count, helicity, physical identities or pattern is accepted. Full explanations and overlay keys are printed beneath every image.</p><p><a href="../../R283_REPORT.md">Report</a> · <a href="../r282/index.html">Preserved R282 A/B/C comparisons</a></p>'+body)
    print(len(items),'review panels',flush=True)

if __name__=='__main__':main()
