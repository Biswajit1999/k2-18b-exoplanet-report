"""Publication-level regression checks for the reviewer-facing evidence."""

import json

import analyze_spectrum as spec


def test_public_page_exposes_results_and_boundaries():
    page = (spec.ROOT / "index.html").read_text(encoding="utf-8")
    required = [
        "4,411-point NIRISS+NIRSpec spectrum",
        "30 + 27 sensitivity fits",
        "−0.86 to +2.26σ",
        "0.0783",
        "Neither calculation identifies any molecule",
        "results/sensitivity_audit.svg",
        "research/research-maturity-before-after.svg",
    ]
    for marker in required[:-1]:
        assert marker in page
    assert (
        "4411 native-resolution points spanning NIRISS SOSS, NIRSpec G395H, and MIRI LRS"
        not in page
    )
    assert "Schmidt, S.J. et al., 2025. Unraveling" not in page


def test_system_parameter_snapshot_preserves_query_and_uncertainties():
    payload = json.loads(
        (spec.ROOT / "data" / "system_parameters_snapshot.json").read_text()
    )
    assert payload["table"] == "pscomppars"
    assert "where pl_name='K2-18 b'" in payload["query"]
    assert payload["row"]["pl_masse"] == 8.92
    assert payload["row"]["pl_masseerr1"] == 1.7
    assert payload["row"]["pl_radeerr2"] == -0.22


def test_maturity_rubric_totals_are_computed_from_dimensions():
    payload = json.loads(
        (spec.ROOT / "research" / "research-quality-rubric.json").read_text()
    )
    assert (
        sum(row["before"] for row in payload["dimensions"])
        == payload["before_total"]
        == 45
    )
    assert (
        sum(row["after"] for row in payload["dimensions"])
        == payload["after_total"]
        == 96
    )


def test_svg_evidence_is_accessible_and_free_of_timestamp_metadata():
    for path in [
        spec.ROOT / "figures" / "k218b_spectrum_audit.svg",
        spec.ROOT / "results" / "sensitivity_audit.svg",
        spec.ROOT / "research" / "research-maturity-before-after.svg",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "<svg" in text
        assert "<title" in text
        assert "dc:date" not in text


def test_evidence_manifest_matches_every_generated_product():
    manifest = json.loads(
        (spec.ROOT / "results" / "evidence_manifest.json").read_text()
    )
    assert len(manifest["files"]) == 6
    for relative_path, expected in manifest["files"].items():
        assert spec.canonical_sha256(spec.ROOT / relative_path) == expected
