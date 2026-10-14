"""Photo-only remeasurement, native support alternatives and fresh band maxima.

Inputs: photograph, preserved image-only proposals, unregistered image centerline.
No physical model, indices, pattern or historical fitted pose is imported/read.
"""
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.color import rgb2hsv
from skimage.morphology import convex_hull_image, disk
from .common import ROOT, OUT, photo, read, save, sha, record, support, pixels, circular_distance, validate

BASELINE = ROOT/'photo2/review/r278/phase1-inventory.json.gz'
CENTERLINE = ROOT/'photo2/review/r255/spline-samples.csv'
CAP = 870
SELECTED = 'C'


def image_features(rgb):
    a = rgb.astype(np.float32)/255
    hsv = rgb2hsv(a)
    linear = np.where(a <= .04045, a/12.92, ((a+.055)/1.055)**2.4)
    lum = linear@np.array([.2126, .7152, .0722], np.float32)
    border = np.concatenate((hsv[:24].reshape(-1, 3), hsv[-24:].reshape(-1, 3),
                              hsv[:, :24].reshape(-1, 3), hsv[:, -24:].reshape(-1, 3)))
    angle = np.angle(np.mean(np.exp(2j*np.pi*border[border[:, 1]>.2, 0])))
    background_hue = float(np.degrees(angle) % 360)
    paper = (circular_distance(hsv[:, :, 0]*360, background_hue)<22)&(hsv[:, :, 1]>.18)
    sample = hsv[::6, ::6]; usable = (~paper[::6, ::6])&(sample[:, :, 1]>.35)&(sample[:, :, 2]>.2)
    hues = sample[:, :, 0][usable]*360
    hist, _ = np.histogram(hues, np.arange(361)); hist = ndi.gaussian_filter1d(hist.astype(float), 2, mode='wrap')
    first = int(hist.argmax()); allowed = circular_distance(np.arange(360), first)>18
    second = int(np.where(allowed, hist, -1).argmax())
    peaks = sorted([first, second], key=lambda h: circular_distance(h, 0))
    palette = {'red': peaks[0], 'yellow': peaks[1]}
    return dict(hsv=hsv, lum=lum, paper=paper, mean5=ndi.uniform_filter(lum, 5),
                palette=palette, background_hue=background_hue)


def component(mask, point):
    labels, count = ndi.label(mask)
    if not count: return np.zeros_like(mask)
    x, y = np.rint(point).astype(int)
    if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and labels[y, x]: k = labels[y, x]
    else:
        yy, xx = np.where(mask); j = np.argmin((xx-x)**2+(yy-y)**2)
        if (xx[j]-x)**2+(yy[j]-y)**2 > 36: return np.zeros_like(mask)
        k = labels[yy[j], xx[j]]
    return labels == k


def shape_metrics(mask):
    yy, xx = np.where(mask)
    if not len(xx): return dict(area=0, components=0, solidity=0., neck_retention=0., compactness=0., radius=0.)
    hull = convex_hull_image(mask)
    distance = ndi.distance_transform_edt(mask)
    opened = ndi.binary_opening(mask, structure=disk(2))
    labels, _ = ndi.label(opened)
    counts = np.bincount(labels.ravel()); counts[0] = 0
    edge = mask&~ndi.binary_erosion(mask)
    return dict(area=int(mask.sum()), components=int(ndi.label(mask)[1]),
                solidity=float(mask.sum()/max(1, hull.sum())),
                neck_retention=float(counts.max()/max(1, mask.sum())),
                compactness=float(4*np.pi*mask.sum()/max(1, edge.sum())**2),
                radius=float(distance.max()))


def attempts(features, xy, previous_color=None):
    x, y = map(int, np.rint(xy)); radius = 24
    hs0, lum0, paper0 = (features[k] for k in ('hsv', 'lum', 'paper'))
    if min(x, y, lum0.shape[1]-1-x, lum0.shape[0]-1-y)<radius: return []
    origin = np.array([x-radius, y-radius]); sl = np.s_[y-radius:y+radius+1, x-radius:x+radius+1]
    hs, lum, paper = hs0[sl], lum0[sl], paper0[sl]
    yy, xx = np.indices(lum.shape); dist = np.hypot(xx-radius, yy-radius)
    central = dist<=4; chromatic = central&(hs[:, :, 1]>.35)&(lum>.025)&~paper
    if chromatic.sum() >= 10:
        hue = float(np.angle(np.mean(np.exp(2j*np.pi*hs[:, :, 0][chromatic])))*180/np.pi % 360)
        differences = sorted((float(circular_distance(hue, h)), name) for name, h in features['palette'].items())
        color = differences[0][1] if differences[0][0]<35 else 'unknown'
    else: color, hue = 'black', None
    # Color labels on inherited proposals are metadata only; pixels determine the branch.
    peak = float(lum[central].max()); results = []
    for method in ('A', 'B', 'C'):
        reasons = []
        if color in ('red', 'yellow'):
            other = features['palette']['yellow' if color == 'red' else 'red']
            own = circular_distance(hs[:, :, 0]*360, hue)
            rival = circular_distance(hs[:, :, 0]*360, other)
            material = (hs[:, :, 1]>.27)&(own<25)&(rival-own>2)&(lum>max(.012, peak*.10))&~paper
            # Neutral bright pixels may continue only an adjacent observed pigment region.
            highlights = (hs[:, :, 1]<.35)&(lum>max(.06, peak*.5))&(dist<8)
            material |= highlights&(ndi.distance_transform_edt(~material)<=3)
            domain = material&(dist<23)
            if method == 'B': domain &= (dist<=12)&(lum>max(.025, peak*.22))
            if method == 'C': domain &= (dist<=17)&((own<19)|highlights)
            mask = component(domain, [radius, radius])
            if method == 'C':
                opened = ndi.binary_opening(mask, structure=disk(2))
                mask = component(opened, [radius, radius])
                # Keep a supported inset: no convex fill or inferred edge pixels.
                mask = ndi.binary_erosion(mask, iterations=1)
                mask = component(mask, [radius, radius])
            dark_fraction = 0.; enclosure = None
        else:
            # Dark-body support and neutral reflection ownership, not a hue-mask darkening.
            neutral = hs[:, :, 1]<.55
            dark = (lum<min(.16, max(.045, peak*.30)))&neutral&~paper
            reflection = (lum>=max(.055, peak*.32))&neutral&(dist<=7)&~paper
            domain = (dark|reflection)&~paper
            if method == 'A': domain &= dist<=20
            elif method == 'B': domain &= dist<=9
            else: domain &= dist<=12
            mask = component(domain, [radius, radius])
            if method == 'C':
                mask = ndi.binary_opening(mask, structure=disk(1))
                mask = component(mask, [radius, radius])
                mask = ndi.binary_erosion(mask, iterations=1)
            dark_fraction = float(dark[mask].mean()) if mask.any() else 0.
            angle = (np.arctan2(yy-radius, xx-radius)+2*np.pi)%(2*np.pi)
            ring = (dist>=7)&(dist<=13)
            sectors = [float(dark[ring&(angle>=k*np.pi/4)&(angle<(k+1)*np.pi/4)].mean()) for k in range(8)]
            enclosure = sum(v>=.35 for v in sectors)/8
            if not reflection.any(): reasons.append('no-owned-neutral-reflection')
            if dark_fraction<.45: reasons.append('weak-dark-body-coherence')
            if enclosure<.625: reasons.append('dark-enclosure-incomplete')
        pre_area = int(mask.sum())
        if pre_area>CAP: reasons.append('native-size-cap')
        metrics = shape_metrics(mask)
        if pre_area<12: reasons.append('too-small-or-no-connected-support')
        if method == 'A' and (mask&(dist>=19 if color == 'black' else dist>=22)).any(): reasons.append('support-reaches-search-boundary')
        if metrics['solidity']<.82: reasons.append('irregular-or-concave-support')
        if metrics['neck_retention']<.65: reasons.append('thin-or-necked-support')
        if color=='unknown': reasons.append('unresolved-material')
        pts = np.c_[xx[mask], yy[mask]]+origin
        mean_lum = float(lum[mask].mean()) if mask.any() else 0.
        brightness = float(features['mean5'][y, x])
        if color!='black' and mean_lum<.035: reasons.append('poor-illumination')
        if color=='black' and peak<.16: reasons.append('weak-reflection')
        reliability = .96
        if pre_area<40: reliability -= .20
        if reasons: reliability = max(.15, .65-.08*len(reasons))
        if previous_color is not None and previous_color!=color: reliability=min(reliability,.6); reasons.append('color-branch-disagrees-with-prior-photo-proposal')
        quality = 'high' if reliability>=.9 else 'medium' if reliability>=.6 else 'unresolved'
        if pre_area>CAP or pre_area<12: quality='rejected'; reliability=0.
        results.append(dict(method=method, color=color, region=support(pts), reliability=float(reliability),
                            quality=quality, reasons=reasons, metrics=metrics, dark_fraction=dark_fraction,
                            enclosure=enclosure, mean_luminance=mean_lum, seed_mean5=brightness,
                            peak_luminance=peak, seed=xy,
                            strategy='pigment-connected interior' if color!='black' else 'neutral reflection plus bounded coherent dark body'))
    return results


def main():
    native, rgb, meta = photo(); features = image_features(rgb)
    old = read(BASELINE); regions = {r['id']: r.get('region') for r in old['beads']}
    candidates = [dict(id=r['id'], xy=[r['point']['x'], r['point']['y']], previous_color=r['color'],
                       source='preserved image-only proposal', old_support=regions.get(r['id'])) for r in old['locations']]
    center = np.genfromtxt(CENTERLINE, delimiter=',', names=True)
    curve = np.c_[center['x'], center['y']]; tree = cKDTree(curve)
    # Fresh maxima scan of the full image-derived near-centerline band.
    mean = features['mean5']; maxima = (mean==ndi.maximum_filter(mean, 9))&(mean>.035)&~features['paper']
    yy, xx = np.where(maxima); pts = np.c_[xx, yy]; distances, _ = tree.query(pts)
    oldtree = cKDTree([r['xy'] for r in candidates]); existing, _ = oldtree.query(pts)
    fresh = pts[(distances<=40)&(existing>=8)]
    for x, y in fresh: candidates.append(dict(id=f'R282-{x:04}-{y:04}', xy=[int(x), int(y)],
                                  previous_color=None, source='fresh native mean5 band maximum', old_support=None))
    rows = []; variants = {}; prior = {}
    for candidate in candidates:
        ident = candidate['id']; alternatives = attempts(features, candidate['xy'], candidate['previous_color'])
        if not alternatives: continue
        variants[ident] = alternatives; chosen = next(a for a in alternatives if a['method']==SELECTED)
        row = record(ident, 'phase1'); row.update(color=chosen['color'],
            color_reliability=float(min(chosen['reliability'], .92)), phase1_reliability=chosen['reliability'],
            measured_support=chosen['region'], measured_photo_location=chosen['region']['centroid'] if chosen['region'] else None,
            reliability_class=chosen['quality'], status=chosen['quality'], notes=chosen['reasons'].copy(),
            seed=candidate['xy'], support_method=SELECTED, source=candidate['source'], metrics=chosen['metrics'],
            illumination=dict(mean=chosen['mean_luminance'], peak=chosen['peak_luminance']),
            black_evidence=dict(dark_fraction=chosen['dark_fraction'], enclosure=chosen['enclosure']),
            visibility_kind='photographic support exists; whole-bead visible fraction unmeasured',
            evidence_links=['photo2/r282/results/phase1-attempts.json.gz'])
        row['notes'].append('Algorithmic reliability class; no independently measured accuracy or completeness.')
        xy = row['measured_photo_location'] or candidate['xy']; distance, index = tree.query(xy)
        row.update(centerline_distance=float(distance), arc_fraction=float(index/len(curve)), near_centerline=bool(distance<=26))
        if candidate['old_support']: prior[ident] = candidate['old_support']
        rows.append(row)
    # Reject competing overlapping supports; no geometry or count quota resolves them.
    owners = {}; conflicts = Counter()
    for row in sorted(rows, key=lambda r:(-r['phase1_reliability'],r['record_id'])):
        if row['status']=='rejected': continue
        pts = pixels(row['measured_support']); overlap = Counter(owners.get((int(x),int(y))) for x,y in pts)
        foreign = sum(v for k,v in overlap.items() if k is not None)
        if foreign>max(4,.12*len(pts)):
            row['status']=row['reliability_class']='unresolved'; row['phase1_reliability']=min(.35,row['phase1_reliability'])
            row['notes'].append('Overlapping photographic support; independent body ownership unresolved.')
            row['competing_record_ids']=[k for k in overlap if k]; conflicts['overlap']+=1
        else:
            for x,y in pts: owners[(int(x),int(y))]=row['record_id']
    arc = np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]; length=float(arc[-1]+np.linalg.norm(curve[0]-curve[-1]))
    high = [r for r in rows if r['status']=='high']
    points = np.array([r['measured_photo_location'] for r in high]).reshape(-1,2)
    nearest = cKDTree(points).query(curve)[0] if len(points) else np.full(len(curve),1e6)
    counts = dict(Counter(r['status'] for r in rows))
    summary = dict(counts=counts, by_color={c:dict(Counter(r['status'] for r in rows if r['color']==c)) for c in ('red','yellow','black','unknown')},
        near_centerline=dict(Counter(r['status'] for r in rows if r['near_centerline'])),
        baseline_locations=len(old['locations']), fresh_maxima=len(fresh), selected_method=SELECTED,
        coverage=dict(reference_length_px=length, stations=len(curve), high_location_within_26px=int((nearest<=26).sum()),
                      fraction=float((nearest<=26).mean()), maximum_gap_distance_px=float(nearest.max()),
                      warning='Distance-to-observation coverage, not a count of missed beads or proof of completeness.'),
        alternatives={m:dict(Counter(next(a for a in v if a['method']==m)['quality'] for v in variants.values())) for m in ('A','B','C')},
        palette=features['palette'], background_hue=features['background_hue'], **meta,
        input_hashes={str(p.relative_to(ROOT)):sha(p) for p in (BASELINE,CENTERLINE)},
        independence='Photo and image-only candidate/centerline lineage only. No physical-model or pattern inputs.')
    for r in rows: validate(r)
    save(OUT/'phase1.json.gz',dict(schema='r282-bead-record-1',records=rows,summary=summary))
    save(OUT/'phase1-attempts.json.gz',variants);save(OUT/'phase1-baseline-supports.json.gz',prior)
    save(OUT/'centerline.json',dict(points=curve.tolist(),nearest_high_distance=nearest.tolist(),source=str(CENTERLINE.relative_to(ROOT)),sha256=sha(CENTERLINE)))
    save(OUT/'phase1-summary.json',summary); print('phase1',summary['counts'],flush=True)
    return rows


if __name__ == '__main__': main()
