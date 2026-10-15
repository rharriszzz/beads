"""Actual photographic review; no synthetic image editing or modified native crops."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r287-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from photo2.r285.run import local_mask
from .common import *
COLORS=dict(J='lime',M='cyan',B='orange')

def draw(ax,im,o,method,fill=False,background=True):
    origin=np.array(o['origin']);r=o['variants'][method];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
    if background:ax.imshow(im,interpolation='nearest')
    if fill:
        mask=local_mask(r['measured_support'],origin,(97,97));rgba=np.zeros((97,97,4));rgba[mask]=[0,1,1,.45];ax.imshow(rgba,interpolation='nearest')
    if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[method],lw=.8)
    if r['measured_photo_location']:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white',ms=6)
    ax.set_title(f'{method}: {r["metrics"]["area"]} native pixels',fontsize=10)

def panel(o,name,native):
    x,y=o['origin'];im=native[y:y+97,x:x+97];Image.fromarray(im).save(REVIEW/(name+'-native.png'));e=o['evidence'];decision=o['selector']['selection'];fig,axs=plt.subplots(3,4,figsize=(14,10));axs[0,0].imshow(im,interpolation='nearest');axs[0,0].set_title('Original native pixels enlarged')
    for ax,m in zip(axs[0,1:],('J','M','B')):draw(ax,im,o,m)
    axs[1,0].imshow(im,interpolation='nearest');init=local_mask(o['initial_support'],np.array(o['origin']),(97,97));axs[1,0].contour(init,levels=[.5],colors=['gold'],linewidths=.7);axs[1,0].plot(48,48,'x',color='white');curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points'])-o['origin'];curve=curve[np.all((curve>=0)&(curve<97),axis=1)];axs[1,0].plot(curve[:,0],curve[:,1],color='white',lw=.8);axs[1,0].set_title('Cue / centerline / inherited A input')
    draw(axs[1,1],im,o,'J',True);draw(axs[1,2],im,o,'M',True)
    ax=axs[1,3];ax.imshow(im,interpolation='nearest')
    for m in decision['alternatives']:draw(ax,im,o,m,background=False)
    ax.set_title(decision['decision'],fontsize=10)
    ax=axs[2,0];ax.imshow(im,interpolation='nearest');routes=e.get('diffuse_routes',{});pts=np.array(routes.get('pixels',[]),int).reshape(-1,2);bad=np.array(routes.get('rejected_pixels',[]),int).reshape(-1,2)
    rgba=np.zeros((97,97,4));
    if len(pts):rgba[pts[:,1],pts[:,0]]=[0,1,0,.5]
    if len(bad):rgba[bad[:,1],bad[:,0]]=[1,0,0,.6]
    ax.imshow(rgba);ax.set_title('M-only pigment: green route-supported / red uncertain',fontsize=8)
    ax=axs[2,1];ax.imshow(im,interpolation='nearest');seams=sorted(e['seams'],key=lambda q:(not q['coherent_seam'],q['distance']))[:3]
    for q in seams:
        for p in q['profiles']:
            xy=np.array(p['route']);ax.plot(xy[:,0],xy[:,1],color='red' if q['coherent_seam'] else 'yellow',lw=.5,alpha=.7)
    ax.set_title('Five nearby paths per marker pair\nred: coherent valley / yellow: inconclusive',fontsize=8)
    ax=axs[2,2]
    for i,p in enumerate(routes.get('route_examples',[])):
        t=np.linspace(0,1,len(p['Y']));line=ax.plot(t,p['Y'],label=f'diffuse route{i+1}')[0];xy=np.clip(np.rint(p['route']).astype(int),0,96);raw=np.array(o['native_Y'])[xy[:,1],xy[:,0]];ax.scatter(t,raw,s=3,color=line.get_color(),alpha=.6)
    if seams:
        q=seams[0]
        for p in q['profiles']:ax.plot(np.linspace(0,1,len(p['Y'])),p['Y'],color='gray',alpha=.5,lw=.7)
    ax.set_title('Lines: smoothed Y; dots: native Y\ngray: marker corridor; colored: diffuse continuation',fontsize=8);ax.set_xlabel('fraction along photographed route');ax.legend(fontsize=6)
    ax=axs[2,3];ax.axis('off');lines=[decision['decision'],f"J/M IoU {e['agreement_iou']:.2f}",f"Diffuse routes: {routes.get('supported_pixels',0)}/{routes.get('eligible_pixels',0)}"]
    for m in ('J','M'):
        c=e['candidates'][m];s=c['stability'];lines.extend([f"{m}: min stability {s['minimum_iou']:.2f}, domain {s['domain_minimum_iou']:.2f}",f"  seam conflicts {c['coherent_seam_conflicts']}"])
    import textwrap
    lines+=textwrap.wrap(decision['reasons'][0],47);lines+=['Unrated preference; physical owner unknown.'];ax.text(0,1,'\n'.join(lines),va='top',fontsize=9)
    for ax in list(axs[:2].flat)+list(axs[2,:2]):ax.set_xlim(-.5,96.5);ax.set_ylim(96.5,-.5);ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle(name+' / '+o['color']+' — white + is photographic centroid, not physical bead center');fig.tight_layout();fig.savefig(REVIEW/(name+'-evidence.png'),dpi=125);plt.close(fig)
    # Direct review strip; no hidden support union for a both decision.
    fig,axs=plt.subplots(1,4,figsize=(13,3.7));axs[0].imshow(im,interpolation='nearest');axs[0].set_title('Original pixels')
    draw(axs[1],im,o,'J');draw(axs[2],im,o,'M');axs[3].imshow(im,interpolation='nearest')
    for m in decision['alternatives']:
        c=np.array(o['variants'][m]['subpixel_contour']).reshape(-1,2)-o['origin']
        if len(c):axs[3].plot(c[:,0],c[:,1],color=COLORS[m],lw=1)
    axs[3].set_title(decision['decision'],fontsize=10)
    for ax in axs:ax.set_xlim(8,88);ax.set_ylim(88,8);ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle(name+' / J green, M cyan; both = separate alternatives');fig.tight_layout();fig.savefig(REVIEW/(name+'-choice.png'),dpi=135);plt.close(fig)

def main(stage='development'):
    native,_,_=photo();data=read(OUT/(stage+'.json.gz'));manifest=[]
    for case in data['cases']:
        obs=case['observations'];anchor=min(obs,key=lambda o:np.linalg.norm(np.array(o['seed'])-case['seed']));panel(anchor,case['name'],native);manifest.append(dict(name=case['name'],id=anchor['id'],origin=anchor['origin']))
        if case['name']=='C02':
            edge=next(o for o in obs if o['id']=='E9-2263-1691');panel(edge,'C02-edge',native);manifest.append(dict(name='C02-edge',id=edge['id'],origin=edge['origin']))
        if len(obs)>1:
            fig,axs=plt.subplots(len(obs),4,figsize=(12,2.7*len(obs)),squeeze=False)
            for i,o in enumerate(obs):
                x,y=o['origin'];im=native[y:y+97,x:x+97];axs[i,0].imshow(im,interpolation='nearest');axs[i,0].plot(48,48,'x',color='orange');axs[i,0].set_title(o['id']+' / '+o['source_status'],fontsize=8)
                for ax,m in zip(axs[i,1:3],('J','M')):draw(ax,im,o,m)
                axs[i,3].imshow(im,interpolation='nearest')
                for m in o['selector']['selection']['alternatives']:
                    c=np.array(o['variants'][m]['subpixel_contour']).reshape(-1,2)-o['origin']
                    if len(c):axs[i,3].plot(c[:,0],c[:,1],color=COLORS[m],lw=.8)
                axs[i,3].set_title(o['selector']['status'],fontsize=9)
                for ax in axs[i]:ax.set_xlim(8,88);ax.set_ylim(88,8);ax.set_xticks([]);ax.set_yticks([])
            fig.suptitle(case['name']+' — every nearby cue, including disagreements/abstentions');fig.tight_layout();fig.savefig(REVIEW/(case['name']+'-atlas.png'),dpi=110);plt.close(fig)
    save(OUT/(stage+'-review-manifest.json'),manifest)
if __name__=='__main__':
    import sys
    main(sys.argv[1] if len(sys.argv)>1 else 'development')
