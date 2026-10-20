"""Three historical maker-colored exclusions, reference-only, fixed-pixel test."""
from common import *
from recognize import sample

def main():
 _,obs,co,rgb,auth=load();previous=read(ROOT/'photo2/r341/excluded-maker-controls.json')['records'];records=[]
 for r in previous:
  o=r['id'];assert o not in obs and o not in co;m=sample(rgb,r['source_xy'],[],'offset-core');records.append(dict(id=o,maker_color=auth[o]['color'],source_xy=r['source_xy'],measurement=m,automatic_decision='unknown',active_admission=False,policy='Historical exclusion authoritative. Raw pixel agreement is not proof of owned glass, indexing, or an active role.'))
 save(OUT/'excluded-maker-controls.json',dict(records=records,role_admissions=0));print('Excluded reference-only',[(r['id'],r['measurement']['score'],r['measurement']['decision']) for r in records])
if __name__=='__main__':main()
