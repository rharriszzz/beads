"""Scientific contracts and artifact invariants for R283."""
import ast
from copy import deepcopy
import unittest
from collections import Counter
import numpy as np
from photo2.r282.phase3 import periods,search
from .common import OUT,OLD,ROOT,read,sha,pixels,support,record,validate
from .ownership import audit
from .coverage import relationships
from .local import light_evidence,INDICES,axis_error

def row(k,xy,status='high'):
    r=record(k,'phase1');r.update(seed=list(np.asarray(xy)[0]),measured_support=support(xy),
        measured_photo_location=np.asarray(xy).mean(0).tolist(),status=status,reliability_class=status,
        color='yellow',phase1_reliability=.95);return r

class Contracts(unittest.TestCase):
    def test_symmetric_overlap(self):
        yy,xx=np.mgrid[30:40,30:40];a=np.c_[xx.ravel(),yy.ravel()];b=a+[7,0]
        rr=[row('A',a),row('B',b)];f={'mean5':np.ones((90,90))}
        out,p=audit(rr,f);self.assertEqual([r['status'] for r in out],['unresolved']*2)
        rev,_=audit(rr[::-1],f);self.assertEqual({r['record_id']:r['status'] for r in rev},{r['record_id']:r['status'] for r in out})
    def test_close_color_is_not_merge(self):
        yy,xx=np.mgrid[30:40,30:40];a=np.c_[xx.ravel(),yy.ravel()];b=a+[15,0]
        rr,p=audit([row('A',a),row('B',b)],{'mean5':np.ones((90,90))})
        self.assertTrue(all(r['likely_duplicate_group'] is None for r in rr))
        self.assertTrue(all(r['status']=='high' for r in rr))
    def test_identical_measurements_preserved(self):
        yy,xx=np.mgrid[30:40,30:40];a=np.c_[xx.ravel(),yy.ravel()]
        rr,_=audit([row('A',a),row('B',a)],{'mean5':np.ones((90,90))})
        self.assertEqual(Counter(r['status'] for r in rr),{'high':1,'unresolved':1})
        self.assertEqual(rr[0]['measured_support'],rr[1]['measured_support'])
    def test_two_sides_and_crossing(self):
        x=np.linspace(0,100,201);curve=np.vstack([np.c_[x,np.full(len(x),50)],np.c_[x[::-1],np.full(len(x),150)]])
        yy,xx=np.mgrid[40:47,45:55];a=np.c_[xx.ravel(),yy.ravel()]
        rr=[row('A',a),row('B',a+[0,14]),row('C',a+[25,7])]
        relationships(rr,curve)
        self.assertEqual({rr[0]['centerline']['side'],rr[1]['centerline']['side']},{'positive','negative'})
        self.assertTrue(all(r['centerline']['near'] for r in rr));self.assertTrue(rr[2]['centerline']['crosses'])
    def test_station_resampling_not_bead_count(self):
        rows=read(OUT/'phase1.json.gz')['records'];bins=read(OUT/'coverage.json')['bins'];ids=[k for b in bins for k in b['ids']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(set(ids),{r['record_id'] for r in rows if r['near_centerline']})
    def test_native_measurements_unchanged(self):
        old={r['record_id']:r for r in read(OLD/'phase1.json.gz')['records']}
        rows=read(OUT/'phase1.json.gz')['records'];self.assertEqual(set(old),{r['record_id'] for r in rows})
        for r in rows:
            validate(r)
            for k in ('measured_support','measured_photo_location','color','seed'):self.assertEqual(r[k],old[r['record_id']][k])
            self.assertEqual(r['importance'],'high');self.assertIsNone(r['photographic_reliability']['calibrated_probability'])
    def test_ownership_independence(self):
        source=(ROOT/'photo2/r283/ownership.py').read_text();tree=ast.parse(source)
        imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any('phase2' in p or 'phase3' in p or 'geometry' in p or 'local' in p for p in imports))
    def test_freeze_and_local_partition(self):
        self.assertEqual(sha(OUT/'phase1.json.gz'),read(OUT/'phase1-freeze.json')['phase1_sha256'])
        for folder in (OUT/'local',OUT/'local-confirmation'):
            a=read(folder/'anchors.json');h=read(folder/'withheld.json');f=read(folder/'prediction-freeze.json');e=read(folder/'evaluation.json')
            self.assertEqual(f['anchors_sha256'],sha(folder/'anchors.json'))
            self.assertEqual(e['prediction_freeze_sha256'],sha(folder/'prediction-freeze.json'))
            self.assertFalse({r['record_id'] for r in a['anchors']}&{r['record_id'] for r in h['records']})
            self.assertTrue(all(m['certificate']['certified'] for m in f['models']))
            self.assertEqual({m['parameters']['hand'] for m in f['models']},{-1,1})
            self.assertTrue(all(1.12<=m['parameters']['pitch']<=1.24 for m in f['models']))
    def test_no_owner_sentinel_is_not_highlight_match(self):
        p=dict(hand=1,pitch=1.2,inclination=0,roll=0,phase=0,scale=8,translation=[100,100])
        r={'record_id':'absent','color':'yellow','highlight':{'point':[10000,10000]}}
        self.assertFalse(light_evidence(p,[r],[-999])[0]['usable'])
    def test_extended_bank_has_no_crop_end_artifact(self):
        from .local import trace
        yy,xx=np.indices((220,280));xy=np.c_[xx.ravel(),yy.ravel()]
        for folder in (OUT/'local',OUT/'local-confirmation'):
            for m in read(folder/'prediction-freeze.json')['models']:
                a,_,u=trace(m['parameters'],xy);b,_,v=trace(m['parameters'],xy,np.arange(-80,81))
                np.testing.assert_array_equal(a[~u&~v],b[~u&~v])
    def test_native_pov_projection(self):
        for folder in (OUT/'local',OUT/'local-confirmation'):
            for r in read(folder/'pov-audit.json')['models']:
                self.assertEqual(r['stable_interior_disagreements'],0)
                self.assertLessEqual(r['disagreements'],8)
    def test_synthetic_certificates_and_frozen_rules(self):
        for f in sorted((OUT/'confirmation').glob('scene-*')):
            self.assertTrue(read(f/'truth.json')['certificate']['certified'])
        s=read(OUT/'confirmation-results.json');self.assertEqual(len(s['scenes']),16)
        self.assertEqual(s['method_freeze_sha256'],sha(OUT/'method-freeze.json'))
        for k in ('before','after'):
            total=s['summary'][k];self.assertEqual(total['high'],total['correct_support']+total['false_or_wrong_body'])
            self.assertLessEqual(total['detected_eligible'],total['eligible'])
    def test_integrated_provenance_visibility_and_uncertainty(self):
        p1={r['record_id']:r for r in read(OUT/'phase1.json.gz')['records']};folder=OUT/'integrated';p2=read(folder/'phase2.json')
        self.assertEqual(sha(folder/'phase1.json.gz'),sha(OUT/'phase1.json.gz'))
        for name in p2['selected_ids']:
            d=read(folder/(name+'-inventory.json.gz'));self.assertEqual(len(d['records']),d['model']['n']);seen=[]
            for r in d['records']:
                validate(r);self.assertLessEqual(r['phase2_identity_reliability'],.35)
                if r['visible_pixels']==0:self.assertEqual(r['visibility'],0);self.assertEqual(r['color'],'unknown')
                for k in r.get('source_record_ids',[]):
                    seen.append(k);self.assertEqual(r['measured_support'],p1[k]['measured_support']);self.assertEqual(r['measured_photo_location'],p1[k]['measured_photo_location'])
            self.assertEqual(len(seen),len(set(seen)))
    def test_pattern_no_upstream_mutation(self):
        f=OUT/'integrated';p2=read(f/'phase2.json')
        for name in p2['selected_ids']:
            original=read(f/(name+'-inventory.json.gz'))['records'];later=read(f/(name+'-phase3-inventory.json.gz'))['records']
            for a,b in zip(original,later):
                for k in ('color','measured_support','measured_photo_location','physical_model_index','phase1_reliability'):self.assertEqual(a[k],b[k])
                self.assertFalse(b['pattern_accepted'])
            patterns=read(f/(name+'-patterns.json'))
            for mode in ('weighted','strict'):
                for c in patterns[mode]:self.assertTrue(c['complete_repeat_rule']);self.assertGreaterEqual(c['repeats'],4);self.assertNotEqual(c['period']%13,0)
    def test_complete_repeat_boundaries(self):
        self.assertIn(12,periods(48));self.assertNotIn(12,periods(36));self.assertNotIn(13,periods(52));self.assertNotIn(7,periods(50))
    def test_known_pattern_and_unknowns(self):
        rows=[]
        for k in range(48):
            r=record(str(k),'phase2');r.update(physical_model_index=k,color=('red','yellow','black')[k%3],visibility=1.,color_reliability=1.,phase2_identity_reliability=1.,phase1_reliability=1.);rows.append(r)
        before=deepcopy(rows);p=next(c for c in search(rows,48) if c['period']==3)
        self.assertEqual(p['sequence'],['red','yellow','black']);self.assertEqual(rows,before)
        for r in rows:r['phase2_identity_reliability']=0.
        self.assertTrue(all(set(c['sequence'])=={'unknown'} for c in search(rows,48)))

if __name__=='__main__':unittest.main()
