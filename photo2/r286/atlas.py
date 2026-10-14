"""All confirmation cues, including weak/fresh failures, without selection hiding."""
from .review import *
def main():
    native,_,_=photo();cases=read(OUT/'confirmation.json.gz')['cases'];manifest=[]
    for case in cases:
        obs=case['observations'];fig,axs=plt.subplots(len(obs),7,figsize=(17,2.5*len(obs)),squeeze=False)
        for i,o in enumerate(obs):
            origin=np.array(o['origin']);x,y=origin;im=native[y:y+97,x:x+97]
            for j,m in enumerate(['raw']+list(o['variants'])):
                ax=axs[i,j];ax.imshow(im,interpolation='nearest');ax.set_xlim(10,86);ax.set_ylim(86,10);ax.set_xticks([]);ax.set_yticks([])
                if m=='raw':ax.plot(48,48,'x',color='orange');ax.set_title(o['id']+'\n'+o['color']+' / '+o['source_status'],fontsize=7);continue
                r=o['variants'][m];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
                if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=.75)
                if r['measured_photo_location']:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white',ms=5)
                ax.set_title(m+f" {r['metrics']['area']}px"+('\nFLAG: '+', '.join(r['abstention_reasons']) if r['abstention_reasons'] else '\nUnrated proposal'),fontsize=7)
        fig.suptitle(case['name']+' — all frozen cues; flags do not certify remaining proposals');fig.tight_layout();fig.savefig(REVIEW/(case['name']+'-atlas.png'),dpi=110);plt.close(fig)
    # Detailed unexpected B-vs-M differences; selected after confirmation only for explanation.
    for case in cases:
        for o in case['observations']:
            if o['variants']['B']['metrics']['area']!=o['variants']['M']['metrics']['area']:
                name=case['name']+'-protected-difference';panel(o,name,native);manifest.append(dict(name=name,id=o['id'],case=case['name'],reason='B differs from marker-only M after frozen confirmation; inspect possible false partition.'))
    save(OUT/'additional-review.json',manifest)
if __name__=='__main__':main()
