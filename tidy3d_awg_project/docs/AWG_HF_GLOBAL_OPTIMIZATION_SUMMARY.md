# AWG High-Fidelity Global Optimization Summary

## Goal

This optimization prioritizes the full 4-channel average and worst-channel behavior rather than a single center wavelength.

## Quality Rubric

- good: dominant output fraction >= 0.60 and second/first <= 0.50
- general: dominant output fraction >= 0.40 and second/first <= 0.80
- passing: dominant output fraction >= 0.30 and second/first <= 0.95
- poor: below the passing threshold

## Best Global Configuration

- Config label: `seed_local_best`
- Array pitch: 1.20 um
- Output pitch: 1.60 um
- Output offset: 0.60 um
- Average dominant fraction: 0.3683
- Minimum dominant fraction: 0.3076
- Average second/first: 0.8351
- Maximum second/first: 0.9320
- Aggregate quality: passing

## Configuration Ranking

| Config | Array pitch | Output pitch | Offset | Avg dom frac | Min dom frac | Avg second/first | Max second/first | Aggregate quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed_local_best | 1.20 | 1.60 | 0.60 | 0.3683 | 0.3076 | 0.8351 | 0.9320 | passing |
| seed_baseline | 1.50 | 2.00 | 0.00 | 0.3494 | 0.3278 | 0.8259 | 0.9671 | poor |
| globscan_372 | 1.25 | 1.65 | 0.55 | 0.3398 | 0.3095 | 0.8195 | 0.9482 | passing |
| globscan_368 | 1.25 | 1.60 | 0.60 | 0.3321 | 0.3195 | 0.8209 | 0.9244 | passing |
| globscan_373 | 1.25 | 1.65 | 0.60 | 0.3262 | 0.3028 | 0.8724 | 0.9965 | poor |
| globscan_369 | 1.25 | 1.60 | 0.65 | 0.3174 | 0.3092 | 0.8710 | 0.9718 | poor |
| globscan_374 | 1.25 | 1.65 | 0.65 | 0.3137 | 0.2869 | 0.9136 | 0.9944 | poor |

## Best Config Per-Channel Results

| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |
| ---: | ---: | ---: | ---: | --- |
| 1547.6 | 4 | 0.3076 | 0.8101 | passing |
| 1549.2 | 2 | 0.3297 | 0.9320 | passing |
| 1550.8 | 2 | 0.4658 | 0.7023 | general |
| 1552.4 | 1 | 0.3701 | 0.8961 | passing |
