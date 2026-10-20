"""All fixed208 conflict responsibilities and native contexts; no relabeling."""
import argparse
from PIL import ImageDraw
from .common import *

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);g,obs,co=baseline();p=read(ROOT/'photo2/r337/results/pattern208.json');r334={r['id']:r for r in read(ROOT/'photo2/r334/classification/audit.json.gz')['records']};r335={r['id']:r for r in read(ROOT/'photo2/r335/results/application.json.gz')['records']};core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']);rows=[]
    for slot in p['entries']:
        if slot['status']!='conflict':continue
        largest=max(slot['counts'].values());winners=[c for c,n in slot['counts'].items() if n==largest]
        for o in slot['ids']:
            a=r334.get(o,{});b=r335.get(o,{});row=dict(id=o,xy=obs[o]['xy'],ab=co[o],residue=slot['residue'],color=obs[o]['color'],counts=slot['counts'],minority=obs[o]['color'] not in winners,plurality_tied=len(winners)>1,core710=o in core,R334_prediction=a.get('body_prediction'),R334_black_decision=a.get('black_test',{}).get('decision'),R335_compact=b.get('compact_decision'),maker_reviewed=bool(a.get('maker_reviewed') or b.get('maker_accepted') or 'maker' in str(obs[o]).lower()),source=obs[o].get('source'),body_identity='current working observation; no new certification from classifier')
            rows.append(row)
    targets=[r for r in rows if r['minority']];targets.sort(key=lambda r:(not r['core710'],r['residue'],r['id']));photo=Image.fromarray(photograph());keys=[]
    for i,r in enumerate(targets):
        x,y=np.rint(r['xy']).astype(int);box=[x-65,y-60,x+66,y+61];crop=photo.crop(box);crop.save(out/f'target-{i+1:02d}-native.png');im=crop.resize((393,363),Image.Resampling.NEAREST);d=ImageDraw.Draw(im);names=sorted([o for o in co if box[0]+3<obs[o]['xy'][0]<box[2]-3 and box[1]+3<obs[o]['xy'][1]<box[3]-3],key=lambda o:(o!=r['id'],obs[o]['xy'][1],obs[o]['xy'][0]));key=[dict(number=j+1,id=o,color=obs[o]['color'],xy=obs[o]['xy'],ab=co[o]) for j,o in enumerate(names)]
        for k in key:
            xx=(k['xy'][0]-box[0])*3;yy=(k['xy'][1]-box[1])*3;d.text((xx+3,yy-9),str(k['number']),fill='white',stroke_width=1,stroke_fill='black');d.ellipse((xx-2,yy-2,xx+2,yy+2),outline='white')
        im.save(out/f'target-{i+1:02d}-numbered.png');keys.append(dict(r,number=i+1,bbox=box,key=key))
    for page in range((len(targets)+8)//9):
        sheet=Image.new('RGB',(393*3,387*3),'white');d=ImageDraw.Draw(sheet)
        for j in range(9):
            i=page*9+j
            if i>=len(targets):break
            x=(j%3)*393;y=(j//3)*387;r=targets[i];sheet.paste(Image.open(out/f'target-{i+1:02d}-numbered.png'),(x,y+24));d.text((x+3,y+4),f"{i+1} {r['id']} r{r['residue']} {r['color']}",fill='black')
        sheet.save(out/f'sheet-{page+1:02d}.png')
    save(out/'responsibilities.json',dict(records=rows,minority_targets=keys,conflicted_residues=[r['residue'] for r in p['entries'] if r['status']=='conflict'],policy='Tied pluralities are retained. Minority means outside a largest observed color group, not a proven bad label. Historical masks/classifiers are evidence only; authoritative labels remain unchanged.'))
    print('CONFLICTS',len(rows),'records',len(targets),'minority outside tied modes')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
