# Spectral influence diagnostics (2026-11-10)

Standalone independent numerical checks for the K2-18 b robustness audit. Requires NumPy; run `cd research && python -m unittest -v test_influence_diagnostics.py`.

- `weighted_constant`: inverse-variance mean, formal uncertainty and chi-square.
- `leave_one_out_constant`: exact weighted delete-one mean/chi-square using sufficient statistics; compared against brute-force refits in regression tests.
- `contrast_windows`: inverse-variance band minus continuum contrast with explicit disjoint-window validation.

These are synthetic unit tests, not a new MIRI measurement. Independent-bin Gaussian uncertainties are assumed; the supplied public spectrum's full covariance is unavailable. The O(n) deletion formula can lose precision for nearly constant very large values because of subtraction of similar sums; direct residual refits should be preferred in that regime. No DMS/DMDS detection or exclusion is inferred. AI-assisted implementation; Biswajit Jana is the requested Git author.
