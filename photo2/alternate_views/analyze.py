"""Analyze the two alternate photographs in native, EXIF-oriented coordinates."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy.interpolate import CubicSpline
from scipy.ndimage import gaussian_filter1d, map_coordinates

from photo2.bead_debugger.vendor.historical_splines import _resample_closed_curve
from photo2.fft_explorer_core import rgb_to_hsv_np
from .registration import PREFIX, WEAK, load_paths, locate, probes, probe_sheet

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Visually traced axes in a 510-pixel-wide preview. Start near the top, clockwise.
VIEWS = {
    "wood": ("bead-example-5.jpg", [
        (250,80),(294,89),(336,109),(367,150),(391,201),(406,250),
        (420,293),(430,351),(422,402),(397,450),(370,496),(310,527),
        (251,548),(208,547),(162,522),(130,488),(117,449),(110,401),
        (102,349),(99,298),(99,251),(106,202),(124,155),(151,116),(195,89)]),
    "plastic": ("beads-photo-2-wb.jpg", [
        (250,107),(300,114),(349,134),(392,164),(422,205),(440,252),
        (458,300),(467,354),(459,396),(438,435),(403,480),(359,511),
        (306,528),(246,535),(203,528),(153,503),(121,482),(90,447),
        (60,401),(55,353),(59,300),(73,250),(91,207),(116,178),
        (150,148),(196,119)])
}


def normals(axis):
    tangent = np.roll(axis,-1,axis=0) - np.roll(axis,1,axis=0)
    tangent /= np.linalg.norm(tangent,axis=1)[:,None]
    return np.column_stack((-tangent[:,1], tangent[:,0]))


def sample(rgb, axis, offsets):
    xy = axis[None,:,:] + offsets[:,None,None]*normals(axis)
    return np.stack([map_coordinates(channel, [xy[:,:,1],xy[:,:,0]], order=1)
                     for channel in rgb.transpose(2,0,1)], axis=-1)


def unwrap(rgb, knots):
    points = np.asarray(knots) * rgb.shape[1]/510
    points = np.vstack((points, points[0]))
    distance = np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    spline = CubicSpline(distance,points,bc_type='periodic')
    dense = spline(np.linspace(0,distance[-1],2001))
    count = round(np.linalg.norm(np.diff(dense,axis=0),axis=1).sum())
    axis = _resample_closed_curve(dense,count)[:-1]
    # Center the texture band within the hand-traced search corridor. The
    # slowly varying correction cannot follow individual bead bodies.
    offsets = np.arange(-65,66)
    band = sample(rgb,axis,offsets).astype(float)
    texture = abs(band-np.roll(band,3,axis=1)).mean(axis=2)
    weight = gaussian_filter1d(texture,32,axis=1,mode='wrap')
    weight += .01
    shift = (offsets[:, None] * weight).sum(axis=0) / weight.sum(axis=0)
    axis += gaussian_filter1d(shift,45,mode='wrap')[:,None]*normals(axis)
    axis = _resample_closed_curve(axis,count)[:-1]
    return axis, sample(rgb,axis,np.arange(-66,67))


def save_strip(strip, name):
    piece = Image.fromarray(strip)
    width = piece.width
    overview = Image.new('RGB',(1110,4*115),'white')
    draw = ImageDraw.Draw(overview)
    for j in range(4):
        lo,hi = j*width//4,(j+1)*width//4
        crop = piece.crop((lo,0,hi,piece.height)).resize((1100,78),Image.Resampling.LANCZOS)
        overview.paste(crop,(5,j*115+22))
        draw.text((5,j*115+3),f'{name}   |   clockwise from {25*j}% to {25*(j+1)}%',fill='black')
    overview.save(HERE/f'{name}-loop.jpg',quality=94)


def color_spectrum(strip):
    h,s,v = rgb_to_hsv_np(strip.astype(float)/255)
    # Chroma-weighted warm-color contrast; never used to label a bead.
    result = []
    for half_width in (15,25,35):
        band = slice(66-half_width,67+half_width)
        for split in (15,20,25):
            amber = (360*h>split) & (360*h<65)
            signal = (s*v*np.where(amber,1,-1))[band].mean(axis=0)
            power = abs(np.fft.rfft(signal-signal.mean()))**2
            order = 1+np.argsort(power[1:81])[::-1]
            result.append(dict(half_width_px=half_width,hue_split_degrees=split,
                               strongest_cycles=order[:3].tolist()))
    return result


def save_path_sheet(view, strip, paths):
    sheet = Image.new('RGB',(928,4*305),'white')
    draw = ImageDraw.Draw(sheet)
    for q in range(4):
        origin = q*strip.shape[1]//4
        crop = Image.fromarray(strip[:,origin:origin+450]).resize((900,266))
        layer = ImageDraw.Draw(crop)
        for site,(x,y,color) in enumerate(paths[view,q],1):
            ink = 'cyan' if site<=PREFIX else '#ffed83'
            layer.ellipse((2*x-6,2*y-6,2*x+6,2*y+6),outline=ink,width=2)
            layer.text((2*x-10,2*y-25),str(site),fill=ink,stroke_width=1,stroke_fill='black')
        draw.text((10,q*305+4),f'{view}  |  quarter {q}  |  cyan: location input    yellow: prediction check',fill='black')
        sheet.paste(crop,(10,q*305+25))
    sheet.save(HERE/f'{view}-paths.jpg',quality=96)


def source_xy(axis, normal, q, x, y):
    station = q*len(axis)//4+x
    point = axis[station]+(y-66)*normal[station]
    return [round(float(value),2) for value in point]


def write_csv(path, rows):
    with path.open('w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def save_witnesses(path_rows):
    """Show the two chromatic half-repeat witnesses in unwarped native pixels."""
    sheet = Image.new('RGB', (720, 370), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, (view, quarter, first) in enumerate([('wood', 3, 7), ('plastic', 1, 2)]):
        rows = [r for r in path_rows if r['view'] == view and r['quarter'] == quarter]
        with Image.open(ROOT / VIEWS[view][0]) as raw:
            source = ImageOps.exif_transpose(raw).convert('RGB')
        for col, row in enumerate([rows[first - 1], rows[first + 15]]):
            x, y = round(row['native_x']), round(row['native_y'])
            crop = source.crop((x-52, y-36, x+52, y+36)).resize((208, 144))
            mark = ImageDraw.Draw(crop)
            mark.ellipse((96, 64, 112, 80), outline='cyan', width=2)
            left, top = 14 + 350*col, 185*i
            sheet.paste(crop, (left, top+30))
            color = {'R':'red', 'Y':'yellow'}[row['observed']]
            draw.text((left, top+9), f"{view}   |   site {row['site']}   |   {color}   |   ({x}, {y})", fill='black')
    sheet.save(HERE / '104-step-pairs.jpg', quality=97)


def score_path(view, q, points, fits, axis, normal):
    obs = ''.join(p[2] for p in points)
    full, = fits['full']
    masked, = fits['masked_shared']
    if full['positions']!=masked['positions']:
        raise ValueError('Full and masked registrations disagree')
    rows = []
    for j,((x,y,color),k) in enumerate(zip(points,masked['positions'])):
        native_x,native_y = source_xy(axis,normal,q,x,y)
        calls = {f['prediction'][j] for f in fits['prefix_shared']}
        rows.append(dict(view=view,quarter=q,site=j+1,native_x=native_x,native_y=native_y,
                         observed=color,residue=k,chart_color=full['prediction'][j],
                         prefix_prediction=('' if j<PREFIX else ''.join(sorted(calls)))))
    witnesses = []
    for j in range(len(obs)-16):
        segment = np.diff([p[1] for p in points[j:j+17]])
        if np.sum(segment>0)==8 and obs[j]!=obs[j+16] and '?' not in (obs[j],obs[j+16]):
            witnesses.append([j+1,j+17,obs[j],obs[j+16]])
    summary = dict(phase=masked['phase'],down_up_steps=masked['orientation'],
                   prefix_fits=len(fits['prefix']),prefix_shared_fits=len(fits['prefix_shared']),
                   masked_fits=len(fits['masked']),masked_shared_fits=len(fits['masked_shared']),
                   full_fits=len(fits['full']),prefix_sites=PREFIX,period104_witnesses=witnesses,
                   full_readable=sum(c!='?' for c in obs),
                   full_agree=sum(c==p for c,p in zip(obs,full['prediction'])))
    return rows,summary


def main():
    word_file = HERE.parent/'r344/provisional-sequence.txt'
    word = word_file.read_text().strip()
    paths = load_paths()
    groups = locate(paths,word)
    axes, normal, strips = {}, {}, {}
    result = dict(chart_sha256=hashlib.sha256(word_file.read_bytes()).hexdigest(),views={})
    path_rows = []
    for view,(filename,knots) in VIEWS.items():
        path = ROOT/filename
        rgb = np.array(ImageOps.exif_transpose(Image.open(path)).convert('RGB'))
        axis,strip = unwrap(rgb,knots)
        axes[view],normal[view],strips[view] = axis,normals(axis),strip
        save_strip(strip,view)
        save_path_sheet(view,strip,paths)
        stats = dict(filename=filename,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     native_size=list(rgb.shape[1::-1]),stations=len(axis),
                     spectrum=color_spectrum(strip),quarters={})
        for q in range(4):
            rows,stats['quarters'][q] = score_path(view,q,paths[view,q],groups[view,q],axis,normal[view])
            path_rows.extend(rows)
        result['views'][view] = stats

    queue = probes(paths,groups)
    probe_sheet(queue,strips,HERE/'neighbor-review.jpg')
    with (HERE/'neighbor-readings.csv').open() as f:
        readings = list(csv.DictReader(f))
    neighbor_rows = []
    for number,(r,reading) in enumerate(zip(queue,readings,strict=True),1):
        if int(reading['number'])!=number or any(str(r[k])!=reading[k] for k in ('view','quarter','site','offset')):
            raise ValueError('A queued photograph has changed relative to its reading')
        v = r['view']
        x,y = source_xy(axes[v],normal[v],r['quarter'],r['x'],r['y'])
        k = r['residue']
        neighbor_rows.append(dict(**reading,native_x=x,native_y=y,residue=k,chart_color=word[k],
                                  group='target' if k in WEAK else 'control'))
    write_csv(HERE/'path-results.csv',path_rows)
    write_csv(HERE/'neighbor-results.csv',neighbor_rows)
    save_witnesses(path_rows)
    (HERE/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
