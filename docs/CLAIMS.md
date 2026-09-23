# Claim ledger

| ID | Claim | Evidence | Status and boundary |
|---|---|---|---|
| C1 | The historical 4.1–4.6 versus 3.6–3.9 µm contrast is 4.07±23.16 ppm (0.176σ). | `results/result_summary.json` | Descriptive, diagonal-error calculation only. |
| C2 | Across 30 declared definitions, signed contrast spans −0.861σ to +2.258σ; all remain below |3σ|. | `results/band_contrast_multiverse.csv` | Supports only a lack of robust ≥3σ window contrast in this design grid. |
| C3 | A flat model on 27 non-overlap MIRI bins gives χ²=54.162 for 26 dof (p=0.000968). | `results/result_summary.json` | Not a molecular detection; systematics/covariance are unmodelled. |
| C4 | MIRI flatness rejection fails the predeclared leave-one-out robustness rule: removing the 5.375 µm bin raises p to 0.07832; 26/27 deletions retain p<0.05. | `results/miri_flatness_leave_one_out.csv` | Negative robustness result; single-bin influence is material. |
| C5 | The committed 4,411-point file is NIRISS+NIRSpec, not MIRI-inclusive. | Zenodo archive member, wavelength range, canonical digest | Corrects the pre-upgrade provenance claim. |

## Superseded claims

- “4,411 native-resolution wavelength points spanning NIRISS, NIRSpec, and
  MIRI” is false and superseded by C5.
- The single 0.2σ contrast remains numerically reproducible but is no longer
  presented as the repository's whole result; its value depends on the window
  definition, as quantified by C2.
- The previous Schmidt et al./arXiv:2507.14983 attribution is corrected. The
  Schmidt et al. reanalysis is arXiv:2501.18477; 2507.14983 is Jaziri et al.
