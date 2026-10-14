"""Native-mask evidence panels and a self-contained local comparison viewer."""
import html,textwrap,csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from photo2.r282.common import ROOT,photo,read,save,pixels
from .run import OUT
REVIEW=ROOT/'photo2/review/r284a'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COLORS={'high':'#24ffff','unresolved':'#ff6ff0','rejected':'#aaaabb','secondary':'#ffa338','medium':'#ffff60'}

def font(size):return ImageFont.truetype(FONT,size)

def annotated(raw,origin,rows,curve,fill=False):
    a=np.asarray(raw).copy();h,w=a.shape[:2];origin=np.array(origin)
    for r in rows:
        p=pixels(r['measured_support'])-origin
        if not len(p):continue
        p=p[(p[:,0]>=0)&(p[:,0]<w)&(p[:,1]>=0)&(p[:,1]<h)]
        mask=np.zeros((h,w),bool);mask[p[:,1],p[:,0]]=True
        mark=mask if fill else mask&~ndi.binary_erosion(mask)
        color=tuple(bytes.fromhex(COLORS[r['status']][1:]))
        a[mark]=(.45*a[mark]+.55*np.array(color)).astype(np.uint8) if fill else color
    im=Image.fromarray(a).resize((w*3,h*3),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
    q=(np.array(curve)-origin)*3;inside=(q[:,0]>=0)&(q[:,0]<w*3)&(q[:,1]>=0)&(q[:,1]<h*3);ix=np.flatnonzero(inside)
    for i,j in zip(ix[:-1],ix[1:]):
        if j-i==1:d.line([tuple(q[i]),tuple(q[j])],fill='white',width=1)
    for n,r in enumerate(rows,1):
        s=(np.array(r['seed'])-origin)*3+1
        if 0<=s[0]<w*3 and 0<=s[1]<h*3:
            d.line((s[0]-3,s[1]-3,s[0]+3,s[1]+3),fill='#ffad35',width=1);d.line((s[0]-3,s[1]+3,s[0]+3,s[1]-3),fill='#ffad35',width=1)
        if not r['measured_photo_location']:continue
        x,y=(np.array(r['measured_photo_location'])-origin)*3+1
        d.ellipse((x-2,y-2,x+2,y+2),fill='white')
        d.text((x+4,y+2),str(n),font=font(12),fill=COLORS[r['status']],stroke_width=1,stroke_fill='black')
    return im


def write_wrapped(draw,xy,text,width=140,size=18):
    y=xy[1]
    for p in text.split('\n'):
        for line in textwrap.wrap(p,width=width) or ['']:
            draw.text((xy[0],y),line,font=font(size),fill='white');y+=size+6
    return y


def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,_,_=photo();photoim=Image.fromarray(native);curve=read(ROOT/'photo2/r282/results/centerline.json')['points'];cases=read(OUT/'cases.json')
    notes=read(OUT/'review-assessment.json') if (OUT/'review-assessment.json').exists() else {}
    panels=[];sections=[];csvrows=[]
    for case in cases:
        name=case['name'];res=read(OUT/(name+'.json.gz'));x,y=case['origin'];raw=photoim.crop((x,y,x+128,y+128));raw.save(REVIEW/(name+'-native.png'));raw.resize((512,512),Image.Resampling.NEAREST).save(REVIEW/(name+'-enlarged.png'))
        columns=[('Raw photograph',None),('R283 preserved masks',res['baseline'])]+[(m+' — '+{'A':'thickness pruning','B':'competing owners','C':'rays + reflections'}[m],res['methods'][m]['records']) for m in 'ABC']
        captions=[]
        for m in 'ABC':
            s=res['methods'][m]['summary'];caption=f"{m}: {s['high_near']} high support-near; {s['high_crossing']} high interior-crossing; {s['overlap_pairs']} overlapping candidate pairs; {s['status'].get('secondary',0)} suspected secondary features. "
            caption+=notes.get(name,{}).get(m,'High is uncalibrated; count differences are not verified additional beads. See the native supports and per-record reasons.')
            captions.append(caption)
        caption=case['selection_rule']+'\n'+'\n'.join(captions)+'\nKey: cyan high; magenta unresolved; gray rejected; orange secondary hypothesis. White curve = saved image centerline; orange × = cue, white dot = support centroid; numbers link to tables. Top: exact native support edges. Bottom: tinted measured pixels. These are interiors, not body silhouettes. No fitted physical centers or indices.'
        lines=sum(max(1,len(textwrap.wrap(p,140))) for p in caption.split('\n'))
        canvas=Image.new('RGB',(2000,872+lines*24),(24,29,36));d=ImageDraw.Draw(canvas);d.text((16,8),'R284A / '+name+' — same pixels, three native ownership methods',font=font(24),fill='white')
        for j,(label,rows) in enumerate(columns):
            xx=16+j*397;d.text((xx,48),label,font=font(19),fill='white')
            for k,fill in enumerate((False,True)):
                im=raw.resize((384,384),Image.Resampling.NEAREST) if rows is None else annotated(raw,case['origin'],rows,curve,fill)
                canvas.paste(im,(xx,78+k*394))
        write_wrapped(d,(16,868),caption);canvas.save(REVIEW/(name+'.png'))
        panels.append(dict(file=name+'.png',title=name,caption=caption))
        detail=[]
        for m in 'ABC':
            table=[]
            for n,r in enumerate(res['methods'][m]['records'],1):
                c=r['centerline'];entry=dict(case=name,method=m,number=n,id=r['record_id'],color=r['color'],status=r['status'],seed=r['seed'],centroid=r['measured_photo_location'],area=r['metrics']['area'],side=c['side'],near=c['near'],min_distance=c['unsigned_support_distance'],signed_extent=c['signed_extent'],arc_px=c['arc_px'],arc_extent=c['arc_interval_relative'],secondary_of=r['secondary_of'],reasons='; '.join(r['notes']))
                csvrows.append(entry)
                distance='—' if c['unsigned_support_distance'] is None else f"{c['unsigned_support_distance']:.1f}"
                extent='—' if c['signed_extent'] is None else ' / '.join(f'{v:.1f}' for v in c['signed_extent'])
                table.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [n,r['record_id'],r['color'],r['status'],r['metrics']['area'],r['seed'],r['measured_photo_location'],c['side'],c['near'],distance,extent,round(c['arc_px'],1),r['secondary_of'] or '',entry['reasons']])+'</tr>')
            detail.append('<details><summary>Method '+m+' — all measurements and reasons</summary><div class="scroll"><table><tr>'+''.join('<th>'+s+'</th>' for s in ['#','Cue ID','Color','Status','Pixels','Cue (native)','Centroid','Side','Near','Min distance','Signed extent','Arc station','Secondary of','Reasons'])+'</tr>'+''.join(table)+'</table></div></details>')
        sections.append(f'<section id="{name}"><h2>{name}</h2><p>{html.escape(case["selection_rule"])}</p><a href="{name}.png"><img class="comparison" src="{name}.png" alt="{name} raw baseline and ABC comparison"></a><p><a href="{name}-native.png">Native 128×128 crop</a> · <a href="{name}-enlarged.png">4× enlargement</a> · <a href="../../r284/results/{name}.json.gz">Exact mask records</a></p><div class="native"><img src="{name}-native.png" width="128" height="128" alt="native unscaled {name}"></div>'+''.join('<p>'+html.escape(c)+'</p>' for c in captions)+''.join(detail)+'</section>')
    with (REVIEW/'measurements.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(csvrows[0]),lineterminator="\n");writer.writeheader();writer.writerows(csvrows)
    save(REVIEW/'panels.json',panels)
    totals=read(OUT/'summary.json')['totals']
    overview='<table><tr><th>Method</th><th>High near cues</th><th>High crossing interiors</th><th>Overlap pairs</th><th>Secondary hypotheses</th></tr>'+''.join('<tr>'+''.join(f'<td>{v}</td>' for v in [m,*[totals[m][k] for k in ('high_near','high_crossing','overlap_pairs','secondary_pairs')]])+'</tr>' for m in 'ABC')+'</table>'
    (REVIEW/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>R284A Phase 1 method choice</title><style>body{background:#181d24;color:#eee;font:18px/1.5 sans-serif;max-width:1600px;margin:24px auto;padding:16px}a{color:#5ee4ef}.comparison{width:100%}section{margin:55px 0}table{border-collapse:collapse;font-size:14px}td,th{border:1px solid #556;padding:6px;text-align:left}.scroll{overflow:auto}summary{cursor:pointer;padding:12px} .native img{image-rendering:pixelated}</style><h1>R284A: compare Phase 1 methods before adoption</h1><p>A: thickness-core pruning. B: geodesic ownership competition. C: straight-path color supports plus reflection/body separation. Eight bounded photographic cases; no production inventory replaced.</p><p>Goal: find every centerline-crossing bead and supported neighbors on both sides. This comparison does not establish that goal has been met. Interior crossing understates full-body crossing. High means algorithmic gates passed; physical distinctness and real recall remain uncalibrated.</p><p><a href="../../R284A_REPORT.md">Report and recommendation</a> · <a href="measurements.csv">All measurements CSV</a> · <a href="../r283/index.html">Preserved R283 review</a></p>'+overview+'<nav>'+ ' · '.join(f'<a href="#{c["name"]}">{c["name"]}</a>' for c in cases)+'</nav>'+''.join(sections)+'</html>')
    print('Saved',len(panels),'comparison panels and',len(csvrows),'measurement rows')

if __name__=='__main__':main()
