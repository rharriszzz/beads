"""Numerical subset of fft-image-explorer/find_splines.py; see PROVENANCE.json.
Historical HSV calibration is deliberately retained for exact regression.
No saved spline coordinates or bead annotations are read by this module.
"""
from __future__ import annotations
import math
import numpy as np
from pathlib import Path
from matplotlib.colors import rgb_to_hsv


def _smooth_closed_curve(points: np.ndarray, window: int = 7, passes: int = 2) -> np.ndarray:
    """Light circular smoothing to make a traced polygon appear spline-like."""
    if points.shape[0] < 8:
        return points

    n = points.shape[0]
    win = max(3, int(window))
    if win % 2 == 0:
        win += 1
    half = win // 2

    out = points.astype(np.float64, copy=True)
    kernel = np.ones(win, dtype=np.float64) / float(win)
    for _ in range(max(1, int(passes))):
        px = np.pad(out[:, 0], (half, half), mode="wrap")
        py = np.pad(out[:, 1], (half, half), mode="wrap")
        sx = np.convolve(px, kernel, mode="valid")
        sy = np.convolve(py, kernel, mode="valid")
        out = np.column_stack([sx[:n], sy[:n]])
    return out.astype(np.float32)


def _cross2d(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * by - ay * bx


def _segments_intersect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    q1: tuple[float, float],
    q2: tuple[float, float],
    eps: float = 1e-9,
) -> bool:
    p1x, p1y = p1
    p2x, p2y = p2
    q1x, q1y = q1
    q2x, q2y = q2

    r_x = p2x - p1x
    r_y = p2y - p1y
    s_x = q2x - q1x
    s_y = q2y - q1y
    rxs = _cross2d(r_x, r_y, s_x, s_y)
    qmp_x = q1x - p1x
    qmp_y = q1y - p1y
    qmpxr = _cross2d(qmp_x, qmp_y, r_x, r_y)

    if abs(rxs) <= eps and abs(qmpxr) <= eps:
        rr = r_x * r_x + r_y * r_y
        if rr <= eps:
            return math.hypot(q1x - p1x, q1y - p1y) <= eps
        t0 = ((q1x - p1x) * r_x + (q1y - p1y) * r_y) / rr
        t1 = ((q2x - p1x) * r_x + (q2y - p1y) * r_y) / rr
        tmin = min(t0, t1)
        tmax = max(t0, t1)
        return tmax >= -eps and tmin <= 1.0 + eps

    if abs(rxs) <= eps:
        return False

    t = _cross2d(qmp_x, qmp_y, s_x, s_y) / rxs
    u = _cross2d(qmp_x, qmp_y, r_x, r_y) / rxs
    return (-eps <= t <= 1.0 + eps) and (-eps <= u <= 1.0 + eps)


def _spline_intersects(outer: np.ndarray, inner: np.ndarray, eps: float = 1e-6) -> bool:
    if outer.shape[0] < 2 or inner.shape[0] < 2:
        return False

    for i in range(outer.shape[0] - 1):
        p1 = (float(outer[i, 0]), float(outer[i, 1]))
        p2 = (float(outer[i + 1, 0]), float(outer[i + 1, 1]))
        for j in range(inner.shape[0] - 1):
            q1 = (float(inner[j, 0]), float(inner[j, 1]))
            q2 = (float(inner[j + 1, 0]), float(inner[j + 1, 1]))
            if _segments_intersect(p1, p2, q1, q2, eps=eps):
                return True
    return False


def _ensure_closed_curve(points: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    if points.shape[0] < 2:
        return points
    if np.hypot(*(points[0] - points[-1])) <= eps:
        return points
    return np.vstack([points, points[0]])


def _resample_closed_curve(points: np.ndarray, n_samples: int) -> np.ndarray:
    pts = _ensure_closed_curve(points.astype(np.float64, copy=False))
    if pts.shape[0] < 2:
        return pts.astype(np.float32)

    seg = pts[1:] - pts[:-1]
    seg_len = np.hypot(seg[:, 0], seg[:, 1])
    total = float(seg_len.sum())
    if total <= 1e-9:
        out = np.repeat(pts[:1], max(2, n_samples), axis=0)
        return out.astype(np.float32)

    cum = np.concatenate(([0.0], np.cumsum(seg_len)))
    targets = np.linspace(0.0, total, num=max(2, n_samples), endpoint=False)
    out = np.zeros((targets.shape[0], 2), dtype=np.float64)

    for i, d in enumerate(targets):
        k = int(np.searchsorted(cum, d, side="right") - 1)
        k = int(np.clip(k, 0, seg_len.shape[0] - 1))
        d0 = cum[k]
        d1 = cum[k + 1]
        t = 0.0 if d1 <= d0 else (d - d0) / (d1 - d0)
        out[i] = pts[k] + t * (pts[k + 1] - pts[k])

    out = np.vstack([out, out[0]])
    return out.astype(np.float32)


def _nearest_point_on_closed_polyline(pt: np.ndarray, curve_closed: np.ndarray) -> tuple[np.ndarray, float]:
    """Return nearest point on a closed polyline to pt and the distance."""
    best_d2 = float("inf")
    best_pt = curve_closed[0].astype(np.float64)

    for i in range(curve_closed.shape[0] - 1):
        a = curve_closed[i].astype(np.float64)
        b = curve_closed[i + 1].astype(np.float64)
        ab = b - a
        ab2 = float(ab[0] * ab[0] + ab[1] * ab[1])
        if ab2 <= 1e-12:
            cand = a
        else:
            t = float(np.dot(pt - a, ab) / ab2)
            t = min(1.0, max(0.0, t))
            cand = a + t * ab

        d = pt - cand
        d2 = float(d[0] * d[0] + d[1] * d[1])
        if d2 < best_d2:
            best_d2 = d2
            best_pt = cand

    return best_pt, float(math.sqrt(best_d2))


def _build_centerline_spline(
    outer: np.ndarray,
    inner: np.ndarray,
    return_radii: bool = False,
) -> np.ndarray | tuple[np.ndarray, np.ndarray] | None:
    if outer is None or inner is None:
        return None
    if outer.shape[0] < 3 or inner.shape[0] < 3:
        return None

    n_samples = max(180, min(1440, 2 * (max(outer.shape[0], inner.shape[0]) - 1)))
    outer_rs = _resample_closed_curve(outer, n_samples=n_samples).astype(np.float64)
    inner_rs = _resample_closed_curve(inner, n_samples=n_samples).astype(np.float64)

    inner_open = inner_rs[:-1]

    center_pts: list[np.ndarray] = []
    center_radii: list[float] = []
    for i_pt in inner_open:
        nearest_outer, dist = _nearest_point_on_closed_polyline(i_pt, outer_rs)
        if dist <= 1e-9:
            center_pts.append(i_pt.copy())
            center_radii.append(0.0)
            continue
        direction = nearest_outer - i_pt
        center_pts.append(i_pt + 0.5 * direction)
        center_radii.append(0.5 * float(dist))

    print(f"Centerline builder: midpoint samples from inner->outer nearest map={len(center_pts)}")

    if len(center_pts) < max(48, n_samples // 3):
        return None

    center = np.asarray(center_pts, dtype=np.float32)
    center = _ensure_closed_curve(center)
    center_out = center.astype(np.float32)
    radii = np.asarray(center_radii, dtype=np.float32)
    if radii.size > 0:
        radii = np.concatenate([radii, radii[:1]])

    if bool(return_radii):
        return center_out, radii.astype(np.float32)
    return center_out


def _plot_trace_failure_debug(*args, **kwargs):
    raise RuntimeError("Historical ring tracer failed; no archived fallback is allowed.")


def _build_step_grid(
    raw_map: np.ndarray,
    step: int,
    threshold: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ys = np.arange(0, raw_map.shape[0], step, dtype=np.int32)
    xs = np.arange(0, raw_map.shape[1], step, dtype=np.int32)
    coarse = raw_map[ys[:, None], xs[None, :]]
    return ys, xs, coarse, coarse >= threshold


def _find_centerline_start(
    coarse: np.ndarray,
    hi: np.ndarray,
    ys: np.ndarray,
    xs: np.ndarray,
    ring_steps: int = 4,
    min_fg_count: int = 5,
) -> tuple[tuple[int, int] | None, list[tuple[int, int, float]]]:
    gh, gw = coarse.shape
    cy = gh // 2
    cx = gw // 2

    start: tuple[int, int] | None = None
    start_scan_tail: list[tuple[int, int, float]] = []

    # Build the same-radius ring offsets used by the tracer.
    ring_offsets: list[tuple[float, int, int]] = []
    r = float(max(1, int(ring_steps)))
    for dy in range(-int(r) - 1, int(r) + 2):
        for dx in range(-int(r) - 1, int(r) + 2):
            if dx == 0 and dy == 0:
                continue
            d = math.hypot(dx, dy)
            if abs(d - r) <= 0.75:
                theta_local = math.atan2(-dy, dx)
                sweep_angle = (2.0 * math.pi - theta_local) % (2.0 * math.pi)
                ring_offsets.append((sweep_angle, dy, dx))
    ring_offsets.sort(key=lambda t: t[0])

    def _ring_midpoint_if_enough_fg(center_y: int, center_x: int) -> tuple[tuple[int, int] | None, int]:
        fg_points: list[tuple[int, int]] = []
        for _ang, dy, dx in ring_offsets:
            ny = center_y + dy
            nx = center_x + dx
            if ny < 1 or nx < 1 or ny >= gh - 1 or nx >= gw - 1:
                continue
            if bool(hi[ny, nx]):
                fg_points.append((ny, nx))
                if len(fg_points) >= max(1, int(min_fg_count)):
                    # User-requested rule: as soon as foreground-count reaches
                    # threshold (e.g. 5), choose the middle of those first hits.
                    mid = fg_points[int(min_fg_count) // 2]
                    return (int(mid[0]), int(mid[1])), len(fg_points)
        return None, len(fg_points)

    endpoint_orders = [
        [(cy, ix) for ix in range(gw - 1, -1, -1)],
        [(cy, ix) for ix in range(0, gw)],
        [(iy, cx) for iy in range(gh - 1, -1, -1)],
        [(iy, cx) for iy in range(0, gh)],
    ]
    for line in endpoint_orders:
        scan_vals: list[tuple[int, int, float]] = []
        for iy, ix in line:
            scan_vals.append((iy, ix, float(coarse[iy, ix])))
            ring_mid, fg_count = _ring_midpoint_if_enough_fg(iy, ix)
            if ring_mid is not None:
                start = ring_mid
                start_scan_tail = scan_vals[-5:]
                print(
                    "Initial start finder: selected ring midpoint from center-line scan "
                    f"at grid(y={iy},x={ix}) with foreground_on_ring={fg_count} "
                    f"(min_required={int(min_fg_count)}); "
                    f"start grid(y={start[0]},x={start[1]})"
                )
                break
        if start is not None:
            break

    if start is not None:
        print("Initial scan tail (last 5 checked from edge):")
        tail_base = max(0, len(start_scan_tail) - 5)
        for j, (iy, ix, val) in enumerate(start_scan_tail, start=tail_base):
            print(
                f"  edge_check[{j}]: grid(y={iy},x={ix}) "
                f"pixel(y={int(ys[iy])},x={int(xs[ix])}) raw={val:.3f}"
            )
    return start, start_scan_tail


def _collect_ring_transitions(
    coarse: np.ndarray,
    threshold: float,
    center_y: int,
    center_x: int,
    radius_steps: int,
) -> list[dict[str, float | int | str | bool]]:
    gh, gw = coarse.shape
    ordered_candidates: list[tuple[float, int, int]] = []
    r = float(radius_steps)
    for dy in range(-radius_steps - 1, radius_steps + 2):
        for dx in range(-radius_steps - 1, radius_steps + 2):
            if dx == 0 and dy == 0:
                continue
            d = math.hypot(dx, dy)
            if abs(d - r) <= 0.75:
                theta_local = math.atan2(-dy, dx)
                sweep_angle = (2.0 * math.pi - theta_local) % (2.0 * math.pi)
                ordered_candidates.append((sweep_angle, dy, dx))
    ordered_candidates.sort(key=lambda t: t[0])

    in_bounds: list[dict[str, float | int | str | bool]] = []
    states: list[bool] = []
    for ord_idx, (sweep_angle, dy, dx) in enumerate(ordered_candidates):
        ny = center_y + dy
        nx = center_x + dx
        if ny < 1 or nx < 1 or ny >= gh - 1 or nx >= gw - 1:
            continue
        val = float(coarse[ny, nx])
        state = bool(val >= threshold)
        in_bounds.append(
            {
                "ord_idx": ord_idx,
                "angle": sweep_angle,
                "dy": dy,
                "dx": dx,
                "ny": ny,
                "nx": nx,
                "raw": val,
                "state": state,
            }
        )
        states.append(state)

    trans: list[dict[str, float | int | str | bool]] = []
    n = len(in_bounds)
    if n < 2:
        return trans

    # Remove isolated one-bin state flips on the circular ring sequence:
    # LOW,HIGH,LOW -> LOW,LOW,LOW and HIGH,LOW,HIGH -> HIGH,HIGH,HIGH.
    # This suppresses singular spikes before counting transitions.
    warned_isolated: set[int] = set()
    cleaned_states = states.copy()
    for _ in range(max(1, n)):
        changed = False
        next_states = cleaned_states.copy()
        for i in range(n):
            prev_s = cleaned_states[(i - 1) % n]
            curr_s = cleaned_states[i]
            next_s = cleaned_states[(i + 1) % n]
            if prev_s == next_s and curr_s != prev_s:
                if i not in warned_isolated:
                    prev_row = in_bounds[(i - 1) % n]
                    curr_row = in_bounds[i]
                    next_row = in_bounds[(i + 1) % n]
                    print(
                        "Warning: removed isolated ring state spike "
                        f"at grid(y={int(curr_row['ny'])},x={int(curr_row['nx'])}) "
                        f"values(prev,mid,next)=({float(prev_row['raw']):.3f},"
                        f"{float(curr_row['raw']):.3f},{float(next_row['raw']):.3f})"
                    )
                    warned_isolated.add(i)
                next_states[i] = prev_s
                changed = True
        cleaned_states = next_states
        if not changed:
            break

    # Ignore short HIGH islands when they are bracketed by long LOW runs.
    # Rule requested by user: if HIGH run <= 4 and both neighboring LOW runs
    # are > 10, convert that HIGH run to LOW.
    for _ in range(max(1, n)):
        changed = False
        runs = _circular_runs(np.asarray(cleaned_states, dtype=bool))
        if not runs:
            break
        m = len(runs)
        for i, (state, start, run_len) in enumerate(runs):
            if not bool(state):
                continue
            left_state, _left_start, left_len = runs[(i - 1) % m]
            right_state, _right_start, right_len = runs[(i + 1) % m]
            if bool(left_state) or bool(right_state):
                continue
            if int(run_len) <= 4 and int(left_len) > 10 and int(right_len) > 10:
                print(
                    "Warning: removed short HIGH island "
                    f"len={int(run_len)} between LOW runs len={int(left_len)} and len={int(right_len)}"
                )
                for k in range(int(run_len)):
                    cleaned_states[(int(start) + k) % n] = False
                changed = True
        if not changed:
            break

    for i, row in enumerate(in_bounds):
        prev_state = cleaned_states[(i - 1) % n]
        curr_state = cleaned_states[i]
        if curr_state != prev_state:
            row_out = dict(row)
            row_out["ring_idx"] = i
            row_out["prev_state"] = prev_state
            row_out["curr_state"] = curr_state
            row_out["transition_type"] = "LOW->HIGH" if (not prev_state and curr_state) else "HIGH->LOW"
            trans.append(row_out)

    if trans:
        transition_positions = [int(t["ring_idx"]) for t in trans]
        m = len(transition_positions)
        for k, t in enumerate(trans):
            i = transition_positions[k]
            prev_i = transition_positions[(k - 1) % m]
            run_len = (i - prev_i) % n
            if run_len == 0:
                run_len = n
            t["run_len_prev"] = int(run_len)
    return trans


def _find_inner_start_from_outer_point0(
    raw_map: np.ndarray,
    step: int,
    threshold: float,
    outer_start: tuple[int, int],
    ys: np.ndarray,
    xs: np.ndarray,
    coarse: np.ndarray,
    start_radius: int = 64,
) -> tuple[int, int] | None:
    oy, ox = outer_start
    print("Inner-start search: begin from outer spline point 0")
    print(
        f"  outer p0 grid(y={oy},x={ox}) pixel(y={int(ys[oy])},x={int(xs[ox])}) "
        f"raw={float(coarse[oy, ox]):.3f}, threshold={threshold:.3f}"
    )

    baseline_r = max(1, int(start_radius))
    base_trans = _collect_ring_transitions(coarse, threshold, oy, ox, baseline_r)
    print(f"  radius={baseline_r}: transitions={len(base_trans)}")
    for i, t in enumerate(base_trans):
        print(
            f"    base[{i}] angle={math.degrees(float(t['angle'])):.2f}deg "
            f"{str(t['transition_type'])} grid(y={int(t['ny'])},x={int(t['nx'])}) "
            f"raw={float(t['raw']):.3f}"
        )

    max_r = max(baseline_r, max(coarse.shape) // 2)
    for radius in range(baseline_r + 1, max_r + 1):
        trans = _collect_ring_transitions(coarse, threshold, oy, ox, radius)
        print(f"  radius={radius}: transitions={len(trans)}")
        for i, t in enumerate(trans):
            run_len = int(t.get("run_len_prev", 0))
            prev_state_txt = "HIGH" if bool(t.get("prev_state", False)) else "LOW"
            print(
                f"    trans[{i}] angle={math.degrees(float(t['angle'])):.2f}deg "
                f"{str(t['transition_type'])} grid(y={int(t['ny'])},x={int(t['nx'])}) "
                f"raw={float(t['raw']):.3f} after {run_len} consecutive {prev_state_txt} samples"
            )

        # Keep center fixed at outer spline point 0 and expand until we have
        # enough transition structure to isolate the inner pair.
        if len(trans) < 4:
            continue

        if len(base_trans) < 2:
            print(
                "    baseline has fewer than 2 transitions; cannot identify which transitions belong to outer boundary."
            )
            continue

        base_angles = [float(t["angle"]) for t in base_trans]

        def circ_dist(a: float, b: float) -> float:
            d = abs(a - b)
            return min(d, 2.0 * math.pi - d)

        scored: list[tuple[float, int]] = []
        for i, t in enumerate(trans):
            a = float(t["angle"])
            dmin = min(circ_dist(a, b) for b in base_angles)
            scored.append((dmin, i))

        scored.sort(key=lambda x: x[0])
        # Two transitions near baseline correspond to outer boundary crossings.
        keep_existing = {idx for _, idx in scored[:2]}
        new_idxs = [i for i in range(len(trans)) if i not in keep_existing]
        if len(new_idxs) < 2:
            print("    unable to isolate two new transitions at this radius; continue.")
            continue

        t1 = trans[new_idxs[0]]
        t2 = trans[new_idxs[1]]

        run1 = int(t1.get("run_len_prev", 0))
        run2 = int(t2.get("run_len_prev", 0))
        if run1 < 12 or run2 < 12:
            print(
                "    rejected new transitions: minimum consecutive run length not met "
                f"(new[1]={run1}, new[2]={run2}, required>=12); continue."
            )
            continue

        print("    identified new transitions:")
        for j, t in enumerate([t1, t2], start=1):
            run_len = int(t.get("run_len_prev", 0))
            prev_state_txt = "HIGH" if bool(t.get("prev_state", False)) else "LOW"
            print(
                f"      new[{j}] angle={math.degrees(float(t['angle'])):.2f}deg "
                f"{str(t['transition_type'])} grid(y={int(t['ny'])},x={int(t['nx'])}) "
                f"pixel(y={int(ys[int(t['ny'])])},x={int(xs[int(t['nx'])])}) "
                f"after {run_len} consecutive {prev_state_txt} samples"
            )

        mid_y = int(round((int(t1["ny"]) + int(t2["ny"])) / 2.0))
        mid_x = int(round((int(t1["nx"]) + int(t2["nx"])) / 2.0))
        mid_y = int(np.clip(mid_y, 1, coarse.shape[0] - 2))
        mid_x = int(np.clip(mid_x, 1, coarse.shape[1] - 2))

        # Prefer a foreground-valued start point so the inner tracer begins on
        # the bracelet side of the boundary when possible.
        if float(coarse[mid_y, mid_x]) < threshold:
            fg_candidate: tuple[int, int] | None = None
            for t in (t1, t2):
                if str(t["transition_type"]) == "LOW->HIGH":
                    ty = int(np.clip(int(t["ny"]), 1, coarse.shape[0] - 2))
                    tx = int(np.clip(int(t["nx"]), 1, coarse.shape[1] - 2))
                    if float(coarse[ty, tx]) >= threshold:
                        fg_candidate = (ty, tx)
                        break
            if fg_candidate is not None:
                mid_y, mid_x = fg_candidate
            else:
                for t in (t1, t2):
                    ty = int(np.clip(int(t["ny"]), 1, coarse.shape[0] - 2))
                    tx = int(np.clip(int(t["nx"]), 1, coarse.shape[1] - 2))
                    if float(coarse[ty, tx]) >= threshold:
                        mid_y, mid_x = ty, tx
                        break
        print(
            f"    inner spline point 0 midpoint grid(y={mid_y},x={mid_x}) "
            f"pixel(y={int(ys[mid_y])},x={int(xs[mid_x])}) raw={float(coarse[mid_y, mid_x]):.3f}"
        )
        return mid_y, mid_x

    print("  inner-start search stop: no expanded radius produced at least 4 transitions.")
    return None


def _trace_outer_spline_step_cells(
    raw_map: np.ndarray,
    step: int,
    threshold: float = 99.0,
    ring_steps: int = 4,
    max_bg_gap: int = 0,
    clockwise: bool = True,
    debug_start_point: int | None = None,
    start_point: tuple[int, int] | None = None,
    spline_label: str = "outer",
    return_partial_on_stop: bool = False,
    verbose: bool = True,
    smooth_output: bool = True,
) -> np.ndarray | None:
    """Trace an outer bracelet spline by stepping along threshold transitions on the step grid."""
    h, w = raw_map.shape
    ys, xs, coarse, hi = _build_step_grid(raw_map, step=step, threshold=threshold)
    if ys.size < 5 or xs.size < 5:
        return None
    gh, gw = coarse.shape

    if start_point is not None:
        sy, sx = start_point
        if sy < 1 or sx < 1 or sy >= gh - 1 or sx >= gw - 1:
            print(
                f"Tracer stop ({spline_label} spline): provided {spline_label} spline point is out of valid tracing bounds; "
                f"grid(y={sy},x={sx})"
            )
            _emit_trace_result("FAILED", "start_out_of_bounds", 0)
            return None
        start = (int(sy), int(sx))
        if verbose:
            print(
                f"Tracer start ({spline_label} spline): using provided {spline_label} spline point "
                f"grid(y={start[0]},x={start[1]}) "
                f"pixel(y={int(ys[start[0]])},x={int(xs[start[1]])}) "
                f"raw={float(coarse[start[0], start[1]]):.3f}"
            )
    else:
        # Start from one end of the centerline and move inward until value drops below threshold.
        start, _ = _find_centerline_start(
            coarse=coarse,
            hi=hi,
            ys=ys,
            xs=xs,
            ring_steps=ring_steps,
            min_fg_count=5,
        )
    trace_output = False

    if start is None:
        print(
            f"Tracer stop ({spline_label} spline): no start {spline_label} spline point found on center lines where raw<threshold; "
            f"threshold={threshold:.3f}"
        )
        _emit_trace_result("FAILED", "no_start_point", 0)
        return None

    def is_transition(iy: int, ix: int) -> bool:
        # Transition is defined only by state change from current point to candidate.
        # No neighborhood/3x3 test.
        return bool(hi[iy, ix] != hi[curr_y, curr_x])

    # Cells approximately ring_steps away from current cell.
    ring_offsets: list[tuple[int, int]] = []
    r = float(ring_steps)
    for dy in range(-ring_steps - 1, ring_steps + 2):
        for dx in range(-ring_steps - 1, ring_steps + 2):
            if dx == 0 and dy == 0:
                continue
            d = math.hypot(dx, dy)
            if abs(d - r) <= 0.75:
                ring_offsets.append((dy, dx))
    if not ring_offsets:
        print("Tracer stop: no ring offsets generated; check ring_steps value.")
        _emit_trace_result("FAILED", "no_ring_offsets", 0)
        return None

    curr_y, curr_x = start
    pts: list[tuple[int, int]] = [(curr_y, curr_x)]
    visited_at: dict[tuple[int, int], int] = {(curr_y, curr_x): 0}
    start_y, start_x = curr_y, curr_x
    if verbose:
        print(
            f"{spline_label.capitalize()} spline point 0: grid(y={curr_y},x={curr_x}) "
            f"pixel(y={int(ys[curr_y])},x={int(xs[curr_x])})"
        )
    prev_dir: tuple[float, float] | None = None
    max_turn_rad = math.radians(90.0)
    stop_reason: str | None = None

    def _emit_trace_result(kind: str, reason: str, points_count: int) -> None:
        print(
            f"Tracer result ({spline_label} spline): {kind}; "
            f"reason={reason}; points={int(points_count)}"
        )

    def _find_near_revisit_index(
        y: int,
        x: int,
        points: list[tuple[int, int]],
        exclude_recent: int = 12,
        near_dist: float = 1.6,
    ) -> int | None:
        end = max(0, len(points) - exclude_recent)
        for i in range(end):
            py, px = points[i]
            if math.hypot(y - py, x - px) <= near_dist:
                return i
        return None

    def _partial_trace_pixels() -> np.ndarray | None:
        if len(pts) < 2:
            return None
        return np.array([[float(xs[ix]), float(ys[iy])] for iy, ix in pts], dtype=np.float32)

    while True:
        trace_output = (
            debug_start_point is not None
            and (len(pts) - 1) >= debug_start_point
        )
        curr_px = int(xs[curr_x])
        curr_py = int(ys[curr_y])

        # Lost-state detection: if the local neighborhood is all above or all below
        # threshold, there is no nearby crossing to follow.
        y0 = max(0, curr_y - ring_steps)
        y1 = min(gh, curr_y + ring_steps + 1)
        x0 = max(0, curr_x - ring_steps)
        x1 = min(gw, curr_x + ring_steps + 1)
        local_hi = hi[y0:y1, x0:x1]
        ly, lx = np.ogrid[y0:y1, x0:x1]
        local_disk = (ly - curr_y) ** 2 + (lx - curr_x) ** 2 <= ring_steps ** 2
        disk_vals = local_hi[local_disk]
        disk_n = int(disk_vals.size)
        disk_hi = int(np.count_nonzero(disk_vals))
        if disk_n > 0 and (disk_hi == 0 or disk_hi == disk_n):
            px = int(xs[curr_x])
            py = int(ys[curr_y])
            raw_here = float(coarse[curr_y, curr_x])
            state = "all>=threshold" if disk_hi == disk_n else "all<threshold"
            print(
                f"Tracer lost ({spline_label} spline): uniform neighborhood within "
                f"{ring_steps} steps ({ring_steps * step} px); {state}."
            )
            print(
                f"Tracer debug ({spline_label} spline): "
                f"grid(y={curr_y}, x={curr_x}), pixel(y={py}, x={px}), "
                f"raw={raw_here:.3f}, threshold={threshold:.3f}, "
                f"disk_hi={disk_hi}/{disk_n}, points_traced={len(pts)}"
            )
            if return_partial_on_stop:
                _emit_trace_result("PARTIAL", "uniform_neighborhood", len(pts))
                return _partial_trace_pixels()
            _emit_trace_result("FAILED", "uniform_neighborhood", len(pts))
            return None

        best: tuple[int, int] | None = None
        best_score = float("inf")
        cand_total = 0
        cand_oob = 0
        cand_not_transition = 0
        cand_too_short = 0
        cand_turn_reject = 0
        cand_scored = 0
        cand_debug_rows: list[dict[str, float | int | str | bool]] = []

        # Process ring candidates by a strict angular sweep around the CURRENT point
        # so debug angle progression matches (dy, dx) ordering intuitively.
        # Debug lines are printed in this exact same sweep order.
        ordered_candidates: list[tuple[float, int, int]] = []
        for dy, dx in ring_offsets:
            # Use a local geometric angle for the offset vector; y-axis inverted so
            # positive angles follow visual CCW on image coordinates.
            theta_local = math.atan2(-dy, dx)
            cw_angle = (2.0 * math.pi - theta_local) % (2.0 * math.pi)
            ccw_angle = (theta_local + 2.0 * math.pi) % (2.0 * math.pi)
            sweep_angle = cw_angle if clockwise else ccw_angle
            ordered_candidates.append((sweep_angle, dy, dx))
        ordered_candidates.sort(key=lambda t: t[0])

        sweep_label = "CW" if clockwise else "CCW"
        ordered_ring_states: list[bool] = []
        ordered_ring_meta: list[tuple[int, float, int, int, int, int, float]] = []
        in_bounds_entries: list[dict[str, float | int | str | bool]] = []

        for ord_idx, (sweep_angle, dy, dx) in enumerate(ordered_candidates):
            cand_total += 1
            ny = curr_y + dy
            nx = curr_x + dx
            if ny < 1 or nx < 1 or ny >= gh - 1 or nx >= gw - 1:
                cand_oob += 1
                cand_debug_rows.append(
                    {
                        "ord_idx": ord_idx,
                        "sweep_angle": sweep_angle,
                        "dy": dy,
                        "dx": dx,
                        "ny": ny,
                        "nx": nx,
                        "status": "out_of_bounds",
                    }
                )
                if trace_output:
                    print(
                        f"  ring[{ord_idx:02d}] {sweep_label} {math.degrees(sweep_angle):6.2f}deg "
                        f"(dy={dy:+d},dx={dx:+d}): out-of-bounds"
                    )
                continue

            val = float(coarse[ny, nx])
            hi_bool = bool(val >= threshold)
            hi_state = "HIGH" if hi_bool else "LOW"
            row: dict[str, float | int | str | bool] = {
                "ord_idx": ord_idx,
                "sweep_angle": sweep_angle,
                "dy": dy,
                "dx": dx,
                "ny": ny,
                "nx": nx,
                "pixel_y": int(ys[ny]),
                "pixel_x": int(xs[nx]),
                "raw": val,
                "state": hi_state,
                "hi": hi_bool,
            }
            ordered_ring_states.append(hi_bool)
            ordered_ring_meta.append(
                (ord_idx, sweep_angle, dy, dx, ny, nx, val)
            )
            in_bounds_entries.append(row)

        # Transition along sweep means a state change relative to the previous
        # in-bounds sample in angular order. Only these changes count.
        ring_n = len(ordered_ring_states)
        if ring_n < 2:
            print(
                f"Tracer stop ({spline_label} spline): insufficient in-bounds ring samples to validate transitions; "
                f"{spline_label} spline point grid(y={curr_y},x={curr_x})"
            )
            if return_partial_on_stop:
                _emit_trace_result("PARTIAL", "insufficient_ring_samples", len(pts))
                return _partial_trace_pixels()
            _emit_trace_result("FAILED", "insufficient_ring_samples", len(pts))
            return None

        # Suppress isolated one-bin flips in the circular ring sequence so
        # patterns like LOW,HIGH,LOW or HIGH,LOW,HIGH do not create spurious
        # extra transitions.
        cleaned_ring_states = ordered_ring_states.copy()
        warned_isolated: set[int] = set()
        for _ in range(max(1, ring_n)):
            changed = False
            next_states = cleaned_ring_states.copy()
            for i in range(ring_n):
                prev_s = cleaned_ring_states[(i - 1) % ring_n]
                curr_s = cleaned_ring_states[i]
                next_s = cleaned_ring_states[(i + 1) % ring_n]
                if prev_s == next_s and curr_s != prev_s:
                    if i not in warned_isolated and verbose:
                        prev_meta = ordered_ring_meta[(i - 1) % ring_n]
                        curr_meta = ordered_ring_meta[i]
                        next_meta = ordered_ring_meta[(i + 1) % ring_n]
                        print(
                            "Warning: removed isolated ring state spike "
                            f"at grid(y={curr_meta[4]},x={curr_meta[5]}) "
                            f"values(prev,mid,next)=({prev_meta[6]:.3f},{curr_meta[6]:.3f},{next_meta[6]:.3f})"
                        )
                        warned_isolated.add(i)
                    next_states[i] = prev_s
                    changed = True
            cleaned_ring_states = next_states
            if not changed:
                break

        # Ignore short HIGH islands bracketed by long LOW runs.
        # This mirrors the inner-start ring cleanup rule.
        for _ in range(max(1, ring_n)):
            changed = False
            runs = _circular_runs(np.asarray(cleaned_ring_states, dtype=bool))
            if not runs:
                break
            m = len(runs)
            for i, (state, start, run_len) in enumerate(runs):
                if not bool(state):
                    continue
                left_state, _left_start, left_len = runs[(i - 1) % m]
                right_state, _right_start, right_len = runs[(i + 1) % m]
                if bool(left_state) or bool(right_state):
                    continue
                if int(run_len) <= 4 and int(left_len) > 10 and int(right_len) > 10:
                    if verbose:
                        print(
                            "Warning: removed short HIGH island in tracer "
                            f"at {spline_label} spline point {len(pts) - 1}; "
                            f"len={int(run_len)} between LOW runs len={int(left_len)} and len={int(right_len)}"
                        )
                    for k in range(int(run_len)):
                        cleaned_ring_states[(int(start) + k) % ring_n] = False
                    changed = True
            if not changed:
                break

        # Optionally bridge short LOW runs enclosed by HIGH runs.
        # In this tracer, HIGH corresponds to bracelet/foreground and LOW to background.
        # Bridging a short LOW run should remove two transitions.
        if int(max_bg_gap) > 0:
            before_bridge = np.asarray(cleaned_ring_states, dtype=bool)
            # Pass 1: merge short LOW gaps into HIGH.
            cleaned_ring_states = _bridge_small_background_gaps(
                before_bridge,
                max_bg_gap=int(max_bg_gap),
            )
            # Pass 2 (temporarily disabled): merge short HIGH islands into LOW.
            enable_high_island_merge = False
            if enable_high_island_merge:
                cleaned_ring_states = np.logical_not(
                    _bridge_small_background_gaps(
                        np.logical_not(np.asarray(cleaned_ring_states, dtype=bool)),
                        max_bg_gap=int(max_bg_gap),
                    )
                )
            if verbose and not np.array_equal(before_bridge, cleaned_ring_states):
                b_lh = 0
                b_hl = 0
                a_lh = 0
                a_hl = 0
                for i in range(ring_n):
                    b0 = before_bridge[i]
                    b1 = before_bridge[(i + 1) % ring_n]
                    if (not b0) and b1:
                        b_lh += 1
                    elif b0 and (not b1):
                        b_hl += 1
                    a0 = cleaned_ring_states[i]
                    a1 = cleaned_ring_states[(i + 1) % ring_n]
                    if (not a0) and a1:
                        a_lh += 1
                    elif a0 and (not a1):
                        a_hl += 1
                print(
                    f"Ring gap-bridge ({spline_label} spline point {len(pts) - 1}): "
                    f"LOW->HIGH {b_lh}->{a_lh}, HIGH->LOW {b_hl}->{a_hl}, max_bg_gap={int(max_bg_gap)}"
                )

        for i, row in enumerate(in_bounds_entries):
            prev_state = cleaned_ring_states[(i - 1) % ring_n]
            curr_state = cleaned_ring_states[i]
            trans = bool(curr_state != prev_state)
            row["transition"] = trans

        ring_runs = _circular_runs(np.asarray(cleaned_ring_states, dtype=bool))
        transition_positions = sorted({int(start) for _state, start, _len in ring_runs})
        if transition_positions:
            m = len(transition_positions)
            for k, i in enumerate(transition_positions):
                prev_i = transition_positions[(k - 1) % m]
                run_len = (i - prev_i) % ring_n
                if run_len == 0:
                    run_len = ring_n
                prev_state = bool(cleaned_ring_states[(i - 1) % ring_n])
                curr_state = bool(cleaned_ring_states[i])
                trans_type = "LOW->HIGH" if ((not prev_state) and curr_state) else "HIGH->LOW"
                print(
                    f"Transition scan ({spline_label} spline point {len(pts) - 1}): {trans_type} at ring[{i:02d}] "
                    f"after {run_len} consecutive {'HIGH' if prev_state else 'LOW'} samples."
                )

        for row in in_bounds_entries:
            ord_idx = int(row["ord_idx"])
            sweep_angle = float(row["sweep_angle"])
            dy = int(row["dy"])
            dx = int(row["dx"])
            ny = int(row["ny"])
            nx = int(row["nx"])
            val = float(row["raw"])
            hi_state = str(row["state"])
            trans = bool(row["transition"])

            if trace_output:
                print(
                    f"  ring[{ord_idx:02d}] {sweep_label} {math.degrees(sweep_angle):6.2f}deg "
                    f"(dy={dy:+d},dx={dx:+d}): "
                    f"grid(y={ny},x={nx}) pixel(y={int(ys[ny])},x={int(xs[nx])}) "
                    f"raw={val:.3f} state={hi_state} transition={'Y' if trans else 'N'}"
                )

            if not trans:
                cand_not_transition += 1
                row["status"] = "reject_non_transition"
                cand_debug_rows.append(row)
                continue

            move = math.hypot(ny - curr_y, nx - curr_x)
            if move < 1.0:
                cand_too_short += 1
                row["move"] = move
                row["status"] = "reject_too_short"
                cand_debug_rows.append(row)
                continue
            row["move"] = move

            # Purely local geometry: keep the turn angle between successive
            # segments small; avoid any global-angle reference.
            if prev_dir is None:
                turn_angle = 0.0
                orientation_penalty = 0.0
                row["turn_deg"] = 0.0
                row["turn_limit_deg"] = math.degrees(max_turn_rad)
                row["cross"] = 0.0
                row["wrong_turn"] = False
            else:
                mvx = (nx - curr_x) / move
                mvy = (ny - curr_y) / move
                dot = prev_dir[0] * mvx + prev_dir[1] * mvy
                dot = float(np.clip(dot, -1.0, 1.0))
                turn_angle = math.acos(dot)
                turn_deg = math.degrees(turn_angle)
                row["dot"] = dot
                row["turn_deg"] = turn_deg
                row["turn_limit_deg"] = math.degrees(max_turn_rad)
                if turn_angle > max_turn_rad:
                    cand_turn_reject += 1
                    row["status"] = "reject_turn"
                    cand_debug_rows.append(row)
                    continue

                # Direction preference is a tie-breaker only.
                cross = prev_dir[0] * mvy - prev_dir[1] * mvx
                wrong_turn = cross > 0.0 if clockwise else cross < 0.0
                orientation_penalty = 0.20 * abs(cross) if wrong_turn else 0.0
                row["cross"] = cross
                row["wrong_turn"] = wrong_turn

            score = turn_angle + 0.03 * abs(move - r) + orientation_penalty
            cand_scored += 1
            row["orientation_penalty"] = orientation_penalty
            row["score"] = score
            row["status"] = "accepted_scored"
            cand_debug_rows.append(row)

            if score < best_score:
                best_score = score
                best = (ny, nx)

        low_to_high = 0
        high_to_low = 0
        for i in transition_positions:
            prev_state = bool(cleaned_ring_states[(i - 1) % ring_n])
            curr_state = bool(cleaned_ring_states[i])
            if (not prev_state) and curr_state:
                low_to_high += 1
            elif prev_state and (not curr_state):
                high_to_low += 1

        if low_to_high != 1 or high_to_low != 1:
            ring_raw_vals = [val for _, _, _, _, _, _, val in ordered_ring_meta]
            ring_raw_vals_sorted = sorted(ring_raw_vals)
            ring_n_vals = len(ring_raw_vals_sorted)
            median_msg = "median=unavailable"
            if ring_n_vals > 0:
                mid = ring_n_vals // 2
                if ring_n_vals % 2 == 1:
                    median_msg = f"median={ring_raw_vals_sorted[mid]:.3f}"
                else:
                    lo = ring_raw_vals_sorted[mid - 1]
                    hi_v = ring_raw_vals_sorted[mid]
                    median_msg = (
                        f"median-neighbors={lo:.3f},{hi_v:.3f}"
                    )

            print(
                f"Tracer stop ({spline_label} spline): ring transition count mismatch "
                f"at grid(y={curr_y},x={curr_x}) pixel(y={curr_py},x={curr_px}); "
                f"LOW->HIGH={low_to_high}, HIGH->LOW={high_to_low}, expected 1 each; "
                f"{median_msg}."
            )
            for ord_idx, sweep_angle, dy, dx, ny, nx, val in ordered_ring_meta:
                if not verbose:
                    break
                state_txt = "HIGH" if val >= threshold else "LOW"
                print(
                    f"  ring[{ord_idx:02d}] {sweep_label} {math.degrees(sweep_angle):6.2f}deg "
                    f"(dy={dy:+d},dx={dx:+d}) grid(y={ny},x={nx}) "
                    f"pixel(y={int(ys[ny])},x={int(xs[nx])}) raw={val:.3f} state={state_txt}"
                )

            # Always show ring diagnostic plot at mismatch so the user can inspect failure.
            _plot_trace_failure_debug(
                raw_map=raw_map,
                coarse=coarse,
                ys=ys,
                xs=xs,
                curr_y=curr_y,
                curr_x=curr_x,
                ring_offsets=[(dy, dx) for _, dy, dx in ordered_candidates],
                threshold=threshold,
                ring_steps=ring_steps,
                step=step,
                spline_point_index=len(pts) - 1,
                spline_label=spline_label,
                is_transition_fn=is_transition,
                wait_for_close=True,
            )

            if verbose and len(pts) >= 2:
                prev_y, prev_x = pts[-2]
                _plot_trace_failure_debug(
                    raw_map=raw_map,
                    coarse=coarse,
                    ys=ys,
                    xs=xs,
                    curr_y=prev_y,
                    curr_x=prev_x,
                    ring_offsets=[(dy, dx) for _, dy, dx in ordered_candidates],
                    threshold=threshold,
                    ring_steps=ring_steps,
                    step=step,
                    spline_point_index=len(pts) - 2,
                    spline_label=spline_label,
                    is_transition_fn=is_transition,
                    wait_for_close=True,
                )
            if return_partial_on_stop:
                _emit_trace_result("PARTIAL", "ring_transition_count_mismatch", len(pts))
                return _partial_trace_pixels()
            _emit_trace_result("FAILED", "ring_transition_count_mismatch", len(pts))
            return None

        if best is None:
            print(
                f"Tracer stopped ({spline_label} spline): no valid transition candidate at this {spline_label} spline point."
            )
            cand_in_bounds = cand_total - cand_oob
            cand_transition = cand_in_bounds - cand_not_transition
            if verbose:
                print(
                    f"Tracer debug(no_candidate, {spline_label} spline): "
                    f"grid(y={curr_y},x={curr_x}) pixel(y={curr_py},x={curr_px}) "
                    f"raw={float(coarse[curr_y, curr_x]):.3f} threshold={threshold:.3f}"
                )
                print(
                    "  candidate counts: "
                    f"total={cand_total}, out_of_bounds={cand_oob}, in_bounds={cand_in_bounds}, "
                    f"transition={cand_transition}, non_transition={cand_not_transition}, "
                    f"too_short={cand_too_short}, turn_reject={cand_turn_reject}, "
                    f"scored={cand_scored}"
                )
                if prev_dir is not None:
                    print(
                        "  local-turn config: "
                        f"max_turn_deg={math.degrees(max_turn_rad):.2f}, "
                        f"prev_dir=({prev_dir[0]:.3f},{prev_dir[1]:.3f})"
                    )
                print("  checked ring candidates (in sweep order):")
                for row in cand_debug_rows:
                    ord_idx = int(row["ord_idx"])
                    sweep_angle = float(row["sweep_angle"])
                    dy = int(row["dy"])
                    dx = int(row["dx"])
                    status = str(row.get("status", "unknown"))
                    if status == "out_of_bounds":
                        print(
                            f"    ring[{ord_idx:02d}] {sweep_label} {math.degrees(sweep_angle):6.2f}deg "
                            f"(dy={dy:+d},dx={dx:+d}) -> out_of_bounds"
                        )
                        continue

                    ny = int(row["ny"])
                    nx = int(row["nx"])
                    py = int(row["pixel_y"])
                    px = int(row["pixel_x"])
                    raw_val = float(row["raw"])
                    state = str(row["state"])
                    trans = bool(row["transition"])
                    base = (
                        f"    ring[{ord_idx:02d}] {sweep_label} {math.degrees(sweep_angle):6.2f}deg "
                        f"(dy={dy:+d},dx={dx:+d}) grid(y={ny},x={nx}) pixel(y={py},x={px}) "
                        f"raw={raw_val:.3f} state={state} transition={'Y' if trans else 'N'}"
                    )

                    if status == "reject_non_transition":
                        print(base + " -> reject_non_transition")
                    elif status == "reject_too_short":
                        print(base + f" -> reject_too_short move={float(row['move']):.3f}")
                    elif status == "reject_turn":
                        print(
                            base
                            + " -> reject_turn "
                            + f"turn_deg={float(row['turn_deg']):.2f} > limit={float(row['turn_limit_deg']):.2f}"
                        )
                    else:
                        print(
                            base
                            + " -> accepted_scored "
                            + f"turn_deg={float(row['turn_deg']):.2f}, "
                            + f"cross={float(row['cross']):.3f}, "
                            + f"wrong_turn={bool(row['wrong_turn'])}, "
                            + f"score={float(row['score']):.4f}"
                        )
            stop_reason = "no_candidate"
            break

        next_y, next_x = best
        expected_step_px = float(ring_steps * step)
        actual_step_px = float(
            math.hypot(
                float(ys[next_y]) - float(ys[curr_y]),
                float(xs[next_x]) - float(xs[curr_x]),
            )
        )
        if not math.isclose(actual_step_px, expected_step_px, rel_tol=0.0, abs_tol=0.75):
            raise RuntimeError(
                "Tracer bug: consecutive spline points are not ring-radius apart; "
                f"expected={expected_step_px:.6f}px, actual={actual_step_px:.6f}px, "
                f"from grid(y={curr_y},x={curr_x}) to grid(y={next_y},x={next_x}), "
                f"spline_point_index={len(pts)} ({spline_label} spline)."
            )

        step_dx = float(next_x - curr_x)
        step_dy = float(next_y - curr_y)
        step_norm = math.hypot(step_dx, step_dy)
        if step_norm > 1e-9:
            prev_dir = (step_dx / step_norm, step_dy / step_norm)
        curr_y, curr_x = next_y, next_x
        pts.append((curr_y, curr_x))
        if verbose:
            print(
                f"{spline_label.capitalize()} spline point {len(pts) - 1}: grid(y={curr_y},x={curr_x}) "
                f"pixel(y={int(ys[curr_y])},x={int(xs[curr_x])})"
            )
        if len(pts) >= 3 and verbose:
            y0, x0 = pts[-3]
            y1, x1 = pts[-2]
            y2, x2 = pts[-1]
            v1x = float(x1 - x0)
            v1y = float(y1 - y0)
            v2x = float(x2 - x1)
            v2y = float(y2 - y1)
            n1 = math.hypot(v1x, v1y)
            n2 = math.hypot(v2x, v2y)
            if n1 > 1e-9 and n2 > 1e-9:
                dot = float(np.clip((v1x * v2x + v1y * v2y) / (n1 * n2), -1.0, 1.0))
                turn_deg = math.degrees(math.acos(dot))
                print(
                    f"  turn angle at {spline_label} spline point {len(pts) - 1}: {turn_deg:.2f} deg "
                    f"(segments {len(pts)-3}->{len(pts)-2} and {len(pts)-2}->{len(pts)-1})"
                )
            else:
                print(
                    f"  turn angle at {spline_label} spline point {len(pts) - 1}: unavailable (zero-length segment)"
                )
        elif verbose:
            print(
                f"  turn angle at {spline_label} spline point {len(pts) - 1}: unavailable (need >= 3 points)"
            )

        # Allow a looser near-start closure radius so completed laps are detected
        # even when the path does not pass exactly through point 0.
        if len(pts) > 30 and math.hypot(curr_y - start_y, curr_x - start_x) <= max(3.0, 0.9 * r):
            stop_reason = "closed_loop"
            break

        key = (curr_y, curr_x)
        if key in visited_at:
            first_idx = visited_at[key]
            print(
                f"Tracer stop ({spline_label} spline): detected repeating cycle away from start; "
                f"revisited grid(y={curr_y},x={curr_x}) at {spline_label} spline point {len(pts) - 1}, "
                f"first seen at {spline_label} spline point {first_idx}."
            )
            if verbose:
                print(
                    f"Tracer debug(cycle, {spline_label} spline): "
                    f"pixel(y={int(ys[curr_y])},x={int(xs[curr_x])}), "
                    f"raw={float(coarse[curr_y, curr_x]):.3f}, threshold={threshold:.3f}"
                )
            stop_reason = "cycle_loop"
            break

        near_idx = _find_near_revisit_index(curr_y, curr_x, pts)
        if near_idx is not None and len(pts) > 30:
            print(
                f"Tracer stop ({spline_label} spline): detected near-cycle away from start; "
                f"current grid(y={curr_y},x={curr_x}) at {spline_label} spline point {len(pts) - 1} "
                f"is within 1.6 steps of {spline_label} spline point {near_idx}."
            )
            if verbose:
                print(
                    f"Tracer debug(near-cycle, {spline_label} spline): "
                    f"pixel(y={int(ys[curr_y])},x={int(xs[curr_x])}), "
                    f"raw={float(coarse[curr_y, curr_x]):.3f}, threshold={threshold:.3f}"
                )
            stop_reason = "near_cycle_loop"
            break
        visited_at[key] = len(pts) - 1

    if stop_reason is None:
        if return_partial_on_stop:
            _emit_trace_result("PARTIAL", "unknown_stop", len(pts))
            return _partial_trace_pixels()
        _emit_trace_result("FAILED", "unknown_stop", len(pts))
        return None

    if len(pts) < 16:
        if return_partial_on_stop:
            _emit_trace_result("PARTIAL", f"{stop_reason}_too_short", len(pts))
            return _partial_trace_pixels()
        _emit_trace_result("FAILED", f"{stop_reason}_too_short", len(pts))
        return None

    # Convert from step-grid indices to image pixel coordinates.
    pix = np.array([[float(xs[ix]), float(ys[iy])] for iy, ix in pts], dtype=np.float32)
    if np.hypot(*(pix[0] - pix[-1])) > 1e-6:
        pix = np.vstack([pix, pix[0]])
    if bool(smooth_output):
        pix = _smooth_closed_curve(pix, window=7, passes=2)
    if np.hypot(*(pix[0] - pix[-1])) > 1e-6:
        pix = np.vstack([pix, pix[0]])
    if stop_reason == "closed_loop":
        _emit_trace_result("COMPLETE", stop_reason, len(pts))
    else:
        _emit_trace_result("PARTIAL", stop_reason, len(pts))
    return pix


def _coerce_spline_xy(spline_xy: np.ndarray | list | tuple) -> np.ndarray | None:
    """Best-effort conversion to an Nx2 float array for spline geometry."""
    arr = np.asarray(spline_xy, dtype=np.float64)
    if arr.size == 0:
        return None

    if arr.ndim == 1:
        if arr.size % 2 != 0:
            return None
        arr = arr.reshape(-1, 2)
    elif arr.ndim == 2:
        if arr.shape[1] == 2:
            pass
        elif arr.shape[0] == 2:
            arr = arr.T
        else:
            return None
    else:
        return None

    if arr.shape[0] < 3:
        return None
    return arr.astype(np.float32, copy=False)


def _normalize_closed_spline_xy(
    spline_xy: np.ndarray | list | tuple,
    min_open_points: int = 300,
) -> np.ndarray | None:
    """Coerce a spline to closed Nx2 and upsample to a consistent point density."""
    arr = _coerce_spline_xy(spline_xy)
    if arr is None:
        return None

    arr = _ensure_closed_curve(arr.astype(np.float32, copy=False))
    if arr.shape[0] < 4:
        return None

    open_n = arr.shape[0] - 1
    target_open = max(int(min_open_points), int(open_n))
    if target_open != open_n:
        arr = _resample_closed_curve(arr, n_samples=target_open)
    return arr.astype(np.float32, copy=False)


def _catmull_rom_closed_interpolating(
    spline_xy: np.ndarray | list | tuple,
    samples_per_segment: int = 6,
) -> np.ndarray | None:
    """Closed Catmull-Rom interpolation that passes through every control point."""
    arr = _coerce_spline_xy(spline_xy)
    if arr is None:
        return None

    arr = _ensure_closed_curve(arr.astype(np.float32, copy=False))
    if arr.shape[0] < 4:
        return arr

    pts = arr[:-1].astype(np.float64, copy=False)
    n = int(pts.shape[0])
    if n < 3:
        return arr

    sps = max(2, int(samples_per_segment))
    t_values = np.linspace(0.0, 1.0, num=sps, endpoint=False, dtype=np.float64)
    out: list[np.ndarray] = []

    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i % n]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]

        for t in t_values:
            t2 = t * t
            t3 = t2 * t
            # Uniform Catmull-Rom basis, interpolating p1 at t=0 and p2 at t=1.
            q = 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
            )
            out.append(q)

    out_arr = np.asarray(out, dtype=np.float32)
    if out_arr.shape[0] < 2:
        return _ensure_closed_curve(pts.astype(np.float32, copy=False))
    out_arr = np.vstack([out_arr, out_arr[0]])
    return out_arr.astype(np.float32, copy=False)


def _anchor_closed_spline_points(
    spline_xy: np.ndarray,
    first_point_xy: tuple[float, float],
    second_point_xy: tuple[float, float] | None = None,
) -> np.ndarray:
    """Rotate/orient a closed spline and pin first/second points to requested anchors."""
    arr = _ensure_closed_curve(np.asarray(spline_xy, dtype=np.float32))
    if arr.shape[0] < 4:
        return arr.astype(np.float32, copy=False)

    open_pts = arr[:-1].astype(np.float64, copy=False)
    n = open_pts.shape[0]

    first = np.asarray(first_point_xy, dtype=np.float64)
    d2 = np.sum((open_pts - first[None, :]) ** 2, axis=1)
    i0 = int(np.argmin(d2))

    forward = np.roll(open_pts, -i0, axis=0)

    reverse_base = open_pts[::-1]
    i0_rev = (n - 1) - i0
    reverse = np.roll(reverse_base, -i0_rev, axis=0)

    chosen = forward
    if second_point_xy is not None and n > 1:
        second = np.asarray(second_point_xy, dtype=np.float64)
        fwd_d = float(np.hypot(*(forward[1] - second)))
        rev_d = float(np.hypot(*(reverse[1] - second)))
        if rev_d < fwd_d:
            chosen = reverse

    chosen = chosen.copy()
    chosen[0] = first
    if second_point_xy is not None and n > 1:
        chosen[1] = np.asarray(second_point_xy, dtype=np.float64)

    closed = np.vstack([chosen, chosen[0]])
    return closed.astype(np.float32, copy=False)


def _hsv_background_predicate_mask(rgb: np.ndarray) -> np.ndarray:
    """Background predicate from user-selected HSV bounds (u8 space)."""
    hsv = rgb_to_hsv(np.clip(rgb, 0.0, 1.0).astype(np.float32))
    hsv_u8 = np.clip(np.round(hsv * 255.0), 0, 255).astype(np.uint8)
    h_u8_full = hsv_u8[..., 0]
    s_u8_full = hsv_u8[..., 1]
    v_u8_full = hsv_u8[..., 2]
    return (
        (h_u8_full >= 219) & (h_u8_full <= 242)
        & (s_u8_full >= 100) & (s_u8_full <= 200)
        & (v_u8_full >= 80) & (v_u8_full <= 250)
    )


def _hsv_preset_union_mask(rgb: np.ndarray) -> np.ndarray:
    """Preset union mask from hsv_mask_triptych (True means selected/foreground)."""
    hsv = rgb_to_hsv(np.clip(rgb, 0.0, 1.0).astype(np.float32))
    hsv_u8 = np.clip(np.round(hsv * 255.0), 0, 255).astype(np.uint8)
    h_u8 = hsv_u8[..., 0]
    v_u8 = hsv_u8[..., 2]

    red = ((h_u8 >= 242) | (h_u8 <= 6)) & (v_u8 >= 128)
    yellow = (h_u8 >= 8) & (h_u8 <= 44)
    black = v_u8 <= 64
    return red | yellow | black


def _sample_ring_states(
    predicate_mask: np.ndarray,
    center_y: int,
    center_x: int,
    radius_px: int,
    n_samples: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    angles = np.linspace(0.0, 2.0 * math.pi, num=max(16, int(n_samples)), endpoint=False, dtype=np.float64)
    ys = np.rint(center_y + radius_px * np.sin(angles)).astype(np.int32)
    xs = np.rint(center_x + radius_px * np.cos(angles)).astype(np.int32)
    ys = np.clip(ys, 0, predicate_mask.shape[0] - 1)
    xs = np.clip(xs, 0, predicate_mask.shape[1] - 1)
    states = predicate_mask[ys, xs].astype(bool)
    return ys, xs, states


def _find_initial_point_from_center_line(predicate_mask: np.ndarray) -> tuple[int, int, str]:
    """Find initial point where a center-line scan transitions background->foreground.

    Starts from image edges on lines passing through the center and scans inward.
    Background is predicate=True, foreground is predicate=False.
    """
    h, w = predicate_mask.shape
    cy = h // 2
    cx = w // 2

    scans: list[tuple[str, list[tuple[int, int]]]] = [
        ("center-row right->left", [(cy, x) for x in range(w - 1, -1, -1)]),
        ("center-row left->right", [(cy, x) for x in range(0, w)]),
        ("center-col bottom->top", [(y, cx) for y in range(h - 1, -1, -1)]),
        ("center-col top->bottom", [(y, cx) for y in range(0, h)]),
    ]

    for label, line in scans:
        if len(line) < 2:
            continue
        y0, x0 = line[0]
        prev_bg = bool(predicate_mask[y0, x0])
        for y, x in line[1:]:
            curr_bg = bool(predicate_mask[y, x])
            if prev_bg and (not curr_bg):
                return int(y), int(x), label
            prev_bg = curr_bg

    # Fallback if no transition is found.
    return int(cy), int(cx), "fallback-center"


def _bridge_small_background_gaps(states: np.ndarray, max_bg_gap: int) -> np.ndarray:
    """Treat short background runs between foreground runs as foreground."""
    n = int(states.size)
    if n == 0:
        return states

    out = np.asarray(states, dtype=bool).copy()
    max_gap = max(0, int(max_bg_gap))
    for _ in range(max(1, n)):
        changed = False
        runs = _circular_runs(out)
        if not runs:
            break
        m = len(runs)
        for i, (state, start, run_len) in enumerate(runs):
            if state:
                continue
            left_fg = bool(runs[(i - 1) % m][0])
            right_fg = bool(runs[(i + 1) % m][0])
            if left_fg and right_fg and int(run_len) <= max_gap:
                for k in range(int(run_len)):
                    out[(int(start) + k) % n] = True
                changed = True
        if not changed:
            break
    return out


def _circular_runs(states: np.ndarray) -> list[tuple[bool, int, int]]:
    """Return circular runs as (state, start_index, length)."""
    n = int(states.size)
    if n == 0:
        return []

    runs: list[tuple[bool, int, int]] = []
    start = 0
    curr = bool(states[0])
    for i in range(1, n):
        v = bool(states[i])
        if v != curr:
            runs.append((curr, start, i - start))
            start = i
            curr = v
    runs.append((curr, start, n - start))

    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        first = runs[0]
        last = runs[-1]
        runs[0] = (first[0], last[1], first[2] + last[2])
        runs.pop()
    return runs


def _run_image_only_hsv_mode(
    rgb: np.ndarray,
    image_path: Path,
    spline_out_path: Path,
    ring_radius_px: int,
    ring_samples: int,
    max_bg_gap: int,
    spline_style: str,
    use_preset_union_mask: bool,
) -> dict[str, object]:
    if bool(use_preset_union_mask):
        union_mask = _hsv_preset_union_mask(rgb)
        # Existing tracing expects predicate=True as background.
        predicate_mask = ~union_mask
        predicate_mode = "preset_union_mask_inverted"
    else:
        predicate_mask = _hsv_background_predicate_mask(rgb)
        predicate_mode = "legacy_hsv_box"

    h, w = predicate_mask.shape
    init_y, init_x, init_scan_label = _find_initial_point_from_center_line(predicate_mask)

    ys, xs, states_raw = _sample_ring_states(
        predicate_mask=predicate_mask,
        center_y=init_y,
        center_x=init_x,
        radius_px=max(1, int(ring_radius_px)),
        n_samples=max(16, int(ring_samples)),
    )
    states = _bridge_small_background_gaps(states_raw, max_bg_gap=max(0, int(max_bg_gap)))
    runs = _circular_runs(states)

    bg_runs = [r for r in runs if r[0]]
    fg_runs = [r for r in runs if not r[0]]
    best_bg = max(bg_runs, key=lambda r: r[2]) if bg_runs else None
    best_fg = max(fg_runs, key=lambda r: r[2]) if fg_runs else None

    def _midpoint_from_run(run: tuple[bool, int, int] | None) -> tuple[int, int] | None:
        if run is None:
            return None
        _state, st, ln = run
        mid_idx = (st + ln // 2) % states.size
        return int(ys[mid_idx]), int(xs[mid_idx])

    bg_mid = _midpoint_from_run(best_bg)
    fg_mid = _midpoint_from_run(best_fg)

    transition_pt: tuple[int, int] | None = None
    transition_idx: int | None = None
    if states.size > 1:
        for i in range(states.size):
            prev_i = (i - 1) % states.size
            if bool(states[i]) != bool(states[prev_i]):
                transition_idx = int(i)
                transition_pt = (int(ys[i]), int(xs[i]))
                break

    # Build outer spline using the same circular ring-transition sampling at each point.
    # Bracelet foreground is predicate=False, map it to high values for threshold tracing.
    seed_fg: tuple[int, int] | None = None
    if not bool(predicate_mask[init_y, init_x]):
        seed_fg = (int(init_y), int(init_x))
    elif transition_idx is not None:
        i = int(transition_idx)
        prev_i = (i - 1) % states.size
        fg_i: int | None = None
        if not bool(states[i]):
            fg_i = i
        elif not bool(states[prev_i]):
            fg_i = prev_i
        if fg_i is not None:
            seed_fg = (int(ys[fg_i]), int(xs[fg_i]))
    elif fg_mid is not None:
        seed_fg = (int(fg_mid[0]), int(fg_mid[1]))

    use_catmull = str(spline_style).lower() in {"smooth", "catmull-rom", "catmull_rom", "catmullrom"}
    catmull_samples_per_segment = 6

    outer_control_xy: np.ndarray | None = None
    outer_spline_xy: np.ndarray | None = None
    inner_control_xy: np.ndarray | None = None
    inner_spline_xy: np.ndarray | None = None
    centerline_xy: np.ndarray | None = None
    centerline_radius: np.ndarray | None = None
    inner_start: tuple[int, int] | None = None
    inner_intersects_outer = False
    if seed_fg is not None:
        foreground_map = np.where(predicate_mask, 0.0, 100.0).astype(np.float32)
        traced = _trace_outer_spline_step_cells(
            raw_map=foreground_map,
            step=1,
            threshold=50.0,
            ring_steps=max(1, int(ring_radius_px)),
            max_bg_gap=max(0, int(max_bg_gap)),
            clockwise=True,
            start_point=(int(seed_fg[0]), int(seed_fg[1])),
            spline_label="outer",
            return_partial_on_stop=True,
            verbose=False,
            smooth_output=False,
        )
        outer_control_xy = _normalize_closed_spline_xy(traced, min_open_points=0)
        if outer_control_xy is not None:
            first_xy = (float(init_x), float(init_y))
            second_xy = (
                (float(transition_pt[1]), float(transition_pt[0]))
                if transition_pt is not None
                else None
            )
            outer_control_xy = _anchor_closed_spline_points(
                outer_control_xy,
                first_point_xy=first_xy,
                second_point_xy=second_xy,
            )
            outer_spline_xy = outer_control_xy
            if use_catmull:
                smooth_xy = _catmull_rom_closed_interpolating(
                    outer_control_xy,
                    samples_per_segment=catmull_samples_per_segment,
                )
                if smooth_xy is not None:
                    outer_spline_xy = smooth_xy

        ys_step, xs_step, coarse_step, _hi_step = _build_step_grid(
            foreground_map,
            step=1,
            threshold=50.0,
        )

        outer_start_for_inner = (int(seed_fg[0]), int(seed_fg[1]))
        if outer_control_xy is not None and outer_control_xy.shape[0] > 0:
            # Point 0 of outer spline is stored in (x, y) pixel coordinates.
            oy = int(round(float(outer_control_xy[0, 1])))
            ox = int(round(float(outer_control_xy[0, 0])))
            oy = int(np.clip(oy, 1, coarse_step.shape[0] - 2))
            ox = int(np.clip(ox, 1, coarse_step.shape[1] - 2))
            outer_start_for_inner = (oy, ox)

        inner_start = _find_inner_start_from_outer_point0(
            raw_map=foreground_map,
            step=1,
            threshold=50.0,
            outer_start=outer_start_for_inner,
            ys=ys_step,
            xs=xs_step,
            coarse=coarse_step,
            start_radius=max(1, int(ring_radius_px)),
        )
        if inner_start is not None:
            traced_inner = _trace_outer_spline_step_cells(
                raw_map=foreground_map,
                step=1,
                threshold=50.0,
                ring_steps=max(1, int(ring_radius_px)),
                max_bg_gap=max(0, int(max_bg_gap)),
                clockwise=True,
                start_point=(int(inner_start[0]), int(inner_start[1])),
                spline_label="inner",
                return_partial_on_stop=True,
                verbose=False,
                smooth_output=False,
            )
            inner_control_xy = _normalize_closed_spline_xy(traced_inner, min_open_points=0)
            inner_spline_xy = inner_control_xy
            if inner_control_xy is not None and use_catmull:
                smooth_inner = _catmull_rom_closed_interpolating(
                    inner_control_xy,
                    samples_per_segment=catmull_samples_per_segment,
                )
                if smooth_inner is not None:
                    inner_spline_xy = smooth_inner

            if outer_control_xy is not None and inner_control_xy is not None:
                centerline_built = _build_centerline_spline(
                    outer_control_xy,
                    inner_control_xy,
                    return_radii=True,
                )
                if centerline_built is not None:
                    centerline_xy, centerline_radius = centerline_built
                inner_intersects_outer = bool(_spline_intersects(outer_spline_xy, inner_spline_xy))

    output = {
        "version": 1,
        "mode": "image_only_hsv",
        "predicate_mode": str(predicate_mode),
        "image_path": str(image_path),
        "ring_radius_px": int(ring_radius_px),
        "ring_samples": int(ring_samples),
        "max_bg_gap": int(max_bg_gap),
        "spline_style": "catmull-rom" if use_catmull else "polyline",
        "initial_point": [int(init_x), int(init_y)],
        "initial_point_source": str(init_scan_label),
        "largest_background_run_samples": int(best_bg[2]) if best_bg is not None else 0,
        "largest_bracelet_run_samples": int(best_fg[2]) if best_fg is not None else 0,
        "largest_background_midpoint": [int(bg_mid[1]), int(bg_mid[0])] if bg_mid is not None else None,
        "largest_bracelet_midpoint": [int(fg_mid[1]), int(fg_mid[0])] if fg_mid is not None else None,
        "outer_spline": (
            [[float(p[0]), float(p[1])] for p in np.asarray(outer_spline_xy, dtype=np.float64)]
            if outer_spline_xy is not None
            else None
        ),
        "outer_spline_control": (
            [[float(p[0]), float(p[1])] for p in np.asarray(outer_control_xy, dtype=np.float64)]
            if outer_control_xy is not None
            else None
        ),
        "inner_spline": (
            [[float(p[0]), float(p[1])] for p in np.asarray(inner_spline_xy, dtype=np.float64)]
            if inner_spline_xy is not None
            else None
        ),
        "inner_spline_control": (
            [[float(p[0]), float(p[1])] for p in np.asarray(inner_control_xy, dtype=np.float64)]
            if inner_control_xy is not None
            else None
        ),
        "centerline_spline": (
            [[float(p[0]), float(p[1])] for p in np.asarray(centerline_xy, dtype=np.float64)]
            if centerline_xy is not None
            else None
        ),
        "centerline_radius": (
            [float(r) for r in np.asarray(centerline_radius, dtype=np.float64)]
            if centerline_radius is not None
            else None
        ),
        "inner_intersects_outer": bool(inner_intersects_outer),
    }
    return output
