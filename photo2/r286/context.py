"""Retain all three original two-sided observations; review selectors only."""
from .common import *
from .run import main as run
from .review import panel,plt,COLORS

def main():
    sel=next(q for q in read(OLD/'selection.json')['development'] if q['example']=='e03');o=next(o for o in read(OLD/'development.json.gz')['observations'] if o['id']==sel['observation_id']);case=dict(name='P1-right-yellow',seed=o['seed'],stratum='previously-reviewed-context',observations=[dict(id=o['id'],seed=o['seed'],color=o['color'],source_status=o['source_status'],controls=o['variants'])]);run(out=OUT/'two-sided-context',cases_override=[case]);d=read(OUT/'two-sided-context/development.json.gz');native,_,_=photo();o=d['cases'][0]['observations'][0];panel(o,'P1-right-yellow',native)
    obs=[q['observations'][0] for q in read(OUT/'development.json.gz')['cases'][:2]]+[o];center=np.rint(np.mean([q['seed'] for q in obs],axis=0)).astype(int);origin=center-65;x,y=origin;im=native[y:y+131,x:x+131];from PIL import Image
    Image.fromarray(im).save(REVIEW/'two-sided-native.png');fig,axs=plt.subplots(1,5,figsize=(16,4))
    for ax,m in zip(axs,('raw','J','S','M','B')):
        ax.imshow(im,interpolation='nearest');ax.set_title(m+' / three separate observations');ax.set_xticks([]);ax.set_yticks([])
        if m=='raw':continue
        curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points'])-origin;curve=curve[np.all((curve>=0)&(curve<131),axis=1)];ax.plot(curve[:,0],curve[:,1],color='white',lw=.8)
        for i,q in enumerate(obs,1):
            r=q['variants'][m];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
            if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=1)
            if r['measured_photo_location']:p=np.array(r['measured_photo_location'])-origin;ax.plot(*p,'+',color='white');ax.text(p[0]+3,p[1],str(i),color='white')
    fig.suptitle('1 lower yellow; 2 left red; 3 right yellow — photo observations, no physical identity');fig.tight_layout();fig.savefig(REVIEW/'two-sided-three.png',dpi=130);plt.close(fig);save(OUT/'two-sided-context/crop.json',dict(origin=origin.tolist(),size=131))
if __name__=='__main__':main()
