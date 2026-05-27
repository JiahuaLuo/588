# AWG Coarse-to-Fine Screening Summary

## Goal

This stage performs a zero-credit local aperture-propagation scan before any 2D cloud FDTD runs.
The purpose is not to replace FDTD, but to find the most promising parameter direction so the later cloud validation only touches a small shortlist.

## Search Space

- FPR length candidates: 50.00, 55.00, 60.00 um
- Array pitch candidates: 1.05, 1.10, 1.15, 1.20, 1.25 um
- Output pitch candidates: 1.45, 1.50, 1.55, 1.60, 1.65 um
- Output offset candidates: 0.45, 0.50, 0.55, 0.60, 0.65 um
- Equivalent input phase tilt used in local model: 1.20 um

## Best Coarse Candidate

- Config label: `coarse_374`
- FPR length: 60.00 um
- Array pitch: 1.25 um
- Output pitch: 1.65 um
- Output offset: 0.65 um
- Average dominant fraction: 0.3320
- Minimum dominant fraction: 0.2503
- Average second/first: 0.8305
- Maximum second/first: 0.9996

## Recommended 2D FDTD Shortlist

| Config | FPR length | Array pitch | Output pitch | Offset | Avg dom frac | Min dom frac | Max second/first |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| coarse_374 | 60.00 | 1.25 | 1.65 | 0.65 | 0.3320 | 0.2503 | 0.9996 |
| coarse_249 | 55.00 | 1.25 | 1.65 | 0.65 | 0.3317 | 0.2503 | 0.9997 |
| coarse_124 | 50.00 | 1.25 | 1.65 | 0.65 | 0.3314 | 0.2503 | 0.9997 |
| coarse_373 | 60.00 | 1.25 | 1.65 | 0.60 | 0.3310 | 0.2503 | 0.9997 |
| coarse_248 | 55.00 | 1.25 | 1.65 | 0.60 | 0.3308 | 0.2503 | 0.9998 |

## Best Candidate Per-Channel Results

| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |
| ---: | ---: | ---: | ---: | --- |
| 1547.6 | 2 | 0.2503 | 0.9996 | poor |
| 1549.2 | 2 | 0.2618 | 0.9720 | poor |
| 1550.8 | 2 | 0.3285 | 0.7802 | passing |
| 1552.4 | 2 | 0.4873 | 0.5702 | general |
