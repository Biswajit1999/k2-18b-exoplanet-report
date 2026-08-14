"""Executable checks on the weighted-mean/binning statistics and a
regression guard that the pipeline still reproduces the documented
headline numbers when run on the real downloaded data."""

import csv

import numpy as np
import analyze_spectrum as spec


def test_weighted_mean_matches_hand_computed_case():
    values = np.array([1.0, 2.0])
    errors = np.array([1.0, 0.5])  # weights 1 and 4
    mean, err = spec.weighted_mean(values, errors)
    assert np.isclose(mean, 1.8, rtol=1e-10)
    assert np.isclose(err, np.sqrt(1.0 / 5.0), rtol=1e-10)


def test_bin_spectrum_reduces_point_count_and_conserves_span():
    rng = np.random.default_rng(0)
    wavelength = np.sort(rng.uniform(1.0, 5.0, 1000))
    depth = np.full(1000, 1000.0) + rng.normal(0, 5, 1000)
    error = np.full(1000, 5.0)
    bin_wave, bin_depth, bin_error = spec.bin_spectrum(wavelength, depth, error, n_bins=20)
    assert len(bin_wave) <= 20
    assert bin_wave.min() >= wavelength.min()
    assert bin_wave.max() <= wavelength.max()
    # Binning many noisy points around a constant should recover that
    # constant well within its binned error.
    assert np.all(np.abs(bin_depth - 1000.0) < 5 * bin_error)


def test_pipeline_reproduces_documented_headline_numbers():
    spec.FIG_DIR.mkdir(exist_ok=True)
    spec.main()
    rows = {}
    with (spec.FIG_DIR / "summary_statistics.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["quantity"]] = row["value"]
    assert int(rows["n_native_points"]) == 4411
    assert abs(float(rows["weighted_mean_depth"]) - 2919.5) < 0.5
    assert abs(float(rows["co2_band_excess_significance"]) - 0.18) < 0.02
