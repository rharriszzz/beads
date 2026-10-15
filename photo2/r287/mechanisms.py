"""Controlled intensity mechanisms, not physical renderings or real accuracy."""
from .evidence import diffuse_routes
from .common import *
def fields():
    y,x=np.indices((41,41));j=(x>=6)&(x<=17)&(abs(y-20)<=5);m=(x>=6)&(x<=33)&(abs(y-20)<=5);pigment=np.ones((41,41),bool);shade=.35-.006*x;seam=shade.copy();seam[:,22:25]=.008
    narrow=(x>=6)&(x<=33)&(abs(y-20)<=1)
    return [('continuous-diffuse-shading',shade,pigment,j,m),('dark-seam-and-renewed-surface',seam,pigment,j,m),('narrow-bright-continuation',shade,pigment,j&narrow,narrow),('same-pixels-internal-dark-texture',seam,pigment,j,m)]
def main():
    rows=[]
    for name,lum,pg,j,m in fields():
        r=diffuse_routes(lum,pg,j,m,.25);rows.append(dict(name=name,evidence=r,field=lum.tolist(),interpretation='No body identity enters the measurement. Identical seam/texture pixels remain indistinguishable.'))
    save(OUT/'mechanisms.json',rows)
    from .review import plt
    fig,axs=plt.subplots(1,4,figsize=(13,4))
    for ax,(name,lum,pg,j,m),r in zip(axs,fields(),rows):
        ax.imshow(lum,cmap='magma');ax.contour(j,levels=[.5],colors=['lime']);ax.contour(m,levels=[.5],colors=['cyan']);p=np.array(r['evidence']['pixels']).reshape(-1,2)
        if len(p):ax.scatter(p[:,0],p[:,1],s=2,c='white')
        ax.set_title(name.replace('-','\n')+f"\n{r['evidence']['supported_pixels']}/{r['evidence']['eligible_pixels']} supported",fontsize=9);ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle('Native route test: shading ≠ valley; identical seam/texture remains ambiguous');fig.tight_layout();fig.savefig(REVIEW/'mechanisms.png',dpi=120);plt.close(fig)
    print([(r['name'],r['evidence']['supported_fraction']) for r in rows])
if __name__=='__main__':main()
