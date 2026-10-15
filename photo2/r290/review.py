"""Package all automatic candidates before any user judgments."""
import shutil
from .common import *

def main():
    (REVIEW/'data').mkdir(parents=True,exist_ok=True);(REVIEW/'crops').mkdir(exist_ok=True)
    records=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']]
    manifest=[]
    extra=read(EVIDENCE/'development-observations.json')['additional_category_cases']
    corrections=read(EVIDENCE/'provenance-corrections.json')
    for r in records:
        r['categories']=sorted(set(r['categories']+[tag for tag,ids in extra.items() if r['case_id'] in ids]))
        correction=corrections.get(r['case_id'])
        if correction:
            r['categories']=sorted((set(r['categories'])-set(correction['remove_categories']))|set(correction['add_categories']))
            r['provenance_correction']=correction
        name=r['case_id'];path=REVIEW/'data'/(name+'.json');save(path,r)
        shutil.copy2(OUT/'crops'/(name+'.png'),REVIEW/'crops'/(name+'.png'))
        manifest.append(dict(case_id=name,split=r['split'],categories=r['categories'],status=r['A']['status'],feature_id=r['feature']['id'],candidate_digest=sha(path),alternative=bool(r['B']),supported_fraction=r['A']['evidence']['T7']['supported_fraction']))
    save(REVIEW/'manifest.json',dict(cases=manifest,photo=records[0]['photo'],algorithm=records[0]['algorithm'],feedback_schema='R290-review-v1',limitations=read(EVIDENCE/'collection.json')['missing_coverage']))
    for src,dst in [('R290_REPORT.md','report.md'),('R290_REPRODUCE.md','reproduce.md')]:
        if (ROOT/'photo2'/src).exists():shutil.copy2(ROOT/'photo2'/src,REVIEW/dst)
    print('Packaged',len(manifest),'cases; no user judgment yet')

if __name__=='__main__':main()
