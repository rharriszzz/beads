from .common import *
from .landmark import detect

def main():
    native,rgb,meta=photo();rows,info=detect(rgb)
    save(OUT/'photo-landmarks.json.gz',dict(records=rows,photograph=meta,detector=info))
    print(len(rows),'maxima',sum(r['accepted'] for r in rows),'accepted')
if __name__=='__main__':main()
