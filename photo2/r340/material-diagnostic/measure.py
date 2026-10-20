"""Diagnostic only: hand-approved material, fixed contiguous 3x3 minimax RGB."""
from pathlib import Path
import json,time,hashlib,datetime,html
import numpy as np
from PIL import Image,ImageDraw,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
# Local native-pixel rectangles chosen by visual inspection BEFORE measurements.
# All endpoints exclusive. No intensity, pattern, morphology or recentering selects these.
BOXES=[
[18,17,26,25],[22,12,28,18],[26,18,31,25],[26,16,31,22],
[26,20,31,26],[26,23,32,29],[24,11,29,17],[22,15,28,21],
[25,18,29,23],[25,18,29,24],[27,17,32,23],[26,14,31,20],
[25,15,30,21],[26,18,30,24],[18,17,25,23],[26,16,31,22],
[25,18,30,24],[26,16,31,22],[25,17,30,23],[26,17,31,23],
[27,18,32,24],[26,19,31,25],[26,18,31,25],[26,17,31,23],
[24,14,29,23],[23,23,29,30],[25,15,31,24],[24,13,29,23],
[24,13,30,24],[21,23,27,29],[25,22,31,28],[25,13,30,22],
[24,14,29,24],[23,12,29,20],[24,12,29,22],[26,18,31,27],
[25,14,30,22],[23,22,29,29],[24,12,29,21],[23,12,29,23],
[24,13,30,24],[25,12,30,24],[25,14,30,24],[24,18,30,28],
[23,15,29,25],[24,17,30,25],[24,13,30,24],[24,15,30,25]]
def main():
 start=time.monotonic();selection=json.loads((OUT/'selection.json').read_text());rows=selection['records'];assert len(rows)==len(BOXES)==48
 photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');pixels=np.asarray(photo);manual=[]
 for r,box in zip(rows,BOXES):
  x0,y0,x1,y1=box;bx,by=r['bbox'][:2];material=pixels[by+y0:by+y1,bx+x0:bx+x1];v=material.max(axis=2)
  patches=np.lib.stride_tricks.sliding_window_view(v,(3,3)).max(axis=(-2,-1));y,x=np.unravel_index(patches.argmin(),patches.shape);score=int(patches[y,x]);ax=bx+x0+int(x);ay=by+y0+int(y)
  # Independent explicit-loop replay checks the statistic and coordinate indexing.
  brute=min(int(v[j:j+3,i:i+3].max()) for j in range(v.shape[0]-2) for i in range(v.shape[1]-2));assert brute==score
  patch=pixels[ay:ay+3,ax:ax+3];assert int(patch.max())==score
  r.update(local_material_box=box,absolute_material_box=[bx+x0,by+y0,bx+x1,by+y1],patch_box=[ax,ay,ax+3,ay+3],patch_RGB=patch.tolist(),score=score,material_pixel_range=[int(v.min()),int(v.max())],previous_threshold_black=score<73.5)
  manual.append(dict(number=r['number'],id=r['id'],local_material_box=box,selection_basis='Native photograph: connected interior glass away from visible glint, outer rim and adjacent bodies; selected before numerical measurement.'))
  crop=photo.crop(r['bbox']).resize((328,328),Image.Resampling.NEAREST);d=ImageDraw.Draw(crop);d.rectangle((x0*8,y0*8,x1*8-1,y1*8-1),outline='lime',width=2);d.rectangle(((ax-bx)*8,(ay-by)*8,(ax-bx+3)*8-1,(ay-by+3)*8-1),outline='cyan',width=2);crop.save(OUT/f'measured-{r["number"]:02d}.png')
 (OUT/'manual-regions.json').write_text(json.dumps(manual,indent=2)+'\n')
 ranges={c:[min(r['score'] for r in rows if r['color']==c),max(r['score'] for r in rows if r['color']==c)] for c in ['black','red','yellow']};b=ranges['black'][1];c=min(ranges['red'][0],ranges['yellow'][0]);exceptions=[dict(id=r['id'],color=r['color'],score=r['score']) for r in rows if (r['score']<73.5)!=(r['color']=='black')]
 result=dict(records=rows,ranges=ranges,previous_threshold=73.5,previous_threshold_errors=exceptions,overlap=b>=c,separating_threshold_interval=[b,c] if b<c else None,threshold_interval_definition='Black <=t, colored >t: lower endpoint included, upper excluded.',definition='For each genuine-glass 3x3 region wholly inside hand-approved material rectangle, take maximum of all 27 RGB values; select smallest maximum. No pixel averaging.',source_photo_sha256=hashlib.sha256((ROOT/'beads-photo-2.jpg').read_bytes()).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),computation_seconds=time.monotonic()-start,independent_check='All48 vectorized sliding-window minima equal explicit nested-loop minima; all saved patch RGB maxima exact.')
 (OUT/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
 colors={'black':'#20242b','red':'#c82e40','yellow':'#b18c00'};fig,ax=plt.subplots(figsize=(12,6))
 for i,color in enumerate(colors):
  rr=[r for r in rows if r['color']==color];xx=np.array([r['score'] for r in rr]);yy=i+np.linspace(-.18,.18,len(rr));ax.plot(ranges[color],[i,i],color=colors[color],lw=13,alpha=.18);ax.scatter(xx,yy,c=colors[color],s=32,zorder=3)
  for r in [min(rr,key=lambda r:r['score']),max(rr,key=lambda r:r['score'])]:
   j=rr.index(r);ax.annotate(f"{r['id']} ({r['score']})",(r['score'],yy[j]),xytext=(4,19 if r['score']==min(xx) else -29),textcoords='offset points',fontsize=8)
 ax.axvline(73.5,color='#087d74',ls='--',label=f'Earlier threshold 73.5: {len(exceptions)} /48 errors')
 ax.set(xlim=(0,255),ylim=(-.6,2.65),yticks=[0,1,2],yticklabels=[f'Black n=24 [{ranges["black"][0]}, {ranges["black"][1]}]',f'Red n=12 [{ranges["red"][0]}, {ranges["red"][1]}]',f'Yellow n=12 [{ranges["yellow"][0]}, {ranges["yellow"][1]}]'],xlabel='Darkest genuine-glass 3×3 patch: maximum RGB channel and pixel (0–255)',title='48 maker-confirmed bodies — one shared brightness scale')
 ax.grid(axis='x',alpha=.25);ax.legend(loc='lower right');fig.tight_layout();fig.savefig(OUT/'brightness.png',dpi=160);plt.close(fig)
 for page in range(4):
  sheet=Image.new('RGB',(984,1464),'white');d=ImageDraw.Draw(sheet)
  for i,r in enumerate(rows[page*12:page*12+12]):
   ox=i%3*328;oy=i//3*366;sheet.paste(Image.open(OUT/f'measured-{r["number"]:02d}.png'),(ox,oy+32));d.text((ox+2,oy+2),f"{r['number']} {r['id']} {r['color']}: {r['score']}",fill='black')
  sheet.save(OUT/f'measured-page-{page+1:02d}.png')
 print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
