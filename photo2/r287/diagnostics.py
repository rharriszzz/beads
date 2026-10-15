"""Review-only perturbation and full-neighborhood coverage panels."""
from .review import *

def main():
    native,_,_=photo();data={stage:read(OUT/(stage+'.json.gz'))['cases'] for stage in ('development','confirmation')};selected=[]
    for stage,names in [('development',('P5','P2')),('confirmation',('N06','N07','N11','N13'))]:
        for name in names:
            case=next(q for q in data[stage] if q['name']==name);o=min(case['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-case['seed']));origin=np.array(o['origin']);x,y=origin;im=native[y:y+97,x:x+97];fig,axs=plt.subplots(1,5,figsize=(16,4));axs[0].imshow(im,interpolation='nearest');axs[0].set_title('Original pixels')
            draw(axs[1],im,o,'J');draw(axs[2],im,o,'M');worst=min(o['variants']['M']['perturbations'],key=lambda p:p['iou']);mask=local_mask(worst['support'],origin,(97,97));axs[3].imshow(im,interpolation='nearest');axs[3].contour(mask,levels=[.5],colors=['red'],linewidths=.8);axs[3].set_title(f"M under {worst['name']}\n{worst['area']}px; IoU {worst['iou']:.2f}")
            stack=np.array([local_mask(p['support'],origin,(97,97)) for p in o['variants']['M']['perturbations']]);axs[4].imshow(im,interpolation='nearest');vote=stack.mean(0);rgba=np.zeros((97,97,4));rgba[:,:,0]=1;rgba[:,:,3]=np.where((vote>0)&(vote<1),.6,0);axs[4].imshow(rgba);axs[4].set_title('Red: M perturbations disagree\nNot an ownership probability')
            for ax in axs:ax.set_xlim(0,96);ax.set_ylim(96,0);ax.set_xticks([]);ax.set_yticks([])
            fig.suptitle(name+' — '+o['selector']['status']+'; instability does not prove the alternative is good');fig.tight_layout();fig.savefig(REVIEW/(name+'-stability.png'),dpi=125);plt.close(fig);selected.append(dict(name=name,method='M',worst=worst['name'],iou=worst['iou'],area=worst['area']))
    for stage,cases in data.items():
        for case in cases:
            if len(case['observations'])==1:continue
            origin=np.array(case['seed'])-72;x,y=origin;im=native[y:y+145,x:x+145];Image.fromarray(im).save(REVIEW/(case['name']+'-group-native.png'));fig,axs=plt.subplots(1,5,figsize=(16,4))
            for ax,m in zip(axs,('raw','J','M','B','selector')):
                ax.imshow(im,interpolation='nearest');ax.set_title(m+' / all nearby observations');ax.set_xticks([]);ax.set_yticks([]);ax.set_xlim(0,144);ax.set_ylim(144,0)
                if m=='raw':continue
                curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points'])-origin;curve=curve[np.all((curve>=0)&(curve<145),axis=1)];ax.plot(curve[:,0],curve[:,1],color='white',lw=.8)
                for o in case['observations']:
                    names=[m] if m!='selector' else o['selector']['selection']['alternatives']
                    for name in names:
                        r=o['variants'][name];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
                        if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[name],lw=.6)
            fig.suptitle(case['name']+' — both alternatives retained separately; no outline for abstentions');fig.tight_layout();fig.savefig(REVIEW/(case['name']+'-group.png'),dpi=125);plt.close(fig)
    save(OUT/'stability-review.json',selected)
    save(OUT/'black-preservation.json',dict(source='photo2/r286/results/reflection-stability.json',sha256=sha(OLD/'reflection-stability.json'),previous_exact_replays=144,retained_default='R2',alternatives=['R1','R4'],physical_owner=None,statement='No R287 black redesign/re-estimation; existing reflection-only records and R286 replay evidence preserved unchanged.'))
if __name__=='__main__':main()
