"""Full dependency-ordered R276 rerun. Preserves everything before R276.

Use saved-model --stage audit for a much cheaper numerical replay.
"""
from .reconstruct_r276 import OUT,run_fit,run_alternatives,run_audit
from .diagnose_r276 import (material_control,correction,packing_fits,mixed_correction,
    metric_fit,structural_screens,contact_fit,full_contact_check,confirmed_support,diagnostics,fixed_and_normals,convergence,color_transfer,ray_termination)
from .report_r276 import main as report
from .validate_r276 import run as validate


def main():
    run_fit();run_audit();material_control('light_only');correction()
    run_alternatives();packing_fits();mixed_correction();metric_fit();structural_screens();contact_fit()
    names=['uniform_before','uniform_joint','uniform_refined','mixed_light','mixed_joint','metric_before','metric_refined','contact_light','contact_joint']
    import json
    for pattern in ('alternative_N*.json','packing_N*.json'):
        for path in sorted(OUT.glob(pattern)):
            doc=json.loads(path.read_text())
            if isinstance(doc,dict) and 'base' in doc and 'p' in doc:names.append(path.stem)
    run_audit(names)
    for name in ('light_only','joint_refined','uniform_refined','mixed_joint','metric_refined','contact_joint'):
        diagnostics(name);fixed_and_normals(name);convergence(name);color_transfer(name);ray_termination(name)
    full_contact_check("contact_joint");full_contact_check("packing_N1950_h-1");confirmed_support()
    report();validate()

if __name__=='__main__':main()
