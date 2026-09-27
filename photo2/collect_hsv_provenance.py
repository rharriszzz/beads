"""Freeze relevant immutable sibling-repository HSV presets and history."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
FFT='2caf0707c2b63a0d7540e2cac447d2f1b883d8c1'
HISTORY=[
    '27b8de7a2e3ac95db8b928156d00bbaca7845ae8',
    '4ebb4b0c8e0d22aadb16287a647c5d21a97c20e8',
    '9bdfdb3dfc644479c4da94890e7c2ed26b883a7e',FFT]
HSV='3e70fe304bd586b160caf12e45b657f33d8141ea'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repos',type=Path,default=ROOT.parent)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/hsv-provenance-r100.json')
    args=parser.parse_args();sources=[];history=[]
    def blob(repo,commit,name):
        return subprocess.check_output(['git','-C',str(args.repos/repo),'show',f'{commit}:{name}'])
    for repo,commit,names in [
        ('hsv_tools',HSV,['hsv_picker.py','beads-photo-2-red.jpg','beads-photo-2-background.jpg']),
        ('fft-image-explorer',FFT,['hsv_mask_triptych.py','beads-photo-2.jpg','beads-photo-2-wb.jpg'])]:
        for name in names:
            sources.append(dict(repo=repo,commit=commit,path=name,sha256=hashlib.sha256(blob(repo,commit,name)).hexdigest()))
    for commit in HISTORY:
        source=blob('fft-image-explorer',commit,'hsv_mask_triptych.py');text=source.decode();tree=ast.parse(text)
        profile=None;legacy=None
        for node in tree.body:
            if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name) and node.target.id=='PRESET_PROFILES':profile=ast.literal_eval(node.value)
            if isinstance(node,ast.FunctionDef) and node.name=='_hsv_preset_components':legacy=ast.get_source_segment(text,node)
        history.append(dict(commit=commit,source_sha256=hashlib.sha256(source).hexdigest(),profiles=profile,legacy_components_source=legacy))
    latest=history[-1]['profiles']['beads-photo-2-wb']
    def subset(a,b):
        hues=lambda p:set(v for lo,hi in p['h'] for v in range(lo,hi+1))
        return hues(a)<=hues(b) and all(b[k][0]<=a[k][0]<=a[k][1]<=b[k][1] for k in ('s','v'))
    assert subset(latest['red-and-shadow'],latest['shadow'])
    assert subset(latest['red-and-edge'],latest['edge'])
    result=dict(sources=sources,history=history,profile=latest,
                user_confirmation='R102: maker identifies red-and-shadow/shadow map as the intended earlier work',
                convention='HSV-space inclusive integer boxes; all H/S/V channels rounded from matplotlib HSV*255; white-balanced profile',
                subset_checks={'red-and-shadow_inside_shadow':True,'red-and-edge_inside_edge':True},
                spatial_annotation_coordinates='Not recovered; presets are HSV boxes, not spatial rectangles. User confirms map provenance, not exact T1/T2 edge pixels.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f'Saved six source hashes, four revisions and two verified subset relations to {args.output}')


if __name__=='__main__':main()
