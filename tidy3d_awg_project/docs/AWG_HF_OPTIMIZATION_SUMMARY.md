# AWG High-Fidelity Optimization Summary

## Quality Rubric

- good: dominant output fraction >= 0.60 and second/first <= 0.50
- general: dominant output fraction >= 0.40 and second/first <= 0.80
- passing: dominant output fraction >= 0.30 and second/first <= 0.95
- poor: anything below the passing threshold

Dominant output fraction measures how much of the detected output flux stays in the strongest port.
Second/first measures how close the second-strongest port is to the strongest one, so lower is better.

## Best Scan Result

- Best configuration: `optscan_c`
- Array pitch: 1.20 um
- Output pitch: 1.60 um
- Output offset: 0.60 um
- Dominant output fraction at 1550.8 nm: 0.4658
- Second/first ratio at 1550.8 nm: 0.7023
- Quality classification: general

## Full Scan Ranking

| Label | Array pitch (um) | Output pitch (um) | Offset (um) | Dominant fraction | Second/first | Quality |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| optscan_c | 1.20 | 1.60 | 0.60 | 0.4658 | 0.7023 | general |
| optscan_a | 1.30 | 1.80 | 0.30 | 0.3581 | 0.8295 | passing |
| optscan_b | 1.20 | 1.70 | 0.40 | 0.3712 | 0.9224 | passing |
| optscan_baseline | 1.50 | 2.00 | 0.00 | 0.3278 | 0.8165 | passing |
| optscan_h | 1.00 | 1.35 | 1.10 | 0.3281 | 0.8278 | passing |
| optscan_d | 1.15 | 1.55 | 0.70 | 0.3613 | 0.9492 | passing |
| optscan_e | 1.10 | 1.50 | 0.80 | 0.3058 | 0.9022 | passing |
| optscan_g | 1.00 | 1.40 | 1.00 | 0.3042 | 0.9157 | passing |
| optscan_f | 1.05 | 1.45 | 0.90 | 0.2835 | 0.9690 | poor |

## Best-Config Verification

| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |
| ---: | ---: | ---: | ---: | --- |
| 1547.6 | 4 | 0.3076 | 0.8101 | passing |
| 1549.2 | 2 | 0.3297 | 0.9320 | passing |
| 1550.8 | 2 | 0.4658 | 0.7023 | general |
| 1552.4 | 1 | 0.3701 | 0.8961 | passing |
