"""Evaluate all three historical maker-colored exclusions as controls only."""
from common import *
from recognize import sample

def main():
 g,obs,co,rgb,auth,old=load();legacy={o['id']:o for o in read(ROOT/'photo2/r335/results/graph.json.gz')['observations']};excluded={o:r for o,r in auth.items() if o not in obs};extra={o:legacy[o] for o in excluded};geo=local_geometry(g,dict(obs,**extra));names=sorted(obs);tree=cKDTree([obs[o]['xy'] for o in names]);records=[]
 for o,a in excluded.items():
  xy=extra[o]['xy'];near=[names[j] for j in tree.query_ball_point(xy,1.1*geo[o]['spacing'])];m=sample(rgb,xy,geo[o],[obs[z]['xy'] for z in near],read(OUT/'selection.json')['selected']);records.append(dict(id=o,maker_color=a['color'],source_xy=xy,measurement=m,role='excluded historical color control ONLY; no counting/indexing/fitting/pattern role',automatic_decision='unknown',reason='Maker-excluded edge body; raw geometric sample does not override original decision or establish ownership'))
 save(OUT/'excluded-maker-controls.json',dict(records=records,active_admissions=0));print([(r['id'],r['maker_color'],r['measurement']['score'],r['measurement']['raw_decision']) for r in records])
 photo=Image.fromarray(rgb);sheet=Image.new('RGB',(1056,366),'white');d=ImageDraw.Draw(sheet)
 for i,r in enumerate(records):
  x,y=map(round,r['source_xy']);box=[x-20,y-20,x+24,y+24];p=photo.crop(box).resize((308,308),Image.Resampling.NEAREST);dp=ImageDraw.Draw(p);a,b,c,e=r['measurement']['patch_box'];dp.rectangle(((a-box[0])*7,(b-box[1])*7,(c-box[0])*7-1,(e-box[1])*7-1),outline='cyan',width=2);sheet.paste(p,(i*352,40));d.text((i*352,0),f"{r['id']} maker{r['maker_color']}\nraw{r['measurement']['score']}",fill='black')
 sheet.save(OUT/'excluded-maker-controls.png')
if __name__=='__main__':main()
