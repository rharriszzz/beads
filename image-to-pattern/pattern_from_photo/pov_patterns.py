"""Canonical bead-pattern tables, parsed directly from ``beads.pov``.

v1 (`image_to_pattern/pov_patterns.py`) hand-transcribed these tables and got
two of them wrong: case 5 was 44 entries instead of 42, and case 6 was 81
entries instead of 84, with the values diverging from the point of error
onward (not just truncated/padded). To avoid repeating that class of bug,
this module parses the `#case` blocks of `beads.pov` directly.

Only `pattern_length`, `ngroups`, and `beads_per_row` feed the geometry in
`layout.py` (these are the values actually used in beads.pov's
`nbeads = ngroups * pattern_length` / `nrows = floor(0.5 + nbeads /
beads_per_row)` formulas). `pattern_rows_per_group` is carried along as
descriptive metadata only -- it is not used by any formula in beads.pov.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

Color = Tuple[float, float, float]

DEFAULT_BEADS_POV = Path(__file__).resolve().parents[2] / "beads.pov"

# RGB values for the standard POV-Ray named colors referenced by beads.pov's
# bead palettes. Transcribed from POV-Ray 3.7's include/colors.inc
# (/usr/share/povray-3.7/include/colors.inc) and cross-checked by the
# povray color dump in povray_golden/ (see generate_golden.py).
NAMED_COLORS: Dict[str, Color] = {
    "Red": (1.0, 0.0, 0.0),
    "Green": (0.0, 1.0, 0.0),
    "Blue": (0.0, 0.0, 1.0),
    "Yellow": (1.0, 1.0, 0.0),
    "White": (1.0, 1.0, 1.0),
    "Black": (0.0, 0.0, 0.0),
    "Gray20": (0.2, 0.2, 0.2),
    "LightBlue": (0.74902, 0.847059, 0.847059),
    "LimeGreen": (0.196078, 0.8, 0.196078),
    "OrangeRed": (1.0, 0.25, 0.0),
    "Plum": (0.917647, 0.678431, 0.917647),
    "SlateBlue": (0.0, 0.498039, 1.0),
    "SteelBlue": (0.137255, 0.419608, 0.556863),
}


@dataclass(frozen=True)
class PatternDefinition:
    case: int
    color_pattern: List[int]
    ngroups: int
    pattern_rows_per_group: Optional[int] = None
    beads_per_row: float = 6.5
    palette: Optional[Sequence[Optional[Color]]] = None

    @property
    def pattern_length(self) -> int:
        return len(self.color_pattern)

    @property
    def nbeads(self) -> int:
        return self.pattern_length * self.ngroups


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _case3_color_pattern(n1: int, n2: int) -> List[int]:
    """Replicate the `#while` construction of case 3's `color_pattern`.

    This is a direct line-for-line port of the loops in beads.pov; it is
    cross-checked against POV-Ray's own `dimension_size`/array contents via
    the golden-value fixture.
    """
    color_pattern = [0] * ((n1 + n2) * 6)
    for index in range(n1):
        color_pattern[3 * index + 0] = 0
        color_pattern[3 * index + 1] = 1
        color_pattern[3 * index + 2] = 1
        color_pattern[3 * (index + n1 + n2) + 0] = 1
        color_pattern[3 * (index + n1 + n2) + 1] = 0
        color_pattern[3 * (index + n1 + n2) + 2] = 0
    for index in range(n2):
        color_pattern[3 * (index + n1) + 0] = 2
        color_pattern[3 * (index + n1) + 1] = 2
        color_pattern[3 * (index + n1) + 2] = 2
        color_pattern[3 * (index + n1 + n2 + n1) + 0] = 2
        color_pattern[3 * (index + n1 + n2 + n1) + 1] = 2
        color_pattern[3 * (index + n1 + n2 + n1) + 2] = 2
    return color_pattern


def _split_switches(text: str) -> Tuple[str, str]:
    """Split beads.pov into (pattern switch, palette switch) source regions.

    beads.pov contains two `#switch (bead_pattern)` blocks: the first
    defines `color_pattern`/`ngroups`/etc, the second defines the `beads`
    palette array. They are separated by the `pattern_length = ...` declare.
    """
    text = _strip_comments(text)
    marker = text.index("pattern_length")
    before, after = text[:marker], text[marker:]
    pattern_region = before[before.index("#switch (bead_pattern)"):]
    palette_region = after[after.index("#switch (bead_pattern)"):]
    return pattern_region, palette_region


def _parse_pattern_switch(region: str) -> Dict[int, dict]:
    patterns: Dict[int, dict] = {}
    for case_match in re.finditer(r"#case\s*\((\d+)\)(.*?)#break", region, re.S):
        case_num = int(case_match.group(1))
        body = case_match.group(2)

        ngroups = int(re.search(r"ngroups\s*=\s*(\d+)", body).group(1))
        beads_per_row = float(re.search(r"beads_per_row\s*=\s*([\d.]+)", body).group(1))
        rows_match = re.search(r"pattern_rows_per_group\s*=\s*(\d+)", body)
        pattern_rows_per_group = int(rows_match.group(1)) if rows_match else None

        if case_num == 3:
            n1 = int(re.search(r"n1\s*=\s*(\d+)", body).group(1))
            n2 = int(re.search(r"n2\s*=\s*(\d+)", body).group(1))
            color_pattern = _case3_color_pattern(n1, n2)
        else:
            arr_match = re.search(r"color_pattern\s*=\s*array\[(\d+)\]\{(.*?)\}", body, re.S)
            declared_len = int(arr_match.group(1))
            values = [int(x) for x in re.split(r"[\s,]+", arr_match.group(2)) if x.strip()]
            if len(values) != declared_len:
                raise ValueError(
                    f"case {case_num}: beads.pov declares array[{declared_len}] but "
                    f"the literal initializer has {len(values)} values"
                )
            color_pattern = values

        patterns[case_num] = dict(
            color_pattern=color_pattern,
            ngroups=ngroups,
            pattern_rows_per_group=pattern_rows_per_group,
            beads_per_row=beads_per_row,
        )
    return patterns


_COLOR_RGB_RE = re.compile(
    r"(?:color\s+)?rgb\s*<\s*([+-]?[\d.]+)\s*,\s*([+-]?[\d.]+)\s*,\s*([+-]?[\d.]+)\s*>"
)
_COLOR_RGBPARTS_RE = re.compile(
    r"(?:color\s+)?"
    r"(?:red\s+([+-]?[\d.]+)\s*)?"
    r"(?:green\s+([+-]?[\d.]+)\s*)?"
    r"(?:blue\s+([+-]?[\d.]+)\s*)?"
)


def _resolve_color_expr(expr: str, known_colors: Dict[str, Color]) -> Color:
    expr = expr.strip().rstrip(";").strip()

    m = _COLOR_RGB_RE.match(expr)
    if m:
        return tuple(float(g) for g in m.groups())  # type: ignore[return-value]

    if re.match(r"(?:color\s+)?(?:red|green|blue)\b", expr):
        m = _COLOR_RGBPARTS_RE.match(expr)
        if m and any(m.groups()):
            r, g, b = (float(x) if x is not None else 0.0 for x in m.groups())
            return (r, g, b)

    name = expr.split()[0]
    if name in known_colors:
        return known_colors[name]
    raise ValueError(f"Cannot resolve color expression: {expr!r}")


_BEADS_ASSIGN_RE = re.compile(
    r"beads\[(\d+)\]\s*=\s*bead\(\s*\w+\(\s*(\w+)\s*\)\s*,"
)
_LOCAL_COLOR_DECL_RE = re.compile(r"#declare\s+(\w+)\s*=\s*((?:color\s+)?(?:rgb|red|green|blue)\b[^;]*);")


def _parse_palette_switch(region: str) -> Dict[int, List[Optional[Color]]]:
    palettes: Dict[int, List[Optional[Color]]] = {}
    for case_match in re.finditer(r"#case\s*\((\d+)\)(.*?)#break", region, re.S):
        case_num = int(case_match.group(1))
        body = case_match.group(2)

        local_colors = dict(NAMED_COLORS)
        for decl in _LOCAL_COLOR_DECL_RE.finditer(body):
            local_colors[decl.group(1)] = _resolve_color_expr(decl.group(2), local_colors)

        size_match = re.search(r"beads\s*=\s*array\[(\d+)\]", body)
        palette: List[Optional[Color]] = [None] * int(size_match.group(1))
        for assign in _BEADS_ASSIGN_RE.finditer(body):
            idx = int(assign.group(1))
            color_name = assign.group(2)
            palette[idx] = _resolve_color_expr(color_name, local_colors)
        palettes[case_num] = palette
    return palettes


def parse_beads_pov(path: Path = DEFAULT_BEADS_POV) -> Dict[int, PatternDefinition]:
    text = Path(path).read_text()
    pattern_region, palette_region = _split_switches(text)
    patterns = _parse_pattern_switch(pattern_region)
    palettes = _parse_palette_switch(palette_region)

    result: Dict[int, PatternDefinition] = {}
    for case_num, fields in patterns.items():
        result[case_num] = PatternDefinition(
            case=case_num,
            palette=palettes.get(case_num),
            **fields,
        )
    return result


PATTERNS_BY_CASE: Dict[int, PatternDefinition] = parse_beads_pov()
PATTERNS: List[PatternDefinition] = [PATTERNS_BY_CASE[c] for c in sorted(PATTERNS_BY_CASE)]


def get_pattern(case: int) -> PatternDefinition:
    try:
        return PATTERNS_BY_CASE[case]
    except KeyError:
        raise KeyError(f"No pattern for case {case}") from None
