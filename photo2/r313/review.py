"""Small static native-photo evidence, overlays, worst cases and conditional-index plots."""
from pathlib import Path
import html,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import read,save
from .objective import boundaries,Objective

FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)

def tint(rgb,mask,color,alpha=.5):
    result=rgb.copy();result[mask]=(rgb[mask]*(1-alpha)+np.array(color)*alpha).astype(np.uint8);return result

def caption(image,text):
    out=Image.new('RGB',(image.width,image.height+36),'#fafafa');out.paste(image,(0,36));ImageDraw.Draw(out).text((8,8),text,fill='black',font=FONT);return out

def overlay(m,owner,unknown):
    rgb=m['native'].copy();edge=boundaries(owner.reshape(tuple(m['shape'])),unknown.reshape(tuple(m['shape']))).any(0)
    near=ndi.distance_transform_edt(~m['edges'].any(0))<=8
    rgb[edge&~near]=[155,160,170];rgb[edge&near]=[0,240,255]
    return rgb

def run(out):
    out=Path(out);dest=out/'review';dest.mkdir(exist_ok=True);m=dict(np.load(out.parent/'evidence/maps.npz'));doc=read(out.parent/'evidence/freeze.json');engine=Objective(m,doc)
    raw=m['native'];e=raw.copy();e=tint(e,m['material'],[20,255,90],.55);e=tint(e,m['paper'],[45,150,255],.35)
    e[m['uncertain_edges'].any(0)]=[160,160,160];e[m['edges'].any(0)]=[255,170,0];e[m['seams'].any(0)]=[255,255,0]
    # Native original photograph preserved separately, with full context.
    Image.fromarray(raw).save(dest/'original.png');caption(Image.fromarray(e),'Fixed evidence: green material, blue paper, orange transitions, yellow seams, gray uncertain').save(dest/'evidence.png')
    split=raw.copy();split=tint(split,(m['split']==1)&m['roi'],[160,50,255]);split=tint(split,(m['split']==2)&m['roi'],[155,155,155]);caption(Image.fromarray(split),'Purple: comparison; gray: 25px buffers; remaining fixed region: fitting').save(dest/'split.png')
    models={};overlays={}
    for path in sorted((out/'models').glob('*.json.gz')):
        r=read(path);name=r['name'];models[name]=r
        if not (out/'models'/f'{name}.npz').exists():continue
        a=np.load(out/'models'/f'{name}.npz');im=overlay(m,a['owner'],a['unknown']);overlays[name]=im
        caption(Image.fromarray(im),name+' | cyan: boundary near evidence; gray: unsupported predicted edge (not a measured contour)').save(dest/f'{name}-overlay.png')
    after='R313-1' if 'R313-1' in models else 'R312-best';before='R306-2405'
    # Image-only exposure ranking: largest retained photographic cores.
    exposed=sorted(doc['regions'],key=lambda r:-r['pixels'])[:8]
    def atlas(rows,path,kind):
        size=170;w=3*size;h=len(rows)*(size+52);canvas=Image.new('RGB',(w,h),'#fafafa');draw=ImageDraw.Draw(canvas)
        for i,r in enumerate(rows):
            x,y=np.rint(np.array(r['point'])-m['origin']).astype(int);box=(x-40,y-40,x+40,y+40)
            for j,name in enumerate(['evidence',before,after]):
                source=e if name=='evidence' else overlays[name];im=Image.fromarray(source).crop(box).resize((size,size),Image.Resampling.NEAREST);canvas.paste(im,(j*size,i*(size+52)+20));draw.text((j*size+3,i*(size+52)+2),name,fill='black',font=SMALL)
            if kind=='worst':
                q=r['transition'];line=f"({r['point'][0]:.0f},{r['point'][1]:.0f}) missing {r['unexplained_percent']:.1f}% | p95/max {q['p95_px'] or 0:.1f}/{q['max_px'] or 0:.1f}px"
            else:line=f"{r['id']} | {r['pixels']} supported core pixels; full bead extent unknown"
            draw.text((4,i*(size+52)+size+24),line,fill='black',font=SMALL)
        canvas.save(path)
    atlas(exposed,dest/'exposed-before-after.png','exposed')
    worst=models[after]['development']['regions'][:20];save(out/'worst20.json',worst);atlas(worst,dest/'worst20.png','worst')
    # All conditional addresses remain on the axis; absent measurements are unverified.
    fig,axes=plt.subplots(2,2,figsize=(12,7))
    for name,color in [(before,'#666666'),(after,'#0077bb')]:
        r=models[name];rows=r['development']['cores']+r['comparison']['cores']
        for col,lim in enumerate([(-100,99),(-40,40)]):
            a=[v for v in rows if v['index'] is not None]
            axes[0,col].scatter([v['index'] for v in a],[100*(1-v['modal_fraction']) for v in a],s=15,label=name,c=color)
            b=[v for v in a if v['boundary']['p95_px'] is not None]
            axes[1,col].scatter([v['index'] for v in b],[v['boundary']['p95_px'] for v in b],s=15,label=name,c=color)
            for ax in axes[:,col]:ax.set_xlim(lim);ax.axvline(0,c='k',lw=.5);ax.grid(alpha=.2);ax.set_xlabel('Conditional modal physical index; gaps are unmeasured')
    axes[0,0].set_ylabel('Core not explained by one body (%)');axes[1,0].set_ylabel('Nearby supported transition p95 (px)')
    for ax in axes.ravel():ax.legend(fontsize=8)
    fig.suptitle('Material and local transition disagreement; modal labels may change, photographic regions stay fixed')
    fig.tight_layout();fig.savefig(dest/'conditional-index-errors.png',dpi=140);plt.close(fig)
    # CSV-style compact metrics JSON plus human table, fixed data unchanged.
    table=[]
    for name,r in models.items():
        for split in ['development','comparison']:
            q=r.get(split)
            if q:table.append(dict(model=name,split=split,score=q['score'],explained_percent=100-q['material_unexplained_percent'],paper_percent=q['background_intrusion_percent'],modal_percent=q['modal_ownership_percent'],transition_p95_px=q['supported_transition_alignment']['p95_px'],transition_max_px=q['supported_transition_alignment']['max_px'],seam_conflict_percent=q['seam_same_owner_percent']))
    save(out/'table.json',table)
    cells=['<tr><th>Model / set</th><th>Score</th><th>Material explained</th><th>Paper intrusion</th><th>One-body core</th><th>Transition p95 / max</th><th>Seam conflicts</th></tr>']
    for r in table:cells.append(f"<tr><td>{r['model']} / {r['split']}</td><td>{r['score']:.3f}</td><td>{r['explained_percent']:.1f}%</td><td>{r['paper_percent']:.2f}%</td><td>{r['modal_percent']:.1f}%</td><td>{r['transition_p95_px']:.1f} / {r['transition_max_px']:.1f}px</td><td>{r['seam_conflict_percent']:.1f}%</td></tr>")
    pictures=['original.png','evidence.png','split.png']+[f'{name}-overlay.png' for name in models if name in overlays]+['exposed-before-after.png','worst20.png','conditional-index-errors.png']
    body=''.join(f'<h2>{html.escape(p)}</h2><a href="review/{p}"><img src="review/{p}" alt="{html.escape(p)}"></a>' for p in pictures)
    (out/'index.html').write_text('<!doctype html><html><meta charset="utf-8"><title>R313 photographic surface evidence</title><style>body{font:16px system-ui;max-width:1250px;margin:24px auto;padding:15px;background:#f8f8f6;color:#222}img{max-width:100%}td,th{padding:8px;border:1px solid #ccc}table{border-collapse:collapse}p{max-width:950px}</style><h1>R313 — fixed photographic surface evidence</h1><p>Original native photograph. No complete photographic bead contours or black silhouettes are inferred. Gray model edges lack nearby independent support; they are not validated. Orange/yellow photographic transitions are local evidence, not certified external contours or identities. Comparison regions have historical exposure. All necklace bodies occlude; exactly −100…99 are the target physical interval.</p><p><a href="../../R313_REPORT.md">Report</a> · <a href="verification.json">Verification</a> · <a href="worst20.json">Worst 20 locations and measured distances</a></p><table>'+''.join(cells)+'</table>'+body+'</html>')
    print('Review written',out/'index.html',flush=True)

if __name__=='__main__':run(Path('photo2/r313/results'))
