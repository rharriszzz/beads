"""Expose post-seal finite-address sensitivity without changing fit outcomes."""
import json
from .core import *

def main():
    audit=read(BASE/'results/verification.json');guards={g['name']:g for g in audit['guard_extension']}
    models=read(BASE/'results/native-manifest.json.gz');affected=[]
    for m in models:
        if m['kind']!='R303' or m['name'] not in guards:continue
        g=guards[m['name']];stable=not(g['missing'] or g['extra'] or g['max_common_error']>1e-9)
        d=m['result'];d['post_seal_guard_audit']=dict(positions=g['positions'],certified=g['physical']['certified'],minimum_margin=g['physical']['minimum_gap_units'],missing=g['missing'],extra=g['extra'],max_common_error=g['max_common_error'],native_predictions_stable=stable)
        d['evaluation_flags']=[]
        if not stable:d['evaluation_flags'].append('Native predictions change with217 addresses; finite-section truncation sensitivity')
        if not g['physical']['certified']:d['evaluation_flags'].append('217-position extension not certified')
        if d['evaluation_flags']:affected.append(m['name'])
        save(BASE/f'results/native-{m["name"]}.json.gz',m)
    save(BASE/'results/native-manifest.json.gz',models)
    review=ROOT/'photo2/review/r303'
    (review/'data.js').write_text('const DATA='+json.dumps(dict(sections=read(BASE/'evidence/sections.json.gz'),models=models),separators=(',',':'))+';\n')
    html=(review/'index.html').read_text()
    html=html.replace("(r.flags?.join('; ')||'check structural evidence')", "([...(r.flags||[]),...(r.evaluation_flags||[])].join('; ')||'check structural evidence')")
    html=html.replace('construction:r.construction,physical:r.contact','construction:r.construction,post_seal_guard_audit:r.post_seal_guard_audit,evaluation_flags:r.evaluation_flags,physical:r.contact')
    (review/'index.html').write_text(html)
    save(BASE/'results/post-seal-guard-review.json',dict(utc=utc(),affected=affected,policy='Evaluation-only warnings; original153-position scores, selected parameters, training flags and sealed outcomes are unchanged.'))
    print('Finite-address warnings:',affected)

if __name__=='__main__':main()
