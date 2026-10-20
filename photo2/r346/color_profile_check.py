"""Sensitivity to the source JPEG's embedded ICC profile; no refit of lighting."""
from .shadows import *
from PIL import ImageCms
import io

def main():
    original=Image.open(ROOT/'beads-photo-2.jpg');profile=original.info.get('icc_profile')
    if not profile:
        save(OUT/'color-profile-sensitivity.json',dict(embedded_profile=False));return
    src=ImageCms.ImageCmsProfile(io.BytesIO(profile));converted=ImageCms.profileToProfile(original,src,ImageCms.createProfile('sRGB'),outputMode='RGB');raw=np.asarray(original.convert('RGB'),float)/255;managed=np.asarray(converted,float)/255
    from scipy.spatial import cKDTree
    yy,xx=np.mgrid[6:H:12,6:W:12];xy=np.c_[xx.ravel(),yy.ravel()];curve=Model(read(ROOT/'photo2/r345/config.json')).image;xy=xy[cKDTree(curve).query(xy)[0]>260];A=design(xy);hold=((xy[:,0]//12+3*(xy[:,1]//12))%5)==0
    light=linear(managed);values=light[xy[:,1],xy[:,0]];coef=[]
    for c in range(3):
        target=np.log(np.maximum(values[:,c],1e-5));fit=least_squares(lambda v:A[~hold]@v-target[~hold],np.linalg.lstsq(A[~hold],target[~hold],rcond=None)[0],loss='soft_l1',f_scale=.06,max_nfev=30);coef.append(fit.x)
    coef=np.array(coef);data=copy.deepcopy(read(OUT/'profiles.json.gz')['profiles'])
    for r in data:
        d=np.array(r['distance']);q=np.array(r['point']);t=np.array(r['tangent']);n=np.array(r['outward']);p=q+np.arange(-18,19,3)[:,None,None]*t+(r['edge_radius']+d)[None,:,None]*n;bg=np.exp(design(p)@coef.T);deficits=[]
        for c in range(3):deficits.append(1-np.nanmedian(sample(light[:,:,c],p)/bg[:,:,c],axis=0))
        reference=np.nanmedian(bg,axis=0).T;lum=np.array([.2126,.7152,.0722]);r['photo_deficit']=((lum@(reference*np.array(deficits)))/(lum@reference)).tolist()
    predictions=np.load(OUT/'rendered-profiles.npz');scores={name:score(predictions[name],data,False) for name in ['R345','R346']};base=read(OUT/'comparison-metrics.json')['profile_scores']
    difference=float(scores['R346']['validation']['rms']-base['R346']['validation']['rms']);assert scores['R346']['validation']['rms']<scores['R345']['validation']['rms']
    result=dict(profile=ImageCms.getProfileDescription(src).strip(),purpose='Sensitivity only; frozen primary metrology retains R345 encoded-RGB/sRGB-transfer convention. This control converts the source through its embedded ICC to sRGB and refits only the smooth paper reference on identical far-control coordinates. Lighting, geometry, color labels, observation eligibility and rendered profile weights remain fixed.',median_absolute_channel_code_change=np.median(abs(raw-managed)*255,axis=(0,1)).tolist(),profile_scores_after_ICC=scores,R346_validation_RMS_change=difference,lighting_not_refitted=True)
    save(OUT/'color-profile-sensitivity.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
