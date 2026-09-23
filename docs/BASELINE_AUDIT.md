# Baseline audit — 2026-09-23

The pre-upgrade repository had a useful public spectrum, an executable script,
three tests, CI, a live report, source attribution, and unusually cautious prose
for a small portfolio project. The following defects nevertheless prevented the
headline from being treated as strong research evidence.

1. The 4,411-row file was described throughout as NIRISS+NIRSpec+MIRI, but its
   0.852–5.174 µm range and exact Zenodo archive member show that it contains
   NIRISS+NIRSpec only. The actual MIRI product is a separate 28-bin file.
2. One band and one continuum window produced the 0.18σ headline. No rationale,
   sensitivity analysis, or design-decision audit showed whether that exact
   number was stable.
3. The result assumed diagonal errors while correctly admitting that the
   covariance was unavailable. There was no test of single-bin influence.
4. The README attributed arXiv:2507.14983 to Schmidt et al.; that identifier is
   the Jaziri et al. non-equilibrium-chemistry paper. The Schmidt et al.
   reanalysis is arXiv:2501.18477.
5. The source record, archive member, download checksum, input digest, analysis
   decisions, and generated result were not joined by a machine-readable
   manifest.
6. CI exercised one Python version, used floating action tags, did not lint, and
   did not verify that generated evidence was current.

Baseline maturity: **45/100** on the repository-practice rubric in
`research/research-quality-rubric.json`. This number is an expert heuristic,
not peer review or a measurement of scientific truth.
