"""Descriptive joint-HSV findings; no pigment classifier or fitted shadow law."""
from common import *

def main():
 data=read(OUT/'source-pixels.json.gz')['points'];regions=read(OUT/'glass-regions.json')['records'];probe=set(P29+['R332-R-0125-0118']);reference=[r for r in data if r['id'] not in probe and r['hue_interpretable']];bins=[]
 for lo,hi in [(.2,.4),(.4,.6),(.6,.8),(.8,1.00001)]:
  row=dict(V_interval=[lo,hi],colors={})
  for c in ['red','yellow']:
   pp=[r for r in reference if r['recorded_pigment']==c and lo<=r['V']<hi];ids=sorted({r['id'] for r in pp});row['colors'][c]=dict(pixels=len(pp),beads=len(ids),ids=ids,H_percentiles=np.percentile([r['H'] for r in pp],[5,50,95]).tolist() if pp else None,S_percentiles=np.percentile([r['S'] for r in pp],[5,50,95]).tolist() if pp else None)
  bins.append(row)
 # Descriptive same-volume bins are only a plot-overlap diagnostic, not a rule.
 def cell(r):return (int(np.floor(r['H']/5)),int(np.floor(r['S']/.1)),min(9,int(r['V']/.1)))
 occupied=defaultdict(lambda:defaultdict(list))
 for r in reference:occupied[cell(r)][r['recorded_pigment']].append(r)
 common=[]
 for key,rows in occupied.items():
  if len(rows)>1:common.append(dict(bin_HSV=list(key),bin_widths=[5,.1,.1],red_example=rows['red'][0],yellow_example=rows['yellow'][0],meaning='Both labeled pigments enter this coarse joint HSV neighborhood; not identical pixels or a classification error.'))
 explicit=[r for r in regions if r['individually_confirmed']];bycolor={c:[r for r in reference if r['recorded_pigment']==c] for c in ['red','yellow']};findings=dict(reference_beads=len({r['id'] for r in reference}),reference_beads_by_color={c:len({r['id'] for r in pp}) for c,pp in bycolor.items()},probe_ids=sorted(probe),explicit_individual_beads_by_color=dict(Counter(r['recorded_pigment'] for r in explicit)),source_pixels=len(data),brightness_strata=bins,shared_joint_bins=common,reference_H_ranges={c:[min(r['H'] for r in pp),max(r['H'] for r in pp)] for c,pp in bycolor.items()},shadow_law_fitted=False,automatic_color_decisions=False,findings=['Confirmed shaded yellow spans orange and near-red hue, including REC266-P146299 at median8.57deg and C62 at21.43deg. Bright native/illustration-approved yellows lie nearer median32-37deg.','Value alone does not specify yellow hue: REC266-P146299 at medianV.65 has lower hue than darker C62 atV.51. Saturation and spatial illumination vary too.','The explicit shaded red control is near medianH-8.00deg. Visually supported red controls extend to+7.43deg, overlapping part of the yellow hue envelope. Some coarse jointHSV neighborhoods are shared.','There is only one individually pigment-confirmed red body in this selected sample. Other red controls retain illustration/native-software authority; do not inflate independent ground truth.','Within-bead brightness strata show nonmonotone hue changes. Spatial variation in one photograph cannot establish a universal relighting trajectory.','NEW1519 and R127 pixels are yellow-like relative to these curated controls; they remain recorded red pending independent pigment judgment. No motif color, neighbor majority, or new automatic correction is used.'])
 save(OUT/'HSV-findings.json',findings);print('Reference controls',findings['reference_beads_by_color'],'explicit',findings['explicit_individual_beads_by_color'],'shared bins',len(common));print('strata',bins)
if __name__=='__main__':main()
