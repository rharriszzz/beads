"""6.5-bead graph paper, extracted from R344; no photograph or inference inputs.

Source: photo2/r344/graph_paper.py at research commit
628351437842b2ecd05f8a1765d17449fbea61f9. The historical I/O entry point is
replaced with a standalone CLI. Geometry and point-field conventions are kept;
public integer arguments are now checked explicitly. See docs/graph-paper.md.
"""

import argparse
import json

X0 = -1
X_SCALE, Y_SCALE = 24, 32
RX, RY = 18, 14


def _integer(name, value, minimum=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


def representative(k, x0=X0):
    """Unique site of integer k in x0 <= x < x0+13, including negative k."""
    _integer("k", k)
    _integer("x0", x0)
    x = x0 + (2 * k - x0) % 13
    return x, (2 * k - x) // 13


def boundary(k, x0=X0):
    """Gap-following cut just before k. Mathematical y increases upward."""
    x, y = representative(k, x0)
    first = x0 + (y - x0) % 2
    left, right = x0 - 1, x0 + 13
    if x == first:
        return [[left, y - .5], [right, y - .5]]
    return [[left, y + .5], [x - 1, y + .5],
            [x - 1, y - .5], [right, y - .5]]


def strip_sides(lower, upper, x0=X0):
    """Solid outlines halfway between basic centers and lateral copies."""
    for name, value in [("lower", lower), ("upper", upper), ("x0", x0)]:
        _integer(name, value)
    if upper < lower:
        raise ValueError("upper must not precede lower")
    sides = {"left": [], "right": []}
    for y in range(lower, upper + 1):
        xs = list(range(x0 + (y - x0) % 2, x0 + 13, 2))
        for name, x in [("left", xs[0] - 1), ("right", xs[-1] + 1)]:
            sides[name].extend([[x, y - .5], [x, y + .5]])
    return sides


def layout(length, start=0, x0=X0, extension_rows=8, minimum_rows=40,
           side_beads=7):
    """Describe an arbitrary repeat interval and its display-only copies.

    The default has exactly seven horizontal continuation beads per side on
    EVERY row. Only basic-strip points with in_chosen_interval=True are members
    of the selected repeat. Neither lateral nor vertical copies add evidence.
    """
    for name, value, minimum in [
        ("length", length, 1), ("start", start, None), ("x0", x0, None),
        ("extension_rows", extension_rows, 0), ("minimum_rows", minimum_rows, 0),
        ("side_beads", side_beads, 0),
    ]:
        _integer(name, value, minimum)
    lower = representative(start, x0)[1] - extension_rows
    upper = representative(start + length - 1, x0)[1] + extension_rows
    shortage = max(0, minimum_rows - (upper - lower + 1))
    lower -= shortage // 2
    upper += shortage - shortage // 2
    points = []
    for y in range(lower, upper + 1):
        basic_x = list(range(x0 + (y - x0) % 2, x0 + 13, 2))
        n = len(basic_x)
        for slot in range(-side_beads, n + side_beads):
            x = basic_x[0] + 2 * slot
            k = (x + 13 * y) // 2
            cx, cy = representative(k, x0)
            side = "left" if slot < 0 else "right" if slot >= n else "basic"
            points.append(dict(
                x=x, y=y, a=(x + y) // 2, b=(y - x) // 2, k=k,
                position=(k - start) % length, repeat_copy=(k - start) // length,
                row_slot=slot, basic_row_count=n, side=side,
                lateral_copy=(x - cx) // 13, canonical_xy=[cx, cy],
                in_chosen_interval=side == "basic" and start <= k < start + length,
            ))
    return dict(
        length=length, start=start, x0=x0, strip=[x0, x0 + 13], rows=[lower, upper],
        start_boundary=boundary(start, x0), end_boundary=boundary(start + length, x0),
        side_boundaries=strip_sides(lower, upper, x0), side_beads=side_beads,
        points=points,
        display_units=dict(x_scale=X_SCALE, y_scale=Y_SCALE, ellipse_rx=RX, ellipse_ry=RY),
        membership="Exactly one canonical representative per k in [start,start+length). Lateral copies are never additional members or observations.",
        axes="Physical display y increases upward; screen ordinate is inverted at rendering.",
    )


def pattern_layout(strict_colors, provisional_colors=None, **geometry):
    """Attach R/Y/B/? colors to general geometry using only sequence position.

    Accept whitespace-separated code strings or lists of full color names.
    Unknowns stay unknown. Provisional colors are optional and remain separate.
    The 13-half-pitch circumference is specific to 6.5-bead crochet.
    """
    codes = {"R": "red", "Y": "yellow", "B": "black", "?": "?"}

    def normalize(colors):
        values = [c for c in colors if not c.isspace()] if isinstance(colors, str) else list(colors)
        if not values or any(not isinstance(c, str) for c in values):
            raise ValueError("Use R/Y/B/? or lists of red/yellow/black/? colors")
        result = [codes.get(c, c) for c in values]
        if any(c not in ["red", "yellow", "black", "?"] for c in result):
            raise ValueError("Use R/Y/B/? or lists of red/yellow/black/? colors")
        return result

    strict = normalize(strict_colors)
    provisional = normalize(provisional_colors) if provisional_colors is not None else strict
    if len(strict) != len(provisional):
        raise ValueError("Color sequences must have equal lengths")
    paper = layout(len(strict), **geometry)
    for point in paper["points"]:
        i = point["position"]
        point.update(strict_color=strict[i], provisional_color=provisional[i],
                     tentative=strict[i] == "?" and provisional[i] != "?")
    return paper


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequence", help="R/Y/B/? codes; quote spaces")
    parser.add_argument("--provisional")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--x0", type=int, default=X0)
    parser.add_argument("--extension-rows", type=int, default=8)
    args = parser.parse_args()
    try:
        paper = pattern_layout(args.sequence, args.provisional, start=args.start,
                               x0=args.x0, extension_rows=args.extension_rows)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(paper, indent=2))


if __name__ == "__main__":
    main()
