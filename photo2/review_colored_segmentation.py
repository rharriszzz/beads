"""R215 curated raw/mask review; no manual beads, chains or geometry fitting."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
from segment_colored_beads import segment
from bead_evidence_inventory import encode_pixels
from auto_label_beads import ROOT,sha


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def overlay(image,masks,show_band=False,show_reflections=False,region=None,reflection=None):
    result=image.copy()
    layers=[((masks['retained']==region) if region is not None else masks['retained']>0,[0,255,0])]
    if show_band:
        band=masks['boundary_band']
        if region is not None: band=band&(masks['candidate']==region)
        layers.append((band,[255,140,0]))
    if show_reflections:
        ref=(masks['reflections']==reflection) if reflection is not None else masks['reflections']>0
        layers.append((ref,[0,255,255]))
    for mask,color in layers:
        result[mask]=(result[mask]*.6+np.asarray(color)*.4).astype(np.uint8)
    return result


def choose_regions(report,image,masks):
    xy=np.asarray([r['retained_centroid_xy'] for r in report['records']]); center=xy.mean(axis=0)
    selected=[]
    for color,target in [('yellow',np.pi*.60),('red',np.pi*.20)]:
        choices=[]
        for row in report['records']:
            if row['display_color']!=color or row['retained_pixels']<300 or row['retained_components']!=1: continue
            x,y=row['retained_centroid_xy']; angle=np.arctan2(y-center[1],x-center[0])
            error=abs((angle-target+np.pi)%(2*np.pi)-np.pi)
            choices.append((error+.10*abs(np.log(row['candidate_pixels']/750)),row))
        selected.append(min(choices,key=lambda pair:pair[0])[1])
    return selected,center


def marked_raw(image,xy,letter,box):
    crop=Image.fromarray(image).crop(box).resize((420,330),Image.Resampling.NEAREST)
    draw=ImageDraw.Draw(crop); font=ImageFont.truetype('DejaVuSans.ttf',25)
    x=(xy[0]-box[0])*3; y=(xy[1]-box[1])*3
    tx=max(5,min(370,x-80)); ty=max(5,min(285,y-75))
    draw.line((tx+20,ty+28,x,y),fill='white',width=2)
    draw.text((tx,ty),letter,fill='white',font=font,stroke_width=2,stroke_fill='black')
    return crop


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r215')
    args=parser.parse_args(); out=args.output; out.mkdir(parents=True,exist_ok=True)
    protected=json.loads((ROOT/'photo2/review/r214/summary.json').read_text())['protected_inputs']
    assert all(sha(ROOT/p)==digest for p,digest in protected.items())
    photo=ROOT/'beads-photo-2.jpg'; image=np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'))
    report,masks=segment(image,sha(photo))
    baseline,baseline_masks=segment(image,sha(photo),use_dark_valleys=False)
    routine=ROOT/'photo2/output/r215'
    save(routine/'segmentation.json',report); np.savez_compressed(routine/'pixel-masks.npz',**masks)
    for key in ['candidate','retained','diffuse_retained','reflections']:
        Image.fromarray(masks[key].astype(np.uint16)).save(routine/(key+'-labels.tiff'))
    Image.fromarray(masks['boundary_band'].astype(np.uint8)*255).save(routine/'boundary-band.png')
    Image.fromarray(overlay(image,masks)).save(routine/'body-overlay.png')
    Image.fromarray(overlay(image,masks,True,True)).save(routine/'body-band-reflections.png')
    Image.fromarray(overlay(image,baseline_masks)).save(routine/'color-only-overlay.png')
    save(out/'regions.json',report)
    save(out/'comparison.json',dict(dark_guided=report['counts'],color_only=baseline['counts'],
        same_domain=True,selected='Dark-valley watershed with local diffuse floor; no identity or coverage guarantee',
        differences='Color-only comparator uses distance-watershed and no seed-relative diffuse floor; seed/radius/retention/reflection rules otherwise identical'))
    font=ImageFont.truetype('DejaVuSans.ttf',18)
    whole=Image.new('RGB',(1800,805),'white'); draw=ImageDraw.Draw(whole)
    for j,(pixels,title) in enumerate([(image,'Raw photo'),(overlay(image,masks),'Retained pixels: green'),
                                       (overlay(image,masks,True,True),'Green body / orange rim / cyan reflections')]):
        whole.paste(Image.fromarray(pixels).resize((600,752),Image.Resampling.LANCZOS),(j*600,45))
        draw.text((j*600+5,10),title,fill='black',font=font)
    whole.save(out/'whole-review.png')
    chosen,center=choose_regions(report,image,masks)
    sheet=Image.new('RGB',(1260,1475),'white'); draw=ImageDraw.Draw(sheet)
    xy=np.asarray([r['retained_centroid_xy'] for r in report['records']]); angles=np.arctan2(xy[:,1]-center[1],xy[:,0]-center[0])
    context_records=[]
    for k,target in enumerate(np.linspace(-np.pi,np.pi,4,endpoint=False)+.3):
        index=np.abs((angles-target+np.pi)%(2*np.pi)-np.pi).argmin(); row=report['records'][index]
        x,y=np.rint(row['retained_centroid_xy']).astype(int); box=[int(x-70),int(y-55),int(x+70),int(y+55)]
        for j,pixels in enumerate([image,overlay(image,masks),overlay(image,masks,True,True)]):
            oy=40+k*355; sheet.paste(Image.fromarray(pixels).crop(box).resize((420,330),Image.Resampling.NEAREST),(j*420,oy))
            draw.text((j*420+4,oy-25),['Raw','Retained pixels','Retained/rim/reflections'][j],fill='black',font=font)
        context_records.append(dict(region_number=row['region_number'],crop=box))
    sheet.save(out/'contexts.png')
    # Favor an obvious compact bright reflection on a dark surround; no black
    # body outline or manually supplied ownership is needed for this question.
    reflections=[r for r in report['reflections'] if r['owner_region'] is None and r['peak_value']>.8 and
                 r['surround_value']<.25 and r['pixels']>=12 and r['xy'][1]>image.shape[0]/2]
    reflection=min(reflections,key=lambda r:r['threshold_position_sensitivity_pixels'])
    questions=Image.new('RGB',(840,1090),'white'); draw=ImageDraw.Draw(questions)
    entries=[]
    for k,row in enumerate(chosen):
        letter=['A','B'][k]; x,y=row['retained_centroid_xy']; box=[round(x)-70,round(y)-55,round(x)+70,round(y)+55]
        questions.paste(marked_raw(image,[x,y],letter,box),(0,40+k*355))
        pixels=overlay(image,masks,show_band=True,region=row['region_number'])
        questions.paste(Image.fromarray(pixels).crop(box).resize((420,330),Image.Resampling.NEAREST),(420,40+k*355))
        draw.text((4,10+k*355),f'{letter}: raw; automatic {row["display_color"]} region {row["region_number"]}',fill='black',font=font)
        draw.text((424,10+k*355),'Green retained / orange excluded rim',fill='black',font=font)
        entries.append(dict(letter=letter,region_number=row['region_number'],observation_id=row['observation_id'],
            retained_centroid_xy=row['retained_centroid_xy'],crop=box,
            retained_pixel_runs=encode_pixels(masks['retained']==row['region_number'],[0,0]),
            proposed_candidate_pixels=row['candidate_pixels'],retained_pixels=row['retained_pixels']))
    x,y=reflection['xy']; box=[round(x)-70,round(y)-55,round(x)+70,round(y)+55]
    questions.paste(marked_raw(image,[x,y],'R',box),(0,750))
    pixels=image.copy(); mask=masks['reflections']==reflection['reflection_number']; pixels[mask]=(pixels[mask]*.4+[0,153,153]).astype(np.uint8)
    questions.paste(Image.fromarray(pixels).crop(box).resize((420,330),Image.Resampling.NEAREST),(420,750))
    draw.text((4,720),'R: raw bright spot on dark surround',fill='black',font=font)
    draw.text((424,720),'Cyan: separate reflection pixels only',fill='black',font=font)
    questions.save(out/'questions.png')
    save(out/'review-locations.json',dict(automatic_contexts=context_records,question_regions=entries,
        question_reflection=reflection,reflection_crop=box,selection='Automatic post-extraction illustration selection only; no runtime spatial prior'))
    # Owner IDs are loaded only after both full-photo masks have been frozen.
    calibration=json.loads((routine/'calibration/report.json').read_text())
    fixture_payloads=[]
    for case in calibration:
        for suffix,key in [('.pov','appearance_scene_sha256'),('-ids.pov','ids_scene_sha256')]:
            source=ROOT/'photo2/output/r167/calibration'/(case['fixture']+suffix)
            target=out/'fixtures'/source.name; target.parent.mkdir(exist_ok=True)
            target.write_bytes(source.read_bytes()); case[key]=sha(source)
            fixture_payloads.append('fixtures/'+source.name)
        for suffix,key in [('.png','appearance_pixel_sha256'),('-ids.png','ids_pixel_sha256')]:
            pixels=np.asarray(Image.open(ROOT/'photo2/output/r167/calibration'/(case['fixture']+suffix)).convert('RGB'))
            case[key]=hashlib.sha256(pixels.tobytes()).hexdigest()
    extra=routine/'holdout/report.json'
    adverse=dict(initial_closed_axis_dependency='Removed: pixel extraction does not require successful curve/graph tracing',
        shared_background_hue='Rejected hue-nearest-background gate suppressed amber beads on brown paper; replaced with learned chromaticity score',
        integer_inset_ties='One-pixel distance rings discarded 20–30% of small faces; brightness/valley ranking now resolves those ties',
        unrefined_dark_candidate_extent='Diffuse/radius/connected-support guards precede defining the near-boundary band')
    if extra.exists():
        adverse['pre_border_tail_cap_regression']=json.loads(extra.read_text())
        adverse['regression_role']='Fourth camera/placement fixture clips beads at image border; old .999 border score contaminated threshold. Cap at existing 50-score Otsu range; evaluate final run separately.'
    save(out/'adverse-controls.json',adverse)
    save(out/'calibration.json',calibration)
    save(out/'specular-control.json',json.loads((routine/'specular-control/report.json').read_text()))
    question=dict(request='R215',photo_sha256=sha(photo),review_image='photo2/review/r215/questions.png',
        review_image_sha256=sha(out/'questions.png'),locations_sha256=sha(out/'review-locations.json'),
        questions=[dict(id='Q215.1',text='Do the green regions A and B capture roughly 70–90% of their red/yellow beads’ visible parts, staying inside their beads?',status='pending'),
                   dict(id='Q215.2',text='Does the cyan patch R mark the specular reflection itself, keeping the surrounding dark bead out of cyan?',status='pending')],
        confirmation_scope='Only the illustrated proposed pixel extents/appearance, not all-photo recall, complete boundaries, exact centers, bead indices or adjacency')
    save(ROOT/'photo2/segmentation-questions-r215.json',question)
    sources=['beads-photo-2.jpg','photo2/segment_colored_beads.py','photo2/review_colored_segmentation.py',
        'photo2/check_colored_segmentation.py','photo2/check_specular_pixels.py','photo2/test_colored_segmentation.py',
        'photo2/auto_label_beads.py','photo2/bead_evidence_inventory.py','photo2/pixel-coverage-scope-r215.json']
    payloads=['regions.json','comparison.json','whole-review.png','contexts.png','questions.png','review-locations.json','calibration.json','specular-control.json','adverse-controls.json']+fixture_payloads
    assert all(sha(ROOT/p)==digest for p,digest in protected.items())
    save(out/'summary.json',dict(request='R215',source_sha256={p:sha(ROOT/p) for p in sources},
        curated_sha256={p:sha(out/p) for p in payloads},protected_inputs=protected,question_manifest_sha256=sha(ROOT/'photo2/segmentation-questions-r215.json'),
        mask_archive_sha256=sha(routine/'pixel-masks.npz'),manual_labels_used=False,adjacency_computed=False,
        current_scope='Image-only visible pixels and separate specular masks; all placement fitting deferred',
        versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','Pillow','matplotlib','scikit-image']},
        reproduction=['.venv/bin/python photo2/check_colored_segmentation.py',
                      '.venv/bin/python photo2/check_colored_segmentation.py --extra-fixture hand+1-palette1-shift3',
                      '.venv/bin/python photo2/check_specular_pixels.py','.venv/bin/python photo2/review_colored_segmentation.py']))
    print(json.dumps(dict(counts=report['counts'],question_regions=[r['region_number'] for r in chosen],
                         question_reflection=reflection['reflection_number'])),flush=True)


if __name__=='__main__':
    main()
