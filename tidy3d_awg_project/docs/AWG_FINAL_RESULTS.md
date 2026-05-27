# Final Simplified AWG Results

## Method

This final-stage analysis uses a simplified local array-factor spectrum model calibrated by the existing Tidy3D MODE results and the first-pass AWG design parameters.
It is intended as a low-cost system-level approximation for the course project and should not be interpreted as a substitute for a full Tidy3D device-level FDTD validation.

## Inputs

- Center wavelength: 1550.0 nm
- Channel spacing target: 1.6 nm
- Target FSR: 19.2 nm
- AWG order: 81
- Arrayed waveguide count: 16
- Path length difference: 30.991 um

## Summary Metrics

- Average insertion loss: 3.00 dB
- Worst insertion loss: 3.00 dB
- Average worst-case crosstalk: -13.71 dB
- Worst-case crosstalk across all channels: -13.71 dB
- Average 3 dB bandwidth: 1.060 nm
- Average adjacent channel spacing: 1.600 nm

## Channel Metrics

| Channel | Target (nm) | Peak (nm) | Peak Tx (dB) | Insertion Loss (dB) | Crosstalk (dB) | 3 dB BW (nm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1547.600 | 1547.600 | -3.00 | 3.00 | -13.71 | 1.060 |
| 2 | 1549.200 | 1549.200 | -3.00 | 3.00 | -13.71 | 1.060 |
| 3 | 1550.800 | 1550.800 | -3.00 | 3.00 | -13.71 | 1.060 |
| 4 | 1552.400 | 1552.400 | -3.00 | 3.00 | -13.71 | 1.060 |

## Output Files

- `results/tables/awg_simplified_spectrum.csv`
- `results/tables/awg_channel_metrics.csv`
- `results/figures/awg_transmission_spectra.png`
- `results/figures/awg_channel_metrics.png`
