"""Regenerate golden_values.json by running dump.pov through POV-Ray.

This is a one-off/manual tool, not needed at test time: the committed
``golden_values.json`` is the fixture tests compare against. Re-run this
script (from anywhere, with ``povray`` on PATH) whenever ``dump.pov`` or
``beads.pov`` changes in a way that should be re-verified.

Usage:
    python3 generate_golden.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DUMP_POV = HERE / "dump.pov"
GOLDEN_JSON = HERE / "golden_values.json"

# beads.pov selects bead_pattern as 1 + floor(bclock*8), bclock = clock*0.99999.
# clock = (case - 0.5) / 8 lands solidly in the middle of case's bclock bucket.
NUM_CASES = 8

_SCALAR_RE = re.compile(r"^([A-Z_]+)=([\d.eE+-]+)$")
_COLOR_RE = re.compile(r"^COLOR (\w+) ([\d.eE+-]+),([\d.eE+-]+),([\d.eE+-]+)$")
_CP_RE = re.compile(r"^CP (\d+) (\d+)$")
_BEAD_RE = re.compile(r"^BEAD(\d+)_(CHAIN_ANGLE|ROW_ANGLE|POS_X|POS_Y|POS_Z)=([\d.eE+-]+)$")

_INT_FIELDS = {"BEAD_PATTERN", "PATTERN_LENGTH", "NGROUPS", "NBEADS", "NROWS"}


def run_case(case: int) -> dict:
    clock = (case - 0.5) / NUM_CASES
    out_png = HERE / f"_dump_case{case}.png"
    cmd = [
        "povray",
        f"+I{DUMP_POV.relative_to(REPO_ROOT)}",
        f"+O{out_png}",
        "+W4",
        "+H4",
        "-D",
        f"+K{clock!r}",
    ]
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    out_png.unlink(missing_ok=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"povray failed for case {case} (exit {proc.returncode}):\n{proc.stderr}"
        )

    text = proc.stdout + proc.stderr

    colors: dict[str, list[float]] = {}
    scalars: dict[str, float] = {}
    color_pattern: dict[int, int] = {}
    bead_samples: dict[int, dict] = {}

    for line in text.splitlines():
        line = line.strip()

        m = _COLOR_RE.match(line)
        if m:
            name, r, g, b = m.groups()
            colors[name] = [float(r), float(g), float(b)]
            continue

        m = _CP_RE.match(line)
        if m:
            color_pattern[int(m.group(1))] = int(m.group(2))
            continue

        m = _BEAD_RE.match(line)
        if m:
            idx, field, value = m.groups()
            idx = int(idx)
            sample = bead_samples.setdefault(idx, {})
            if field == "CHAIN_ANGLE":
                sample["chain_angle"] = float(value)
            elif field == "ROW_ANGLE":
                sample["row_angle"] = float(value)
            elif field == "POS_X":
                sample.setdefault("pos", [None, None, None])[0] = float(value)
            elif field == "POS_Y":
                sample.setdefault("pos", [None, None, None])[1] = float(value)
            elif field == "POS_Z":
                sample.setdefault("pos", [None, None, None])[2] = float(value)
            continue

        m = _SCALAR_RE.match(line)
        if m:
            name, value = m.groups()
            scalars[name] = float(value)
            continue

    if scalars.get("BEAD_PATTERN") != case:
        raise RuntimeError(
            f"requested case {case} but dump.pov reported "
            f"BEAD_PATTERN={scalars.get('BEAD_PATTERN')}"
        )

    pattern_length = int(scalars["PATTERN_LENGTH"])
    if sorted(color_pattern) != list(range(pattern_length)):
        raise RuntimeError(
            f"case {case}: CP indices {sorted(color_pattern)} != "
            f"range(pattern_length={pattern_length})"
        )

    result = {
        "colors": colors,
        "color_pattern": [color_pattern[i] for i in range(pattern_length)],
        "bead_samples": {str(k): v for k, v in sorted(bead_samples.items())},
    }
    for name, value in scalars.items():
        key = name.lower()
        result[key] = int(value) if name in _INT_FIELDS else value
    return result


def main() -> None:
    cases = {}
    shared_colors = None
    for case in range(1, NUM_CASES + 1):
        print(f"Running dump.pov for case {case}...", file=sys.stderr)
        data = run_case(case)
        if shared_colors is None:
            shared_colors = data.pop("colors")
        else:
            assert data.pop("colors") == shared_colors, (
                f"case {case}: named colors differ from case 1 (unexpected)"
            )
        cases[str(case)] = data

    golden = {"colors": shared_colors, "cases": cases}
    GOLDEN_JSON.write_text(json.dumps(golden, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {GOLDEN_JSON}", file=sys.stderr)


if __name__ == "__main__":
    main()
