"""Native-pixel contracts and the six R261 pre-photograph fixtures."""
import unittest
from dataclasses import replace
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .pixel_detect import detect, grow, Parameters


def fixtures():
    y,x=np.mgrid[:65,:97]
    def color(v):
        out=np.stack([v,.24*v,.12*v],axis=2).clip(0,255).astype(np.uint8)
        out[v<=20]=[150,160,170]
        return out
    a=230-11*np.hypot(x-28,y-32);b=210-10*np.hypot(x-67,y-32)
    two=color(np.maximum(15,np.maximum(a,b)))
    base=np.where(np.hypot(x-48,y-32)<24,150-3*np.hypot(x-48,y-32),15)
    multi=color(np.maximum(15,base)+70*np.exp(-((x-40)**2+(y-29)**2)/8)+80*np.exp(-((x-56)**2+(y-32)**2)/8))
    black=np.repeat(np.maximum(5,240-32*np.hypot(x-48,y-32))[:,:,None],3,axis=2).astype(np.uint8)
    shadow=np.repeat((160-100*np.exp(-((x-48)**2+(y-32)**2)/200))[:,:,None],3,axis=2).astype(np.uint8)
    uneven=color(np.maximum(15,np.maximum(240-8*np.hypot(x-28,y-30)-.8*(x-28),190-10*np.hypot(x-67,y-34))))
    rng=np.random.default_rng(261)
    noisy=color(np.maximum(15,np.maximum(a,b))+rng.integers(-2,3,x.shape))
    bg=np.maximum(a,b)<=15
    noisy[bg]=(noisy[bg].astype(int)+rng.integers(-2,3,(int(bg.sum()),1))).astype(np.uint8)
    return dict(two_adjacent=two,several_highlights=multi,black_reflection=black,dark_shadow=shadow,uneven_light=uneven,noise_and_equal=noisy)


def audit_trace(region, ownership, width=None):
    t=region['trace'];a=t['accepted'];seen=set();blocked={}
    assert a
    for s in t['stops']:blocked.setdefault((s[0],s[1]),s[8])
    for i,row in enumerate(a):
        x,y,prev,v,*_=row
        assert (x,y) not in seen;seen.add((x,y))
        assert ownership[y,x]==int(region['id'][1:])
        assert (x,y) not in blocked or i<blocked[x,y]
        if i:
            assert 0<=prev<i
            q=a[prev];assert max(abs(x-q[0]),abs(y-q[1]))==1
            assert v<=q[3] and v<=a[i-1][3]
            if row[7]:assert q[7]
        else:assert prev==-1
    points=[(r[0],r[1]) for r in a if r[7]]
    expected={(x,y) for y,x1,x2 in region['pixel_runs'] for x in range(x1,x2+1)}
    assert set(points)==expected
    assert len(points)==region['pixel_count']
    assert np.allclose(np.mean(points,axis=0),region['centroid'],rtol=0,atol=1e-12)
    assert tuple(region['location']) in expected
    for c in region['contours']:assert c[0]==c[-1]
    for s in t['stops']:
        q=a[s[2]];assert max(abs(s[0]-q[0]),abs(s[1]-q[1]))==1
    return len(a),len(t['stops'])


class PixelTests(unittest.TestCase):
    def test_six_requested_cases(self):
        for name,rgb in fixtures().items():
            with self.subTest(name=name):
                data,labels,owners=detect(rgb)
                for r in data['regions']+data['rejected']:audit_trace(r,owners)
                if name=='dark_shadow':self.assertEqual(len(data['regions']),0)
                if name=='black_reflection':
                    self.assertTrue(any(r['dark_enclosure'] for r in data['regions']))
                    for r in data['regions']:self.assertLess(r['pixel_count'],100)
                if name in ('two_adjacent','uneven_light','noise_and_equal'):
                    self.assertGreaterEqual(len(data['regions']),2)
                    for r in data['regions']:
                        peak=r['bright_patch']['peak']
                        if peak[0]<45:self.assertLess(r['bbox'][2],50)
                        if peak[0]>55:self.assertGreater(r['bbox'][0],45)
                if name=='several_highlights':
                    self.assertGreaterEqual(len(data['regions']),2)
                    self.assertTrue(all(len(r['maxima_ids'])==1 for r in data['regions']))

    def test_alternate_route_cannot_reopen_rise(self):
        # Broad monotone detour toward a bright island, plus a direct dark valley.
        v=np.array([[100,95,90,85,80,75,70],[95,50,50,50,50,50,65],
                    [90,50,60,60,60,50,60],[85,50,55,50,55,50,55],
                    [80,75,70,65,60,55,50]],np.uint8)
        hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        mask,t=grow(v,hsv,np.ones_like(v),1,(0,0),replace(Parameters(),dark_dn=0,retreat_dn=0,retreat_fraction=0))
        blocked={(s[0],s[1]):s[8] for s in reversed(t['stops'])}
        for i,a in enumerate(t['accepted']):
            self.assertTrue((a[0],a[1]) not in blocked or i<blocked[a[0],a[1]])
            if i:self.assertLessEqual(a[3],t['accepted'][i-1][3])
        # Island is not accessible by an uphill edge even with a single owner.
        self.assertFalse(mask[2,3])
        self.assertNotIn((3,2),[(a[0],a[1]) for a in t['accepted']])

    def test_every_blocked_approach_has_a_stop(self):
        rng=np.random.default_rng(261)
        for _ in range(50):
            v=rng.integers(100,200,(9,9),dtype=np.uint8);v[4,4]=220
            hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
            _,t=grow(v,hsv,np.ones_like(v),1,(4,4),replace(Parameters(),dark_dn=0))
            accepted={(a[0],a[1]) for a in t['accepted']}
            stopped={(s[2],s[0],s[1]) for s in t['stops']}
            for i,a in enumerate(t['accepted']):
                for dy in [-1,0,1]:
                    for dx in [-1,0,1]:
                        x,y=a[0]+dx,a[1]+dy
                        if 0<=x<9 and 0<=y<9 and (x,y) not in accepted:
                            self.assertIn((i,x,y),stopped)

    def test_equal_plateau_individual_acceptances(self):
        v=np.zeros((9,9),np.uint8);v[2:7,2:7]=180
        hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        mask,t=grow(v,hsv,np.ones_like(v),1,(4,4))
        self.assertEqual(mask.sum(),25)
        self.assertEqual(len(t['accepted']),25)
        for i,a in enumerate(t['accepted'][1:],1):
            prev=t['accepted'][a[2]];self.assertLess(a[2],i);self.assertEqual(max(abs(a[0]-prev[0]),abs(a[1]-prev[1])),1)

    def test_single_dn_rise_and_no_tolerance_accumulation(self):
        v=np.array([[200,199,198,199,200,201]],np.uint8)
        hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        mask,t=grow(v,hsv,np.ones_like(v),1,(0,0),replace(Parameters(),dark_dn=0))
        self.assertEqual([a[0] for a in t['accepted']],[0,1,2])
        self.assertEqual(t['stops'][0][7],'brightness-rise')

    def test_color_guard_symmetric_and_circular(self):
        from matplotlib.colors import hsv_to_rgb
        for h0,h1,stops in [(0,60,True),(60,0,True),(355,5,False),(140,200,True)]:
            hsv=np.array([[[h0/360,.8,.9],[h0/360,.8,.8],[h1/360,.8,.7]]])
            rgb=(hsv_to_rgb(hsv)*255).astype(np.uint8);v=rgb.max(axis=2)
            mask,t=grow(v,hsv,np.ones_like(v),1,(0,0),replace(Parameters(),dark_dn=0,retreat_dn=0,retreat_fraction=0))
            self.assertEqual(any(s[7]=='relative-hue-change' for s in t['stops']),stops)

    def test_retreat_removes_dark_on_bead_pixels(self):
        v=np.array([[220,200,180,160,140,120,100]],np.uint8)
        hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        mask,t=grow(v,hsv,np.ones_like(v),1,(0,0),replace(Parameters(),dark_dn=0,retreat_fraction=.3))
        self.assertEqual([a[3] for a in t['accepted'] if a[7]],[220,200,180,160,140])
        self.assertFalse(mask[0,5]);self.assertFalse(mask[0,6])

    def test_noise_maxima_not_erased_or_merged(self):
        rgb=fixtures()['noise_and_equal'];data,_,_=detect(rgb)
        self.assertGreater(len(data['maxima']),sum(m['meaningful'] for m in data['maxima']))
        self.assertTrue(all(m['plateau_runs'] for m in data['maxima']))
        self.assertEqual(len(data['maxima']),len({m['id'] for m in data['maxima']}))

    def test_rotation_palette_and_repeatability(self):
        rgb=fixtures()['two_adjacent']
        a,_,_=detect(rgb);b,_,_=detect(rgb.copy())
        self.assertEqual(a,b)
        for transformed in [np.rot90(rgb),rgb[:,:,[1,2,0]]]:
            d,_,o=detect(transformed)
            self.assertEqual(len(d['regions']),len(a['regions']))
            for r in d['regions']:audit_trace(r,o)

if __name__=='__main__':unittest.main()
