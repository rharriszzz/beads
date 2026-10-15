"""Native photograph overlays and static initial/revised review comparisons."""
import html,json
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from photo2.r293.geometry import Reference
from .common import *
from .geometry import Chain

ORANGE=(255,177,45); GREEN=(76,255,174); WHITE=(245,245,255); RED=(255,78,85); CYAN=(85,220,255)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(size):return ImageFont.truetype(FONT,size)
def text(d,xy,t,size=16,color=WHITE):d.text(tuple(xy),t,font=font(size),fill=color,stroke_width=max(1,size//12),stroke_fill=(12,14,20))

def label_chain(im,scene,origin=(0,0),scale=1,color=GREEN,interval=10,connect=False,box=None):
    d=ImageDraw.Draw(im);xy=(scene.pc-origin)*scale;keep=(scene.indices>=REQUESTED[0])&(scene.indices<=REQUESTED[1])
    if connect:d.line([tuple(p) for p in xy[keep]],fill=(*color,100) if im.mode=='RGBA' else color,width=1)
    for j,(k,p) in enumerate(zip(scene.indices,xy)):
        if not keep[j] or not (-20<=p[0]<=im.width+20 and -20<=p[1]<=im.height+20):continue
        radius=3 if scale==1 else 3.3
        d.ellipse((*tuple(p-radius),*tuple(p+radius)),outline=color,width=1)
        if k==0:
            d.ellipse((*tuple(p-12),*tuple(p+12)),outline=(255,245,55),width=3)
            text(d,p+[12,-28],'BEAD 0',int(18*max(1,scale/1.5)),(255,245,55))
        elif k%interval==0:text(d,p+[6,-15],f'{k:+d}',int(14*max(1,scale/1.5)),color)
    return im

def banner(im,title,lines):
    d=ImageDraw.Draw(im);height=70+len(lines)*25
    d.rectangle((0,0,im.width,height),fill=(12,16,25))
    text(d,(20,12),title,25)
    for i,line in enumerate(lines):text(d,(20,50+25*i),line,17)

def whole(stage,native,scene):
    im=Image.fromarray(native);d=ImageDraw.Draw(im)
    ref=Reference();d.line([tuple(p) for p in ref.points[::5]],fill=(180,215,240),width=1)
    label_chain(im,scene,color=ORANGE if stage=='initial' else GREEN,connect=True)
    banner(im,f'R294 {stage} conditional fit: -20 through +200',[
        'Yellow ring = bead 0; numbered rings = projected physical model centers, not measured centers.',
        'Thin pale line = image-derived necklace reference. Indices follow the helix along the chain.',
        'Only this bounded run is indexed. Hidden and unsupported predictions retain their labels.'])
    im.save(REVIEW/(stage+'-whole.png'))
    thumb=im.copy();thumb.thumbnail((1000,1250));thumb.save(REVIEW/(stage+'-preview.png'))

def local_owner(path,box):
    z=np.load(path);xy=z['xy'];owner=z['owner'];x0,y0,x1,y1=box
    keep=(xy[:,0]>=x0)&(xy[:,0]<x1)&(xy[:,1]>=y0)&(xy[:,1]<y1)
    a=np.full((y1-y0,x1-x0),-999,np.int32);p=xy[keep]-[x0,y0];a[p[:,1],p[:,0]]=owner[keep]
    a[(a<REQUESTED[0])|(a>REQUESTED[1])]=-999
    return a

def model_boundaries(im,owner,color,factor):
    edge=np.zeros(owner.shape,bool)
    for shift in ((1,0),(-1,0),(0,1),(0,-1)):
        other=ndi.shift(owner,shift,order=0,mode='constant',cval=-999)
        edge|=(owner>=REQUESTED[0])&(owner!=other)
    # One native pixel only. Native geometry boundary is displayed, not a photo segmentation.
    a=np.asarray(im).copy();a[edge]=color
    return Image.fromarray(a).resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)

def crop_panel(name,box,caption,native,scenes,source=None):
    x0,y0,x1,y1=box;raw=Image.fromarray(native[y0:y1,x0:x1]);factor=2
    panels=[raw.resize((raw.width*factor,raw.height*factor),Image.Resampling.NEAREST)]
    for stage,color in (('initial',ORANGE),('revised',GREEN)):
        owner=local_owner(OUT/stage/'visibility.npz',box)
        im=model_boundaries(raw,owner,color,factor)
        label_chain(im,scenes[stage],origin=np.array(box[:2]),scale=factor,color=color,interval=5)
        if source:
            # Exact historical automatic interior shown only on annotated panels.
            xy=pixels(source['measured_support']);mask=np.zeros(owner.shape,bool);q=xy-[x0,y0]
            ok=(q[:,0]>=0)&(q[:,0]<raw.width)&(q[:,1]>=0)&(q[:,1]<raw.height);q=q[ok];mask[q[:,1],q[:,0]]=True
            edge=mask&~ndi.binary_erosion(mask)
            d=ImageDraw.Draw(im)
            for yy,xx in np.argwhere(edge)[::2]:d.rectangle((xx*factor,yy*factor,xx*factor+1,yy*factor+1),fill=WHITE)
        panels.append(im)
    width=sum(p.width for p in panels);height=panels[0].height
    sheet=Image.new('RGB',(width,height+140),(12,16,25));d=ImageDraw.Draw(sheet)
    for i,(p,title) in enumerate(zip(panels,('Original photograph','Initial model','Revised model'))):
        sheet.paste(p,(i*p.width,36));text(d,(i*p.width+10,7),title,18)
    import textwrap
    wrapped=textwrap.wrap(caption,width=max(80,width//10))
    for i,line in enumerate(wrapped[:4]):text(d,(12,height+49+i*21),line,16)
    sheet.save(REVIEW/(name+'.png'));raw.save(REVIEW/(name+'-native.png'))
    return dict(id=name,box=box,image=name+'.png',native=name+'-native.png',caption=caption,
        source_record=source['record_id'] if source else None)

def anchor_panel(native,inputs,scenes):
    box=(1400,205,1660,345);raw=Image.fromarray(native[205:345,1400:1660]);im=raw.resize((1040,560),Image.Resampling.NEAREST)
    d=ImageDraw.Draw(im);ref=Reference();p=ref.points;keep=(p[:,0]>=1400)&(p[:,0]<1660)&(p[:,1]>=205)&(p[:,1]<345)
    d.line([tuple((q-[1400,205])*4) for q in p[keep]],fill=CYAN,width=2)
    a=inputs['anchor'];xy=pixels(a['measured_support']);mask=np.zeros(raw.size[::-1],bool);q=xy-[1400,205];mask[q[:,1],q[:,0]]=True
    edge=mask&~ndi.binary_erosion(mask)
    for yy,xx in np.argwhere(edge):d.rectangle((xx*4,yy*4,xx*4+2,yy*4+2),fill=(255,245,55))
    p=(np.array(a['measured_photo_location'])-[1400,205])*4
    d.line((*tuple(p-[7,0]),*tuple(p+[7,0])),fill=WHITE,width=2);d.line((*tuple(p-[0,7]),*tuple(p+[0,7])),fill=WHITE,width=2)
    text(d,p+[15,-65],'BEAD 0: red crossing',23,(255,245,55))
    sheet=Image.new('RGB',(1040,730),(12,16,25));sheet.paste(im,(0,35));d=ImageDraw.Draw(sheet)
    text(d,(12,5),'Highest supported crossing; source region and reference only',21)
    lines=['Yellow: unchanged C-1497-0271 automatic interior (393 native pixels). Cyan: image reference.',
        'White cross: visible-interior centroid (1499.36, 271.20), not a physical center.',
        'Independent H-1497-0270 patch: (1496.95, 271.15), threshold sensitivity 0.30px.',
        'The neighboring C-1582-0272 crossing is unresolved; it does not displace the clearer origin.',
        'This is a plausible conditional anchor; no new human ownership judgment is asserted.']
    for i,t in enumerate(lines):text(d,(12,610+i*21),t,16)
    sheet.save(REVIEW/'bead-zero.png')

def main():
    REVIEW.mkdir(parents=True,exist_ok=True);inputs=read(EVIDENCE/'inputs.json.gz');native,_,meta=photo()
    ev={k:read(OUT/(k+'-evaluation.json')) for k in ('initial','revised')};scenes={k:Chain(v['parameters'],inputs) for k,v in ev.items()}
    for k,s in scenes.items():whole(k,native,s)
    anchor_panel(native,inputs,scenes)
    old={k:{r['record_id']:r for r in v['legacy']} for k,v in ev.items()};source={r['source']['record_id']:r['source'] for r in inputs['legacy_colored']}
    pairs=[(rid,old['initial'][rid],r) for rid,r in old['revised'].items()]
    selected=[];used=[]
    def pick(pool,count,kind,separation=60):
        added=0
        for rid,a,b in pool:
            p=np.array(b['source_location'])
            if any(np.linalg.norm(p-q)<separation for q in used):continue
            used.append(p);x,y=np.rint(p).astype(int);box=[int(x-105),int(y-85),int(x+105),int(y+85)]
            name=f'{kind}-{added+1:02}';delta=b['containment']-a['containment']
            caption=f'{rid}, {b["split"]}: full historical interior containment {a["containment"]:.1%} -> {b["containment"]:.1%}; conditional index {a["conditional_index"]} -> {b["conditional_index"]}. White dotted line = old automatic interior, not boundary truth. Colored lines = modeled first-hit boundaries. No Phase1 pixels changed.'
            item=crop_panel(name,box,caption,native,scenes,source[rid]);item.update(kind=kind,initial=a,revised=b)
            selected.append(item);added+=1
            if added>=count:break
    central=[v for v in pairs if (source[v[0]]['centerline_distance']<=26 or source[v[0]]['centerline']['crosses'])
        and v[2]['conditional_index'] is not None and REQUESTED[0]<=v[2]['conditional_index']<=REQUESTED[1]]
    pick(sorted(central,key=lambda v:v[2]['containment']),3,'mismatch')
    pick(sorted(central,key=lambda v:-min(v[1]['containment'],v[2]['containment'])),3,'matched')
    pick(sorted([v for v in pairs if v[2]['containment']>v[1]['containment']+.03],key=lambda v:-(v[2]['containment']-v[1]['containment'])),1,'improved',35)
    pick(sorted([v for v in central if v[2]['containment']<v[1]['containment']-.03],key=lambda v:v[2]['containment']-v[1]['containment']),1,'regressed',35)
    neutral=[r for r in ev['revised']['light']['evidence'] if r['context']=='unknown' and r['split']=='holdout']
    if neutral:
        r=max(neutral,key=lambda r:r.get('angle_deg',0));obs=next(o for o in ev['revised']['observations'] if o['observation_id']==r['observation_id'])
        x,y=np.rint(obs['source_location']).astype(int);box=[int(x-105),int(y-85),int(x+105),int(y+85)]
        caption=f'{r["observation_id"]}: held-out neutral reflection candidate, conditional owner {obs["conditional_index"]}, mirror-light disagreement {r["angle_deg"]:.1f} degrees. A contained reflection does not locate a physical black-bead center or certify its owner.'
        item=crop_panel('reflection-01',box,caption,native,scenes);item.update(kind='reflection');selected.append(item)
    # Whole-photo comparison identifies the locations of the review crops.
    im=Image.fromarray(native);d=ImageDraw.Draw(im)
    for k in range(-20,201,10):
        j=np.flatnonzero(scenes['initial'].indices==k)[0];a=scenes['initial'].pc[j];b=scenes['revised'].pc[j]
        d.line([tuple(a),tuple(b)],fill=WHITE,width=2);d.ellipse((*tuple(a-4),*tuple(a+4)),outline=ORANGE,width=2);d.ellipse((*tuple(b-4),*tuple(b+4)),outline=GREEN,width=2)
    for j,c in enumerate(selected):
        color=RED if c['kind'] in ('mismatch','regressed') else GREEN
        d.rectangle(tuple(c['box']),outline=color,width=3);text(d,(c['box'][0],c['box'][1]-26),f'{j+1}: {c["id"]}',20,color)
    j=np.flatnonzero(scenes['revised'].indices==0)[0];p=scenes['revised'].pc[j];text(d,p+[15,-45],'BEAD 0',24,(255,245,55))
    banner(im,'R294 initial vs revised: compatibility and index changes',[
        'Orange = initial centers; green = revised centers; white segments connect the same conditional index.',
        'Red boxes locate failures/regressions; green boxes locate matched/improved review crops.',
        'The certified revision keeps the initial hand; a higher-scoring alternative physically interpenetrates.'])
    im.save(REVIEW/'mismatch-comparison-whole.png');im.thumbnail((1000,1250));im.save(REVIEW/'comparison-preview.png')
    # An enlarged full-run comparison makes systematic index movement visible.
    runbox=(1390,205,2220,850)
    crop_panel('full-run-comparison',runbox,'Original / initial / revised; literal annular first-hit boundaries. All coordinates remain native photograph pixels. Sequence goes right around the top, then down the right bend.',native,scenes)
    manifest=dict(photo=meta,crops=selected,full_run_box=runbox,original_observations_unchanged=True,
        overview_images=['initial-whole.png','revised-whole.png','mismatch-comparison-whole.png'],
        symbols='Colored outlines are model geometry, white dotted lines are historical automatic interiors; circles are predicted physical centers. Unknown body ownership stays unresolved.')
    save(REVIEW/'manifest.json',manifest)
    cards=[]
    for c in selected:cards.append(f'<article><h2>{html.escape(c["id"])}</h2><a href="{c["image"]}"><img src="{c["image"]}" alt="{html.escape(c["caption"])}"></a><p>{html.escape(c["caption"])}</p><a href="{c["native"]}">Unmarked native crop</a></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R294 bounded chain fit</title><style>body{margin:auto;max-width:1350px;padding:22px;background:#10151f;color:#eaf0fc;font:17px/1.5 system-ui}a{color:#8fdcff}img{width:100%;height:auto}article{margin:36px 0;padding:12px;background:#182131}h1{font-size:30px}.overviews{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:14px}h2{font-size:22px}p{max-width:1000px}</style><h1>R294: bead 0 through a conditional −20…200 chain</h1><p>Original photograph only. Initial and revised models preserve all Phase1 evidence. The revised fit improves containment but changes preferred hand; physical bead indexing remains unresolved. Click images for full native resolution.</p><p><a href="../../../R294_REPORT.md">Report</a> · <a href="../../../R294_REPRODUCE.md">Reproduction</a> · <a href="../../r294/results/revised-positions.csv">Revised positions CSV</a></p><h2>Bead 0</h2><a href="bead-zero.png"><img src="bead-zero.png" alt="Bead zero native photographic evidence"></a><div class="overviews">'''
    for title,preview,full in [('Initial','initial-preview.png','initial-whole.png'),('Revised','revised-preview.png','revised-whole.png'),('Comparison','comparison-preview.png','mismatch-comparison-whole.png')]:page+=f'<section><h2>{title}</h2><a href="{full}"><img src="{preview}" alt="{title} whole-photo overlay"></a></section>'
    page+='</div><h2>Full bounded run, original / initial / revised</h2><a href="full-run-comparison.png"><img src="full-run-comparison.png" alt="Entire fitted arc side by side"></a>'+''.join(cards)+'</html>'
    # Links are relative to photo2/review/r294.
    page=page.replace('../../../R294_','../../R294_')
    page=page.replace('The revised fit improves containment but changes preferred hand; physical bead indexing remains unresolved.', 'The certified revised fit preserves the initial hand. A higher-scoring alternative interpenetrates; physical bead indexing remains conditional.')
    (REVIEW/'index.html').write_text(page)
    print('Review:',len(selected),'native crops; three whole-photo overlays')
if __name__=='__main__':main()
