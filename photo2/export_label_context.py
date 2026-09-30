"""Export a larger raw crop and portable translated labels, preserving identity.

The preferred in-repo workflow keeps original coordinates and widens --crop.
This portable pair is for viewing/labeling independently of the original JPEG.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from label_beads import LabelStore,validate_annotations,validate_series

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations',type=Path,default=ROOT/'photo2/manual-labels-r161.json')
    parser.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    parser.add_argument('--crop',type=int,nargs=4,default=[900,0,1900,700])
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r164')
    args=parser.parse_args();doc=json.loads(args.annotations.read_text());source=sha(args.image)
    assert source==doc['source']['sha256'],'Labels must match the source photo'
    rgb=ImageOps.exif_transpose(Image.open(args.image)).convert('RGB')
    assert list(rgb.size)==doc['source']['oriented_size']
    x0,y0,x1,y1=args.crop;ox0,oy0,ox1,oy1=doc['view_crop']
    assert 0<=x0<=ox0<ox1<=x1<=rgb.width and 0<=y0<=oy0<oy1<=y1<=rgb.height,'New crop must contain the saved view'
    # Refuse a crop that would discard any saved point.
    assert all(x0<=a['x']<x1 and y0<=a['y']<y1 for a in doc['annotations'])
    args.output.mkdir(parents=True,exist_ok=True)
    image=args.output/'wider-photo.png';rgb.crop(args.crop).save(image)
    exported=json.loads(json.dumps(doc))
    exported['source']=dict(filename=image.name,sha256=sha(image),oriented_size=[x1-x0,y1-y0],
        coordinates=doc['source']['coordinates'])
    exported['view_crop']=[0,0,x1-x0,y1-y0]
    for point in exported['annotations']:point['x']-=x0;point['y']-=y0
    validate_annotations(exported['annotations'],exported['source']['oriented_size'])
    validate_series(exported['series'],exported['annotations'])
    labels=args.output/'wider-labels.json';labels.write_text(json.dumps(exported,indent=2)+'\n')
    assert np.array_equal(np.array(Image.open(image)),np.array(rgb.crop(args.crop)))
    store=LabelStore(image,None,labels);loaded=store.read()
    assert loaded['annotations']==exported['annotations'] and loaded['series']==doc['series']
    for old,new in zip(doc['annotations'],loaded['annotations']):
        assert old['id']==new['id'] and old['number']==new['number']
        assert old['x']==new['x']+x0 and old['y']==new['y']+y0
        assert old['label_dx']==new['label_dx'] and old['label_dy']==new['label_dy']
    # Check the recommended original-coordinate workflow with the actual loader,
    # without starting a server or writing to the user's live file.
    original=LabelStore(args.image,args.crop,args.annotations).read()
    assert original['annotations']==doc['annotations'] and original['series']==doc['series']
    manifest=dict(source_sha256=source,input_labels_sha256=sha(args.annotations),
        exporter_sha256=sha(Path(__file__)),crop_in_original_source=args.crop,
        image_sha256=sha(image),labels_sha256=sha(labels),revision=doc['revision'],
        bead_count=len(doc['annotations']),series_count=len(doc['series']),
        coordinates='Portable x/y = original x/y minus crop left/top; IDs, numbers, offsets and series unchanged',
        inverse_transform=dict(add_x=x0,add_y=y0),
        verified=dict(raw_pixels_identical=True,all_markers_and_series_preserved=True,
            original_positions_recover_exactly=True,real_label_store_loads_both_workflows=True),
        preferred_command='.venv/bin/python photo2/label_beads.py --crop 900 0 1900 700 --port 0',
        portable_command='.venv/bin/python photo2/label_beads.py --image photo2/review/r164/wider-photo.png --annotations photo2/output/labeler-wider/annotations.json --port 0')
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
