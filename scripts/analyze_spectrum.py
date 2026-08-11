"""Analyze the real combined JWST NIRISS+NIRSpec+MIRI transmission spectrum
of K2-18 b.

Data source: Zenodo record 10.5281/zenodo.16277833, "Investigating aerosols
as a way to reconcile K2-18 b JWST MIRI and NIRISS/NIRSpec observations",
file Spectra/K2-18b_both_offset1_-41ppm_native.txt (native-resolution
combined spectrum with the paper's own MIRI cross-instrument offset applied).
Retrieved directly from Zenodo; reproduced unmodified in data/.

Columns (no header in the source file): wavelength [micron],
transit depth (Rp/Rs)^2, 1-sigma uncertainty.

This script bins the ~4400-point native-resolution spectrum down to a
readable resolution for plotting, computes a weighted mean depth, and
directly compares the mean depth in the CO2 absorption band (4.1-4.6
micron, the feature central to the 2023 CO2/CH4 detection claim) against a
nearby continuum window, reporting the real difference -- without asserting
a detection significance beyond what this simple binned comparison can
support.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 (registers 'science' style)
import numpy as np

plt.style.use(["science", "no-latex"])

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"

CO2_BAND = (4.1, 4.6)
CONTINUUM_BAND = (3.6, 3.9)


def load_spectrum(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    wavelength, depth, error = [], [], []
    with path.open() as handle:
        for line in handle:
            parts = line.split()
            if len(parts) != 3:
                continue
            w, d, e = map(float, parts)
            wavelength.append(w)
            depth.append(d)
            error.append(e)
    return np.array(wavelength), np.array(depth), np.array(error)


def weighted_mean(depth: np.ndarray, error: np.ndarray) -> tuple[float, float]:
    weights = 1.0 / error**2
    mean = np.sum(depth * weights) / np.sum(weights)
    mean_error = np.sqrt(1.0 / np.sum(weights))
    return mean, mean_error


def bin_spectrum(wavelength, depth, error, n_bins=90):
    edges = np.linspace(wavelength.min(), wavelength.max(), n_bins + 1)
    bin_wave, bin_depth, bin_error = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (wavelength >= lo) & (wavelength < hi)
        if not mask.any():
            continue
        w = depth[mask]
        e = error[mask]
        weights = 1.0 / e**2
        bin_wave.append(0.5 * (lo + hi))
        bin_depth.append(np.sum(w * weights) / np.sum(weights))
        bin_error.append(np.sqrt(1.0 / np.sum(weights)))
    return np.array(bin_wave), np.array(bin_depth), np.array(bin_error)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    wavelength, depth, error = load_spectrum(
        DATA_DIR / "k218b_niriss_nirspec_miri_combined_spectrum.txt"
    )
    order = np.argsort(wavelength)
    wavelength, depth, error = wavelength[order], depth[order], error[order]

    mean_depth, mean_depth_error = weighted_mean(depth, error)

    co2_mask = (wavelength >= CO2_BAND[0]) & (wavelength <= CO2_BAND[1])
    continuum_mask = (wavelength >= CONTINUUM_BAND[0]) & (wavelength <= CONTINUUM_BAND[1])
    co2_mean, co2_err = weighted_mean(depth[co2_mask], error[co2_mask])
    cont_mean, cont_err = weighted_mean(depth[continuum_mask], error[continuum_mask])
    co2_excess_ppm = (co2_mean - cont_mean) * 1e6
    co2_excess_sigma = abs(co2_mean - cont_mean) / np.sqrt(co2_err**2 + cont_err**2)

    bin_wave, bin_depth, bin_error = bin_spectrum(wavelength, depth, error, n_bins=90)

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_native_points", len(wavelength), "count"])
        writer.writerow(["n_binned_points", len(bin_wave), "count"])
        writer.writerow(["wavelength_min", f"{wavelength.min():.3f}", "micron"])
        writer.writerow(["wavelength_max", f"{wavelength.max():.3f}", "micron"])
        writer.writerow(["weighted_mean_depth", f"{mean_depth*1e6:.1f}", "ppm"])
        writer.writerow(["weighted_mean_depth_error", f"{mean_depth_error*1e6:.2f}", "ppm"])
        writer.writerow(["co2_band_mean_depth", f"{co2_mean*1e6:.1f}", "ppm (4.1-4.6 micron)"])
        writer.writerow(["continuum_mean_depth", f"{cont_mean*1e6:.1f}", "ppm (3.6-3.9 micron)"])
        writer.writerow(["co2_band_excess", f"{co2_excess_ppm:.1f}", "ppm"])
        writer.writerow(["co2_band_excess_significance", f"{co2_excess_sigma:.2f}", "sigma"])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.errorbar(
        bin_wave, bin_depth * 1e6, yerr=bin_error * 1e6,
        fmt="o", ms=4, color="#2a5c8a", ecolor="#9fbfd8", elinewidth=1,
        label=f"K2-18 b, JWST NIRISS+NIRSpec+MIRI ({len(bin_wave)}-point binned)",
    )
    ax.axhline(mean_depth * 1e6, color="#555555", lw=1, ls="--", label="weighted mean")
    ax.axvspan(*CO2_BAND, color="#c0562a", alpha=0.12, label="CO2 band (4.1-4.6 um)")
    ax.axvspan(*CONTINUUM_BAND, color="#1f6f5c", alpha=0.12, label="continuum window (3.6-3.9 um)")
    ax.set_xlabel("Wavelength [micron]")
    ax.set_ylabel("Transit depth (Rp/Rs)^2 [ppm]")
    ax.set_title("K2-18 b transmission spectrum (real combined JWST data, binned for display)")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "k218b_transmission_spectrum.png", dpi=200)

    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'k218b_transmission_spectrum.png'}")
    print(f"n_native={len(wavelength)}, binned to {len(bin_wave)} points")
    print(f"Weighted mean depth = {mean_depth*1e6:.1f} +/- {mean_depth_error*1e6:.2f} ppm")
    print(
        f"CO2-band ({CO2_BAND[0]}-{CO2_BAND[1]} um) mean = {co2_mean*1e6:.1f} ppm vs. "
        f"continuum ({CONTINUUM_BAND[0]}-{CONTINUUM_BAND[1]} um) mean = {cont_mean*1e6:.1f} ppm "
        f"-> excess = {co2_excess_ppm:.1f} ppm ({co2_excess_sigma:.1f} sigma)"
    )


if __name__ == "__main__":
    main()
