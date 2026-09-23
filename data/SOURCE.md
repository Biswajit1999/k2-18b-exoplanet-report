# Data source

Both committed spectra are copied without numerical modification from Zenodo
record **10.5281/zenodo.16277833** ("Investigating aerosols as a reconciliation
mechanism for K2-18 b JWST MIRI and NIRISS/NIRSpec observations"), archive
`Spectra.zip` (MD5 `fb6453bba9e0dd2a94bb741c0777418c`).

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/16277833`.

## NIRISS + NIRSpec

`k218b_niriss_nirspec_miri_combined_spectrum.txt` retains its historical local
filename for stable links, but it is **not a MIRI-inclusive file**. Its archive
member is `Spectra/K2-18b_both_offset1_-41ppm_native.txt`: 4,411 rows spanning
0.852268–5.174292 µm, covering NIRISS SOSS and NIRSpec G395H. Canonical-LF
SHA-256: `0622a1761cbd1e8f920425fd0b54b9489517f66f0a885ed8190cfc0471aedf24`.

Three whitespace-separated columns, no header:

1. wavelength [micron]
2. transit depth, (Rp/Rs)^2
3. 1-sigma uncertainty on the transit depth

"native" indicates the source's unbinned sampling. `offset1_-41ppm` denotes the
source's NIRISS/NIRSpec offset treatment; it is not a MIRI offset.

## MIRI

`k218b_miri_lrs_eureka_spectrum.txt` is archive member
`Spectra/K2-18b_miri_lrs_eureka_taurex.txt`: 28 published MIRI LRS bins spanning
5.125–11.875 µm. Canonical-LF SHA-256:
`1b0959ba7513ee2c4ff14b8c6060cec05670a547d85f1fd99b8a6fb6eae0e7c2`.

Its four columns are wavelength centre [µm], transit depth, one-sigma
uncertainty, and wavelength half-width [µm]. The study excludes the 5.125 µm
MIRI centre from the joint non-overlap audit because it overlaps the NIRSpec
range ending at 5.174292 µm. The +160 ppm MIRI shift from the source paper is
used only when plotting the instruments together; it cancels from the MIRI
flatness statistic.

These are reduced spectra, not raw detector exposures. The repository does not
reproduce the upstream extraction or covariance matrix.

## System parameters

`system_parameters_snapshot.json` records the exact NASA Exoplanet Archive TAP
query and returned composite row used by the public page on 2026-09-23. This
prevents a future mutable catalogue value from being mistaken for the value
reviewed in this release.
