# Reproducibility

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# POSIX: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/analyze_spectrum.py
python -m pytest -q
python -m ruff check scripts tests
git diff --exit-code
```

The generator writes the two CSV audits, JSON summary, summary-statistics CSV,
and two SVG figures. SVG date/creator metadata and hash salts are fixed. Input
hashes canonicalize text line endings so Windows and Linux check the same
scientific bytes. CI requires the numerical CSV/JSON evidence to remain
byte-identical on Python 3.10, 3.12, and 3.13. SVG glyph paths can differ with
Matplotlib/FreeType versions, so CI validates their titles, accessibility, and
committed manifest hashes instead of pretending renderer bytes are universal.
The manifest records the clean implementation revision used for the release.

To revalidate upstream provenance, download `Spectra.zip` from Zenodo record
10.5281/zenodo.16277833, verify MD5
`fb6453bba9e0dd2a94bb741c0777418c`, and compare the canonical-LF hashes in
`data/SOURCE.md` with the named archive members.
