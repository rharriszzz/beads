import json,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from photo2.r324 import fast_tracker as old
from .spectral import directions
OUT=Path(__file__).parent/'results'
def main():
    g=json.load(open(OUT/'graph.json'));data=old.preprocess(ImageOps.exif_transpose(Image.open('beads-photo-2.jpg')).convert('RGB'));grid=np.indices((200,200))[::-1].reshape(2,-1).T-99.5;tm=[0.,0.];checks=[]
    for w in g['windows']:
        pts=grid@np.array(w['frame']).T+w['center'];patch={k:old.base.sample(data[k],pts).reshape(200,200) for k in ['z','fg']};patch['fg']=patch['fg']>.5;patch['weight']=ndi.gaussian_filter(patch['fg'].astype(float),5)*np.hanning(200)[None,:];results=[]
        for j,f in enumerate([old.base.directions,directions]):
            t=time.perf_counter()
            try:results.append(f(patch)[1])
            except ValueError as ex:results.append(str(ex))
            tm[j]+=time.perf_counter()-t
        checks.append(dict(window=w['id'],exact=results[0]==results[1]))
    report=dict(reference_seconds=tm[0],restricted_seconds=tm[1],speedup=tm[0]/tm[1],windows=len(checks),all_spectra_exact=all(x['exact'] for x in checks),checks=checks)
    old.save(OUT/'spectral-benchmark.json',report);print({k:v for k,v in report.items() if k!='checks'})
if __name__=='__main__':main()
