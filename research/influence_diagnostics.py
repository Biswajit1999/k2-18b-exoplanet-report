"""Independent diagnostics for heteroscedastic spectral bins.

The routines do not infer molecular detections; errors are assumed independent.
"""
import numpy as np


def weighted_constant(values, sigma):
    y, s = np.asarray(values,float), np.asarray(sigma,float)
    if y.ndim != 1 or y.size < 2 or s.shape != y.shape:
        raise ValueError('need matching vectors with at least two bins')
    if not np.all(np.isfinite(y)) or not np.all(np.isfinite(s)) or np.any(s <= 0):
        raise ValueError('invalid bin or uncertainty')
    w = 1/s**2
    mean = np.sum(w*y)/np.sum(w)
    chi2 = np.sum(w*(y-mean)**2)
    return float(mean), float(np.sqrt(1/np.sum(w))), float(chi2), len(y)-1


def leave_one_out_constant(values, sigma):
    """Exact O(n) leave-one-out chi-square without repeated refitting."""
    y, s = np.asarray(values,float), np.asarray(sigma,float)
    weighted_constant(y,s)
    if len(y)<3:
        raise ValueError('need >=3 bins for leave-one-out')
    w = 1/s**2
    sw, swy, swy2 = np.sum(w), np.sum(w*y), np.sum(w*y*y)
    rem_w, rem_wy, rem_wy2 = sw-w, swy-w*y, swy2-w*y*y
    means = rem_wy/rem_w
    chi2 = np.maximum(0, rem_wy2 - rem_wy**2/rem_w)
    return means, chi2, np.full(len(y),len(y)-2,dtype=int)


def contrast_windows(wavelength, depth, sigma, band, continuum):
    """Inverse-variance mean difference, with disjoint window requirement."""
    lam=np.asarray(wavelength,float)
    y=np.asarray(depth,float)
    s=np.asarray(sigma,float)
    if lam.ndim != 1 or y.shape != lam.shape or s.shape != lam.shape:
        raise ValueError('mismatched arrays')
    b=(lam>=band[0])&(lam<=band[1]); c=(lam>=continuum[0])&(lam<=continuum[1])
    if np.any(b&c) or np.sum(b)<2 or np.sum(c)<2:
        raise ValueError('windows must be disjoint and contain >=2 bins each')
    mb,eb,_,_=weighted_constant(y[b],s[b])
    mc,ec,_,_=weighted_constant(y[c],s[c])
    return mb-mc, float(np.hypot(eb,ec))
