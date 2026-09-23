#!/usr/bin/env python3
"""Render an invented pattern through beads.pov, without an inverse model."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess

from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parent.parent
PATTERN = ROOT / 'photo2/practice-pattern.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'photo2/output/legacy-practice')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    pattern = json.loads(PATTERN.read_text())
    colors, groups = pattern['colors'], pattern['groups']
    if not colors or any(type(c) is not int or c not in range(3) for c in colors):
        raise ValueError('Expected nonempty legacy case-1 palette indices 0..2')
    if type(groups) is not int or groups <= 0:
        raise ValueError('Expected positive integer groups')
    wrapper = out / 'practice.pov'
    wrapper.write_text(
        '// Generated from photo2/practice-pattern.json; original scene does placement.\n'
        f'#declare CustomColorPattern=array[{len(colors)}] {{'
        + ','.join(map(str, colors)) + '};\n'
        f'#declare CustomPatternGroups={groups};\n'
        '#include "beads.pov"\n'
        '#debug concat("PRACTICE ", str(bead_pattern,0,0), " ", '
        'str(pattern_length,0,0), " ", str(nbeads,0,0), " ", '
        'str(nrows,0,0), " ", str(exact_beads_per_row,0,9), " ", '
        'str(rclock,0,9), "\\n")\n')
    report = {'pattern': pattern, 'commands': [], 'rendered_parameters': {},
              'environment': {'python': platform.python_version(), 'pillow': pillow_version},
              'sources': {str(p.relative_to(ROOT)): digest(p) for p in
                          [Path(__file__), PATTERN, ROOT/'beads.pov', ROOT/'bead-shape.inc']}}
    for name, clock in [('phase-0', '0'), ('phase-half', '0.0625')]:
        command = ['povray', f'+I{wrapper}', f'+L{ROOT}', f'+O{out/name}.png',
                   '+W2400', '+H1800', f'+K{clock}', '+FN8', '-D', '+A0.1', '+WT2']
        log = out / f'{name}.log'
        with log.open('w') as stream:
            subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                           check=True)
        report['commands'].append({'cwd': str(ROOT), 'argv': command})
        match = re.search(r'PRACTICE (\d+) (\d+) (\d+) (\d+) ([\d.]+) ([\d.]+)',
                          log.read_text())
        if match is None:
            raise RuntimeError('POV-Ray did not report scene parameters')
        case, length, count, rows = map(int, match.groups()[:4])
        assert (case, length, count) == (1, len(colors), len(colors)*groups)
        assert rows == int(count/6.5 + .5)
        report['rendered_parameters'][name] = {
            'case': case, 'pattern_length': length, 'beads': count, 'turns': rows,
            'exact_beads_per_row': float(match[5]), 'rclock': float(match[6])}
        im = Image.open(out / f'{name}.png').convert('RGB')
        assert im.size == (2400, 1800)
        # Fixed crops retain original pixels; no inferred edges or bead labels.
        box = (1850, 600, 2400, 1200)
        im.crop(box).save(out / f'{name}-detail.png')
        report['rendered_parameters'][name]['detail_box'] = box
    report['artifacts'] = {p.name: digest(p) for p in sorted(out.iterdir())
                           if p.name.startswith(('phase-', 'practice.')) and p.is_file()}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['rendered_parameters'], indent=2))


if __name__ == '__main__':
    main()
