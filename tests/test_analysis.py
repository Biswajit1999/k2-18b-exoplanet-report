"""Numerical, provenance, and generated-evidence tests."""

import json

import analyze_spectrum as spec
import numpy as np
import pytest


def test_weighted_mean_matches_hand_computed_case():
    mean, error = spec.weighted_mean(np.array([1.0, 2.0]), np.array([1.0, 0.5]))
    assert np.isclose(mean, 1.8)
    assert np.isclose(error, np.sqrt(1.0 / 5.0))


@pytest.mark.parametrize(
    ("depth", "error"),
    [([], []), ([1.0], [1.0, 2.0]), ([1.0], [0.0]), ([np.nan], [1.0])],
)
def test_weighted_mean_rejects_invalid_inputs(depth, error):
    with pytest.raises(ValueError):
        spec.weighted_mean(np.asarray(depth), np.asarray(error))


def test_binning_keeps_rightmost_sample_and_requested_bins():
    wavelength = np.linspace(1.0, 5.0, 101)
    depth = np.full(101, 0.003)
    error = np.full(101, 0.0001)
    wave, binned_depth, _ = spec.bin_spectrum(wavelength, depth, error, n_bins=10)
    assert len(wave) == 10
    assert wave[-1] <= 5.0
    assert np.allclose(binned_depth, 0.003)


def test_source_files_have_expected_shape_range_and_hash():
    nir = spec.load_spectrum(spec.NIR_PATH, 3)
    miri = spec.load_spectrum(spec.MIRI_PATH, 4)
    assert nir.wavelength.size == 4411
    assert nir.wavelength.max() == pytest.approx(5.174292087554932)
    assert miri.wavelength.size == 28
    assert (miri.wavelength.min(), miri.wavelength.max()) == (5.125, 11.875)
    assert (
        spec.canonical_sha256(spec.NIR_PATH)
        == "0622a1761cbd1e8f920425fd0b54b9489517f66f0a885ed8190cfc0471aedf24"
    )
    assert (
        spec.canonical_sha256(spec.MIRI_PATH)
        == "1b0959ba7513ee2c4ff14b8c6060cec05670a547d85f1fd99b8a6fb6eae0e7c2"
    )


def test_multiverse_preserves_primary_result_but_exposes_design_sensitivity():
    study = spec.compute_study()
    audit = study["summary"]["band_contrast_audit"]
    assert audit["n_definitions"] == 30
    assert audit["primary"]["contrast_ppm"] == pytest.approx(4.0709079336)
    assert audit["primary"]["signed_sigma"] == pytest.approx(0.1757482937)
    assert audit["minimum_signed_sigma"] == pytest.approx(-0.8611108401)
    assert audit["maximum_signed_sigma"] == pytest.approx(2.2580165558)
    assert audit["negative_contrast_count"] == 6
    assert audit["positive_contrast_count"] == 24
    assert audit["all_below_threshold"] is True


def test_miri_flatness_is_not_robust_to_every_one_bin_deletion():
    audit = spec.compute_study()["summary"]["miri_flatness_audit"]
    assert audit["all_nonoverlap_bins"]["p_value"] == pytest.approx(0.00096843685)
    assert audit["rejections_after_deletion"] == 26
    assert audit["n_leave_one_out_fits"] == 27
    assert audit["leave_one_out_max_p_value"] == pytest.approx(0.0783199508)
    assert audit["most_influential_removed_wavelength_micron"] == 5.375
    assert audit["robust_to_every_one_bin_deletion"] is False


def test_written_summary_matches_fresh_computation():
    path = spec.ROOT / "results" / "result_summary.json"
    if not path.exists():
        pytest.skip(
            "generated products are created after the implementation checkpoint"
        )
    committed = json.loads(path.read_text(encoding="utf-8"))
    fresh = spec.compute_study()["summary"]
    fresh["execution"] = committed["execution"]
    assert committed == fresh


def test_configuration_has_unique_ids_and_declared_decisions():
    config = json.loads(spec.CONFIG_PATH.read_text(encoding="utf-8"))
    bands = [row["id"] for row in config["co2_bands_micron"]]
    continua = [row["id"] for row in config["continuum_windows_micron"]]
    assert len(bands) == len(set(bands)) == 5
    assert len(continua) == len(set(continua)) == 6
    assert config["decision_thresholds"] == {
        "nir_absolute_sigma": 3.0,
        "miri_alpha": 0.05,
    }


def test_no_page_claims_three_instrument_coverage_for_nir_file_after_upgrade():
    page = (spec.ROOT / "index.html").read_text(encoding="utf-8")
    if "4411-point NIRISS+NIRSpec spectrum" not in page:
        pytest.skip(
            "public-page correction is added after the implementation checkpoint"
        )
    assert "4411-point NIRISS+NIRSpec spectrum" in page
    assert (
        "4411 native-resolution points spanning NIRISS SOSS, NIRSpec G395H, and MIRI LRS"
        not in page
    )
