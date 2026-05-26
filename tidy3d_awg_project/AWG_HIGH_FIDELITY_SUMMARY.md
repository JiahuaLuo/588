# AWG High-Fidelity Validation Summary

This file summarizes the cloud-run Tidy3D validation of the simplified AWG output FPR stage.
The model is more physical than the local array-factor script because it uses actual FDTD propagation through the slab/output section, while still avoiding the full 2 mm-scale array-arm meander geometry.

## Baseline 4-Channel Runs

- 1547.6 nm -> dominant output 3; fluxes = [0.3896, 1.145, 1.184, 0.3981]
- 1549.2 nm -> dominant output 3; fluxes = [0.8407, 0.4479, 1.004, 0.6568]
- 1550.8 nm -> dominant output 4; fluxes = [0.7655, 0.4004, 0.7562, 0.9375]
- 1552.4 nm -> dominant output 4; fluxes = [0.5077, 0.4398, 0.5492, 0.8047]

## Stretch-Goal Attempts

- 8-channel aperture/output layout:
  - stretch_8ch_1550.0nm: 1550.0 nm, dominant output 7, estimated cost 0.0736
- temperature dependence:
  - stretch_temp_1560.0nm_plus40K: 1550.8 nm, dominant output 2, estimated cost 0.0743
- pitch/offset optimization:
  - stretch_opt_1550.8nm: 1550.8 nm, dominant output 2, estimated cost 0.0735
