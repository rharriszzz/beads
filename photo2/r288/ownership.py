"""Marker and union diagnostics; counts never imply distinct physical bead truth."""
from .common import *
def main():
    result={}
    for stage in ('development','confirmation'):
        rows=[]
        for q in read(OUT/(stage+'.json.gz'))['cases']:
            for o in q['observations']:
                m=o['variants']['M']['method_evidence'];w=o['variants']['W']['method_evidence'];ledger=m['marker_ledger'];rows.append(dict(case=q['name'],id=o['id'],same_marker_ledger=ledger==w['marker_ledger'],raw_maxima=len(ledger),placed=len([r for r in ledger if r.get('placed') is not None]),unsupported=len([r for r in ledger if r.get('placed') is None]),projected=len([r for r in ledger if r['reason']=='context-supported maximum projected to eligible pigment']),M_group=len(m['group']),W_group=len(w['group']),W_short_dark_interfaces=w['short_dark_interfaces']))
        result[stage]=dict(rows=rows,all_markers_identical=all(q['same_marker_ledger'] for q in rows),proposals_with_merged_markers_M=sum(q['M_group']>1 for q in rows),proposals_with_merged_markers_W=sum(q['W_group']>1 for q in rows),raw_maxima_sum=sum(q['raw_maxima'] for q in rows),projected_sum=sum(q['projected'] for q in rows),unsupported_sum=sum(q['unsupported'] for q in rows),proposals_with_short_dark_interfaces=sum(q['W_short_dark_interfaces']>0 for q in rows))
    result['limits']='Local windows repeat features; totals are processing events, not unique markers/beads. Missing true-body markers and redundant same-body markers cannot be verified without independent ownership truth.'
    save(OUT/'marker-audit.json',result)
    for stage in ('development','confirmation'):print(stage,{k:v for k,v in result[stage].items() if k!='rows'})
if __name__=='__main__':main()
