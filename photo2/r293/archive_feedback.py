"""Archive every R292 review event and verify its exact displayed evidence."""
import collections,gzip,json
import numpy as np
from PIL import Image
from .common import *

def main():
    folder=ROOT/'photo2/r292/feedback';path=folder/'judgments.jsonl'
    if not path.exists():raise FileNotFoundError('Completed R292 feedback unavailable at '+str(path))
    raw=path.read_bytes();events=[json.loads(l) for l in raw.splitlines() if l.strip()];latest={e['case_id']:e for e in events};native,_,meta=photo();records=[]
    for cid,e in latest.items():
        snap=folder/'snapshots'/e['candidate_digest'];assert sha(snap/'candidate.json')==e['candidate_digest'];d=read(snap/'candidate.json');assert sha(snap/'crop.png')==e['crop_sha256'];assert meta['photo_sha256']==e['image_sha256'];assert e['displayed_candidates']=={k:d[k] for k in ('A','B')};assert e['displayed_separator_arcs']==d['separator_arcs'];assert (snap/'candidate.json').read_bytes()==(ROOT/f'photo2/review/r292/data/{cid}.json').read_bytes();assert (snap/'crop.png').read_bytes()==(ROOT/f'photo2/review/r292/crops/{cid}.png').read_bytes();x0,y0,x1,y1=d['box'];np.testing.assert_array_equal(np.asarray(Image.open(snap/'crop.png')),native[y0:y1,x0:x1])
        records.append(dict(case_id=cid,feature_id=e['feature_id'],point=e['feature_point'],answer=e['payload']['answer'],revision=e['revision'],diagnostics=e['payload']['diagnostics'],ownership=e['payload']['ownership'],candidate_digest=e['candidate_digest'],crop_sha256=e['crop_sha256'],candidate_path=f'photo2/review/r292/data/{cid}.json',crop_path=f'photo2/review/r292/crops/{cid}.png',evidence=d['A']['evidence'],pixels=d['A']['candidate_pixels']['pixel_count']))
    archive=EVIDENCE/'completed-r292-review.jsonl.gz';archive.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(archive.read_bytes())==raw
    import hashlib
    save(EVIDENCE/'r292-review-analysis.json',dict(schema='R293-R292-review-analysis-v1',source=str(path.relative_to(ROOT)),archive=str(archive.relative_to(ROOT)),archive_sha256=sha(archive),original_ledger_sha256=hashlib.sha256(raw).hexdigest(),photo=meta,events=len(events),reviewed_cases=len(latest),final_answers=dict(collections.Counter(e['payload']['answer'] for e in latest.values())),history=[{k:e[k] for k in ('case_id','revision','logical_parent_revision','payload','utc','action')} for e in events],records=records,verification=dict(native_crops=len(records),immutable_digests=len(records),displayed_candidates_and_separators=len(records),archive_byte_exact=True),interpretation='Selected difficult-case review, not representative accuracy. Answers/ownership are human evidence, never runtime rules. No optional diagnostic explanations supplied.'))
    print('Archived',len(events),'events,',len(records),'final cases:',collections.Counter(e['payload']['answer'] for e in latest.values()))
if __name__=='__main__':main()
