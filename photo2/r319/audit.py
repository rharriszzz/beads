"""Actual serialized R318 coverage, including failed proposals, never trial-count proxy."""
from collections import Counter
import numpy as np
from .common import *

def flat(p):
    out={}
    for k,v in p.items():
        if isinstance(v,list):
            for j,x in enumerate(v):out[f'{k}[{j}]']=x
        else:out[k]=v
    return out

def main():
    documents=[];matrices=[];epochs=[]
    for folder in [OLD,OLD/'epoch2']:
        rr=[read(p) for p in sorted((folder/'trials').glob('*.gz'))];documents+=rr
        js=read(folder/'jacobians.json.gz');matrices+=js
        epochs.append(dict(epoch=folder.name,trials=len(rr),stages=dict(Counter(r['stage'] for r in rr)),classifications=dict(Counter(r['classification'] for r in rr)),jacobians=len(js),column_counts=dict(Counter(len(r['fields']) for r in js))))
    flats=[flat(r['parameters']) for r in documents];keys=sorted(set().union(*(p.keys() for p in flats)));ranges=[]
    for k in keys:
        vals=[p[k] for p in flats if k in p];numeric=all(isinstance(v,(int,float)) for v in vals)
        rr=dict(key=k,present=len(vals),unique=len(set(vals)),varied=len(set(vals))>1)
        if numeric:rr.update(minimum=float(min(vals)),maximum=float(max(vals)),span=float(max(vals)-min(vals)))
        else:rr['values']=sorted(set(vals))
        ranges.append(rr)
    p=read(OLD/'epoch2/best.json.gz')['parameters'];vs=variables(p)
    inactive=['bend','strain','phase_knots','local_bend','local_metric','local_turn','phase_transport','local_phase_bias','pitch','yaw']
    families=[
      dict(family='axis_nodes[32]',meaning='periodic image-normal displacement of planar major axis, pixels',constraints='No bound called by R318 search; historical R306 valid() used ±30px but is not invoked.',r318='fixed',local_support='75.16 addresses/node; global cubic spline tails, cannot independently resolve 13–20 addresses'),
      dict(family='local_phase[32]',meaning='periodic minor phase correction, radians',constraints='Interpolated derivative <=2% of 2pi/6.5 per address, numerical regularization',r318='fixed',redundancy='constant mode duplicates global phase'),
      dict(family='local_spacing[32]',meaning='fractional longitudinal rate, integrated and renormalized to full extent',constraints='Interpolated rate departure <=2%, numerical regularization',r318='fixed',redundancy='uniform rate perturbation cancels exactly only when field is constant; nearly gauge-like for small nonuniform field'),
      dict(family='compact phase/spacing/tilt/cant',meaning='shared smooth bump fields; rad / fraction / deg / inward deg',constraints='phase rate <=5%, station rate <=2%; tilt correction <=20deg; cant <=12deg; combined orientation slope <=3deg/address; all numerical',r318='Only three new coefficients per family at 25,55,85 varied. Earlier 5 frozen.',local_support='phase/orientation support 36 addresses, spacing 70; centers 30 apart leave weak overlap. Basis locations/widths fixed.'),
      dict(family='camera/registration',meaning='elevation,roll deg; scale px/unit; inverse perspective 1/unit; translation and s0 px',constraints='R318 only elevation 45..75 enforced here; singular camera and bounding-sphere constraints also enforced; other historical bounds not called',r318='elevation roll translation s0 varied; scale perspective fixed',redundancy='radius/minor/scale and deprojected centerline create local size/depth coupling; station and translation locally similar'),
      dict(family='minor placement / count / topology',meaning='minor radius units, phase rad, turn beads/revolution; count integer, hand ±1, topology open/closed',constraints='minor 3.7..4.6 R318 numerical; count=2405, hand=-1, open, turn=6.485; no count evidence inferred',r318='minor/phase varied; count hand turn gap topology fixed',local_support='relative depth prescribed by planar major axis + minor helix, no independent z offset'),
      dict(family='shape',meaning='shared radius units, axial ratio, legacy hole fraction and rounding; alternate independent exterior edge/face/bore',constraints='axial .7..1.2 R318; hole .02..60 rounding .25..1 from ShapeMixin; R318 shadow kernel ASSERTS exact hole=.14 rounding=.8 exterior=false',r318='radius axial varied; hole/profile fixed',limitation='Changing profile with R318 Engine directly fails its exact-kernel assertion; requires generic shadow renderer, not physical impossibility.'),
      dict(family='hole-axis law',meaning='tilt tangent/circumferential degrees; radial_cant inward deg; trajectory_mix fraction; height orientation coefficients deg',constraints='cant <=12deg and slope <=3deg/address numerical; trajectory/height law inherited but R318 did not vary',r318='global tilt and new compact tilt/cant varied; radial_cant/trajectory_mix/tilt_y/tilt_y2 fixed zero'),
      dict(family='illumination',meaning='shared az/el deg, roughness angular width deg (mapped to BRDF exponent); inverse distance 1/unit and angular width deg',constraints='roughness3..45 elevation-10..90 inverse0...01 in R318; finite and extended mutually exclusive',r318='az/el roughness inverse varied;144 separate finite/extended controls',limitation='No refraction or calibrated irradiance; retained one shared source'),
      dict(family='inactive legacy',meaning=','.join(inactive),constraints='Serialized but absent from current placement/shape/projection path',r318='fixed',limitation='Do not count as available search dimensions'),
      dict(family='winding/seam/profile switch',meaning='winding active only closed; seam_fraction changes open end addresses; edge/face/bore active only exterior=true',constraints='discrete topology changes alter actual chain; not an infinitesimal derivative',r318='fixed',limitation='Inactive conditional parameters, not omitted independent local variables')]
    out=dict(epochs=epochs,range_table=ranges,families=families,varied_coordinates=[r['key'] for r in ranges if r['varied']],serialized_trials=len(documents),saved_jacobians=len(matrices),scientific_interpretation='Two frozen map epochs near one inherited 2405/-/open family. Trial count is not coverage. R318 uses positive one-sided quarter-scale columns (negative fallback), no central derivative checks or SVD; coordinate descent and subset minimax can stall on coupled directions.')
    save(OUT/'search-space-audit.json',out)
    lines=['# Actual R318 serialized coverage','','All outcomes, including infeasible proposals. These are exploration ranges, not measured physical limits.','','| Coordinate | Min | Max | Distinct |','|---|---:|---:|---:|']
    for r in ranges:lines.append(f"| {r['key']} | {r.get('minimum',' / '.join(map(str,r.get('values',[]))))} | {r.get('maximum','')} | {r['unique']} |")
    (OUT/'parameter-ranges.md').write_text('\n'.join(lines)+'\n')
    print('AUDIT',len(documents),len(matrices),len(out['varied_coordinates']),out['varied_coordinates'],flush=True)
if __name__=='__main__':main()
