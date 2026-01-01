"""Matching sampled bead indices against known POV patterns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from .pov_patterns import PatternDefinition, PATTERNS


@dataclass
class MatchResult:
    pattern: PatternDefinition
    offset: int
    mismatches: int
    matched: int

    @property
    def match_rate(self) -> float:
        if self.matched == 0:
            return 0.0
        return 1.0 - (self.mismatches / self.matched)


def _hamming_distance(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def match_pattern(indices: Sequence[int], pattern: PatternDefinition) -> MatchResult:
    """Find the best offset of `pattern.color_pattern` against `indices`.

    Compares the sampled indices against the repeated pattern, returning
    the offset with the fewest mismatches over the observed length.
    """
    if not indices:
        return MatchResult(pattern=pattern, offset=0, mismatches=0, matched=0)
    pat = pattern.color_pattern
    pat_len = len(pat)
    best_offset = 0
    best_mismatches = len(indices) + 1
    for offset in range(pat_len):
        repeated = [pat[(offset + i) % pat_len] for i in range(len(indices))]
        mismatches = _hamming_distance(indices, repeated)
        if mismatches < best_mismatches:
            best_mismatches = mismatches
            best_offset = offset
    return MatchResult(
        pattern=pattern,
        offset=best_offset,
        mismatches=best_mismatches,
        matched=len(indices),
    )


def best_pattern_match(indices: Sequence[int], patterns: Iterable[PatternDefinition] = PATTERNS) -> MatchResult:
    """Return the best matching pattern among provided definitions."""
    best: Optional[MatchResult] = None
    for pat in patterns:
        res = match_pattern(indices, pat)
        if best is None or res.match_rate > best.match_rate:
            best = res
    return best if best is not None else MatchResult(pattern=PATTERNS[0], offset=0, mismatches=0, matched=0)
