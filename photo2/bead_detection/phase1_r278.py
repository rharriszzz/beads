"""Independent image feature search; no construction/index imports or inputs.

R275 locations/masks are frozen. New multiscale LoG and chromatic-core candidates
must pass the existing native enclosure, hue and ownership checks. Failed and
overlapping supports remain evidence, not fabricated independent beads.
"""
from __future__ import annotations
import copy, gzip, json
from collections import Counter
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image,ImageOps,ImageDraw
from .centerline_r275 import ROOT,Band
from .brightness_r270 import color_managed_photo
from .recover_r275 import Recovery,resolve
from .coverage_r272 import Parameters
from .reflection_r275 import reflection_region
from .homogeneous_r275 import guard_ownership
from .core_r275 import core
from .interiors_r273 import pixels
from .inventory_r272 import hue_distance
from ..bead_debugger.generate import save,sha

OUT=ROOT/'photo2/review/r278'


def features(engine):
    lum=engine.lum; allowed=(engine.paper==0)
    responses=[]; peaks=[]
    for scale in (2.,3.,4.):
        response=-ndi.gaussian_laplace(lum,scale)*scale**2
        yy,xx=np.where((response==ndi.maximum_filter(response,7))&(response>.008)&allowed)
        safe=(xx>=34)&(yy>=34)&(xx<lum.shape[1]-34)&(yy<lum.shape[0]-34)
        pts=np.c_[xx[safe],yy[safe]];peaks.append(pts);responses.append(response)
    trees=[cKDTree(p) for p in peaks]
    result=[]
    for x,y in peaks[1]:
        persistence=max(float(t.query([x,y])[0]) for t in trees)
        result.append(dict(anchor=[int(x),int(y)],method='LoG scales 2/3/4',persistence_px=persistence,
                           feature_value=float(responses[1][y,x]),stable=bool(persistence<=3)))
    hs=engine.hsv
    for color,own in engine.palette.items():
        other=engine.palette.get('red' if color=='yellow' else 'yellow')
        if other is None:continue
        support=allowed&(hs[:,:,1]>=.35)&(lum>=.025)&(hue_distance(hs[:,:,0]*360,own)<=20)&(hue_distance(hs[:,:,0]*360,other)-hue_distance(hs[:,:,0]*360,own)>=6)
        distance=ndi.distance_transform_edt(support)
        maxima=(distance==ndi.maximum_filter(distance,9))&(distance>=3)
        labels,n=ndi.label(maxima)
        for sl in ndi.find_objects(labels):
            if sl is None:continue
            local=distance[sl];y,x=np.unravel_index(local.argmax(),local.shape);x+=sl[1].start;y+=sl[0].start
            if min(x,y,lum.shape[1]-1-x,lum.shape[0]-1-y)<34:continue
            result.append(dict(anchor=[int(x),int(y)],method='chromatic distance core',color=color,
                               feature_value=float(distance[y,x]),stable=True))
    return result


class WholePhoto:
    def qualifies(self,point,region=None):return dict(in_band=True,scope='whole photograph; actual centerline membership recorded separately')


def recover(native,srgb,old,base):
    band=Band();e=Recovery(native,srgb,base,band,pale=True)
    known=cKDTree(np.array([[l['point']['x'],l['point']['y']] for l in old['locations']]).reshape(-1,2))
    owned=set().union(*(pixels(r) for r in old['beads']));proposals=[];decisions=[]
    fs=features(e)
    for i,f in enumerate(fs):
        f['id']=f'F278-{i:05d}';f['nearest_existing_distance']=float(known.query(f['anchor'])[0])
        if not f['stable'] or f['nearest_existing_distance']<8:
            f['status']='unstable scale response' if not f['stable'] else 'near existing photographic location';continue
        r=e.new_colored(f['anchor'],'R278',True)
        if r.get('color'):
            if r.get('region'):
                # Some new full-photo seeds fail before a bounded broad region
                # exists. Use the ordinary hue fallback then the guarded core.
                r=e.interior(r,layered=False)
                if not r.get('accepted'):r=core(e,r,owned)
                r=guard_ownership(r,old,e)
        elif f['method'].startswith('LoG'):
            r=dict(id='R278-K-%04d-%04d'%tuple(f['anchor']),anchor=f['anchor'],accepted=False,reasons=[],confidence={})
            reflection_region(r,native,srgb,e.hsv,e.nhsv,e.lum,e.paper,replace(Parameters(),black_maximum_value=.40,black_surround_fraction=.25),.70,list(e.palette.values()),True)
        r['r278_feature']=f;f['status']='native measurement attempted';proposals.append(r)
    beads,locations,decisions=resolve(proposals,old,WholePhoto())
    prior={l['id'] for l in old['locations']}
    for l in locations:
        if l['id'] not in prior:
            l['source']='R278 image-only multiscale/component recovery'
            b=next(b for b in beads if b['id']==l['id'])
            l['centerline_near']=band.qualifies([l['point']['x'],l['point']['y']],b['region'])
            l['physical_center']=None
            l['identity_warning']='Image-supported proposal; reflection/interior location is not the physical center.'
    return {**copy.deepcopy(old),'beads':beads,'locations':locations},fs,decisions


def confidence_gate(r):
    """New full-photo scope requires intact enclosure, not an inset-core rescue.

    Failed upstream caps must not disappear inside the historical hue fallback.
    All smaller-support rescues stay candidates because same-material patches
    and paper can satisfy their local hue tests without identifying a bead.
    """
    if not r.get('accepted'):return
    reasons=[]
    if max(r.get('confidence',{}).get('pre_retreat_pixels',0),r.get('region',{}).get('pixel_count',0))>870:
        reasons.append('native-size-cap')
    if r['color']!='black':
        if r.get('recovery_method')!='r274-broad':reasons.append('broad-enclosure-unverified')
        ev=r.get('color_evidence',{});ds=ev.get('distances',[[180]])
        if ds[0][0]>10 or ev.get('hue_deviation90',180)>12:reasons.append('mixed-or-transitional-color')
        if r.get('confidence',{}).get('mean7_y',0)<.08:reasons.append('dim-body-uncertain')
        if r.get('region',{}).get('pixel_count',0)<60:reasons.append('small-colored-extent-uncertain')
    else:
        if not r.get('dark_perimeter',{}).get('closed'):reasons.append('dark-enclosure-unverified')
        if r.get('brightest',{}).get('hsv_srgb',{}).get('s',1)>.35:reasons.append('tinted-secondary-reflection-uncertain')
        if r.get('brightest',{}).get('luminance',0)<.25:reasons.append('weak-reflection-uncertain')
    if reasons:r['accepted']=False;r['reasons']+=reasons


def atlas(rgb,old,data,decisions):
    im=Image.fromarray(rgb);prior={r['id'] for r in old['locations']}
    cases=[dict(id=l['id'],anchor=[l['point']['x'],l['point']['y']],status='new image-only '+l['color']) for l in data['locations'] if l['id'] not in prior]
    cases+=json.loads((ROOT/'photo2/review/r275/unresolved-candidates.json').read_text())
    cases += [dict(id=l['id'],anchor=[l['point']['x'],l['point']['y']],status='small colored support') for l in old['locations'] if l.get('audit_warnings')]
    stations=json.loads((ROOT/'photo2/review/r275/stations.json').read_text())
    loc={l['id']:l for l in data['locations']}
    for g in stations['groups']:
        if g['short_flag']:
            xy=np.mean([[loc[k]['point']['x'],loc[k]['point']['y']] for k in g['ids']],axis=0)
            cases.append(dict(id='short-station-'+str(g['station']),anchor=xy.tolist(),status='short interval; not evidence of duplicate identity'))
    band=Band()
    for l in old['locations']:
        d=float(band.distance([l['point']['x'],l['point']['y']]))
        if abs(d-26)<=1:cases.append(dict(id=l['id'],anchor=[l['point']['x'],l['point']['y']],status='band edge'))
    tree=cKDTree([[l['point']['x'],l['point']['y']] for l in data['locations']])
    overview=im.resize((762,955));draw=ImageDraw.Draw(overview)
    for l in data['locations']:
        x,y=l['point']['x']*.3,l['point']['y']*.3;c='lime' if l['id'] not in prior else 'cyan';draw.ellipse((x-1,y-1,x+1,y+1),fill=c)
    overview.save(OUT/'phase1-overview.png')
    for page in range((len(cases)+7)//8):
        sheet=Image.new('RGB',(1000,4*258),'white');draw=ImageDraw.Draw(sheet)
        for j,r in enumerate(cases[page*8:page*8+8]):
            x,y=map(int,r['anchor']);box=(x-40,y-40,x+40,y+40);raw=im.crop(box).resize((240,240));mark=raw.copy();d=ImageDraw.Draw(mark)
            for k in tree.query_ball_point([x,y],58):
                l=data['locations'][k];px=(l['point']['x']-box[0])*3;py=(l['point']['y']-box[1])*3
                color='lime' if l['id'] not in prior else 'cyan';d.ellipse((px-3,py-3,px+3,py+3),outline=color,width=1)
            d.rectangle((118,118,122,122),outline='orange')
            ox=(j%2)*500;oy=(j//2)*258;sheet.paste(raw,(ox,oy+18));sheet.paste(mark,(ox+245,oy+18));draw.text((ox,oy),r['id']+' '+r.get('status','unresolved'),fill='black')
            r['atlas']=f'phase1-atlas-{page+1:02d}.jpg'
        sheet.save(OUT/f'phase1-atlas-{page+1:02d}.jpg',quality=93)
    save(OUT/'phase1-review-cases.json',cases)


def main():
    OUT.mkdir(exist_ok=True)
    old=json.loads((ROOT/'photo2/review/r275/inventory.json').read_text())
    base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads']
    native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,icc=color_managed_photo()
    import sys
    if '--select-saved' in sys.argv:
        archive=OUT/'failed-wide-control'
        with gzip.open(archive/'phase1-decisions.json.gz','rt') as f:proposals=json.load(f)
        with gzip.open(archive/'phase1-features.json.gz','rt') as f:fs=json.load(f)
        for r in proposals:confidence_gate(r)
        beads,locations,decisions=resolve(proposals,old,WholePhoto());data={**copy.deepcopy(old),'beads':beads,'locations':locations}
        prior={l['id'] for l in old['locations']};band=Band();regions={b['id']:b for b in beads}
        for l in locations:
            if l['id'] not in prior:
                l['source']='R278 image-only multiscale/component recovery';l['centerline_near']=band.qualifies([l['point']['x'],l['point']['y']],regions[l['id']]['region']);l['physical_center']=None
    else:
        _,fs,proposals=recover(native,srgb,old,base)
        for r in proposals:confidence_gate(r)
        beads,locations,decisions=resolve(proposals,old,WholePhoto());data={**copy.deepcopy(old),'beads':beads,'locations':locations}
        prior={l['id'] for l in old['locations']};band=Band();regions={b['id']:b for b in beads}
        for l in locations:
            if l['id'] not in prior:
                l['source']='R278 image-only multiscale/component recovery';l['centerline_near']=band.qualifies([l['point']['x'],l['point']['y']],regions[l['id']]['region']);l['physical_center']=None
    # Preserve all decisions, including failed broad masks and secondary highlights.
    for name,obj in [('phase1-inventory.json.gz',data),('phase1-decisions.json.gz',decisions),('phase1-features.json.gz',fs)]:
        with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:f.write(json.dumps(obj,separators=(',',':'),allow_nan=False).encode())
    prior={l['id'] for l in old['locations']};new=[l for l in data['locations'] if l['id'] not in prior]
    summary=dict(locations=len(data['locations']),interiors=len(data['beads']),prior_locations=len(prior),new=len(new),new_target=sum(l['centerline_near']['in_band'] for l in new),new_colors=dict(Counter(l['color'] for l in new)),features=len(fs),attempts=len(decisions),decisions=dict(Counter(r['status'] for r in decisions)),
        source_image_sha256=sha(ROOT/'beads-photo-2.jpg'),prior_inventory_sha256=sha(ROOT/'photo2/review/r275/inventory.json'),icc=icc,
        unresolved_prior_groups=63,completeness='Not certified. Dark bodies without reflections and merged same-color supports remain unresolved.',
        independence='No physical construction, spacing, indices, predicted coordinates or colors used.')
    save(OUT/'phase1-summary.json',summary);atlas(srgb,old,data,decisions);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
