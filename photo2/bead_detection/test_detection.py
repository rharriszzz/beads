"""Known photographic-like fixtures; no historical observations or positions."""
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from .detect import detect, measurements, Parameters, radial_boundary


def fixture(palette=0, shift=(0,0)):
    yy,xx=np.indices((180,240));rgb=np.full((180,240,3),0.,float)
    paper=np.array([.72,.42,.65]) if palette==0 else np.array([.45,.69,.72])
    rgb[:]=paper
    targets=[]
    for x,y,color in [(65,65,[.9,.18,.14]),(106,65,[.95,.70,.12]),(150,110,[.13,.13,.14])]:
        x+=shift[0];y+=shift[1];d=np.hypot(xx-x,yy-y);mask=d<=17
        color=np.array(color) if palette==0 else np.roll(color,1)
        shade=.55+.45*np.maximum(0,1-(d/18)**2)
        body=color[None,None,:]*shade[:,:,None]
        rgb[mask]=body[mask]
        spec=np.exp(-((xx-(x-4))**2+(yy-(y-4))**2)/5)*.75
        rgb=np.clip(rgb+spec[:,:,None]*mask[:,:,None],0,1)
        targets.append((x,y,mask))
    # Smooth cast-paper shadow and an unlit dark gap have no bead evidence.
    shadow=1-.52*np.exp(-((xx-195)**2+(yy-50)**2)/200)
    rgb*=shadow[:,:,None]
    rgb[(xx-40)**2+(yy-130)**2<12**2]=.07
    return (rgb*255).astype(np.uint8),targets


class DetectionTests(unittest.TestCase):
    def test_known_bodies_palette_and_translation(self):
        for palette,shift in [(0,(0,0)),(1,(15,10))]:
            rgb,truth=fixture(palette,shift);data,labels=detect(rgb)
            for index,(x,y,mask) in enumerate(truth):
                matches=[r for r in data['regions'] if np.linalg.norm(np.array(r['centroid'])-[x,y])<15]
                self.assertEqual(len(matches),1,(palette,(x,y),[(r['centroid'],r['kind']) for r in matches]))
                r=matches[0];prediction=np.zeros(mask.shape,bool)
                for row,a,b in r['pixel_runs']:prediction[row,a:b+1]=True
                iou=(prediction&mask).sum()/(prediction|mask).sum()
                if index<2:self.assertGreater(iou,.45,(palette,r['id'],iou))
                else:
                    self.assertEqual(r['extent'],'reflection-and-dark-perimeter')
                    self.assertEqual(r['evidence']['dark_perimeter_fraction'],1.)
                    self.assertLess(r['pixel_count'],mask.sum()*.5)
                    self.assertLess(np.linalg.norm(np.array(r['centroid'])-[x-4,y-4]),3)
            self.assertFalse(any(np.linalg.norm(np.array(r['centroid'])-[195,50])<20 for r in data['regions']))
            self.assertFalse(any(np.linalg.norm(np.array(r['centroid'])-[40,130])<15 for r in data['regions']))

    def test_masks_statistics_closure_and_exclusivity(self):
        rgb,_=fixture();data,labels=detect(rgb);occupied=np.zeros(labels.shape,bool)
        for r in data['regions']:
            mask=np.zeros(labels.shape,bool)
            for y,a,b in r['pixel_runs']:mask[y,a:b+1]=True
            self.assertEqual(int(mask.sum()),r['pixel_count'])
            self.assertFalse((mask&occupied).any());occupied|=mask
            yy,xx=np.where(mask);np.testing.assert_allclose(r['centroid'],[xx.mean(),yy.mean()])
            for c in r['contours']:self.assertEqual(c[0],c[-1])
        np.testing.assert_array_equal(occupied,labels>0)
        self.assertEqual(len({r['id'] for r in data['regions']+data['rejected']}),len(data['regions'])+len(data['rejected']))
        self.assertEqual(sum(len(r['maxima_ids']) for r in data['regions']+data['rejected']),len(data['maxima']))
        json.dumps(data,allow_nan=False)

    def test_hue_wrap(self):
        hsv=np.array([[[.999,1.,.8],[.001,1.,.8]]]);m=measurements(np.ones((1,2),bool),hsv,0,0)
        self.assertLess(min(m['hsv']['hue_circular_mean_deg'],360-m['hsv']['hue_circular_mean_deg']),1)

    def test_location_does_not_fall_into_a_concave_gap(self):
        mask=np.zeros((15,15),bool);mask[2:13,2:5]=True;mask[2:5,2:13]=True;mask[10:13,2:13]=True
        r=measurements(mask,np.full((15,15,3),.5),10,20)
        self.assertFalse(r['centroid_inside_region'])
        x,y=r['location'];self.assertTrue(mask[y-20,x-10])

    def test_uniform_image_and_determinism(self):
        data,labels=detect(np.full((100,100,3),150,np.uint8))
        self.assertFalse(data['regions']);self.assertFalse(labels.any())
        rgb,_=fixture();a,aa=detect(rgb);b,bb=detect(rgb)
        self.assertEqual(a,b);np.testing.assert_array_equal(aa,bb)

    def test_noise_and_double_peak_neighbor_separation(self):
        rgb,truth=fixture();rng=np.random.default_rng(4)
        rgb=np.clip(rgb.astype(float)+rng.normal(0,1.3,rgb.shape),0,255).astype(np.uint8)
        data,_=detect(rgb)
        for x,y,_ in truth:
            self.assertEqual(sum(np.linalg.norm(np.array(r['centroid'])-[x,y])<15 for r in data['regions']),1)
        # One broad interior with two shallow-saddle maxima is one region.
        y,x=np.indices((120,120));v=.3+.5*np.exp(-((x-60)**2+(y-60)**2)/180)
        v+=.14*np.exp(-((x-56)**2+(y-60)**2)/3)+.14*np.exp(-((x-64)**2+(y-60)**2)/3)
        rgb=(np.stack([v,v*.2,v*.15],axis=-1)*255).clip(0,255).astype(np.uint8)
        # Different border chromaticity prevents treating the body as paper.
        rgb[np.hypot(x-60,y-60)>24]=[160,100,145]
        data,_=detect(rgb,Parameters(prominence=.03))
        near=[r for r in data['regions'] if np.linalg.norm(np.array(r['centroid'])-[60,60])<15]
        self.assertEqual(len(near),1)
        self.assertGreaterEqual(len(near[0]['maxima_ids']),2)

    def test_black_growth_stops_at_first_dark_perimeter(self):
        from .detect import dark_perimeter_region
        y,x=np.indices((101,101));v=np.full((101,101),.08)
        v+=.8*np.exp(-((x-50)**2+(y-50)**2)/8)
        mask,origin,closed,maximum,fraction=dark_perimeter_region(v,[50,50],Parameters())
        self.assertTrue(closed);self.assertEqual(fraction,1)
        self.assertLessEqual(maximum,Parameters().dark_value)
        self.assertLess(mask.sum(),100)  # Does not grow across the extensive dark body.
        # Removing its single added dark shell exposes above-threshold pixels.
        core=ndi.binary_erosion(mask,structure=np.ones((3,3)))
        rim=core&~ndi.binary_erosion(core,structure=np.ones((3,3)))
        x0,y0=origin
        self.assertGreater(v[y0:y0+mask.shape[0],x0:x0+mask.shape[1]][rim].max(),Parameters().dark_value)

    def test_shallow_neighbor_valley_stops_growth_despite_small_noise(self):
        from dataclasses import replace
        y,x=np.indices((121,121));radius=np.hypot(x-60,y-60)
        value=np.interp(radius,[0,10,13,20,30,45],[1,.5,.5,.535,.1,.7])
        value+=.003*np.sin(radius*3)
        sensitive=radial_boundary(value,[60,60],Parameters())[-1]
        previous=radial_boundary(value,[60,60],replace(Parameters(),rise=.045))[-1]
        self.assertLess(sensitive.mean(),17)
        self.assertGreater(previous.mean(),20)
        self.assertGreater(sensitive.min(),7)  # Tiny ripples do not stop immediately.

    def test_less_blur_preserves_narrow_dark_separator(self):
        from .detect import dark_perimeter_region
        y,x=np.indices((101,121));raw=np.full(x.shape,.08)
        raw[(x-40)**2+(y-50)**2<=6**2]=.8
        raw[(x>=48)&(y>=35)&(y<=65)]=.8
        coarse=ndi.gaussian_filter(raw,Parameters().blur_sigma)
        detail=ndi.gaussian_filter(raw,Parameters().dark_detail_sigma)
        a=dark_perimeter_region(coarse,[40,50],Parameters())
        b=dark_perimeter_region(detail,[40,50],Parameters())
        self.assertFalse(a[2]);self.assertTrue(b[2])
        self.assertLess(b[0].sum(),200)
        self.assertLessEqual(b[3],Parameters().dark_value)


if __name__=='__main__':unittest.main()
