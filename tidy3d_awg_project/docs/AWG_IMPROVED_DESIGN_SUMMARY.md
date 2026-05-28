# AWG Improved Design Results

## Improvement rationale
Previous scans all used N=16 array arms, giving array-factor 3-dB BW = FSR/16 ≈ 1.2 nm.
Channel spacing is 1.6 nm, so adjacent channels heavily overlap.
N=24 reduces the 3-dB BW to ≈ 0.8 nm, well inside the channel spacing.
A longer FPR (70 μm) further increases linear dispersion.

## Quality rubric
- good:    dom_frac ≥ 0.60, s2f ≤ 0.50
- general: dom_frac ≥ 0.40, s2f ≤ 0.80
- passing: dom_frac ≥ 0.30, s2f ≤ 0.95
- poor:    below passing

## Per-config results

### impr_A_n24
  N=24, FPR=55.0 μm, array_pitch=1.2, output_pitch=1.6, offset=0.6
  avg dom_frac=0.3765, min dom_frac=0.3127
  avg s2f=0.8199,     max s2f=0.9774

  | λ (nm) | dom_out | dom_frac | s2f | quality |
  | ---: | ---: | ---: | ---: | --- |
  | 1547.6 | 1 | 0.3127 | 0.8458 | passing |
  | 1549.2 | 2 | 0.3932 | 0.8219 | passing |
  | 1550.8 | 2 | 0.4054 | 0.9774 | poor |
  | 1552.4 | 2 | 0.3949 | 0.6345 | passing |

### impr_B_n24_off09
  N=24, FPR=55.0 μm, array_pitch=1.2, output_pitch=1.6, offset=0.9
  avg dom_frac=0.3283, min dom_frac=0.2997
  avg s2f=0.9111,     max s2f=0.9656

  | λ (nm) | dom_out | dom_frac | s2f | quality |
  | ---: | ---: | ---: | ---: | --- |
  | 1547.6 | 4 | 0.2997 | 0.9076 | poor |
  | 1549.2 | 4 | 0.3091 | 0.9656 | poor |
  | 1550.8 | 2 | 0.3271 | 0.8655 | passing |
  | 1552.4 | 2 | 0.3772 | 0.9057 | passing |

### impr_C_n24_p18
  N=24, FPR=55.0 μm, array_pitch=1.2, output_pitch=1.8, offset=0.9
  avg dom_frac=0.4033, min dom_frac=0.3070
  avg s2f=0.7715,     max s2f=0.9245

  | λ (nm) | dom_out | dom_frac | s2f | quality |
  | ---: | ---: | ---: | ---: | --- |
  | 1547.6 | 3 | 0.4731 | 0.5456 | general |
  | 1549.2 | 3 | 0.4188 | 0.7256 | general |
  | 1550.8 | 1 | 0.3070 | 0.9245 | passing |
  | 1552.4 | 3 | 0.4142 | 0.8902 | passing |

### impr_D_n24_fpr70
  N=24, FPR=70.0 μm, array_pitch=1.2, output_pitch=2.0, offset=0.8
  avg dom_frac=0.3775, min dom_frac=0.3312
  avg s2f=0.7463,     max s2f=0.8968

  | λ (nm) | dom_out | dom_frac | s2f | quality |
  | ---: | ---: | ---: | ---: | --- |
  | 1547.6 | 3 | 0.3312 | 0.8968 | passing |
  | 1549.2 | 2 | 0.4344 | 0.6072 | general |
  | 1550.8 | 3 | 0.3428 | 0.8004 | passing |
  | 1552.4 | 4 | 0.4015 | 0.6809 | general |

## Comparison with prior best (N=16, FPR=55, 1.20/1.60/0.60)
| Metric | Prior best | Best new config |
| --- | --- | --- |
| avg dom_frac (4-channel) | 0.3683 | 0.4033 |
| max s2f (worst channel)  | 0.9320 | 0.9245 |
| best new config label    | — | impr_C_n24_p18 |
