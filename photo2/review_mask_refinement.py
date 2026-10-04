"""R218 raw-first diffuse-core review, frozen question pixels and provenance."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
from auto_label_beads import ROOT,sha
from bead_evidence_inventory import encode_pixels
from segment_colored_beads import segment
from refine_colored_masks import refine
from review_colored_segmentation import overlay,marked_raw


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def select_examples(report,base,arrays):
    examples=[]
    for color in ['red','yellow']:
        choices=[]
        for row in report['records']:
            if row['display_color']!=color or not row['central_candidate'] or row['retained_components']!=1:continue
            area=row['retained_pixels'];d=report['parameters']['native_diameter']
            if not .45*d*d<area<1.10*d*d or row['seed_clearance_diameters']<.95:continue
            if row['seed_diffuse_brightness']<.75:continue
            mask=arrays['retained']==row['region_number']
            old_fraction=float(np.mean(base['retained'][mask]>0))
            # Post-extraction review selection; these coordinates never feed
            # extraction or confidence gating. Favor newly recovered clear faces.
            choices.append((old_fraction,row['region_number'],row))
        _,_,row=min(choices,key=lambda p:(p[0],p[1]))
        examples.append(row)
    return examples


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r218')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    prior=json.loads((ROOT/'photo2/review/r215/summary.json').read_text())
    for field in ['source_sha256','protected_inputs']:
        assert all(sha(ROOT/p)==v for p,v in prior[field].items())
    assert all(sha(ROOT/'photo2/review/r215'/p)==v for p,v in prior['curated_sha256'].items())
    photo=ROOT/'beads-photo-2.jpg';image=np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'))
    base_report,base=segment(image,sha(photo))
    report,arrays=refine(image,sha(photo),method='reseed',base=(base_report,base))
    assert np.array_equal(base['reflections'],arrays['reflections'])
    routine=ROOT/'photo2/output/r218';routine.mkdir(parents=True,exist_ok=True)
    save(routine/'regions.json',report);np.savez_compressed(routine/'pixel-masks.npz',**arrays)
    for key in ['candidate','retained','diffuse_retained','reflections','central_candidates']:
        Image.fromarray(arrays[key].astype(np.uint16)).save(routine/(key+'-labels.tiff'))
    Image.fromarray(arrays['boundary_band'].astype(np.uint8)*255).save(routine/'boundary-band.png')
    Image.fromarray(overlay(image,arrays)).save(routine/'body-overlay.png')
    Image.fromarray(overlay(image,arrays,True,True)).save(routine/'body-band-reflections.png')
    central=dict(arrays,retained=arrays['central_candidates'])
    Image.fromarray(overlay(image,central)).save(routine/'central-candidates.png')
    font=ImageFont.truetype('DejaVuSans.ttf',18)
    whole=Image.new('RGB',(2400,805),'white');draw=ImageDraw.Draw(whole)
    displays=[(image,'Raw photo'),(overlay(image,base),'R215 regions'),
              (overlay(image,arrays),'R218: all region proposals'),
              (overlay(image,central),'R218: stronger central candidates')]
    for j,(pixels,title) in enumerate(displays):
        whole.paste(Image.fromarray(pixels).resize((600,752),Image.Resampling.LANCZOS),(j*600,45))
        draw.text((j*600+5,10),title,fill='black',font=font)
    whole.save(out/'whole-review.png')
    # Reuse automatically selected earlier contexts only as a fixed diagnostic
    # comparison after both full-photo extractions finish. No maker bead labels.
    locations=json.loads((ROOT/'photo2/review/r215/review-locations.json').read_text())
    contexts=Image.new('RGB',(1680,1475),'white');draw=ImageDraw.Draw(contexts)
    for k,location in enumerate(locations['automatic_contexts']):
        for j,(pixels,title) in enumerate(displays):
            contexts.paste(Image.fromarray(pixels).crop(location['crop']).resize((420,330),Image.Resampling.NEAREST),(j*420,40+k*355))
            draw.text((j*420+4,10+k*355),title,fill='black',font=font)
    contexts.save(out/'contexts.png')
    examples=select_examples(report,base,arrays)
    questions=Image.new('RGB',(840,735),'white');draw=ImageDraw.Draw(questions);entries=[]
    for k,row in enumerate(examples):
        letter=['A','B'][k];x,y=row['retained_centroid_xy'];box=[round(x)-70,round(y)-55,round(x)+70,round(y)+55]
        questions.paste(marked_raw(image,[x,y],letter,box),(0,40+k*355))
        pixels=overlay(image,arrays,show_band=True,region=row['region_number'])
        questions.paste(Image.fromarray(pixels).crop(box).resize((420,330),Image.Resampling.NEAREST),(420,40+k*355))
        draw.text((4,10+k*355),f'{letter}: raw {row["display_color"]}; region {row["region_number"]}',fill='black',font=font)
        draw.text((424,10+k*355),'Green retained / orange excluded rim',fill='black',font=font)
        mask=arrays['retained']==row['region_number']; old_ids,n=np.unique(base['retained'][mask],return_counts=True)
        entries.append(dict(letter=letter,region_number=row['region_number'],observation_id=row['observation_id'],
            display_color=row['display_color'],retained_centroid_xy=row['retained_centroid_xy'],crop=box,
            retained_pixels=row['retained_pixels'],candidate_pixels=row['candidate_pixels'],
            retained_pixel_runs=encode_pixels(mask,[0,0]),
            previous_mask_pixel_fraction=float(np.mean(base['retained'][mask]>0)),
            previous_automatic_region_overlaps=[dict(region_number=int(i),pixels=int(k)) for i,k in zip(old_ids,n)],
            status='Pending maker review of extent only'))
    questions.save(out/'questions.png')
    save(out/'review-locations.json',dict(photo_sha256=sha(photo),question_regions=entries,
        automatic_contexts=locations['automatic_contexts'],selection='Post-extraction illustration selection only; never runtime priors'))
    # Newly confirmed R215 masks are validation records only, checked after
    # extraction; manual bead/adjacency datasets are never opened.
    confirmed=json.loads((ROOT/'photo2/review/r215/confirmed-pixel-facts.json').read_text())
    validation=[]
    for region in confirmed['confirmed_colored_regions']:
        pixels=[]
        for y,lo,hi in region['retained_pixel_runs']:pixels.extend(arrays['retained'][y,lo:hi+1].tolist())
        ids,n=np.unique(pixels,return_counts=True)
        validation.append(dict(old_letter=region['letter'],old_automatic_region=region['region_number'],
            confirmed_pixels=len(pixels),retained_in_new_union=sum(v>0 for v in pixels),
            new_region_overlaps=[dict(region_number=int(i),pixels=int(k)) for i,k in zip(ids,n)],
            limitation='Only overlap of old confirmed pixels; does not confirm expanded/new masks or centers'))
    r=confirmed['confirmed_reflection'];reflection_verified=all(np.all(arrays['reflections'][y,lo:hi+1]==r['reflection_number']) for y,lo,hi in r['pixel_runs'])
    assert reflection_verified
    save(out/'prior-confirmation-check.json',dict(previous_fact_sha256=sha(ROOT/'photo2/review/r215/confirmed-pixel-facts.json'),
        colored_mask_overlaps=validation,reflection28_pixels_unchanged=True,
        maker_confirmations_not_promoted_to_new_extents=True))
    # All truth/evaluation data is read after complete photo extraction.
    calibration=json.loads((routine/'calibration-final/report.json').read_text())
    save(out/'calibration.json',calibration)
    earlier=json.loads((routine/'probe/hue-biased/report.json').read_text())
    neutral_holes=json.loads((routine/'probe/neutral-holes/report.json').read_text())
    save(out/'development-comparison.json',dict(absolute_hue_error_cost=earlier,neutral_highlight_hue_holes=neutral_holes,
        limitation='Earlier hue-weight .15 and no-neutral-support runs used during development; final zero-weight/support-restored run is in calibration.json. No independent holdout claim.'))
    save(out/'regions.json',report)
    manifest=dict(request='R218',photo_sha256=sha(photo),review_image='photo2/review/r218/questions.png',
        review_image_sha256=sha(out/'questions.png'),locations_sha256=sha(out/'review-locations.json'),
        questions=[dict(id='Q218.1',text='Does green A cover roughly 70–90% of this red bead’s visible part and stay inside that one bead?',status='pending'),
                   dict(id='Q218.2',text='Does green B cover roughly 70–90% of this yellow bead’s visible part and stay inside that one bead?',status='pending')],
        scope='Illustrated mask extents only; not all-photo recall, exact centers, string indices or adjacency')
    manifest_path=ROOT/'photo2/mask-refinement-questions-r218.json';save(manifest_path,manifest)
    sources=['beads-photo-2.jpg','photo2/refine_colored_masks.py','photo2/check_mask_refinement.py',
        'photo2/review_mask_refinement.py','photo2/test_mask_refinement.py','photo2/segment_colored_beads.py',
        'photo2/auto_label_beads.py','photo2/bead_evidence_inventory.py','photo2/check_colored_segmentation.py',
        'photo2/review_colored_segmentation.py']
    payloads=['regions.json','calibration.json','development-comparison.json','whole-review.png','contexts.png',
        'questions.png','review-locations.json','prior-confirmation-check.json']
    assert all(sha(ROOT/p)==v for p,v in prior['protected_inputs'].items())
    save(out/'summary.json',dict(request='R218',source_sha256={p:sha(ROOT/p) for p in sources},
        curated_sha256={p:sha(out/p) for p in payloads},protected_inputs=prior['protected_inputs'],
        previous_extraction_summary_sha256=sha(ROOT/'photo2/review/r215/summary.json'),
        previous_answer_summary_sha256=sha(ROOT/'photo2/review/r215/answer-curation-summary.json'),
        development_reproduction=[
            '.venv/bin/python photo2/check_mask_refinement.py --hue-weight .15 --no-neutral-support --output photo2/output/r218/probe/hue-biased',
            '.venv/bin/python photo2/check_mask_refinement.py --no-neutral-support --output photo2/output/r218/probe/neutral-holes'],
        question_manifest_sha256=sha(manifest_path),mask_archive_sha256=sha(routine/'pixel-masks.npz'),
        versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','Pillow','matplotlib','scikit-image']},
        selected_method='Diffuse reseeding, zero absolute hue-error boundary cost',
        manual_labels_used=False,adjacency_computed=False,placement_fit_performed=False,
        reflection_pixel_mask_unchanged=True,all_photo_masks_confirmed=False,
        reproduction=['.venv/bin/python photo2/check_mask_refinement.py --output photo2/output/r218/calibration-final',
            '.venv/bin/python photo2/refine_colored_masks.py','.venv/bin/python photo2/review_mask_refinement.py',
            '.venv/bin/python -m unittest discover -s photo2 -p test_mask_refinement.py']))
    print(json.dumps(dict(counts=report['counts'],question_regions=[dict(letter=r['letter'],region_number=r['region_number'],xy=r['retained_centroid_xy']) for r in entries])),flush=True)


if __name__=='__main__':main()
