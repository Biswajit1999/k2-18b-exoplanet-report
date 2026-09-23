# Limitations

- This repository does not perform an atmospheric retrieval. A band contrast
  cannot identify a molecule because overlapping absorbers, temperature,
  metallicity, clouds, hazes, offsets, and priors all affect the spectrum.
- The supplied arrays do not include a full spectral covariance matrix. All
  quoted σ and chi-square values therefore use the published diagonal errors.
- The 30-definition grid is declared and broad enough to expose design
  sensitivity, but it is not an exhaustive set of scientifically admissible
  continuum models and creates correlated comparisons.
- The MIRI leave-one-out exercise diagnoses influence; it does not correct the
  unresolved instrument systematics discussed in the source literature.
- The +160 ppm MIRI shift is inherited from the source analysis and is used for
  visualization only. It is not independently estimated here.
- The repository begins with reduced public spectra and cannot reproduce the
  detector-level JWST calibration, light-curve extraction, or alternative data
  reductions.
- No result here establishes or excludes CO2, CH4, DMS/DMDS, a Hycean ocean,
  habitability, biological production, or life.
