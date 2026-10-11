"""Numerical excerpts from rharriszzz/fft-image-explorer, unchanged.

Source commit: 2caf0707c2b63a0d7540e2cac447d2f1b883d8c1
Source file SHA256: 73ced947b1825e55ca0d1337fc508bbd4917e574cbea150ae660b61ee8013c24
Original source: https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/fft_image_explorer.py
Selected by AST for reproducible headless reuse in R243. No numerical changes.
The experiment adapter handles origin exclusion, peak qualification and correct
inverse-bin mapping explicitly; upstream display statistics remain legacy values.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np

def rgb_to_hsv_np(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized RGB->HSV for rgb in [0,1].
    Returns H, S, V where H is normalized to [0,1].
    """
    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]

    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    h = np.zeros_like(cmax)

    mask = delta > 1e-12

    idx = mask & (cmax == r)
    h[idx] = ((g[idx] - b[idx]) / delta[idx]) % 6.0

    idx = mask & (cmax == g)
    h[idx] = ((b[idx] - r[idx]) / delta[idx]) + 2.0

    idx = mask & (cmax == b)
    h[idx] = ((r[idx] - g[idx]) / delta[idx]) + 4.0

    h = h / 6.0

    s = np.zeros_like(cmax)
    nz = cmax > 1e-12
    s[nz] = delta[nz] / cmax[nz]

    v = cmax
    return h, s, v


def robust_normalize(x: np.ndarray) -> np.ndarray:
    """Normalize a scalar image to roughly [0,1] using percentiles."""
    x = x.astype(np.float32)
    lo, hi = np.percentile(x, [1, 99])
    if hi <= lo:
        return np.zeros_like(x)
    y = (x - lo) / (hi - lo)
    return np.clip(y, 0, 1)


@dataclass
class ChannelBank:
    names: list[str]
    arrays: dict[str, np.ndarray]


def make_channel_bank(rgb: np.ndarray) -> ChannelBank:
    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]

    # Rec. 601 luma, common for JPEG-like Y.
    y = 0.299 * r + 0.587 * g + 0.114 * b

    h, s, v = rgb_to_hsv_np(rgb)

    # CMYK conversion from normalized RGB.
    # K is black key; C/M/Y are normalized by (1-K) when possible.
    k = 1.0 - np.maximum(np.maximum(r, g), b)
    denom = 1.0 - k
    c = np.zeros_like(k)
    m = np.zeros_like(k)
    y_cmyk = np.zeros_like(k)
    mask = denom > 1e-12
    c[mask] = (1.0 - r[mask] - k[mask]) / denom[mask]
    m[mask] = (1.0 - g[mask] - k[mask]) / denom[mask]
    y_cmyk[mask] = (1.0 - b[mask] - k[mask]) / denom[mask]
    c = np.clip(c, 0.0, 1.0)
    m = np.clip(m, 0.0, 1.0)
    y_cmyk = np.clip(y_cmyk, 0.0, 1.0)
    k = np.clip(k, 0.0, 1.0)

    arrays = {
        "Y luminance": y,
        "R": r,
        "G": g,
        "B": b,
        "HSV H": h,
        "HSV S": s,
        "HSV V": v,
        "CMYK C": c,
        "CMYK M": m,
        "CMYK Y": y_cmyk,
        "CMYK K": k,
    }
    names = list(arrays.keys())
    return ChannelBank(names=names, arrays=arrays)


def smoothstep01(t: np.ndarray) -> np.ndarray:
    """Smooth 0..1 transition."""
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def make_mask(
    shape: tuple[int, int],
    mask_type: str,
    edge_type: str,
    cx: float,
    cy: float,
    width: float,
    height: float,
    angle_deg: float,
    softness: float,
) -> np.ndarray:
    """
    Return a 2D mask/window in [0,1].

    Coordinates:
        cx, cy are pixel coordinates.
        width, height are full dimensions in pixels.
        angle_deg rotates the local x/y axes.

    mask_type:
        "Full image", "Rectangle", "Rotated rectangle", "Ellipse/circle"

    edge_type:
        "Hard", "Cosine", "Gaussian"
    """
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]

    if mask_type == "Full image":
        base = np.ones((h, w), dtype=np.float32)
        if edge_type == "Hard":
            return base
        # For full image with non-hard edge, use a separable taper at the image borders.
        local_x = (xx - (w - 1) / 2) / max(w / 2, 1)
        local_y = (yy - (h - 1) / 2) / max(h / 2, 1)
        return edge_falloff_rect(local_x, local_y, edge_type, softness).astype(np.float32)

    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)

    dx = xx - cx
    dy = yy - cy

    # Rotate image coordinates into local mask coordinates.
    # local x-axis is rotated by angle_deg in image coordinates.
    xloc = c * dx + s * dy
    yloc = -s * dx + c * dy

    half_w = max(width / 2.0, 1.0)
    half_h = max(height / 2.0, 1.0)

    if mask_type in ("Rectangle", "Rotated rectangle"):
        xn = xloc / half_w
        yn = yloc / half_h
        return edge_falloff_rect(xn, yn, edge_type, softness).astype(np.float32)

    if mask_type == "Ellipse/circle":
        # Ellipse equation: radius <= 1 inside.
        rn = np.sqrt((xloc / half_w) ** 2 + (yloc / half_h) ** 2)
        return edge_falloff_radial(rn, edge_type, softness).astype(np.float32)

    raise ValueError(f"Unknown mask type: {mask_type}")


def edge_falloff_rect(xn: np.ndarray, yn: np.ndarray, edge_type: str, softness: float) -> np.ndarray:
    """
    Rectangular window on normalized coords where |xn|<=1 and |yn|<=1 is nominally inside.

    softness is a fraction of half-size. Example: 0.2 means the outer 20% tapers.
    """
    ax = np.abs(xn)
    ay = np.abs(yn)

    if edge_type == "Hard":
        return ((ax <= 1) & (ay <= 1)).astype(np.float32)

    if edge_type == "Gaussian":
        # Gaussian centered at the window center. softness controls sigma relative to window size.
        # Make softness=1 broad, softness small tight.
        sigma = max(softness, 0.03)
        m = np.exp(-0.5 * ((xn / sigma) ** 2 + (yn / sigma) ** 2))
        # Truncate very far out for readability/performance.
        m[(ax > 1) | (ay > 1)] = 0.0
        return m.astype(np.float32)

    if edge_type == "Cosine":
        # Flat center, cosine fade near edge.
        soft = np.clip(softness, 0.001, 0.95)
        # Distance to nearest rectangle edge in normalized units.
        inside = (ax <= 1) & (ay <= 1)
        dist_to_edge = np.minimum(1 - ax, 1 - ay)
        # dist_to_edge >= soft => full value.
        t = dist_to_edge / soft
        m = smoothstep01(t)
        m[~inside] = 0.0
        return m.astype(np.float32)

    raise ValueError(f"Unknown edge type: {edge_type}")


def edge_falloff_radial(rn: np.ndarray, edge_type: str, softness: float) -> np.ndarray:
    """Radial/elliptical window where rn<=1 is nominally inside."""
    if edge_type == "Hard":
        return (rn <= 1).astype(np.float32)

    if edge_type == "Gaussian":
        sigma = max(softness, 0.03)
        m = np.exp(-0.5 * (rn / sigma) ** 2)
        m[rn > 1] = 0.0
        return m.astype(np.float32)

    if edge_type == "Cosine":
        soft = np.clip(softness, 0.001, 0.95)
        inside = rn <= 1
        dist_to_edge = 1 - rn
        t = dist_to_edge / soft
        m = smoothstep01(t)
        m[~inside] = 0.0
        return m.astype(np.float32)

    raise ValueError(f"Unknown edge type: {edge_type}")


def crop_to_mask_nonzero(xm: np.ndarray, mask: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Crop to the tight bounding box where mask is non-zero-ish."""
    idx = np.argwhere(mask > eps)
    if idx.size == 0:
        return np.zeros((1, 1), dtype=np.float32)

    y0, x0 = idx.min(axis=0)
    y1, x1 = idx.max(axis=0) + 1
    return xm[y0:y1, x0:x1].astype(np.float32)


def pad_with_tiled_edge_blocks(
    x: np.ndarray,
    pad_top: int,
    pad_bottom: int,
    pad_left: int,
    pad_right: int,
    block_size: int = 20,
) -> np.ndarray:
    """Pad by repeating edge-adjacent blocks, not single edge pixels."""
    h, w = x.shape
    out_h = h + pad_top + pad_bottom
    out_w = w + pad_left + pad_right
    out = np.zeros((out_h, out_w), dtype=x.dtype)

    out[pad_top:pad_top + h, pad_left:pad_left + w] = x

    bh = max(1, min(block_size, h))
    bw = max(1, min(block_size, w))

    def pingpong_index(k: int, n: int) -> int:
        if n <= 1:
            return 0
        period = 2 * n
        t = k % period
        return t if t < n else (2 * n - 1 - t)

    # Build inward-oriented edge bands: index 0 is the nearest source sample at the edge.
    top_band = x[:bh, :]
    bottom_band = x[h - bh:, :][::-1, :]

    for i in range(pad_top):
        out[pad_top - 1 - i, pad_left:pad_left + w] = top_band[pingpong_index(i, bh), :]

    for i in range(pad_bottom):
        out[pad_top + h + i, pad_left:pad_left + w] = bottom_band[pingpong_index(i, bh), :]

    center_cols = out[:, pad_left:pad_left + w]
    left_band = center_cols[:, :bw]
    right_band = center_cols[:, w - bw:][:, ::-1]

    for j in range(pad_left):
        out[:, pad_left - 1 - j] = left_band[:, pingpong_index(j, bw)]

    for j in range(pad_right):
        out[:, pad_left + w + j] = right_band[:, pingpong_index(j, bw)]

    return out


def find_top_fft_peaks(logmag: np.ndarray, top_k: int = 7, min_distance: int = 6) -> list[dict[str, float]]:
    """Find the strongest local maxima in a 2D log-magnitude FFT image, merging conjugate pairs."""
    h, w = logmag.shape
    cy, cx = h // 2, w // 2

    def canonical_offset(yy: int, xx: int) -> tuple[int, int]:
        dx = int(xx - cx)
        dy = int(cy - yy)
        if dy < 0 or (dy == 0 and dx < 0):
            dx = -dx
            dy = -dy
        return dx, dy

    def peak_region_stats(yy: int, xx: int) -> dict[str, float]:
        peak_val = float(logmag[yy, xx])
        radius = 8
        y0 = max(0, yy - radius)
        y1 = min(h, yy + radius + 1)
        x0 = max(0, xx - radius)
        x1 = min(w, xx + radius + 1)
        patch = logmag[y0:y1, x0:x1]
        py, px = np.mgrid[y0:y1, x0:x1]

        support = patch >= max(0.5 * peak_val, 1e-9)
        if not np.any(support):
            support = patch > 0

        weights = patch[support]
        dx_support = px[support] - xx
        dy_support = yy - py[support]
        dist2 = dx_support ** 2 + dy_support ** 2
        broadness = float(np.sqrt((weights * dist2).sum() / max(weights.sum(), 1e-12)))
        log_power_sum = float(weights.sum())
        radius_support = np.sqrt(dist2)

        # Track the flat-top region (pixels equal to the local max) to compare
        # against what the detail popup shows as a uniform bright disk.
        plateau = patch >= (peak_val - 1e-12)
        if np.any(plateau):
            dx_plateau = px[plateau] - xx
            dy_plateau = yy - py[plateau]
            dist2_plateau = dx_plateau ** 2 + dy_plateau ** 2
            radius_plateau = np.sqrt(dist2_plateau)
            plateau_count = int(plateau.sum())
            plateau_rmax = float(radius_plateau.max())
            plateau_dx_min = float(dx_plateau.min())
            plateau_dx_max = float(dx_plateau.max())
            plateau_dy_min = float(dy_plateau.min())
            plateau_dy_max = float(dy_plateau.max())
        else:
            plateau_count = 0
            plateau_rmax = 0.0
            plateau_dx_min = 0.0
            plateau_dx_max = 0.0
            plateau_dy_min = 0.0
            plateau_dy_max = 0.0

        threshold = float(max(0.5 * peak_val, 1e-9))
        return {
            "peak_val": peak_val,
            "support_threshold": threshold,
            "log_power_sum": log_power_sum,
            "broadness": broadness,
            "support_count": float(support.sum()),
            "support_rmax": float(radius_support.max()) if radius_support.size else 0.0,
            "support_rms_unweighted": float(np.sqrt(dist2.mean())) if dist2.size else 0.0,
            "support_dx_min": float(dx_support.min()) if dx_support.size else 0.0,
            "support_dx_max": float(dx_support.max()) if dx_support.size else 0.0,
            "support_dy_min": float(dy_support.min()) if dy_support.size else 0.0,
            "support_dy_max": float(dy_support.max()) if dy_support.size else 0.0,
            "plateau_count": float(plateau_count),
            "plateau_rmax": plateau_rmax,
            "plateau_dx_min": plateau_dx_min,
            "plateau_dx_max": plateau_dx_max,
            "plateau_dy_min": plateau_dy_min,
            "plateau_dy_max": plateau_dy_max,
        }

    # Simple 3x3 local-maximum test without extra dependencies.
    padded = np.pad(logmag, 1, mode="constant", constant_values=-np.inf)
    local_max = np.ones((h, w), dtype=bool)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            if oy == 0 and ox == 0:
                continue
            neigh = padded[1 + oy:1 + oy + h, 1 + ox:1 + ox + w]
            local_max &= logmag >= neigh

    candidates = np.argwhere(local_max & (logmag > 0))
    if candidates.size == 0:
        candidates = np.array([[cy, cx]])

    values = logmag[candidates[:, 0], candidates[:, 1]]
    order = np.argsort(values)[::-1]
    candidates = candidates[order]

    selected: list[tuple[int, int]] = [(cy, cx)]
    selected_keys: set[tuple[int, int]] = {canonical_offset(cy, cx)}

    for yy, xx in candidates:
        if len(selected) >= top_k:
            break
        yy_i = int(yy)
        xx_i = int(xx)
        key = canonical_offset(yy_i, xx_i)
        if key in selected_keys:
            continue
        if any((yy_i - sy) ** 2 + (xx_i - sx) ** 2 < min_distance ** 2 for sy, sx in selected):
            continue
        selected.append((yy_i, xx_i))
        selected_keys.add(key)

    if len(selected) < top_k:
        for yy, xx in candidates:
            if len(selected) >= top_k:
                break
            yy_i = int(yy)
            xx_i = int(xx)
            key = canonical_offset(yy_i, xx_i)
            if key in selected_keys:
                continue
            selected.append((yy_i, xx_i))
            selected_keys.add(key)

    peaks: list[dict[str, float]] = []
    for yy, xx in selected[:top_k]:
        stats = peak_region_stats(yy, xx)
        peak_val = float(stats["peak_val"])
        log_power_sum = float(stats["log_power_sum"])
        broadness = float(stats["broadness"])
        dx = float(xx - cx)
        dy = float(cy - yy)
        angle_deg = float(np.degrees(np.arctan2(dy, dx))) if dx != 0 or dy != 0 else 0.0
        distance = float(np.hypot(dx, dy))

        mirror_y = int(2 * cy - yy)
        mirror_x = int(2 * cx - xx)
        if 0 <= mirror_y < h and 0 <= mirror_x < w and not (mirror_y == yy and mirror_x == xx):
            mirror_stats = peak_region_stats(mirror_y, mirror_x)
            log_power_sum += float(mirror_stats["log_power_sum"])
            broadness = 0.5 * (broadness + float(mirror_stats["broadness"]))

        peaks.append(
            {
                "x": dx,
                "y": dy,
                "distance": distance,
                "angle_deg": angle_deg,
                "log_power_sum": log_power_sum,
                "broadness": broadness,
                "peak_val": peak_val,
                "support_threshold": float(stats["support_threshold"]),
                "support_count": float(stats["support_count"]),
                "support_rmax": float(stats["support_rmax"]),
                "support_rms_unweighted": float(stats["support_rms_unweighted"]),
                "support_dx_min": float(stats["support_dx_min"]),
                "support_dx_max": float(stats["support_dx_max"]),
                "support_dy_min": float(stats["support_dy_min"]),
                "support_dy_max": float(stats["support_dy_max"]),
                "plateau_count": float(stats["plateau_count"]),
                "plateau_rmax": float(stats["plateau_rmax"]),
                "plateau_dx_min": float(stats["plateau_dx_min"]),
                "plateau_dx_max": float(stats["plateau_dx_max"]),
                "plateau_dy_min": float(stats["plateau_dy_min"]),
                "plateau_dy_max": float(stats["plateau_dy_max"]),
            }
        )

    return peaks


def compute_fft_products(
    channel: np.ndarray,
    mask: np.ndarray,
    zero_pad: bool,
    square_fft: bool = True,
    square_pad_mode: str = "edge_block20",
    fft_highpass_percent: float = 0.0,
    fft_lowpass_percent: float = 0.0,
    fft_threshold_percent: float = 0.0,
    debug_peak_stats: bool = False,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    dict[str, int | bool],
    float,
    float,
    float,
    list[dict[str, float]],
]:
    """
    Build all FFT-related displays.

    Returns:
        pre_fft_display: masked image cropped to non-zero mask support
        fft_logmag_display: shifted log magnitude of FFT after display normalization
        fft_logmag_raw: shifted log magnitude of FFT before display normalization
        radial_r: radial distance bins from FFT center (pixels)
        radial_log_power: log-compressed total power in each radial bin
        ifft_display: inverse FFT (real part), cropped back to FFT input size
        fft_complex_shifted: shifted complex FFT after all active filters
        fft_recon_meta: metadata needed to crop inverse FFT back to analysis ROI
        low_pass_removed_percent: percent of original power removed by the low-pass mask
        high_pass_removed_percent: percent of original power removed by the high-pass mask
        remaining_percent: percent of original power remaining after all active filters
        peaks: strongest local peaks in the current FFT log-magnitude image
    """
    x = channel.astype(np.float32)
    m = mask.astype(np.float32)

    xm = x * m
    xm_crop = crop_to_mask_nonzero(xm, m)

    # The FFT is computed on the cropped non-zero region so the display focuses on useful content.
    fft_input = xm_crop
    src_h, src_w = fft_input.shape
    pad_top = 0
    pad_left = 0
    if square_fft and src_h != src_w:
        side = max(src_h, src_w)
        pad_h = side - src_h
        pad_w = side - src_w
        pad_top = pad_h // 2
        pad_bottom = pad_h - pad_top
        pad_left = pad_w // 2
        pad_right = pad_w - pad_left
        if square_pad_mode not in {"edge", "reflect", "edge_block20"}:
            raise ValueError(f"Unsupported square pad mode: {square_pad_mode}")
        if square_pad_mode == "edge_block20":
            fft_input = pad_with_tiled_edge_blocks(
                fft_input,
                pad_top=pad_top,
                pad_bottom=pad_bottom,
                pad_left=pad_left,
                pad_right=pad_right,
                block_size=20,
            )
        else:
            # Propagate boundary values outward to avoid zero-padding discontinuities.
            fft_input = np.pad(
                fft_input,
                ((pad_top, pad_bottom), (pad_left, pad_right)),
                mode=square_pad_mode,
            )

    in_h, in_w = fft_input.shape

    if zero_pad:
        padded = np.zeros((2 * in_h, 2 * in_w), dtype=np.float32)
        y0 = in_h // 2
        x0 = in_w // 2
        padded[y0:y0 + in_h, x0:x0 + in_w] = fft_input
        fft_input = padded

    f = np.fft.fftshift(np.fft.fft2(fft_input))
    base_power = float((np.abs(f) ** 2).sum())

    fh, fw = f.shape
    fcy, fcx = fh // 2, fw // 2
    yy, xx = np.ogrid[:fh, :fw]
    max_radius_px = math.hypot(fh / 2.0, fw / 2.0)

    hp_keep_mask = np.ones((fh, fw), dtype=bool)
    lp_keep_mask = np.ones((fh, fw), dtype=bool)

    # High-pass filter in frequency domain: zero bins near the FFT origin.
    if fft_highpass_percent > 0.0:
        hp_radius_px = fft_highpass_percent * 0.01 * max_radius_px
        low_freq_mask = (yy - fcy) ** 2 + (xx - fcx) ** 2 <= hp_radius_px ** 2
        hp_keep_mask = ~low_freq_mask
        f = f * hp_keep_mask

    # Low-pass filter in frequency domain: keep only bins near the FFT origin.
    if fft_lowpass_percent > 0.0:
        lp_radius_px = fft_lowpass_percent * 0.01 * max_radius_px
        lp_keep_mask = (yy - fcy) ** 2 + (xx - fcx) ** 2 <= lp_radius_px ** 2
        f = f * lp_keep_mask

    # Apply FFT thresholding if enabled (based on log-magnitude)
    if fft_threshold_percent > 0.0:
        mag = np.log1p(np.abs(f))
        mag_max = float(mag.max())
        threshold_val = mag_max * (fft_threshold_percent / 100.0)
        f_mask = mag >= threshold_val
        f = f * f_mask.astype(np.complex64)

    final_power = float((np.abs(f) ** 2).sum())
    hp_only_power = float((np.abs(np.fft.fftshift(np.fft.fft2(fft_input)) * hp_keep_mask) ** 2).sum()) if fft_highpass_percent > 0.0 else base_power
    lp_only_power = float((np.abs(np.fft.fftshift(np.fft.fft2(fft_input)) * lp_keep_mask) ** 2).sum()) if fft_lowpass_percent > 0.0 else base_power

    eps = 1e-12
    low_pass_removed_percent = 100.0 * (base_power - lp_only_power) / max(base_power, eps)
    high_pass_removed_percent = 100.0 * (base_power - hp_only_power) / max(base_power, eps)
    remaining_percent = 100.0 * final_power / max(base_power, eps)

    mag_raw = np.log1p(np.abs(f))
    peaks = find_top_fft_peaks(mag_raw, top_k=7)
    if debug_peak_stats and peaks:
        lines = ["\n[FFT peak debug] top-peak support metrics from raw log-magnitude"]
        for idx, peak in enumerate(peaks, start=1):
            lines.append(
                (
                    f"  peak#{idx} offset=({peak['x']:.0f},{peak['y']:.0f}) "
                    f"peak={peak['peak_val']:.6f} thr={peak['support_threshold']:.6f} "
                    f"broad={peak['broadness']:.4f}"
                )
            )
            lines.append(
                (
                    f"    support: count={peak['support_count']:.0f} "
                    f"rmax={peak['support_rmax']:.4f} "
                    f"rms_unw={peak['support_rms_unweighted']:.4f} "
                    f"dx=[{peak['support_dx_min']:.2f},{peak['support_dx_max']:.2f}] "
                    f"dy=[{peak['support_dy_min']:.2f},{peak['support_dy_max']:.2f}]"
                )
            )
            lines.append(
                (
                    f"    plateau(==peak): count={peak['plateau_count']:.0f} "
                    f"rmax={peak['plateau_rmax']:.4f} "
                    f"dx=[{peak['plateau_dx_min']:.2f},{peak['plateau_dx_max']:.2f}] "
                    f"dy=[{peak['plateau_dy_min']:.2f},{peak['plateau_dy_max']:.2f}]"
                )
            )
        print("\n".join(lines), flush=True)
    mag = mag_raw

    # Sparse-aware contrast for display: after strong filtering many bins are exactly 0,
    # so compute robust limits from non-zero bins when available.
    nz = mag[mag > 0]
    if nz.size >= 32:
        lo, hi = np.percentile(nz, [5, 99.5])
    else:
        lo, hi = np.percentile(mag, [1, 99.7])

    if hi > lo:
        mag = (mag - lo) / (hi - lo)
        mag = np.clip(mag, 0, 1)
        # Gentle gamma lift improves visibility of retained low-amplitude structure.
        mag = np.sqrt(mag)
    else:
        mag = np.zeros_like(mag)

    inv_full = np.real(np.fft.ifft2(np.fft.ifftshift(f))).astype(np.float32)
    if zero_pad:
        y0 = in_h // 2
        x0 = in_w // 2
        inv = inv_full[y0:y0 + in_h, x0:x0 + in_w]
    else:
        inv = inv_full

    # Remove any square-padding frame so inverse display maps to original FFT ROI.
    if square_fft and (src_h != in_h or src_w != in_w):
        inv = inv[pad_top:pad_top + src_h, pad_left:pad_left + src_w]

    # Show the actual array sent to FFT so square/edge padding is visible in UI.
    pre_fft_display = robust_normalize(fft_input)
    fft_logmag_display = np.clip(mag, 0, 1).astype(np.float32)
    fft_logmag_raw = mag_raw.astype(np.float32)

    # Direction-independent spectrum summary: total FFT power by radius.
    yy_i, xx_i = np.indices(f.shape)
    rr = np.sqrt((yy_i - fcy) ** 2 + (xx_i - fcx) ** 2)
    rbin = np.floor(rr).astype(np.int32)
    power2d = np.abs(f) ** 2
    radial_power = np.bincount(rbin.ravel(), weights=power2d.ravel())
    radial_r = np.arange(radial_power.size, dtype=np.float32)
    radial_log_power = np.log1p(radial_power).astype(np.float32)

    ifft_display = robust_normalize(inv)
    fft_recon_meta: dict[str, int | bool] = {
        "src_h": int(src_h),
        "src_w": int(src_w),
        "in_h": int(in_h),
        "in_w": int(in_w),
        "pad_top": int(pad_top),
        "pad_left": int(pad_left),
        "zero_pad": bool(zero_pad),
        "square_fft": bool(square_fft),
    }
    return (
        pre_fft_display,
        fft_logmag_display,
        fft_logmag_raw,
        radial_r,
        radial_log_power,
        ifft_display,
        f.astype(np.complex64),
        fft_recon_meta,
        low_pass_removed_percent,
        high_pass_removed_percent,
        remaining_percent,
        peaks,
    )
