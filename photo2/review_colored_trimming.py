"""R220: raw-first trimming review, exact question pixels and preservation seals."""
import argparse
import importlib.metadata
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

from auto_label_beads import ROOT, sha
from bead_evidence_inventory import encode_pixels
from refine_colored_masks import refine
from trim_colored_masks import trim
from review_colored_segmentation import overlay, marked_raw
from review_mask_refinement import save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/review/r220')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    prior_path = ROOT/'photo2/review/r218/summary.json'
    prior = json.loads(prior_path.read_text())
    for field in ('source_sha256', 'protected_inputs'):
        assert all(sha(ROOT/p)==v for p,v in prior[field].items())
    assert all(sha(ROOT/'photo2/review/r218'/p)==v for p,v in prior['curated_sha256'].items())
    photo = ROOT/'beads-photo-2.jpg'
    image = np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'))
    base = refine(image, sha(photo))
    report, arrays = trim(image, sha(photo), 'stable', base)
    # Verify the fresh baseline, without feeding prior photo masks into runtime.
    original = dict(np.load(ROOT/'photo2/output/r218/pixel-masks.npz'))
    assert all(np.array_equal(v, original[k]) for k,v in base[1].items())
    unchanged = ('candidate','domain','valley','family','reflections')
    assert all(np.array_equal(arrays[k], base[1][k]) for k in unchanged)
    assert report['reflections']==base[0]['reflections']
    assert not np.any((arrays['retained']>0)&(arrays['retained']!=base[1]['retained']))
    routine = ROOT/'photo2/output/r220'
    routine.mkdir(parents=True, exist_ok=True)
    save(routine/'regions.json', report)
    np.savez_compressed(routine/'pixel-masks.npz', **arrays)
    for key in ('candidate','retained','diffuse_retained','reflections','central_candidates'):
        Image.fromarray(arrays[key].astype(np.uint16)).save(routine/(key+'-labels.tiff'))
    for key in ('boundary_band','removed_source'):
        Image.fromarray(arrays[key].astype(np.uint8)*255).save(routine/(key+'.png'))
    Image.fromarray(overlay(image, arrays)).save(routine/'body-overlay.png')
    Image.fromarray(overlay(image, arrays, True, True)).save(routine/'body-band-reflections.png')
    central = dict(arrays, retained=arrays['central_candidates'])
    Image.fromarray(overlay(image, central)).save(routine/'central-candidates.png')
    base_central = dict(base[1], retained=base[1]['central_candidates'])
    font = ImageFont.truetype('DejaVuSans.ttf',18)
    whole = Image.new('RGB',(2400,805),'white')
    draw = ImageDraw.Draw(whole)
    displays = [(image,'Raw photo'),(overlay(image,base[1]),'R218: original proposals'),
                (overlay(image,arrays),'R220: trimmed proposals'),
                (overlay(image,central),'R220: stronger central proposals')]
    for j,(pixels,title) in enumerate(displays):
        whole.paste(Image.fromarray(pixels).resize((600,752),Image.Resampling.LANCZOS),(j*600,45))
        draw.text((j*600+5,10),title,fill='black',font=font)
    whole.save(out/'whole-review.png')
    # Diagnostic crops and maker facts are read only after all photo extraction.
    locations_path = ROOT/'photo2/review/r218/review-locations.json'
    locations = json.loads(locations_path.read_text())
    facts_path = ROOT/'photo2/review/r219/reviewed-mask-facts.json'
    facts = json.loads(facts_path.read_text())
    rows = {r['region_number']:r for r in report['records']}
    contexts = Image.new('RGB',(1680,1475),'white')
    draw = ImageDraw.Draw(contexts)
    context_displays = [(image,'Raw photo'),(overlay(image,base_central),'R218 central proposals'),
                        (overlay(image,central),'R220 central proposals'),
                        (overlay(image,arrays,True,True),'Body / omitted rim / reflections')]
    for k,location in enumerate(locations['automatic_contexts']):
        for j,(pixels,title) in enumerate(context_displays):
            contexts.paste(Image.fromarray(pixels).crop(location['crop']).resize((420,330),Image.Resampling.NEAREST),(j*420,40+k*355))
            draw.text((j*420+4,10+k*355),title,fill='black',font=font)
    contexts.save(out/'contexts.png')
    questions = Image.new('RGB',(1260,735),'white')
    draw = ImageDraw.Draw(questions)
    entries = []
    for k,loc in enumerate(locations['question_regions']):
        row = rows[loc['region_number']]
        letter, box = loc['letter'], loc['crop']
        questions.paste(marked_raw(image, loc['retained_centroid_xy'], letter, box),(0,40+k*355))
        for j,(mask,title) in enumerate(((base[1],'Original'),(arrays,'Revised')),1):
            pixels = overlay(image, mask, region=loc['region_number'])
            questions.paste(Image.fromarray(pixels).crop(box).resize((420,330),Image.Resampling.NEAREST),(j*420,40+k*355))
            count = loc['retained_pixels'] if j==1 else row['retained_pixels']
            draw.text((j*420+4,10+k*355),f'{title} green: {count} pixels',fill='black',font=font)
        draw.text((4,10+k*355),f'{letter}: raw {row["display_color"]}; automatic {row["region_number"]}',fill='black',font=font)
        old_fact = next(f for f in facts['facts'] if f['automatic_region_number']==loc['region_number'])
        entries.append(dict(question_id=f'Q220.{k+1}',letter=letter,region_number=row['region_number'],
            observation_id=row['observation_id'],source_observation_id=row['source_observation_id'],
            display_color=row['display_color'],crop=box,raw_arrow_xy=loc['retained_centroid_xy'],
            retained_centroid_xy=row['retained_centroid_xy'],retained_pixels=row['retained_pixels'],
            retained_pixel_runs=encode_pixels(arrays['retained']==row['region_number'],[0,0]),
            source_retained_pixels=loc['retained_pixels'],removed_source_pixels=row['removed_pixels'],
            retained_fraction_of_source_mask=row['retained_fraction_of_source_mask'],
            previous_rejection=old_fact['acceptance']['status'],
            status='Pending maker review of this revised extent; no old approval inherited'))
    questions.save(out/'questions.png')
    save(out/'review-locations.json', dict(photo_sha256=sha(photo),question_regions=entries,
        automatic_contexts=locations['automatic_contexts'],source_locations_sha256=sha(locations_path),
        selection='Frozen earlier automatic crops used only after extraction; no manual labels, centers or adjacency input'))
    # Positive facts are overlap checks, never an approval of changed extents.
    earlier_path = ROOT/'photo2/review/r215/confirmed-pixel-facts.json'
    earlier = json.loads(earlier_path.read_text())
    overlaps = []
    for region in earlier['confirmed_colored_regions']:
        values = []
        for y,lo,hi in region['retained_pixel_runs']:
            values.extend(arrays['retained'][y,lo:hi+1].tolist())
        ids,counts = np.unique(values,return_counts=True)
        overlaps.append(dict(source_region_number=region['region_number'],source_confirmed_pixels=len(values),
            retained_in_new_union=sum(v>0 for v in values),
            new_region_overlaps=[dict(region_number=int(i),pixels=int(n)) for i,n in zip(ids,counts)]))
    save(out/'prior-fact-check.json',dict(earlier_confirmation_sha256=sha(earlier_path),
        rejected_extent_fact_sha256=sha(facts_path),positive_pixel_overlaps=overlaps,
        unchanged_reflection_masks_and_positions=True,no_prior_approval_of_new_extents=True))
    calibration_path = routine/'calibration/report.json'
    save(out/'calibration.json',json.loads(calibration_path.read_text()))
    initial_path = routine/'calibration-initial/report.json'
    no_floor_path = routine/'calibration-no-raw-floor/report.json'
    save(out/'development-comparison.json',dict(
        earlier_stable_fixed_inset=[r for r in json.loads(initial_path.read_text()) if r['method']=='stable'],
        stable_rank_without_raw_floor=[r for r in json.loads(no_floor_path.read_text()) if r['method']=='stable'],
        adverse_failure='Blur-only stability admitted a dark extension in the known circular-face test; the raw diffuse floor removes it. Original pre-fix records retained.',
        role='Development snapshots; four existing scenes are not independent holdouts'))
    save(out/'regions.json',report)
    # Coarse display sectors are a coverage diagnostic, not torus arc lengths.
    points = np.asarray([r['retained_centroid_xy'] for r in report['records'] if r['central_candidate'] and r['retained_pixels']>0])
    center = points.mean(axis=0)
    angles = np.mod(np.arctan2(points[:,1]-center[1],points[:,0]-center[0]),2*np.pi)
    sector_counts = np.bincount((angles/(2*np.pi)*8).astype(int),minlength=8)
    save(out/'distribution.json',dict(display_center_xy=center.tolist(),clockwise_image_sectors=8,
        stronger_central_proposals_per_sector=sector_counts.tolist(),
        limitation='Image-angle occupancy only, not physical arc-length uniformity, confirmed distinct bodies or actual photo recall'))
    manifest = dict(request='R220',photo_sha256=sha(photo),review_image='photo2/review/r220/questions.png',
        review_image_sha256=sha(out/'questions.png'),locations_sha256=sha(out/'review-locations.json'),
        questions=[dict(id='Q220.1',text='Does revised green A retain roughly 70–90% of the red bead’s visible part while staying inside it, excluding the nearby black bead?',status='pending'),
                   dict(id='Q220.2',text='Does revised green B retain roughly 70–90% of the yellow bead’s visible part while staying inside it, excluding the adjacent yellow bead?',status='pending')],
        scope='Only revised illustrated masks; no whole-photo recall, exact centers, body identities, indices or adjacency')
    manifest_path = ROOT/'photo2/trimming-questions-r220.json'
    save(manifest_path,manifest)
    sources = ['beads-photo-2.jpg','photo2/trim_colored_masks.py','photo2/check_colored_trimming.py',
               'photo2/review_colored_trimming.py','photo2/test_colored_trimming.py',
               'photo2/refine_colored_masks.py','photo2/segment_colored_beads.py',
               'photo2/check_mask_refinement.py','photo2/review_colored_segmentation.py']
    payloads = ['regions.json','calibration.json','development-comparison.json','whole-review.png',
                'contexts.png','questions.png','review-locations.json','prior-fact-check.json','distribution.json']
    save(out/'summary.json',dict(request='R220',source_sha256={p:sha(ROOT/p) for p in sources},
        curated_sha256={p:sha(out/p) for p in payloads},protected_inputs=prior['protected_inputs'],
        prior_extraction_summary_sha256=sha(prior_path),prior_reply_sha256=sha(ROOT/'photo2/mask-refinement-answer-r219.json'),
        prior_rejected_facts_sha256=sha(facts_path),question_manifest_sha256=sha(manifest_path),
        mask_archive_sha256=sha(routine/'pixel-masks.npz'),
        versions={p:importlib.metadata.version(p) for p in ('numpy','scipy','Pillow','matplotlib','scikit-image')},
        selected_method='Brightness stability, raw diffuse floor, seed connectivity and weakest 15% candidate rim ranking',
        reflections_and_candidate_associations_unchanged=True,prior_photo_arrays_repeat_exactly=True,
        manual_labels_used=False,adjacency_computed=False,placement_fit_performed=False,all_photo_masks_confirmed=False,
        reproduction=['.venv/bin/python photo2/check_colored_trimming.py --stable-rim-rule inset --no-stable-raw-floor --output photo2/output/r220/calibration-initial',
            '.venv/bin/python photo2/check_colored_trimming.py --no-stable-raw-floor --output photo2/output/r220/calibration-no-raw-floor',
            '.venv/bin/python photo2/check_colored_trimming.py','.venv/bin/python photo2/trim_colored_masks.py',
            '.venv/bin/python photo2/review_colored_trimming.py',
            '.venv/bin/python -m unittest discover -s photo2 -p test_colored_trimming.py']))
    print(json.dumps(dict(counts=report['counts'],questions=[dict(question_id=r['question_id'],region_number=r['region_number'],retained_pixels=r['retained_pixels']) for r in entries],display_sector_counts=sector_counts.tolist())),flush=True)


if __name__ == '__main__':
    main()
