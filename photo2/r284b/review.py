"""Native photographic review: plotting only, no measurement edits."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r284b-mpl')
from pathlib import Path
import html
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r282.common import ROOT,photo,read,save,pixels
from photo2.r284.assess import TARGETS
from .run import OUT,mask_of
from .methods import COLOR_METHODS,BLACK_METHODS
REVIEW=ROOT/'photo2/review/r284b'
LABELS={'A':'Original A','T':'T: thickness','E':'E: brightness flood','W':'W: watershed','L':'L: edge level set','I':'I: local isophote','J':'J: I wide-domain control','R283':'R283 baseline','R1':'R1: smooth isophote','R2':'R2: adaptive isophote','R3':'R3: gradient snake','R4':'R4: competing isophote'}

def get_target(data,xy):return min(data['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-xy))

def draw(ax,r,origin,color='cyan',fill=False):
    p=pixels(r['measured_support'])-origin
    if len(p):
        if fill:ax.scatter(p[:,0],p[:,1],s=9,c=color,alpha=.38,marker='s',linewidths=0)
        curve=np.array(r['subpixel_contour'])-origin
        if len(curve):ax.plot(curve[:,0],curve[:,1],color=color,lw=1)
        cen=np.array(r['measured_photo_location'])-origin;ax.plot(*cen,'+',color='white',ms=8,mew=1)
    seed=np.array(r['seed'])-origin;ax.plot(*seed,'x',color='orange',ms=5)
    if r['peak_location']:
        peak=np.array(r['peak_location'])-origin;ax.plot(*peak,'.',color='lime',ms=4)

def focus(native,curve,data,targets,path):
    isblack=get_target(data,targets[0][1])['color']=='black';methods=BLACK_METHODS if isblack else COLOR_METHODS
    rows=3 if isblack or len(targets)==1 else len(targets)*2
    fig,axs=plt.subplots(rows,len(methods)+1,figsize=(3*(len(methods)+1),2.8*rows),squeeze=False)
    table=[]
    for ti,(label,xy) in enumerate(targets):
        ob=get_target(data,xy);origin=np.array(ob['origin']);x,y=origin;im=native[y:y+49,x:x+49];lum=np.array(ob['native_Y']);initial=mask_of(ob['initial_support'],origin)
        row=0 if isblack or len(targets)==1 else ti*2
        axs[row,0].imshow(im,interpolation='nearest');axs[row,0].set_title(label+'\nRaw pixels enlarged',fontsize=10)
        axs[row+1,0].imshow(lum,cmap='magma',vmin=0,vmax=lum.max());axs[row+1,0].contour(initial,levels=[.5],colors=['cyan'],linewidths=.7);axs[row+1,0].set_title('Native linear Y / initial A',fontsize=10)
        if rows==3:
            ax=axs[2,0];ax.plot(lum[24,:],label='horizontal');ax.plot(lum[:,24],label='vertical');ax.legend(fontsize=7);ax.set_title('Native profiles through cue');ax.set_xlabel('native pixel')
        for col,method in enumerate(methods,1):
            ax=axs[row,col];ax.imshow(im,interpolation='nearest');r=ob['variants'].get(method)
            if r is None:ax.set_title(method+' absent');continue
            cc=curve-origin;ax.plot(cc[:,0],cc[:,1],color='#79baff',ls='--',lw=.7);draw(ax,r,origin)
            met=r['metrics'];shift=met['centroid_shift'];ax.set_title(f"{LABELS[method]}\n{met['area']} px; shift {shift:.2f}px" if shift is not None else LABELS[method]+' empty',fontsize=10)
            ax=axs[row+1,col];m=mask_of(r['measured_support'],origin);ax.imshow(lum,cmap='gray',vmin=0,vmax=lum.max(),interpolation='nearest');ax.imshow(np.ma.masked_where(~m,m),cmap='cool',alpha=.4,vmin=0,vmax=1,interpolation='nearest');draw(ax,r,origin)
            ax.set_title(f"Native support: −{met['removed']} +{met['added']} px\n{r['centerline']['side']}; near={r['centerline']['near']}",fontsize=9)
            if rows==3:
                ax=axs[2,col];p=r.get('peak_location') or ob['seed'];px,py=np.rint(np.array(p)-origin).astype(int)
                ax.plot(lum[py,:],label='horizontal Y');ax.plot(lum[:,px],label='vertical Y');ax.plot(np.where(m[py,:])[0],lum[py,m[py,:]],'.',color='cyan',ms=4)
                if 'level' in r['method_evidence']:ax.axhline(r['method_evidence']['level'],color='orange',ls='--',label='smooth level')
                ax.legend(fontsize=6);ax.set_title(f"boundary gradient {met['boundary_gradient'] or 0:.4f}\nturn energy {met['turn_energy'] or 0:.3f}",fontsize=9)
            table.append(dict(feature=label,method=method,**met,centerline=r['centerline'],evidence=r['method_evidence']))
    for i,row in enumerate(axs):
        for ax in row:
            if rows!=3 or i<2:ax.set_xlim(-.5,48.5);ax.set_ylim(48.5,-.5);ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle(data['case']['name']+' — cyan boundary, native filled support, white centroid, orange cue, green peak; dashed blue centerline\nSupports are photographic measurements. Black-body ownership/crossing unresolved.',fontsize=13)
    fig.tight_layout(rect=[0,0,1,.965]);fig.savefig(path,dpi=130);plt.close(fig)
    return table

def overview(native,curve,data,path):
    origin=np.array(data['case']['origin']);x,y=origin;im=native[y:y+128,x:x+128]
    methods=['raw',*COLOR_METHODS,'R1','R2','R3','R4'];fig,axs=plt.subplots(3,4,figsize=(16,12))
    for ax,method in zip(axs.flat,methods):
        ax.imshow(im,interpolation='nearest');cc=curve-origin
        if method!='raw':
            ax.plot(cc[:,0],cc[:,1],color='#79baff',lw=.7,ls='--')
            for ob in data['observations']:
                r=ob['variants'].get(method)
                if r:draw(ax,r,origin,{'red':'#ff6969','yellow':'#ffed55','black':'#ff68e9'}[ob['color']])
        ax.set_title('Raw native crop enlarged' if method=='raw' else LABELS[method]);ax.set_xlim(0,128);ax.set_ylim(128,0);ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle(data['case']['name']+' — all retained cues, including unresolved; A includes historical black collars. R1–R3 show reflections only.');fig.tight_layout();fig.savefig(path,dpi=130);plt.close(fig)

def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,_,_=photo();curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);cases=read(OUT/'cases.json');tables={};sections=[]
    for case in cases:
        name=case['name'];data=read(OUT/(name+'.json.gz'));x,y=case['origin'];Image.fromarray(native[y:y+128,x:x+128]).save(REVIEW/(name+'-native.png'))
        overview(native,curve,data,REVIEW/(name+'-overview.png'))
        if name in TARGETS:
            targets=TARGETS[name]
            if name=='duplicate':targets=[targets[0]]
            tables[name]=focus(native,curve,data,targets,REVIEW/(name+'-focus.png'))
            if name=='duplicate':
                tables['secondary']=focus(native,curve,data,[TARGETS[name][1]],REVIEW/'secondary-focus.png')
                tables['red-neighbor']=focus(native,curve,data,[TARGETS[name][2]],REVIEW/'red-neighbor-focus.png')
        sections.append(f'<section id="{name}"><h2>{name}</h2><p>{html.escape(case["selection_rule"])}</p><p>Native 128 × 128 crop:</p><img class="native" src="{name}-native.png">'+
            (f'<a href="{name}-focus.png"><img src="{name}-focus.png"></a>' if name in TARGETS else '')+
            f'<details><summary>All cues and alternatives on this crop</summary><a href="{name}-overview.png"><img src="{name}-overview.png"></a></details><p><a href="../../r284b/results/{name}.json.gz">Exact supports, contours, profiles, provenance and pair diagnostics</a></p></section>')
    save(OUT/'focus-metrics.json',tables)
    body='''<!doctype html><html lang="en"><meta charset="utf-8"><title>R284B photographic measurements</title><style>body{font:17px system-ui;margin:24px;max-width:1700px;background:#17191c;color:#eee}a{color:#83caff}img{max-width:100%;height:auto}img.native{width:128px;height:128px;image-rendering:pixelated}section{border-top:1px solid #555;margin-top:32px}summary{cursor:pointer;padding:12px}table{border-collapse:collapse}td,th{border:1px solid #666;padding:7px}</style><h1>R284B — photographic interiors and specular reflections</h1><p>Method comparison only. Production unchanged. Black measurements are reflections, never inferred dark bodies. Click images for full resolution.</p><p><a href="../../R284B_REPORT.md">Report and recommendation</a> · <a href="../../R284B_SPECIFICATION.md">Complete specification</a> · <a href="../../R284B_ALGORITHM_EXPLANATION.md">Existing algorithm explained</a> · <a href="../../r284b/results/focus-metrics.json">Principal numerical comparisons</a></p><p>Native masks (filled cells) and independent subpixel curves are separate. White + = measured centroid, orange × = input cue, green dot = intensity peak, dashed blue = image-derived centerline. No curve establishes a physical bead center.</p>'''
    body+=''.join(sections[:3])+'''<details><summary>Secondary reflection and red neighboring comparison</summary><img src="secondary-focus.png"><img src="red-neighbor-focus.png"></details><h2>Automatically selected validation</h2>'''+''.join(sections[3:])+'</html>'
    (REVIEW/'index.html').write_text(body)
    print('review generated',len(cases),'cases',flush=True)

if __name__=='__main__':main()
