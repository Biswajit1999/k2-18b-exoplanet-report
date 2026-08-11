# Data source

`k218b_niriss_nirspec_miri_combined_spectrum.txt` is downloaded, unmodified,
from Zenodo record **10.5281/zenodo.16277833** ("Investigating aerosols as a
way to reconcile K2-18 b JWST MIRI and NIRISS/NIRSpec observations"), file
`Spectra/K2-18b_both_offset1_-41ppm_native.txt`.

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/16277833`.

Three whitespace-separated columns, no header:

1. wavelength [micron]
2. transit depth, (Rp/Rs)^2
3. 1-sigma uncertainty on the transit depth

"native" indicates this is the un-binned, instrument-native-resolution
spectrum; "offset1 -41ppm" indicates the source paper's own best-fit
cross-instrument offset (applied to reconcile MIRI with NIRISS/NIRSpec) is
already included in these values.
