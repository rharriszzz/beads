"""Export every partial motif and its original source evidence for review."""
import csv,html
from .common import *
def main():
    out=artifact('periods-selected');r=read(out/'periods.json.gz');tables=[]
    for m in r['motifs']:
        suffix=f'{m["family"]}-{m["period"]}'+('-hier' if m['parent'] else '');path=out/f'motif-{suffix}.csv'
        with path.open('w',newline='') as f:
            wr=csv.DictWriter(f,['residue','color','plurality','fraction','sections','observations','supporting','ids','indices'],lineterminator='\n');wr.writeheader();wr.writerows(m['entries'])
        cells=''.join(f'<span class="{e["color"]}" title="{html.escape(str(e))}"><small>{e["residue"]}</small>{e["color"][0].upper() if e["color"]!="?" else "?"}</span>' for e in m['entries']);tables.append(f'<section><h2>{m["family"]}/{m["period"]} {"hierarchical predictor" if m["parent"] else "flat predictor"}</h2><p>{m["known"]} known, {m["unknown"]} unknown; {m["unobserved"]} wholly unobserved. Consensus is fitted to exposed data, not truth. Own N={m["N"]}; closes: {m["N"]%m["period"]==0}. <a href="motif-{suffix}.csv">Every source ID/index</a></p><div class="motif">{cells}</div></section>')
    (out/'motifs.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R333 partial motifs</title><style>body{font:15px system-ui;background:#f4f7fa;color:#183044;padding:24px;max-width:1200px;margin:auto}section{margin:30px 0}.motif{display:flex;flex-wrap:wrap;gap:4px}.motif span{display:flex;flex-direction:column;align-items:center;width:36px;border:1px solid #98adbf;padding:3px;font-weight:bold}.motif small{font-size:9px}.red{background:#d63840;color:white}.yellow{background:#f2d456}.black{background:#242e3a;color:white}a{color:#08758c}</style><h1>Partial repeating sequences</h1><p>Consensus colors require ≥80% weighted agreement, ≥3 observations and ≥3 geographic sections. Unknown entries remain ?. Rotations/reversal are convention choices. The208 tile is maker-incompatible; no exact full design is adopted.</p><p><a href="../../R333_REPORT.md">Report</a> · <a href="../review/index.html">Photograph and graph paper</a></p>'+''.join(tables)+'</html>')
if __name__=='__main__':main()
