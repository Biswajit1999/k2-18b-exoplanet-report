# Methods — window sensitivity and MIRI influence audit

## Question and decision rules

Before inspecting the grid result, the versioned configuration declares two
tests. First, all 30 combinations of five plausible 4.3 µm band windows and six
nearby continuum windows must remain below |3σ| under the supplied diagonal
uncertainties. Second, rejection of a constant MIRI spectrum at α=0.05 must
survive deletion of every individual non-overlap MIRI bin.

The first is a robustness screen for a descriptive contrast, not a test of CO2
abundance. The second is an influence diagnostic, not a molecular model.

## Inputs

The NIRISS SOSS+NIRSpec G395H array has 4,411 points from 0.852268 to 5.174292
µm. The separate MIRI LRS array has 28 bins from 5.125 to 11.875 µm. Both are
from the public Zenodo deposit identified in `data/SOURCE.md`. The overlapping
5.125 µm MIRI centre is excluded from the 27-bin MIRI audit. A +160 ppm shift is
used only for the joint display and cannot affect a within-MIRI flatness test.

## Band contrast

For depths d_i with quoted standard errors s_i, each window mean is

    mean = sum(d_i / s_i^2) / sum(1 / s_i^2)
    standard error = sqrt(1 / sum(1 / s_i^2)).

The signed contrast is the band mean minus the continuum mean. Its diagonal
standard error is the quadrature sum of the two window errors. The 5×6 grid is
declared in `configs/sensitivity_audit_v1.json`; no window is selected after
examining its significance.

## MIRI flatness and influence

The constant-depth model is the inverse-variance weighted mean. Its statistic
is the sum of squared standardized residuals and is compared with a chi-square
distribution with n−1 degrees of freedom. The model is refit 27 times, deleting
one MIRI bin each time. The robustness claim passes only if every refit remains
below p=0.05.

## Interpretation boundary

Neither calculation includes a spectral covariance matrix, a physical forward
model, chemical opacity, cloud or haze physics, stellar contamination, model
evidence, reduction-level systematics, or retrieval priors. Consequently,
neither can detect or exclude CO2, DMS/DMDS, an ocean, habitability, or life.
