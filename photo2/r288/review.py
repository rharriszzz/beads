"""Original photographs, exact supports and diagnostic routes, without model renders."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r288-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from photo2.r285.run import local_mask
from photo2.r284b.methods import contour
from .common import *
COLORS=dict(J='lime',M='cyan',B='orange',E='gold',W='magenta',H='dodgerblue')

def draw(ax,im,o,m,fill=False):
    ax.imshow(im,interpolation='nearest');r=o['variants'][m];origin=np.array(o['origin']);c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
    if fill:
        mm=local_mask(r['measured_support'],origin,im.shape[:2]);rgba=np.zeros((*mm.shape,4));rgba[mm]=[0,1,1,.5];ax.imshow(rgba,interpolation='nearest')
    if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=.8)
    if r['measured_photo_location'] is not None:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white',ms=6)
    ax.set_title(f'{m}: {r["metrics"]["area"]} native pixels',fontsize=9)

def decision(ax,im,o):
    ax.imshow(im,interpolation='nearest')
    for m in o['selector']['selection']['alternatives']:
        c=np.array(o['variants'][m]['subpixel_contour']).reshape(-1,2)-o['origin']
        if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=.9)
    ax.set_title(o['selector']['status']+' '+','.join(o['selector']['selection']['alternatives']),fontsize=9)

def limits(ax,n=97):
    ax.set_xlim(-.5,n-.5);ax.set_ylim(n-.5,-.5);ax.set_xticks([]);ax.set_yticks([])

def panel(o,name,native,curve):
    x,y=o['origin'];im=native[y:y+97,x:x+97];Image.fromarray(im).save(REVIEW/(name+'-native.png'));origin=np.array(o['origin']);fig,axs=plt.subplots(4,4,figsize=(14,13));axs[0,0].imshow(im,interpolation='nearest');axs[0,0].set_title('Original native photograph')
    for ax,m in zip(axs[0,1:],('J','M','B')):draw(ax,im,o,m)
    for ax,m in zip(axs[1,:3],('E','W','H')):draw(ax,im,o,m)
    decision(axs[1,3],im,o)
    for ax,m in zip(axs[2,:3],('J','M','W')):draw(ax,im,o,m,True)
    ax=axs[2,3];ax.imshow(im);m=local_mask(o['variants']['M']['measured_support'],origin,(97,97));w=local_mask(o['variants']['W']['measured_support'],origin,(97,97));rgba=np.zeros((97,97,4));rgba[w&~m]=[0,1,0,.6];rgba[m&~w]=[1,0,0,.6];ax.imshow(rgba);ax.set_title(f'W vs M: green +{(w&~m).sum()} / red −{(m&~w).sum()}',fontsize=9)
    ax=axs[3,0];ax.imshow(im);cc=curve-origin;cc=cc[np.all((cc>=0)&(cc<97),axis=1)];ax.plot(cc[:,0],cc[:,1],color='white',lw=.8);ax.plot(48,48,'x',color='white');info=o['variants']['W']['method_evidence'];lo=np.array(info['local_origin'])
    for r in info['marker_ledger']:
        if r.get('placed') is not None:ax.plot(*(np.array(r['placed'])+lo),'+',color='gold',ms=4)
    ax.set_title('Photographic cue / centerline / markers',fontsize=9)
    ax=axs[3,1];ax.imshow(im);edges=sorted(info['interfaces'],key=lambda e:(not e['short_interface'],not e['protected']))[:3]
    for edge in edges:
        p=np.array(edge['interface']).reshape(-1,2)+lo;ax.scatter(p[:,0],p[:,1],s=5,color='red' if edge['protected'] else 'yellow')
        for p in edge['corridor']['profiles']:
            rr=np.array(p['route'])+lo;ax.plot(rr[:,0],rr[:,1],color='white',alpha=.4,lw=.5)
    ax.set_title('Exact interface pixels and corridor routes',fontsize=9)
    ax=axs[3,2];examples=o['evidence']['continuation_to_new']['W'].get('route_examples',[])
    for i,p in enumerate(examples):
        t=np.linspace(0,1,len(p['Y']));line=ax.plot(t,p['Y'],label='diffuse'+str(i+1))[0];xy=np.clip(np.rint(p['route']).astype(int),0,96);ax.scatter(t,np.array(o['native_Y'])[xy[:,1],xy[:,0]],s=3,color=line.get_color())
    if edges:
        for p in edges[0]['corridor']['profiles']:ax.plot(np.linspace(0,1,len(p['Y'])),p['Y'],color='gray',alpha=.4,lw=.7)
    ax.set_title('Lines: smoothed Y; dots: native Y\ngray: marker paths',fontsize=8);ax.set_xlabel('fraction along route');ax.legend(fontsize=6)
    ax=axs[3,3];ax.axis('off');text=[o['selector']['status']+' '+','.join(o['selector']['selection']['alternatives']),'R287: '+o['r287_selector']['decision']]
    for m in ('J','M','E','W','H'):
        e=o['evidence']['candidates'][m];text.append(f"{m}: minIoU {e['stability']['minimum_iou']:.2f}, seam {e['coherent_seam_conflicts']}")
    r=o['variants']['W'];text+=['W centroid: '+str(np.round(r['measured_photo_location'],2)),f"W near {r['centerline']['near']}; crossing {r['centerline']['crosses']}",'Physical ownership unknown.','No contour certifies a full body.']
    ax.text(0,1,'\n'.join(text),va='top',fontsize=9)
    for ax in list(axs[:3].flat)+list(axs[3,:2]):limits(ax)
    fig.suptitle(name+' — measured photographic interiors, not physical silhouettes');fig.tight_layout();fig.savefig(REVIEW/(name+'-evidence.png'),dpi=120);plt.close(fig)
    fig,axs=plt.subplots(1,4,figsize=(13,3.7));axs[0].imshow(im,interpolation='nearest');axs[0].set_title('Original pixels')
    for ax,m in zip(axs[1:],('J','M','W')):draw(ax,im,o,m)
    for ax in axs:ax.set_xlim(8,88);ax.set_ylim(88,8);ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle(name+' / J green · M cyan · W magenta — '+o['selector']['status']+' '+','.join(o['selector']['selection']['alternatives']));fig.tight_layout();fig.savefig(REVIEW/(name+'-choice.png'),dpi=135);plt.close(fig)

def main(stage='development'):
    native,_,_=photo();curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);data=read(OUT/(stage+'.json.gz'));manifest=[]
    for q in data['cases']:
        anchor=min(q['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-q['seed']));panel(anchor,q['name'],native,curve);manifest.append(dict(name=q['name'],id=anchor['id'],origin=anchor['origin']))
        fig,axs=plt.subplots(len(q['observations']),4,figsize=(12,2.7*len(q['observations'])),squeeze=False)
        for i,o in enumerate(q['observations']):
            x,y=o['origin'];im=native[y:y+97,x:x+97];axs[i,0].imshow(im);axs[i,0].plot(48,48,'x',color='white');axs[i,0].set_title(o['id']+' / '+o['color']+' / '+o['source_status'],fontsize=7);draw(axs[i,1],im,o,'M');draw(axs[i,2],im,o,'W');decision(axs[i,3],im,o)
            for ax in axs[i]:limits(ax)
        fig.suptitle(q['name']+' — every cue, including overlap, weak cues and abstention');fig.tight_layout(rect=(0,0,1,.98));fig.savefig(REVIEW/(q['name']+'-atlas.png'),dpi=110);plt.close(fig)
        origin=np.array(q['seed'])-72;x,y=origin;im=native[y:y+145,x:x+145];Image.fromarray(im).save(REVIEW/(q['name']+'-group-native.png'));fig,axs=plt.subplots(1,4,figsize=(14,4))
        for ax in axs:ax.imshow(im,interpolation='nearest');limits(ax,145)
        axs[0].set_title('Original neighborhood')
        for ax,method in zip(axs[1:],('J','M','selector')):
            cc=curve-origin;cc=cc[np.all((cc>=0)&(cc<145),axis=1)];ax.plot(cc[:,0],cc[:,1],color='white',lw=.8)
            for i,o in enumerate(q['observations']):
                names=[method] if method!='selector' else o['selector']['selection']['alternatives']
                for m in names:
                    c=np.array(o['variants'][m]['subpixel_contour']).reshape(-1,2)-origin
                    if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=.8)
                p=np.array(o['seed'])-origin;ax.text(*p,str(i+1),color='white',fontsize=7)
            ax.set_title(method+' / support geometry')
        fig.suptitle(q['name']+' — observations are not verified distinct beads');fig.tight_layout();fig.savefig(REVIEW/(q['name']+'-group.png'),dpi=120);plt.close(fig)
    save(OUT/(stage+'-review-manifest.json'),manifest)
if __name__=='__main__':
    import sys
    main(sys.argv[1] if len(sys.argv)>1 else 'development')
