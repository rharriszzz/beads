"""Curated R239 measurement cards. Coordinates select illustrations, never detection."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from photo2.stage1_pilot import ROOT,read,save,sha
from photo2.stage1_recovery import local_fields,RULES as R238_RULES
from photo2.stage1_ownership import BUNDLE,RULES,shape_regions

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def references(out):
    im=Image.open(ROOT/'beads-photo-2.jpg');font=ImageFont.truetype(FONT,14)
    refs=read(BUNDLE/'references.json')
    for s in read(BUNDLE/'protocol.json')['transfer']:
        raw=im.crop(s['halo']).resize((880,840),Image.Resampling.NEAREST)
        grid=raw.copy();d=ImageDraw.Draw(grid);d.rectangle((120,120,760,720),outline='white',width=2)
        for x in range(0,161,20):d.text((120+4*x,92),str(x),fill='white',font=font,stroke_width=2,stroke_fill='black')
        for y in range(0,151,20):d.text((85,120+4*y),str(y),fill='white',font=font,stroke_width=2,stroke_fill='black')
        grid.save(out/f"{s['id']}-raw.png")
        d=ImageDraw.Draw(raw);d.rectangle((120,120,760,720),outline='white')
        for r in refs:
            if r['section']!=s['id']:continue
            x,y=(np.array(r['reference_representative_xy'])-s['halo'][:2])*4
            col='white' if r['eligibility']=='eligible' else '#66ffcc'
            d.ellipse((x-4,y-4,x+4,y+4),outline=col,width=2)
            d.text((x+5,y-16),r['observation_id'].split('-')[1],fill=col,font=font,stroke_width=2,stroke_fill='black')
        raw.save(out/f"{s['id']}-references.png")


def cards(out):
    sections={s['section']:s for split in ['development','transfer'] for s in read(BUNDLE/split/'ownership.json')['results']}
    params=read(ROOT/'photo2/review/r238/inputs.json')['parameters'];diam=params['native_diameter']
    im=Image.open(ROOT/'beads-photo-2.jpg');rgb=np.asarray(im);font=ImageFont.truetype(FONT,14)
    cases=[
        ('black','H1',['A04','A07'],'Paper rim versus genuine black reflection', 'A04 abstains; A07 retained. Dark rays: 8 versus 16.'),
        ('black','H4',['A13'],'Colored bead owns the bright feature', 'Wrong-black A13 abstains: 10 rays reach color first.'),
        ('black','T1',['A13'],'Fresh transfer: a real black reflection is lost', 'B07 abstains: only 10 dark rays. Occlusion defeats enclosure.'),
        ('black','T2',['A15'],'Fresh transfer: enclosure is insufficient', 'Retained, but weak diffuse light on deferred B05 stays unresolved.'),
        ('color','D4',['P10','A08'],'Two samples on one red body', 'P10 retained; duplicate A08 abstains. Shared shape lobe 12.'),
        ('color','T1',['P15','A08'],'Fresh transfer: duplicate removed', 'P15 retained; duplicate A08 abstains. Shared shape lobe 19.'),
        ('color','T2',['A01','A06'],'Fresh transfer: two yellow beads falsely grouped', 'A01 is halo context; B02 sample A06 lost. Shared lobe 1.'),
        ('color','D4',['P14','A02'],'Merged yellow faces produce abstention', 'B27 and B30 lost: joint lobe 1239px exceeds 1220px limit.')]
    sheets={'black':[],'color':[]};records=[]
    for kind,sec,ids,title,caption in cases:
        s=sections[sec];points=[next(p for p in s['proposals'] if p['candidate_id']==sec+'-'+i) for i in ids]
        xy=np.mean([p['xy'] for p in points],axis=0).round().astype(int);box=[int(xy[0]-35),int(xy[1]-30),int(xy[0]+35),int(xy[1]+30)]
        raw=im.crop(box).resize((420,360),Image.Resampling.NEAREST);marked=raw.copy();dr=ImageDraw.Draw(marked)
        if kind=='color':
            halo=s['halo'];patch=rgb[halo[1]:halo[3],halo[0]:halo[2]];hsv,masks,_,_=local_fields(patch,params,R238_RULES)
            mode=points[0]['ownership_evidence']['mode'];mask=masks[mode];v=hsv[...,2]
            diffuse=ndi.gaussian_filter(v*mask,1.)/np.maximum(ndi.gaussian_filter(mask.astype(float),1.),1e-6)
            maximum=ndi.maximum_filter(diffuse,size=max(3,round(RULES['seam_window_d']*diam)))
            support,depth,labels=shape_regions(mask&(diffuse>=RULES['seam_diffuse_fraction']*maximum),diam)
            for p in points:
                lab=p['ownership_evidence']['shape_label'];region=labels==lab;edge=region&~ndi.binary_erosion(region)
                for ey,ex in np.argwhere(edge):
                    gx,gy=ex+halo[0],ey+halo[1]
                    if box[0]<=gx<box[2] and box[1]<=gy<box[3]:
                        x,y=(gx-box[0])*6,(gy-box[1])*6;dr.rectangle((x,y,x+4,y+4),fill='#44ddff')
        for p in points:
            x,y=(np.array(p['xy'])-box[:2])*6;col='#55ff55' if p['ownership_decision']=='retain' else '#ff7777'
            if kind=='black':
                e=p['ownership_evidence'];rr=e['radii_px']
                for i,(dark,color) in enumerate(zip(e['first_dark_samples'],e['first_color_samples'])):
                    angle=i*2*np.pi/RULES['rays'];r=rr[min(dark,color,len(rr)-1)]*6
                    raycol='#55ff55' if dark<color and dark<len(rr) else '#ffaa33' if color<len(rr) else '#ff7777'
                    dr.line((x+rr[0]*6*np.cos(angle),y+rr[0]*6*np.sin(angle),x+r*np.cos(angle),y+r*np.sin(angle)),fill=raycol,width=1)
            dr.ellipse((x-4,y-4,x+4,y+4),outline='white',width=2)
            dr.text((x+5,y-18),p['candidate_id'].split('-')[1],fill=col,font=font,stroke_width=2,stroke_fill='black')
        card=Image.new('RGB',(840,442),'white');card.paste(raw,(0,82));card.paste(marked,(420,82));d=ImageDraw.Draw(card)
        for y,text in [(5,sec+': '+title),(26,caption),(49,'Raw | sampling rays / cyan support boundaries; neither is a physical bead outline')]:d.text((7,y),text,fill='black',font=font)
        sheets[kind].append(card);records.append(dict(section=sec,crop=box,title=title,caption=caption,proposals=points))
    for kind,panels in sheets.items():
        sheet=Image.new('RGB',(840,442*len(panels)),'white')
        for i,panel in enumerate(panels):sheet.paste(panel,(0,i*442))
        sheet.save(out/f'{kind}-evidence.png')
    save(out/'measurement-cards.json',records)


def losses(out):
    report=read(BUNDLE/'report.json');before=report['r238'];after=report['ownership']
    states={p['candidate_id']:p for split in ['development','transfer'] for s in read(BUNDLE/split/'ownership.json')['results'] for p in s['proposals']}
    old={r['observation_id']:r for r in before['observations']}
    rows=[];lines=['# Previously correct body detections lost by R239','','These bodies remain eligible; abstention is a coverage loss, not a reference deletion.','','| Body | Color | R238 correct proposals | Why all were lost |','| --- | --- | --- | --- |']
    for r in after['observations']:
        b=old[r['observation_id']]
        if b['automatic_candidate_ids'] and not r['automatic_candidate_ids']:
            pp=[states[c] for c in b['automatic_candidate_ids']]
            rows.append(dict(observation_id=r['observation_id'],color=r['color'],previous_proposals=pp))
            lines.append(f"| {r['observation_id']} | {r['color']} | {', '.join(b['automatic_candidate_ids'])} | {'; '.join(sorted({p['ownership_reason'] for p in pp}))} |")
    save(out/'lost-correct.json',rows);(out/'lost-correct.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args();out=Path(args.output or BUNDLE);out.mkdir(parents=True,exist_ok=True)
    references(out);cards(out);losses(out)
