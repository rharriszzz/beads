"""Locate local bead paths with the existing integer lattice and color word."""
import csv
import hashlib
from itertools import product
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from photo2.r344.common import index

HERE = Path(__file__).resolve().parent
WEAK = {43, 75, 82, 89, 140, 147, 186}
PREFIX = 12


def load_paths():
    paths = {}
    with (HERE/'paths.csv').open() as f:
        for row in csv.DictReader(f):
            points = []
            for point in row['points_local_x_y_appearance_in_clockwise_order'].split():
                x, y, color = point.split(':')
                points.append((int(x), int(y), color))
            paths[row['view'], int(row['quarter'])] = points
    return paths


def candidates(points, word):
    """Four signed assignments of the two photographed diagonals, all phases."""
    if len(word) != 208:
        raise ValueError('This comparison uses the historical 208-position chart')
    x, y, _ = zip(*points)
    if not np.all(np.diff(x)>0) or np.any(np.diff(y)==0):
        raise ValueError('A path requires ordered adjacent columns and resolved up/down steps')
    down = np.diff(y)>0
    for sign, swap in product((1,-1),(False,True)):
        a_step = down if not swap else ~down
        a = sign*np.r_[0,np.cumsum(a_step)]
        b = sign*np.r_[0,np.cumsum(~a_step)]
        relative = index((a,b)) % len(word)
        orientation = (sign*(6 if swap else 7),sign*(7 if swap else 6))
        for phase in range(len(word)):
            positions = (relative+phase) % len(word)
            yield dict(orientation=orientation,phase=phase,positions=positions.tolist(),
                       prediction=''.join(word[k] for k in positions))


def best(rows, observations, mask_weak=False):
    def score(row):
        return sum(obs!=pred for obs,pred,k in
                   zip(observations,row['prediction'],row['positions'])
                   if obs!='?' and (not mask_weak or (obs in 'RY' and k not in WEAK)))
    losses = [score(row) for row in rows]
    min_loss = min(losses)
    return [row for row, loss in zip(rows,losses) if loss==min_loss]


def locate(paths, word):
    groups = {}
    for key,points in paths.items():
        obs = ''.join(p[2] for p in points)
        rows = list(candidates(points,word))
        groups[key] = dict(full=best(rows,obs), prefix=best(rows,obs[:PREFIX]),
                           masked=best(rows,obs,mask_weak=True))
    # Require one common physical orientation for a consistently clockwise photo.
    for view in {k[0] for k in paths}:
        matching = [g for (name,q),g in groups.items() if name==view]
        for mode in ('prefix','masked'):
            shared = set.intersection(*[{r['orientation'] for r in g[mode]} for g in matching])
            if not shared:
                raise ValueError(f'Inconsistent orientation for {view}, {mode}')
            for g in matching:
                g[mode+'_shared'] = [r for r in g[mode] if r['orientation'] in shared]
    return groups


def shuffled_id(row):
    return hashlib.sha256(str((row['view'], row['quarter'], row['site'], row['offset'])).encode()).hexdigest()


def probes(paths, groups):
    """Queue off-path neighbors and matched controls without looking at their pixels."""
    all_probes = []
    for (view,q), points in sorted(paths.items()):
        fits = groups[view,q]['masked_shared']
        if len(fits)!=1:
            continue
        fit = fits[0]
        down,up = fit['orientation']
        rows = []
        for site,((x,y,_),k) in enumerate(zip(points,fit['positions']),1):
            for offset in [-1,1]:
                v = y + 31*offset
                if 32<=v<=95:
                    rows.append(dict(view=view,quarter=q,site=site,offset=offset,
                                     x=x,y=v,anchor_y=y,residue=(k+(down-up)*offset)%208))
        targets = sorted([r for r in rows if r['residue'] in WEAK],key=shuffled_id)
        controls = [r for r in rows if r['residue'] not in WEAK]
        all_probes.extend(targets)
        for t in targets:
            pool = [r for r in controls if r['offset']==t['offset']]
            control = min(pool,key=lambda r:(abs(t['y']-r['y']),shuffled_id(r)))
            all_probes.append(control)
            controls.remove(control)
    return sorted(all_probes,key=shuffled_id)


def probe_sheet(queue, strips, filename):
    # Numbered photographic context only. Residues/predictions are hidden.
    width,height=195,180
    sheet=Image.new('RGB',(width*5,height*((len(queue)+4)//5)), 'white')
    draw=ImageDraw.Draw(sheet)
    for number,r in enumerate(queue,1):
        strip=strips[r['view']]
        x=r['quarter']*strip.shape[1]//4 + r['x']
        y=r['y']
        crop=Image.fromarray(strip).crop((x-39,y-36,x+39,y+36)).resize((156,144))
        d=ImageDraw.Draw(crop)
        d.ellipse((64,58,92,86),outline='cyan',width=2)
        anchor_y=72+(r['anchor_y']-y)*2
        d.line((72,anchor_y,84,anchor_y),fill='white',width=2)
        col=(number-1)%5*width
        top=(number-1)//5*height
        sheet.paste(crop,(col,top+19))
        draw.text((col+2,top+3),str(number),fill='black')
    sheet.save(filename,quality=96)
