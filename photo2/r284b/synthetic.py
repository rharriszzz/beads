"""Small mathematical intensity bridge control; not physical scene validation."""
import numpy as np
from photo2.r282.common import save,support
from .methods import reflection
from .run import OUT

def main():
    y,x=np.indices((49,49));lum=.002+.07*np.exp(-((x-24)**2+(y-26)**2)/8)+.4*np.exp(-((x-24)**2+(y-17)**2)/8)
    initial=(x-24)**2+(y-26)**2<49;results={}
    for method in ('R1','R2','R3','R4'):
        mask,curve,meta=reflection(lum,np.ones_like(initial),initial,seed=[24,26],variant=method)
        yy,xx=np.where(mask);results[method]=dict(support=support(np.c_[xx,yy]),contour=curve.tolist(),evidence=meta,
            weak_peak_retained=bool(mask[26,24]),bright_peak_in_weak_support=bool(mask[17,24]))
    save(OUT/'synthetic-bridge.json',dict(native_Y=lum.tolist(),formula='0.002 + 0.07 exp(-((x-24)^2+(y-26)^2)/8) + 0.4 exp(-((x-24)^2+(y-17)^2)/8)',
        results=results,scope='Two intensity features; no physical bodies or identity truth. Tests feature separation only.'))
    print({m:(r['weak_peak_retained'],r['bright_peak_in_weak_support']) for m,r in results.items()})

if __name__=='__main__':main()
