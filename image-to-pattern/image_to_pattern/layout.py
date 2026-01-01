"""Layout utilities for mapping bead counts to row/column structure.

The POV file uses `beads_per_row = 6.5` and derives:
    nrows = floor(0.5 + nbeads / beads_per_row)
    exact_beads_per_row = nbeads / nrows

We mirror that math, then distribute floor/ceil row lengths to sum to
`nbeads` while keeping rows as even as possible (alternating 6/7 beads
when exact_beads_per_row is ~6.5).
"""

import math
from typing import List, Tuple


def compute_nrows(nbeads: int, beads_per_row: float = 6.5) -> int:
    """Compute number of rows using the POV formula."""
    return math.floor(0.5 + (nbeads / beads_per_row))


def row_lengths_for_beads(nbeads: int, beads_per_row: float = 6.5) -> List[int]:
    """Return a list of row lengths (beads per row) that sum to nbeads.

    Rows alternate between floor/ceil(exact_beads_per_row) distributed
    evenly (Bresenham-style) to minimize run length of the same count.
    """
    nrows = compute_nrows(nbeads, beads_per_row)
    exact = nbeads / nrows
    floor_len = math.floor(exact)
    ceil_len = math.ceil(exact)

    num_ceil = nbeads - nrows * floor_len  # how many rows get the ceil length
    rows: List[int] = []
    error = 0
    for _ in range(nrows):
        error += num_ceil
        if error >= nrows:
            rows.append(ceil_len)
            error -= nrows
        else:
            rows.append(floor_len)

    if sum(rows) != nbeads or any(length not in (floor_len, ceil_len) for length in rows):
        raise ValueError("Row distribution failed to match bead count")
    return rows


def bead_index_to_row_col(nbeads: int, beads_per_row: float = 6.5) -> List[Tuple[int, int]]:
    """Map bead_index (0-based) to (row, col) based on computed row lengths.

    This assumes linear progression along rows (not spatial coords),
    which is enough for unwrapping sequences and testing ordering logic.
    """
    rows = row_lengths_for_beads(nbeads, beads_per_row)
    mapping: List[Tuple[int, int]] = []
    bead_idx = 0
    for row_idx, row_len in enumerate(rows):
        for col_idx in range(row_len):
            mapping.append((row_idx, col_idx))
            bead_idx += 1
    if bead_idx != nbeads:
        raise ValueError("Mapping length mismatch")
    return mapping
