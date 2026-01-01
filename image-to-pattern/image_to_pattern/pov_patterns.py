"""Canonical bead patterns derived from `beads.pov`.

We capture the `color_pattern`, `ngroups`, and palette metadata so we can
test mapping logic and later generate POV-ready output. Case numbers match
`bead_pattern` cases in the POV file.
"""

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


Color = Tuple[float, float, float]  # rgb in [0,1]


@dataclass(frozen=True)
class PatternDefinition:
    case: int
    color_pattern: List[int]
    ngroups: int
    pattern_rows_per_group: Optional[int] = None
    beads_per_row: float = 6.5
    palette: Optional[Sequence[Color]] = None

    @property
    def pattern_length(self) -> int:
        return len(self.color_pattern)

    @property
    def nbeads(self) -> int:
        return self.pattern_length * self.ngroups


def _case3_pattern() -> List[int]:
    """Reconstruct the programmatic pattern from beads.pov case 3."""
    n1 = 50
    n2 = 12
    color_pattern = [0] * ((n1 + n2) * 6)  # matches array size in POV
    index = 0
    while index < n1:
        color_pattern[3 * index + 0] = 0
        color_pattern[3 * index + 1] = 1
        color_pattern[3 * index + 2] = 1
        color_pattern[3 * (index + n1 + n2) + 0] = 1
        color_pattern[3 * (index + n1 + n2) + 1] = 0
        color_pattern[3 * (index + n1 + n2) + 2] = 0
        index += 1
    index = 0
    while index < n2:
        color_pattern[3 * (index + n1) + 0] = 2
        color_pattern[3 * (index + n1) + 1] = 2
        color_pattern[3 * (index + n1) + 2] = 2
        color_pattern[3 * (index + n1 + n2 + n1) + 0] = 2
        color_pattern[3 * (index + n1 + n2 + n1) + 1] = 2
        color_pattern[3 * (index + n1 + n2 + n1) + 2] = 2
        index += 1
    return color_pattern


# Palette values are taken from POV definitions where explicit; implicit named
# colors (e.g., Red, Green) are standard POVRGB. We keep them for reference.
MyBlue = (0.20, 0.0, 0.75)
Dark_Purple = (0.38, 0.12, 0.37)
Med_Purple = (0.73, 0.16, 0.96)
Light_Purple = (0.87, 0.58, 0.98)


PATTERNS: List[PatternDefinition] = [
    PatternDefinition(
        case=1,
        color_pattern=[
            0,
            1,
            1,
            1,
            1,
            2,
            0,
            0,
            1,
            1,
            1,
            2,
            0,
            0,
            0,
            1,
            1,
            2,
            0,
            0,
            0,
            0,
            1,
            2,
        ],
        ngroups=28,
        pattern_rows_per_group=4,
    ),
    PatternDefinition(
        case=2,
        color_pattern=[
            0,
            1,
            1,
            2,
            3,
            2,
            1,
            0,
            1,
            2,
            3,
            3,
            2,
            1,
            0,
            1,
            2,
            3,
            2,
            1,
            1,
            0,
            1,
            2,
            2,
            1,
            2,
            1,
            0,
            1,
            2,
            1,
            2,
            2,
            1,
        ],
        ngroups=20,
        pattern_rows_per_group=5,
        palette=(MyBlue, None, None, None),
    ),
    PatternDefinition(
        case=3,
        color_pattern=_case3_pattern(),
        ngroups=2,
    ),
    PatternDefinition(
        case=4,
        color_pattern=[
            0,
            1,
            1,
            2,
            2,
            3,
            3,
            0,
            1,
            4,
            2,
            4,
            3,
            4,
            0,
            3,
            3,
            1,
            1,
            2,
            2,
            0,
            3,
            4,
            1,
            4,
            2,
            4,
            0,
            2,
            2,
            3,
            3,
            1,
            1,
            0,
            2,
            4,
            3,
            4,
            1,
            4,
        ],
        ngroups=18,
        pattern_rows_per_group=6,
    ),
    PatternDefinition(
        case=5,
        color_pattern=[
            3,
            2,
            1,
            0,
            1,
            2,
            3,
            2,
            1,
            0,
            0,
            1,
            2,
            2,
            1,
            0,
            1,
            0,
            1,
            2,
            1,
            0,
            1,
            1,
            0,
            1,
            1,
            0,
            1,
            2,
            1,
            0,
            1,
            0,
            1,
            2,
            2,
            1,
            0,
            1,
            2,
            0,
            1,
            2,
        ],
        ngroups=18,
        pattern_rows_per_group=6,
    ),
    PatternDefinition(
        case=6,
        color_pattern=[
            2,
            1,
            3,
            0,
            3,
            1,
            2,
            1,
            3,
            0,
            0,
            3,
            1,
            1,
            3,
            0,
            3,
            0,
            3,
            1,
            3,
            0,
            3,
            3,
            0,
            3,
            3,
            0,
            3,
            2,
            3,
            0,
            3,
            0,
            3,
            2,
            2,
            3,
            0,
            0,
            3,
            2,
            1,
            2,
            3,
            0,
            3,
            2,
            1,
            2,
            3,
            0,
            0,
            3,
            2,
            2,
            3,
            0,
            3,
            0,
            3,
            2,
            3,
            0,
            3,
            3,
            0,
            3,
            1,
            3,
            0,
            3,
            0,
            3,
            1,
            1,
            3,
            0,
            0,
            3,
            1,
        ],
        ngroups=9,
        pattern_rows_per_group=6,
        palette=(None, Dark_Purple, Light_Purple, None),
    ),
    PatternDefinition(
        case=7,
        color_pattern=[
            0,
            1,
            2,
            2,
            2,
            2,
            0,
            1,
            1,
            2,
            2,
            2,
            0,
            1,
            1,
            1,
            2,
            2,
            0,
            1,
            1,
            1,
            1,
            2,
        ],
        ngroups=28,
        pattern_rows_per_group=4,
    ),
    PatternDefinition(
        case=8,
        color_pattern=[
            0,
            0,
            1,
            1,
            3,
            3,
            0,
            0,
            2,
            2,
            3,
            3,
            3,
            3,
            2,
            2,
            0,
            0,
            3,
            3,
            1,
            1,
            0,
            0,
            4,
            4,
            4,
            4,
            4,
            4,
        ],
        ngroups=24,
        pattern_rows_per_group=5,
    ),
]


def get_pattern(case: int) -> PatternDefinition:
    for p in PATTERNS:
        if p.case == case:
            return p
    raise KeyError(f"No pattern for case {case}")
