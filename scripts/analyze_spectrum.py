"""Deterministic sensitivity audit of the public K2-18 b spectrum.

This is not an atmospheric retrieval. It tests how a descriptive 4.3-micron
band contrast changes across predeclared window definitions and whether a
constant MIRI spectrum is rejected after every one-bin deletion.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2

matplotlib.rcParams["svg.hashsalt"] = "k218b-sensitivity-audit-v1"

ROOT = Path(__file__).resolve().parents[1]
NIR_PATH = ROOT / "data" / "k218b_niriss_nirspec_miri_combined_spectrum.txt"
MIRI_PATH = ROOT / "data" / "k218b_miri_lrs_eureka_spectrum.txt"
CONFIG_PATH = ROOT / "configs" / "sensitivity_audit_v1.json"


@dataclass(frozen=True)
class Spectrum:
    wavelength: np.ndarray
    depth: np.ndarray
    error: np.ndarray
    half_width: np.ndarray | None = None


def canonical_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def load_spectrum(path: Path, expected_columns: int = 3) -> Spectrum:
    values = np.loadtxt(path, dtype=float)
    if values.ndim != 2 or values.shape[1] != expected_columns:
        raise ValueError(f"{path} must have exactly {expected_columns} numeric columns")
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{path} contains non-finite values")
    if not np.all(np.diff(values[:, 0]) > 0):
        raise ValueError(f"{path} wavelengths must be strictly increasing")
    if not np.all(values[:, 2] > 0):
        raise ValueError(f"{path} uncertainties must be positive")
    half_width = values[:, 3] if expected_columns == 4 else None
    if half_width is not None and not np.all(half_width > 0):
        raise ValueError(f"{path} half-widths must be positive")
    return Spectrum(values[:, 0], values[:, 1], values[:, 2], half_width)


def weighted_mean(depth: np.ndarray, error: np.ndarray) -> tuple[float, float]:
    depth = np.asarray(depth, dtype=float)
    error = np.asarray(error, dtype=float)
    if depth.shape != error.shape or depth.size == 0:
        raise ValueError("depth and error must be non-empty arrays with matching shape")
    if not np.all(np.isfinite(depth)) or not np.all(np.isfinite(error)):
        raise ValueError("depth and error must be finite")
    if not np.all(error > 0):
        raise ValueError("uncertainties must be positive")
    weights = 1.0 / np.square(error)
    return float(np.sum(depth * weights) / np.sum(weights)), float(
        np.sqrt(1.0 / np.sum(weights))
    )


def bin_spectrum(
    wavelength: np.ndarray,
    depth: np.ndarray,
    error: np.ndarray,
    n_bins: int = 90,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if n_bins < 1:
        raise ValueError("n_bins must be positive")
    edges = np.linspace(float(wavelength.min()), float(wavelength.max()), n_bins + 1)
    membership = np.clip(np.digitize(wavelength, edges) - 1, 0, n_bins - 1)
    output: list[tuple[float, float, float]] = []
    for index in range(n_bins):
        mask = membership == index
        if mask.any():
            mean, mean_error = weighted_mean(depth[mask], error[mask])
            weights = 1.0 / np.square(error[mask])
            centre = float(np.sum(wavelength[mask] * weights) / np.sum(weights))
            output.append((centre, mean, mean_error))
    return tuple(np.asarray(column) for column in zip(*output, strict=True))  # type: ignore[return-value]


def band_contrast(
    spectrum: Spectrum, band: dict[str, Any], continuum: dict[str, Any]
) -> dict[str, Any]:
    band_mask = (spectrum.wavelength >= band["lo"]) & (
        spectrum.wavelength <= band["hi"]
    )
    cont_mask = (spectrum.wavelength >= continuum["lo"]) & (
        spectrum.wavelength <= continuum["hi"]
    )
    band_mean, band_error = weighted_mean(
        spectrum.depth[band_mask], spectrum.error[band_mask]
    )
    cont_mean, cont_error = weighted_mean(
        spectrum.depth[cont_mask], spectrum.error[cont_mask]
    )
    difference = band_mean - cont_mean
    difference_error = float(np.hypot(band_error, cont_error))
    return {
        "band_id": band["id"],
        "band_lo_micron": band["lo"],
        "band_hi_micron": band["hi"],
        "continuum_id": continuum["id"],
        "continuum_lo_micron": continuum["lo"],
        "continuum_hi_micron": continuum["hi"],
        "band_points": int(band_mask.sum()),
        "continuum_points": int(cont_mask.sum()),
        "contrast_ppm": difference * 1e6,
        "contrast_error_ppm": difference_error * 1e6,
        "signed_sigma": difference / difference_error,
    }


def flat_model(depth: np.ndarray, error: np.ndarray) -> dict[str, float | int]:
    mean, mean_error = weighted_mean(depth, error)
    statistic = float(np.sum(np.square((depth - mean) / error)))
    dof = int(depth.size - 1)
    return {
        "weighted_mean_ppm": mean * 1e6,
        "weighted_mean_error_ppm": mean_error * 1e6,
        "chi_square": statistic,
        "degrees_of_freedom": dof,
        "reduced_chi_square": statistic / dof,
        "p_value": float(chi2.sf(statistic, dof)),
    }


def git_revision(root: Path) -> tuple[str | None, bool | None]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return revision, dirty
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None, None


def compute_study(
    nir_path: Path = NIR_PATH,
    miri_path: Path = MIRI_PATH,
    config_path: Path = CONFIG_PATH,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    nir = load_spectrum(nir_path, 3)
    miri_all = load_spectrum(miri_path, 4)
    contrasts = [
        band_contrast(nir, band, continuum)
        for band in config["co2_bands_micron"]
        for continuum in config["continuum_windows_micron"]
    ]
    threshold = float(config["decision_thresholds"]["nir_absolute_sigma"])
    primary = next(
        row
        for row in contrasts
        if row["band_id"] == "B3_primary" and row["continuum_id"] == "C2_primary"
    )

    nonoverlap = miri_all.wavelength > float(nir.wavelength.max())
    miri = Spectrum(
        miri_all.wavelength[nonoverlap],
        miri_all.depth[nonoverlap],
        miri_all.error[nonoverlap],
        miri_all.half_width[nonoverlap] if miri_all.half_width is not None else None,
    )
    miri_fit = flat_model(miri.depth, miri.error)
    leave_one_out: list[dict[str, Any]] = []
    for index in range(miri.wavelength.size):
        keep = np.arange(miri.wavelength.size) != index
        leave_one_out.append(
            {
                "removed_index": index,
                "removed_wavelength_micron": float(miri.wavelength[index]),
                **flat_model(miri.depth[keep], miri.error[keep]),
            }
        )
    alpha = float(config["decision_thresholds"]["miri_alpha"])
    max_loo = max(leave_one_out, key=lambda row: row["p_value"])
    revision, dirty = git_revision(ROOT)
    nir_pass = all(abs(row["signed_sigma"]) < threshold for row in contrasts)
    miri_pass = all(row["p_value"] < alpha for row in leave_one_out)
    summary = {
        "study_id": config["study_id"],
        "generated_date": config["generated_date"],
        "implementation_revision": config["source_revision"],
        "research_question": config["research_question"],
        "scope": "Descriptive sensitivity and influence audit; not an atmospheric retrieval or molecular detection test.",
        "nir_dataset": {
            "instruments": ["NIRISS SOSS", "NIRSpec G395H"],
            "n_points": int(nir.wavelength.size),
            "wavelength_min_micron": float(nir.wavelength.min()),
            "wavelength_max_micron": float(nir.wavelength.max()),
            "canonical_sha256": canonical_sha256(nir_path),
        },
        "miri_dataset": {
            "instrument": "MIRI LRS",
            "n_published_bins": int(miri_all.wavelength.size),
            "n_nonoverlap_bins": int(miri.wavelength.size),
            "wavelength_min_micron": float(miri_all.wavelength.min()),
            "wavelength_max_micron": float(miri_all.wavelength.max()),
            "canonical_sha256": canonical_sha256(miri_path),
            "display_offset_ppm": float(config["miri_offset_ppm_for_display"]),
        },
        "band_contrast_audit": {
            "n_definitions": len(contrasts),
            "primary": primary,
            "minimum_signed_sigma": min(row["signed_sigma"] for row in contrasts),
            "maximum_signed_sigma": max(row["signed_sigma"] for row in contrasts),
            "maximum_absolute_sigma": max(
                abs(row["signed_sigma"]) for row in contrasts
            ),
            "negative_contrast_count": sum(
                row["contrast_ppm"] < 0 for row in contrasts
            ),
            "positive_contrast_count": sum(
                row["contrast_ppm"] > 0 for row in contrasts
            ),
            "all_below_threshold": nir_pass,
            "threshold_absolute_sigma": threshold,
            "null_result": "not_rejected" if nir_pass else "rejected",
        },
        "miri_flatness_audit": {
            "all_nonoverlap_bins": miri_fit,
            "leave_one_out_min_p_value": min(row["p_value"] for row in leave_one_out),
            "leave_one_out_max_p_value": max_loo["p_value"],
            "most_influential_removed_wavelength_micron": max_loo[
                "removed_wavelength_micron"
            ],
            "rejections_after_deletion": sum(
                row["p_value"] < alpha for row in leave_one_out
            ),
            "n_leave_one_out_fits": len(leave_one_out),
            "robust_to_every_one_bin_deletion": miri_pass,
            "alpha": alpha,
            "null_result": "not_rejected" if miri_pass else "rejected",
        },
        "provenance": config["source"],
        "execution": {"git_revision": revision, "git_dirty": dirty},
    }
    return {
        "nir": nir,
        "miri": miri,
        "contrasts": contrasts,
        "leave_one_out": leave_one_out,
        "summary": summary,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_products(study: dict[str, Any], root: Path) -> None:
    nir, miri = study["nir"], study["miri"]
    offset = study["summary"]["miri_dataset"]["display_offset_ppm"] * 1e-6
    bw, bd, be = bin_spectrum(nir.wavelength, nir.depth, nir.error, 90)
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.errorbar(
        bw,
        bd * 1e6,
        yerr=be * 1e6,
        fmt="o",
        ms=3.5,
        color="#155e75",
        label="NIRISS + NIRSpec (display-binned)",
    )
    ax.errorbar(
        miri.wavelength,
        (miri.depth + offset) * 1e6,
        yerr=miri.error * 1e6,
        fmt="s",
        ms=4,
        color="#b45309",
        label="MIRI LRS (+160 ppm source offset)",
    )
    ax.axvspan(4.1, 4.6, color="#7c3aed", alpha=0.11, label="Primary 4.3 µm window")
    ax.set(
        xlabel="Wavelength [µm]",
        ylabel="Transit depth [ppm]",
        title="K2-18 b public spectra and tested band",
    )
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(root / "figures" / "k218b_spectrum_audit.svg", metadata={"Date": None})
    plt.close(fig)

    rows, loo = study["contrasts"], study["leave_one_out"]
    labels = [f"{r['band_id']}·{r['continuum_id']}" for r in rows]
    values = np.asarray([r["signed_sigma"] for r in rows])
    fig, axes = plt.subplots(
        2, 1, figsize=(11, 8), gridspec_kw={"height_ratios": [1.15, 1]}
    )
    axes[0].bar(
        np.arange(len(values)),
        values,
        color=np.where(values >= 0, "#155e75", "#b45309"),
    )
    axes[0].axhline(3, color="#991b1b", ls="--", lw=1)
    axes[0].axhline(-3, color="#991b1b", ls="--", lw=1)
    axes[0].set(
        ylabel="Signed contrast [σ]", title="30 predeclared band/continuum definitions"
    )
    axes[0].set_xticks(
        np.arange(len(labels)), labels, rotation=70, ha="right", fontsize=7
    )
    axes[0].grid(axis="y", alpha=0.2)
    axes[1].plot(
        [r["removed_wavelength_micron"] for r in loo],
        [r["p_value"] for r in loo],
        "o-",
        color="#155e75",
        ms=4,
    )
    axes[1].axhline(0.05, color="#991b1b", ls="--", lw=1, label="α = 0.05")
    axes[1].set(
        xlabel="Deleted MIRI bin centre [µm]",
        ylabel="Flat-model p-value",
        title="MIRI leave-one-bin-out influence audit",
        yscale="log",
    )
    axes[1].grid(alpha=0.2)
    axes[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(root / "results" / "sensitivity_audit.svg", metadata={"Date": None})
    plt.close(fig)


def write_products(study: dict[str, Any], root: Path = ROOT) -> None:
    (root / "results").mkdir(parents=True, exist_ok=True)
    write_csv(root / "results" / "band_contrast_multiverse.csv", study["contrasts"])
    write_csv(
        root / "results" / "miri_flatness_leave_one_out.csv", study["leave_one_out"]
    )
    (root / "results" / "result_summary.json").write_text(
        json.dumps(study["summary"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    primary = study["summary"]["band_contrast_audit"]["primary"]
    rows = [
        ("nir_native_points", study["summary"]["nir_dataset"]["n_points"], "count"),
        (
            "miri_published_bins",
            study["summary"]["miri_dataset"]["n_published_bins"],
            "count",
        ),
        (
            "miri_nonoverlap_bins",
            study["summary"]["miri_dataset"]["n_nonoverlap_bins"],
            "count",
        ),
        ("primary_co2_band_excess", f"{primary['contrast_ppm']:.1f}", "ppm"),
        ("primary_co2_band_significance", f"{primary['signed_sigma']:.2f}", "sigma"),
        (
            "multiverse_maximum_absolute_significance",
            f"{study['summary']['band_contrast_audit']['maximum_absolute_sigma']:.3f}",
            "sigma",
        ),
        (
            "miri_flat_model_p_value",
            f"{study['summary']['miri_flatness_audit']['all_nonoverlap_bins']['p_value']:.8f}",
            "p",
        ),
        (
            "miri_leave_one_out_max_p_value",
            f"{study['summary']['miri_flatness_audit']['leave_one_out_max_p_value']:.8f}",
            "p",
        ),
    ]
    with (root / "figures" / "summary_statistics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerows(rows)
    plot_products(study, root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="compute without writing products"
    )
    args = parser.parse_args()
    study = compute_study()
    if not args.check:
        write_products(study)
    print(json.dumps(study["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
