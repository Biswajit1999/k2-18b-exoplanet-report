# Changelog

## 1.0.0 — 2026-09-23

- Corrected the critical provenance error that described a 0.852–5.174 µm
  NIRISS+NIRSpec array as MIRI-inclusive.
- Added the actual 28-bin public MIRI LRS spectrum and canonical source hashes.
- Froze a 30-definition CO2 band/continuum sensitivity protocol and a 27-fit
  MIRI leave-one-bin-out influence protocol before evidence generation.
- Published every configuration, the negative robustness results, deterministic
  SVGs, a machine-readable summary, claim ledger, limitations, methods, and
  before/after research-practice graph.
- Corrected the Schmidt/Jaziri citation mismatch.
- Expanded tests, linting, deterministic evidence checks, and CI to Python
  3.10, 3.12, and 3.13 with immutable action revisions.

## Before 1.0.0

The repository published one 0.18σ band/continuum statistic, three tests, and a
live explanatory report. That value remains reproducible but is now presented
inside its full window-definition sensitivity range.
