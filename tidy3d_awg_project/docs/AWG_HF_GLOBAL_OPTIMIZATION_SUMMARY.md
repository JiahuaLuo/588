# AWG High-Fidelity Global Optimization Summary

## Goal

This optimization prioritizes the full 4-channel average and worst-channel behavior rather than a single center wavelength.

## Quality Rubric

- good: dominant output fraction >= 0.60 and second/first <= 0.50
- general: dominant output fraction >= 0.40 and second/first <= 0.80
- passing: dominant output fraction >= 0.30 and second/first <= 0.95
- poor: below the passing threshold

## Best Global Configuration

- Config label: `globscan_e`
- Array pitch: 1.15 um
- Output pitch: 1.60 um
- Output offset: 0.65 um
- Average dominant fraction: 0.3579
- Minimum dominant fraction: 0.3106
- Average second/first: 0.7959
- Maximum second/first: 0.8482
- Aggregate quality: passing

## Configuration Ranking

| Config | Array pitch | Output pitch | Offset | Avg dom frac | Min dom frac | Avg second/first | Max second/first | Aggregate quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| globscan_e | 1.15 | 1.60 | 0.65 | 0.3579 | 0.3106 | 0.7959 | 0.8482 | passing |
| globscan_a | 1.25 | 1.65 | 0.50 | 0.3487 | 0.3143 | 0.7825 | 0.9185 | passing |
| seed_local_best | 1.20 | 1.60 | 0.60 | 0.3683 | 0.3076 | 0.8351 | 0.9320 | passing |
| globscan_b | 1.25 | 1.60 | 0.55 | 0.3433 | 0.3184 | 0.8018 | 0.9262 | passing |
| seed_baseline | 1.50 | 2.00 | 0.00 | 0.3494 | 0.3278 | 0.8259 | 0.9671 | poor |
| globscan_c | 1.20 | 1.55 | 0.55 | 0.3656 | 0.2887 | 0.8321 | 0.9984 | poor |
| globscan_d | 1.15 | 1.55 | 0.60 | 0.3243 | 0.2819 | 0.8878 | 0.9762 | poor |

## Best Config Per-Channel Results

| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |
| ---: | ---: | ---: | ---: | --- |
| 1547.6 | 3 | 0.3106 | 0.7911 | passing |
| 1549.2 | 4 | 0.3363 | 0.6981 | passing |
| 1550.8 | 1 | 0.3701 | 0.8482 | passing |
| 1552.4 | 4 | 0.4145 | 0.8462 | passing |
