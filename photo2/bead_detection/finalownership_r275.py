"""Apply the same photographic dominance checks to late recovery proposals."""
import json,sys
import numpy as np
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save
from .brightness_r270 import color_managed_photo
from .dominance_r275 import suppress

def main():
 path=OUT/'before-finalownership-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();data,dec=suppress(old,native,srgb,Band());save('inventory.json',data);save('final-ownership.json',dec);print(dec)
if __name__=='__main__':main()
