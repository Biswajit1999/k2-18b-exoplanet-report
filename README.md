# K2-18 b — Exoplanet Atmosphere Report

The most contested atmosphere in exoplanet science right now: a temperate
sub-Neptune with a disputed CO2/CH4 detection, a tentative and unconfirmed
DMS signal, and a live debate about whether combining data from different
JWST instruments manufactures the very feature it claims to find. This repo
tests that debate directly against real, offset-corrected combined data.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## What's real here

- **System parameters** — queried live from the NASA Exoplanet Archive TAP
  service (`pscomppars` table).
- **Combined JWST spectrum** — 4411 real native-resolution wavelength points
  spanning NIRISS SOSS, NIRSpec G395H, and MIRI LRS, with the source paper's
  own best-fit inter-instrument offset already applied, from a 2025
  reanalysis investigating whether aerosols/offsets can reconcile the
  MIRI and NIRISS/NIRSpec observations. Released publicly on Zenodo
  ([10.5281/zenodo.16277833](https://doi.org/10.5281/zenodo.16277833)).
- **Analysis** — `scripts/analyze_spectrum.py` bins the native spectrum for
  display and directly compares the mean depth in the CO2 absorption band
  (4.1-4.6 micron) against a nearby continuum window, computing the real
  significance of any excess. Run it yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    real combined JWST spectrum file (Zenodo)
scripts/analyze_spectrum.py   real binning + CO2-band-vs-continuum analysis
figures/                 generated plot + summary_statistics.csv
```

## Key finding this repo shows directly -- and doesn't oversell

Using this offset-corrected combined spectrum, the CO2-band mean depth
exceeds the nearby continuum by only ~4 ppm, at ~0.2 sigma significance —
statistically indistinguishable from noise. This is the real, honest result
of this specific comparison; it does not prove CO2 is absent (the original
2023 claim used NIRISS+NIRSpec alone, without the offset correction applied
here), but it directly demonstrates why the result remains disputed rather
than settled.

## References

1. Madhusudhan, N. et al., 2023. Carbon-bearing Molecules in a Possible
   Hycean Atmosphere. *The Astrophysical Journal Letters*, 956, L13.
2. Madhusudhan, N. et al., 2023. Potential Biosignature Detection: Possible
   Indications of Dimethyl Sulfide in the Atmosphere of K2-18 b. *The
   Astrophysical Journal Letters*, 963, L6.
3. Zenodo record
   [10.5281/zenodo.16277833](https://doi.org/10.5281/zenodo.16277833),
   "Investigating aerosols as a way to reconcile K2-18 b JWST MIRI and
   NIRISS/NIRSpec observations."
4. Wogan, N. et al., 2024. JWST Reveals CH4, CO2, and H2O in a Metal-rich
   Miscible Atmosphere on a Two-Column Sub-Neptune. *The Astrophysical
   Journal Letters*, 963, L7.
5. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/>.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
