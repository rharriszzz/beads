#!/usr/bin/env python3
"""Verify R087 reproducibility and recompute descriptive metrics from saved RGB."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review',type=Path,required=True)
    parser.add_argument('--repeat',type=Path,required=True)
    args = parser.parse_args()
    a = json.loads((args.review/'report.json').read_text())
    b = json.loads((args.repeat/'report.json').read_text())
    for name,sha in a['sources'].items():
        assert digest(ROOT/name)==sha,name
    for name,sha in a['artifacts'].items():
        assert digest(args.review/name)==sha==digest(args.repeat/name),name
    a.pop('command');b.pop('command')
    assert a==b
    rows = list(csv.DictReader((args.review/'profiles.csv').open()))
    assert len(rows)==a['checks']['sample_rows']==9240
    groups = {}
    for r in rows:
        key = (r['path'],float(r['sigma_px']),float(r['offset_px']))
        groups.setdefault(key,[]).append(r)
    assert len(groups)==165
    paths = json.loads((args.review/'measurements.json').read_text())['paths']
    count = 0
    for p in paths:
        ends = np.array(p['ends'],dtype=float)
        delta = ends[1]-ends[0]
        length = np.linalg.norm(delta)
        normal = np.array([-delta[1],delta[0]])/length
        for m in p['measurements']:
            group = groups[p['id'],m['sigma_px'],m['offset_px']]
            d = np.array([float(r['distance_px']) for r in group])
            rgb = np.array([[float(r[k]) for k in ['red','green','blue']] for r in group])
            xy = np.array([[float(r[k]) for k in ['x','y']] for r in group])
            np.testing.assert_allclose(xy,ends[0]+d[:,None]*delta/length+m['offset_px']*normal)
            np.testing.assert_allclose([d[0],d[-1]],[0,length])
            assert (np.diff(d)>0).all() and np.diff(d).max()<=.25+1e-12
            v = rgb.max(axis=1)
            s = np.divide(v-rgb.min(axis=1),v,out=np.zeros_like(v),where=v!=0)
            np.testing.assert_allclose(v,[float(r['value']) for r in group])
            np.testing.assert_allclose(s,[float(r['saturation']) for r in group])
            left,right = d<=2,d>=length-2
            inner = np.flatnonzero((d>2)&(d<length-2))
            i = inner[np.argmin(v[inner])]
            vl,vr = np.median(v[left]),np.median(v[right])
            sl,sr = np.median(s[left]),np.median(s[right])
            expected = dict(s_start=sl,s_end=sr,s_delta=sr-sl,s_range=np.ptp(s),
                            v_start=vl,v_end=vr,v_dip=min(vl,vr)-v[i],
                            v_dip_distance_px=d[i],v_peak=v[inner].max()-max(vl,vr))
            for k,value in expected.items():
                assert abs(m[k]-value)<1e-10,(p['id'],k,m[k],value)
            assert m['trough_at_search_edge']==bool(i in [inner[0],inner[-1]])
            count+=1
    assert count==165
    for link in re.findall(r'(?:href|src)="([^"]+)"',(args.review/'review.html').read_text()):
        assert (args.review/link).is_file(),link
    print(f"Verified {len(a['sources'])} source hashes, {len(a['artifacts'])} byte-identical artifacts, 9240 samples, 165 metrics and HTML links.")


if __name__=='__main__':
    main()
