"""Image-only detection and ranking. No construction or evaluation imports."""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.color import rgb2hsv
from skimage.segmentation import watershed

PARAMETERS=dict(scales=[1.,2.,3.],peak_window=7,min_peak=.065,min_region=10,max_region=870,local_radius=13,seed=279013)

def detect(rgb):
    a=np.asarray(rgb,float)/255;hsv=rgb2hsv(a);lum=a@np.array([.2126,.7152,.0722]);h,s,v=np.moveaxis(hsv,-1,0)
    border=np.r_[h[:8].ravel(),h[-8:].ravel(),h[:,:8].ravel(),h[:,-8:].ravel()]
    bh=np.angle(np.mean(np.exp(2j*np.pi*border)))/(2*np.pi)%1
    dh=abs((h-bh+.5)%1-.5)
    # Paper hue includes shadow; neutral highlights/dark regions remain provisional.
    fg=((dh>.065)&(s>.24))|((s<.30)&(v<.65))
    fg=ndi.binary_fill_holes(ndi.binary_closing(fg,iterations=1))
    smooth=[ndi.gaussian_filter(lum,z) for z in PARAMETERS['scales']]
    peaks=(smooth[1]==ndi.maximum_filter(smooth[1],7))&(smooth[1]>.065)&fg
    peaks[:14]=False;peaks[-14:]=False;peaks[:,:14]=False;peaks[:,-14:]=False
    yy,xx=np.where(peaks);seed=np.c_[xx,yy];markers=np.zeros(lum.shape,np.int32);markers[yy,xx]=np.arange(1,len(xx)+1)
    labels=watershed(-smooth[1],markers,mask=fg)
    response=-ndi.gaussian_laplace(lum,3)*9
    trees=[]
    for z in smooth:
        y,x=np.where((z==ndi.maximum_filter(z,7))&fg&(z>.065));trees.append(cKDTree(np.c_[x,y]))
    obs=[]
    for i,(x,y) in enumerate(seed):
        y0,y1=y-13,y+14;x0,x1=x-13,x+14
        Y,X=np.mgrid[y0:y1,x0:x1];local=labels[y0:y1,x0:x1]==i+1
        local &= (X-x)**2+(Y-y)**2<=13**2
        # Conservative native support around seed, no invented full silhouette.
        local &= lum[y0:y1,x0:x1]>max(.015,.16*smooth[1][y,x])
        pix=np.c_[X[local],Y[local]]
        if len(pix)<10:continue
        vals=hsv[pix[:,1],pix[:,0]];sat=float(np.median(vals[:,1]));hue=float(np.angle(np.mean(np.exp(2j*np.pi*vals[:,0])))/(2*np.pi)%1)
        color='black' if sat<.32 or np.median(vals[:,2])<.18 else ('yellow' if .09<hue<.25 else 'red')
        cen=pix.mean(0);spread=np.sqrt(np.mean(np.sum((pix-cen)**2,axis=1)));persist=max(float(t.query([x,y])[0]) for t in trees)
        unc=max(2.,.65*spread)+np.linalg.norm(cen-[x,y])*.3
        if color=='black':unc+=3.
        obs.append(dict(id=f'O{y:04d}-{x:04d}',point=[int(x),int(y)],centroid=cen.tolist(),physical_center=None,pixels=pix.tolist(),color=color,hue=hue,saturation=sat,area=len(pix),uncertainty=float(unc),persistence=persist,quality=float(np.sqrt(len(pix))*smooth[1][y,x]/(1+persist)),region=i+1,peak=float(lum[y,x]),log_response=float(response[y,x])))
    return obs,dict(background_hue=float(bh),known_background=(~fg),luminance=lum)

def select(obs,n=21):
    chosen=[];eligible=[o for o in obs if o['area']>=25 and o['persistence']<=3]
    for i in range(n):
        color=('red','yellow','black')[i%3];pool=[o for o in eligible if o not in chosen and o['color']==color]
        if not pool:pool=[o for o in eligible if o not in chosen]
        if not pool:break
        # Keep top half by support quality, then spread spatially, independent of neighbors.
        pool=sorted(pool,key=lambda o:(-o['quality'],o['id']))[:max(1,(len(pool)+1)//2)]
        best=max(pool,key=lambda o:min(np.linalg.norm(np.array(o['point'])-c['point']) for c in chosen)) if chosen else pool[0]
        chosen.append(best)
    return [o['id'] for o in chosen]

def cues(a,b,state):
    x=np.array(a['centroid']);y=np.array(b['centroid']);t=np.linspace(0,1,max(5,int(np.linalg.norm(x-y)*2)))
    xy=np.rint(x+(y-x)*t[:,None]).astype(int);lum=state['luminance'][xy[:,1],xy[:,0]]
    valley=float(1-np.min(lum)/max(1e-6,min(np.max(lum[:max(1,len(lum)//3)]),np.max(lum[-max(1,len(lum)//3):]))))
    hue=abs((a['hue']-b['hue']+.5)%1-.5);gap=float(cKDTree(a['pixels']).query(b['pixels'])[0].min())
    bg=float(state['known_background'][xy[:,1],xy[:,0]].mean())
    return dict(valley=valley,hue_difference=hue,supported_surface_gap_px=gap,background_fraction=bg,possible_same_body=bool(hue<.045 and valley<.35 and gap<4))

def neighbors(obs,anchors,state):
    by={o['id']:o for o in obs};out=[]
    for aid in anchors:
        a=by[aid];near=sorted((o for o in obs if o['id']!=aid),key=lambda o:np.linalg.norm(np.array(o['point'])-a['point']))[:8]
        methods={}
        for method in 'ABC':
            rows=[]
            for b in near:
                cue=cues(a,b,state);coord='point' if method=='A' else 'centroid';dist=float(np.linalg.norm(np.array(a[coord])-b[coord]));u=0 if method=='A' else a['uncertainty']+b['uncertainty']
                score=dist
                if method=='B' and cue['possible_same_body']:score+=12
                if method=='C':score+=18*cue['possible_same_body']+2*min(b['persistence'],5)-3*max(0,cue['valley'])-3*min(cue['hue_difference']/.08,1)
                rows.append(dict(id=b['id'],distance_px=dist,interval_px=[max(0,dist-u),dist+u],score=float(score),cues=cue))
            rows.sort(key=lambda r:(r['score'],r['id']));first=rows[0] if rows else None
            alternatives=[r['id'] for r in rows if first and r['interval_px'][0]<=first['interval_px'][1] and r['score']<=first['score']+15]
            single=bool(first and (method=='A' or (len(alternatives)==1 and not first['cues']['possible_same_body'])))
            methods[method]=dict(answer=first['id'] if single else None,top=first['id'] if first else None,alternatives=alternatives,status='single proposal' if single else 'ambiguous',ranking=rows)
        out.append(dict(anchor=aid,methods=methods))
    return out
