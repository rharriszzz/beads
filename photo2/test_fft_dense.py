import unittest
import numpy as np
from photo2.fft_dense import Scanner,match_edges,associate,DELTA
from photo2.fft_transfer import measure,VARIANTS


def peak(o,a=0,f=.04,rank=1):
    return dict(observation=o,relative_angle=a,angle=a,frequency=f,frequency_resolution=DELTA,candidate=rank,weak=False)


class DenseChecks(unittest.TestCase):
    def test_ranking_changes_do_not_change_identity(self):
        a=[peak('a',-40,rank=1),peak('b',45,rank=2)]
        b=[peak('c',45,rank=1),peak('d',-40,rank=4)]
        links={(e['source'],e['target']) for e in match_edges(a,b) if e['accepted']}
        self.assertEqual(links,{('a','d'),('b','c')})
    def test_axial_wrap(self):
        e=match_edges([peak('a',89)],[peak('b',-89)])
        self.assertTrue(e[0]['accepted'])
    def test_crossing_ambiguity_is_not_forced(self):
        e=match_edges([peak('a',-1),peak('b',1)],[peak('c',0),peak('d',2)])
        self.assertTrue(e);self.assertFalse(any(x['accepted'] for x in e))
    def test_disappearance_reappearance_and_closed_seam(self):
        rs=[dict(channel='V',index=i,s=i*10.,curvature=0,peaks=[] if i==2 else [peak(str(i))]) for i in range(8)]
        t=associate(rs,80)
        # Same fragment continues around seam; disappearance remains a measured gap.
        self.assertEqual(len(t['tracks']),1);self.assertTrue(t['tracks'][0]['wrap']);self.assertFalse(t['tracks'][0]['closed'])
        self.assertEqual(t['tracks'][0]['count'],7)
        self.assertFalse(any(e['accepted'] and e['arc_gap']>10 for e in t['associations']))
        rs[2]['peaks']=[peak('2')];t=associate(rs,80);self.assertTrue(t['tracks'][0]['closed'])
    def test_tentative_gap_not_interpolated(self):
        rs=[dict(channel='V',index=i,s=i*10.,curvature=0,peaks=[peak(str(i))] if i in (1,2,4,5) else []) for i in range(10)]
        t=associate(rs,100);self.assertEqual(len(t['tracks']),2)
        self.assertTrue(any(e['kind']=='tentative_gap' and e['source']=='2' and e['target']=='4' for e in t['associations']))
        self.assertEqual(sum(x['count'] for x in t['tracks']),4)
    def test_measured_waves_change_intensity_and_disappear(self):
        yy,xx=np.mgrid[:321,:321];frequencies=[(10/301,0),(5/301,8/301),(-5/301,8/301)]
        records=[];identities=[]
        for i in range(9):
            amplitudes=[.14-.012*i,.04+.012*i,0 if i in (3,4) else .09]
            z=np.full(xx.shape,.5)
            for (fx,fy),amp in zip(frequencies,amplitudes):z+=amp*np.cos(2*np.pi*(fx*xx-fy*yy))
            rgb=np.repeat(z[...,None],3,axis=2).astype(np.float32)
            rr=Scanner(rgb).measure(dict(index=i,s=i*10.,x=160.,y=160.,tangent_deg=0.,curvature=0.))[0]
            row=[]
            for fx,fy in frequencies:
                expected=np.array([fx,fy]);ps=rr['peaks']
                near=[p for p in ps if min(np.linalg.norm(np.array(p['offset'])/301-expected),np.linalg.norm(np.array(p['offset'])/301+expected))<.002]
                row.append(near[0] if near else None)
            records.append(rr);identities.append(row)
        self.assertLess(identities[0][0]['candidate'],identities[0][1]['candidate'])
        self.assertGreater(identities[-1][0]['candidate'],identities[-1][1]['candidate'])
        self.assertIsNone(identities[3][2]);self.assertIsNone(identities[4][2]);self.assertIsNotNone(identities[5][2])
        t=associate(records,90)
        for family in (0,1):
            self.assertEqual(len({t['assignment'][row[family]['observation']] for row in identities}),1)
        self.assertTrue(any(e['kind']=='tentative_gap' and e['source']==identities[2][2]['observation'] and e['target']==identities[5][2]['observation'] for e in t['associations']))

    def test_closed_associations_do_not_depend_on_seam(self):
        rs=[dict(channel='V',index=i,s=i*10.,curvature=0,peaks=[peak(str(i),a=89 if i%2 else -89)]) for i in range(8)]
        a=associate(rs,80)
        shifted=[dict(r,s=(r['s']-30)%80) for r in rs];b=associate(shifted,80)
        self.assertEqual({(e['source'],e['target']) for e in a['associations'] if e['accepted']},{(e['source'],e['target']) for e in b['associations'] if e['accepted']})
    def test_reciprocal_hand_sign_and_unequal_diagonals(self):
        from photo2.fft_helicity import predicted
        plus=predicted(0,1,90,0);minus=predicted(0,-1,90,0)
        self.assertGreater(plus[0]['relative_angle'],0)
        for a,b in zip(plus,minus):self.assertAlmostEqual(a['relative_angle'],-b['relative_angle'])
        self.assertGreater(abs(abs(plus[1]['relative_angle'])-abs(plus[2]['relative_angle'])),4)
        self.assertAlmostEqual(plus[0]['relative_angle'],4.291674136016752)
    def test_constant_least_squares_minimum(self):
        from photo2.fft_dense_angles import fit
        a=np.array([3.,5.,7.]);w=np.array([1.,2.,1.]);mu=fit(a,w)
        self.assertEqual(mu,5.)
        self.assertLess(np.sum(w*(a-mu)**2),np.sum(w*(a-4.9)**2))

    def test_fast_scanner_exact_r249_parity(self):
        rng=np.random.default_rng(77);rgb=rng.random((321,321,3),dtype=np.float32)
        yy,xx=np.mgrid[:321,:321];rgb=.25*rgb+.25+.2*np.cos(2*np.pi*(xx/30+yy/42))[...,None];rgb=rgb.astype(np.float32)
        q=dict(index=0,s=0.,x=160.,y=160.,tangent_deg=23.,curvature=0.)
        fast=Scanner(rgb).measure(q)
        for rr in fast:
            old=measure(rgb,dict(id='p',source_site='p',s=0,xy=[160,160],tangent_deg=23),rr['channel'],VARIANTS[0])
            for a,b in zip(rr['peaks'],old['peaks']):
                for key in b:
                    if key not in ('physical_assignment',):self.assertEqual(a[key],b[key],key)
            self.assertEqual(len(rr['peaks']),len(old['peaks']));self.assertEqual(rr['trios'],old['trios'])


if __name__=='__main__':unittest.main()
