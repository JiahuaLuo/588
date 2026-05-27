# AWG High-Fidelity Validation Summary

This file summarizes the cloud-run Tidy3D validation of the simplified AWG output FPR stage.
The model is more physical than the local array-factor script because it uses actual FDTD propagation through the slab/output section, while still avoiding the full 2 mm-scale array-arm meander geometry.

## Quality Rubric

- good: dominant output fraction `>= 0.60` and second/first `<= 0.50`
- general: dominant output fraction `>= 0.40` and second/first `<= 0.80`
- passing: dominant output fraction `>= 0.30` and second/first `<= 0.95`
- poor: below the passing threshold

Here, dominant output fraction measures how much of the total detected flux stays in the strongest output port, while second/first measures how close the second strongest output is to the strongest one. Higher dominant fraction and lower second/first are both better.

## Baseline 4-Channel Runs

- 1547.6 nm -> dominant output 3; fluxes = [0.3896, 1.145, 1.184, 0.3981]
- 1549.2 nm -> dominant output 3; fluxes = [0.8407, 0.4479, 1.004, 0.6568]
- 1550.8 nm -> dominant output 4; fluxes = [0.7655, 0.4004, 0.7562, 0.9375]
- 1552.4 nm -> dominant output 4; fluxes = [0.5077, 0.4398, 0.5492, 0.8047]

Using the rubric above, all four baseline cases fall into the `passing` range. This confirms real wavelength-dependent output routing in the FDTD model, but it also shows that the routing is not yet sharp enough to be considered `general` or `good` across the full 4-channel set.

## Stretch-Goal Attempts

- 8-channel aperture/output layout:
  - stretch_8ch_1550.0nm: 1550.0 nm, dominant output 7, estimated cost 0.0736
- temperature dependence:
  - stretch_temp_1560.0nm_plus40K: 1550.8 nm, dominant output 2, estimated cost 0.0743
- pitch/offset optimization:
  - stretch_opt_1550.8nm: 1550.8 nm, dominant output 2, estimated cost 0.0735

## Optimization Follow-Up

The dedicated optimization sweep is summarized in [AWG_HF_OPTIMIZATION_SUMMARY.md](/Users/luojiahua/Library/CloudStorage/OneDrive-UW/Slides/Slides/EE588/project/tidy3d_awg_project/docs/AWG_HF_OPTIMIZATION_SUMMARY.md). The best scanned configuration was:

- array pitch = `1.20 um`
- output pitch = `1.60 um`
- output offset = `0.60 um`

At `1550.8 nm`, this improved the dominant output fraction from about `0.328` to about `0.466`, and improved the quality level from `passing` to `general`. However, when re-checked across the full 4-channel set, the optimized configuration remained mostly in the `passing` range except near the center wavelength. This means the current optimization is a successful local improvement, but not yet a full-band solution.

A further full-band optimization pass is summarized in [AWG_HF_GLOBAL_OPTIMIZATION_SUMMARY.md](/Users/luojiahua/Library/CloudStorage/OneDrive-UW/Slides/Slides/EE588/project/tidy3d_awg_project/docs/AWG_HF_GLOBAL_OPTIMIZATION_SUMMARY.md). That second pass prioritized average and worst-channel behavior across all 4 wavelengths rather than only the center wavelength. The best global configuration was:

- array pitch = `1.15 um`
- output pitch = `1.60 um`
- output offset = `0.65 um`

This global-best configuration did not lift the entire 4-channel set into the `general` range, but it produced a more balanced result than the original baseline by reducing the worst-case second/first ratio and avoiding the `poor` behavior seen in some more aggressive local optimizations. In other words, the local-best design is stronger at the center wavelength, while the global-best design is more even across the full 4-channel set.
