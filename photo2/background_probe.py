"""R092: reproducible local FFT probes, not a segmentation or helicity solver."""
import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = [
    ("A", "open paper, inside loop", 1100, 950),
    ("B", "open paper, outside loop", 450, 2350),
    ("C", "necklace, upper section", 1410, 275),
    ("D", "necklace, right section", 2210, 1170),
    ("E", "paper/shadow beside D", 2320, 1170),
    ("F", "paper/shadow at inner bend", 1870, 1690),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spectrum(patch, sigma):
    """Remove a Gaussian-weighted plane; FFT the Gaussian-windowed residual.

    Units are displayed JPEG grayscale, not radiance. The 1/64 px cutoff is
    exploratory and fixed across window scales. No paper-color predicate.
    """
    y, x = np.indices(patch.shape, dtype=float)
    x -= (patch.shape[1] - 1) / 2
    y -= (patch.shape[0] - 1) / 2
    w = np.exp(-(x*x + y*y) / (2*sigma*sigma))
    design = np.stack([np.ones_like(x), x/sigma, y/sigma], axis=-1)
    a = design.reshape(-1, 3)
    weights = w.ravel()
    fit = np.linalg.solve(a.T @ (weights[:, None]*a), a.T @ (weights*patch.ravel()))
    residual = patch - design @ fit
    z = w * residual
    power = np.abs(np.fft.fftshift(np.fft.fft2(z))) ** 2
    fy = np.fft.fftshift(np.fft.fftfreq(patch.shape[0]))
    fx = np.fft.fftshift(np.fft.fftfreq(patch.shape[1]))
    freq = np.hypot(fy[:, None], fx[None, :])
    hi = power[freq >= 1/64].sum()
    norm = patch.size * np.sum(w*w)
    total = power.sum()
    metrics = {
        "high_frequency_rms": float(np.sqrt(hi/norm)),
        "residual_rms": float(np.sqrt(total/norm)),
        "high_frequency_fraction": float(hi/total) if total > 1e-20 else 0.,
        "parseval_error": float(abs(total/patch.size - np.sum(z*z))),
    }
    return metrics, power


def checks():
    y, x = np.indices((257, 257), dtype=float)
    flat, _ = spectrum(np.full_like(x, .6), 35)
    ramp, _ = spectrum(.3 + .001*x + .0005*y, 35)
    fast, _ = spectrum(.5 + .1*np.sin(2*np.pi*x/16), 35)
    slow, _ = spectrum(.5 + .1*np.sin(2*np.pi*x/128), 35)
    assert flat["residual_rms"] < 1e-12
    assert ramp["residual_rms"] < 1e-12
    # Finite Gaussian windows broaden peaks: the 128px wave leaks across the
    # cutoff. Check useful separation, not an ideal brick-wall-filter claim.
    assert fast["high_frequency_rms"] > 5*slow["high_frequency_rms"]
    assert fast["high_frequency_fraction"] > .99
    assert slow["high_frequency_fraction"] < .05
    assert abs(fast["high_frequency_rms"] - .1/np.sqrt(2)) < .001
    assert fast["parseval_error"] < 1e-10
    return {"constant_removed": True, "linear_ramp_removed": True,
            "16px_vs_128px_separation": True, "sinusoid_rms": True,
            "parseval": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"photo2/output/r092")
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT/"beads-photo-2.jpg"
    im = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
    rgb = np.asarray(im, dtype=float)/255
    gray = rgb @ np.array([.299, .587, .114])
    height, width = gray.shape
    radius = .05*np.sqrt(width*height)
    sigmas = [radius, radius/3, radius/6]
    rows, powers = [], {}
    for label, meaning, cx, cy in SAMPLES:
        for sigma in sigmas:
            half = int(np.ceil(3*sigma))
            # Explicit reflection when a 3-sigma square crosses the photo edge.
            padded = np.pad(gray, half, mode="reflect")
            patch = padded[cy:cy+2*half+1, cx:cx+2*half+1]
            metric, power = spectrum(patch, sigma)
            reflected = cx-half < 0 or cy-half < 0 or cx+half >= width or cy+half >= height
            rows.append(dict(label=label, description=meaning, x=cx, y=cy,
                             sigma_px=sigma, half_support_px=half,
                             reflected_photo_edge=reflected, **metric))
            powers[label, sigma] = power
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.imshow(im)
    colors = plt.get_cmap("tab10").colors
    for i, (label, meaning, x, y) in enumerate(SAMPLES):
        c = colors[i]
        ax.plot(x, y, "+", color="white", markersize=8)
        ax.add_patch(Circle((x,y), radius, fill=False, color=c, linewidth=2))
        ax.text(x+30, y-30, label, color="white", fontsize=15, weight="bold",
                bbox=dict(facecolor=c, alpha=.9, edgecolor="none"))
    ax.set_title(f"Sample centers; rings = sigma = 0.05 sqrt(N) = {radius:.1f} px\n"
                 "Gaussian support extends beyond each ring; these are not bead boundaries")
    ax.set_xlabel("Original-photo x (pixels)")
    ax.set_ylabel("Original-photo y (pixels)")
    fig.tight_layout()
    fig.savefig(out/"sample-context.png", dpi=145)
    plt.close(fig)

    fig, axes = plt.subplots(3, 4, figsize=(13, 10))
    small_sigma = sigmas[-1]
    # Shared scale for the FFT panels, displaying energy amplitude per window.
    spectra = []
    for label, *_ in SAMPLES:
        p = powers[label, small_sigma]
        spectra.append(np.log10(1 + 1e4*np.sqrt(p)/p.size))
    vmax = max(float(p.max()) for p in spectra)
    for i, (label, meaning, x, y) in enumerate(SAMPLES):
        row, col = i//2, 2*(i%2)
        half = 155
        axes[row,col].imshow(im)
        axes[row,col].set_xlim(x-half, x+half)
        axes[row,col].set_ylim(y+half, y-half)
        axes[row,col].set_title(f"{label}: {meaning}", fontsize=10)
        axes[row,col].set_axis_off()
        axes[row,col+1].imshow(spectra[i], origin="lower", cmap="magma", vmin=0, vmax=vmax,
                              extent=(-.5,.5,-.5,.5))
        axes[row,col+1].set_xlim(-.15,.15)
        axes[row,col+1].set_ylim(-.15,.15)
        axes[row,col+1].set_title(f"{label}: local FFT, sigma {small_sigma:.1f} px", fontsize=10)
        axes[row,col+1].set_xlabel("cycles/pixel")
    fig.suptitle("Raw 310-pixel contexts and small-window spectra\n"
                 "Crop center = sample center; shared FFT display scale; no boundary inferred")
    fig.tight_layout()
    fig.savefig(out/"raw-and-fft.png", dpi=145)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    for i, sigma in enumerate(sigmas):
        vals = [r["high_frequency_rms"] for r in rows if r["sigma_px"] == sigma]
        ax.bar(np.arange(6)+(i-1)*.25, vals, width=.25, label=f"sigma {sigma:.1f} px")
    ax.set_xticks(np.arange(6), [s[0] for s in SAMPLES])
    ax.set_ylabel("Fine-scale grayscale RMS (0–1 JPEG units)")
    ax.set_title("High-frequency energy is a neighborhood cue, not a pixel label")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out/"scale-comparison.png", dpi=145)
    plt.close(fig)
    report = dict(source_sha256=digest(source), script_sha256=digest(__file__),
                  image_size=[width,height], gaussian_radius_requested_px=radius,
                  interpretation="radius treated as sigma; sigma/3 and sigma/6 sensitivity probes",
                  channel="0.299 R + 0.587 G + 0.114 B on displayed JPEG RGB / 255",
                  detrending="Gaussian-weighted least-squares plane",
                  cutoff_cycles_per_pixel=1/64, support="square +/- ceil(3 sigma)",
                  edge_handling="reflect, explicitly flagged per sample", checks=checks(),
                  versions=dict(numpy=np.__version__, matplotlib=matplotlib.__version__),
                  samples=rows,
                  illustrations={p.name:digest(p) for p in sorted(out.glob("*.png"))})
    (out/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"radius_px":radius,"checks":report["checks"],"output":str(out)}, indent=2))


if __name__ == "__main__":
    main()
