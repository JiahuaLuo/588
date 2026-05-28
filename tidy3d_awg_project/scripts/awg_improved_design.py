"""
awg_improved_design.py

Motivation
----------
All previous scans (awg_hf_optimizer, awg_hf_global_optimizer) fixed the
array arm count at N=16.  With FSR ≈ 19.2 nm and N=16, the array-factor
3-dB bandwidth is FSR/N ≈ 1.2 nm — too close to the 1.6 nm channel spacing,
which is the root cause of the high crosstalk.

Increasing N to 24 (same array_pitch → aperture grows from 18 μm to 27.6 μm,
still inside the 34 μm slab) cuts the 3-dB bandwidth to ≈ 0.8 nm, well below
the channel spacing.  This is the single highest-leverage change left on the
table.

In addition, a longer FPR (70 μm vs 55 μm) increases the linear dispersion
between channels, making the output ports easier to separate.

Four configurations are tested × 4 wavelengths each = 16 FDTD runs.
Estimated cost: ~1.3 FlexCredit  (well within the 2.0 FC budget).

  Config A: N=24, FPR=55 μm, same best pitch/offset as prior local-best
  Config B: N=24, FPR=55 μm, slightly larger offset (explore)
  Config C: N=24, FPR=55 μm, wider output pitch (explore)
  Config D: N=24, FPR=70 μm, proportionally scaled pitch & offset

Results are written to:
  results/tables/awg_improved_design_results.csv
  docs/AWG_IMPROVED_DESIGN_SUMMARY.md
  results/figures/awg_improved_design_channels.png
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MPLCONFIGDIR = ROOT / ".mplconfig"
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tidy3d as td
import tidy3d.web as web
from tidy3d.constants import C_0

# ── Output paths ──────────────────────────────────────────────────────────────
TABLES = ROOT / "results" / "tables"
ASSETS = ROOT / "results" / "figures"
DOCS   = ROOT / "docs"
DATA_DIR = ROOT / "data" / "high_fidelity_awg"
RESULTS_CSV = TABLES / "awg_improved_design_results.csv"
SUMMARY_MD  = DOCS  / "AWG_IMPROVED_DESIGN_SUMMARY.md"
PLOT_PNG    = ASSETS / "awg_improved_design_channels.png"

TASK_FOLDER = "ee588_awg"
MAX_CREDITS = 2.0
CHANNEL_WAVELENGTHS_NM = [1547.6, 1549.2, 1550.8, 1552.4]

# ── Fixed AWG physical parameters (same as all previous scripts) ──────────────
CLAD_N          = 1.44
WG_WIDTH_UM     = 0.50
LAMBDA0_UM      = 1.55
NEFF0           = 2.444579740420668
NGROUP0         = 4.051219463271623
DELTA_LENGTH_UM = 30.990668646375973   # ΔL = m·λ₀/n_g

# ── Simulation geometry constants ─────────────────────────────────────────────
INPUT_STUB_UM   = 8.0
OUTPUT_STUB_UM  = 14.0
PML_MARGIN_X_UM = 5.0
PML_MARGIN_Y_UM = 3.0
MIN_STEPS_PER_WVL = 18


# ── Helper: n_eff as a function of wavelength (linear dispersion model) ────────
def neff_at(wavelength_um: float) -> float:
    dneff_dlambda = (NEFF0 - NGROUP0) / LAMBDA0_UM
    return float(NEFF0 + dneff_dlambda * (wavelength_um - LAMBDA0_UM))


# ── Core simulation builder ────────────────────────────────────────────────────
def build_simulation(
    wavelength_nm: float,
    array_count: int,
    slab_length_um: float,
    slab_span_y_um: float,
    array_pitch_um: float,
    output_pitch_um: float,
    output_offset_um: float,
) -> td.Simulation:
    wavelength_um = wavelength_nm / 1000.0
    neff = neff_at(wavelength_um)
    freq0  = C_0 / wavelength_um
    fwidth = freq0 / 80.0
    core_medium = td.Medium(name="core_eff", permittivity=neff ** 2)
    clad_medium = td.Medium(name="clad_eff", permittivity=CLAD_N ** 2)

    # Array arm y-positions (centred on 0)
    arm_indices = np.arange(array_count)
    arr_y = (arm_indices - (array_count - 1) / 2.0) * array_pitch_um

    # Output waveguide y-positions
    out_indices = np.arange(4)
    out_y = (out_indices - 1.5) * output_pitch_um + output_offset_um

    x_arr   = -slab_length_um / 2.0
    x_out   =  slab_length_um / 2.0
    sim_Lx  = INPUT_STUB_UM + slab_length_um + OUTPUT_STUB_UM + 2 * PML_MARGIN_X_UM
    sim_Ly  = slab_span_y_um + 2 * PML_MARGIN_Y_UM

    structures: list[td.Structure] = [
        td.Structure(
            geometry=td.Box(center=(0.0, 0.0, 0.0),
                            size=(slab_length_um, slab_span_y_um, td.inf)),
            medium=core_medium,
            name="slab_fpr",
        )
    ]
    for i, y in enumerate(arr_y):
        structures.append(td.Structure(
            geometry=td.Box(center=(x_arr - INPUT_STUB_UM / 2.0, float(y), 0.0),
                            size=(INPUT_STUB_UM, WG_WIDTH_UM, td.inf)),
            medium=core_medium, name=f"arr_stub_{i:02d}"))
    for i, y in enumerate(out_y):
        structures.append(td.Structure(
            geometry=td.Box(center=(x_out + OUTPUT_STUB_UM / 2.0, float(y), 0.0),
                            size=(OUTPUT_STUB_UM, WG_WIDTH_UM, td.inf)),
            medium=core_medium, name=f"out_wg_{i+1}"))

    # Phased sources at each array arm
    beta = 2.0 * np.pi * neff / wavelength_um
    sources: list[td.ModeSource] = []
    src_x = x_arr - INPUT_STUB_UM * 0.55
    for k, y in enumerate(arr_y):
        phase_k = float(beta * k * DELTA_LENGTH_UM)
        sources.append(td.ModeSource(
            name=f"src_{k:02d}",
            center=(float(src_x), float(y), 0.0),
            size=(0.0, 1.2, td.inf),
            source_time=td.GaussianPulse(freq0=freq0, fwidth=fwidth, phase=phase_k),
            direction="+",
            mode_spec=td.ModeSpec(num_modes=1, target_neff=neff),
            mode_index=0,
        ))

    # Flux monitors at each output waveguide
    monitors: list[td.FluxMonitor] = []
    mon_x = x_out + OUTPUT_STUB_UM * 0.65
    for i, y in enumerate(out_y):
        monitors.append(td.FluxMonitor(
            name=f"out_{i+1}",
            center=(float(mon_x), float(y), 0.0),
            size=(0.0, 1.4, td.inf),
            freqs=[freq0],
        ))

    return td.Simulation(
        center=(0.0, 0.0, 0.0),
        size=(sim_Lx, sim_Ly, 0.0),
        run_time=1.5e-12,
        medium=clad_medium,
        structures=structures,
        sources=sources,
        monitors=monitors,
        boundary_spec=td.BoundarySpec(
            x=td.Boundary.pml(),
            y=td.Boundary.pml(),
            z=td.Boundary.periodic(),
        ),
        grid_spec=td.GridSpec.auto(min_steps_per_wvl=MIN_STEPS_PER_WVL,
                                   wavelength=wavelength_um),
        shutoff=1e-5,
    )


# ── Metric helpers ─────────────────────────────────────────────────────────────
def extract_fluxes(sim_data: td.SimulationData) -> list[float]:
    return [float(np.real(np.array(sim_data[f"out_{i}"].flux).reshape(-1)[0]))
            for i in range(1, 5)]


def routing_quality(fluxes: list[float]) -> tuple[float, float, str]:
    f = np.array(fluxes, dtype=float)
    total = float(f.sum())
    s = np.sort(f)[::-1]
    dom = s[0] / total if total > 0 else 0.0
    s2f = s[1] / s[0] if s[0] > 0 else 1.0
    if dom >= 0.60 and s2f <= 0.50:  grade = "good"
    elif dom >= 0.40 and s2f <= 0.80: grade = "general"
    elif dom >= 0.30 and s2f <= 0.95: grade = "passing"
    else:                              grade = "poor"
    return dom, s2f, grade


# ── Configuration table ────────────────────────────────────────────────────────
# Physics rationale for each config is in the module docstring above.
CONFIGS = [
    # Config A: N=24, same FPR geometry, same best output params as prior local-best
    # Benchmark: does more arms alone improve things?
    dict(label="impr_A_n24",
         array_count=24, slab_length_um=55.0, slab_span_y_um=34.0,
         array_pitch_um=1.20, output_pitch_um=1.60, output_offset_um=0.60),

    # Config B: N=24, shift offset outward — channels may focus further from center
    dict(label="impr_B_n24_off09",
         array_count=24, slab_length_um=55.0, slab_span_y_um=34.0,
         array_pitch_um=1.20, output_pitch_um=1.60, output_offset_um=0.90),

    # Config C: N=24, wider pitch — give adjacent channels more room
    dict(label="impr_C_n24_p18",
         array_count=24, slab_length_um=55.0, slab_span_y_um=34.0,
         array_pitch_um=1.20, output_pitch_um=1.80, output_offset_um=0.90),

    # Config D: N=24 + longer FPR (70 μm vs 55 μm)
    # Longer FPR increases linear dispersion → channels spread further apart.
    # Output pitch and offset scaled proportionally: 1.6*(70/55)=2.04→2.0,
    # offset 0.6*(70/55)=0.76→0.8.
    dict(label="impr_D_n24_fpr70",
         array_count=24, slab_length_um=70.0, slab_span_y_um=36.0,
         array_pitch_um=1.20, output_pitch_um=2.00, output_offset_um=0.80),
]


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    for d in (TABLES, ASSETS, DOCS, DATA_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: build all sims, estimate costs (upload once per sim) ─────────
    tasks: list[dict] = []
    total_est = 0.0
    print("Estimating credit costs …")
    for cfg in CONFIGS:
        for wl_nm in CHANNEL_WAVELENGTHS_NM:
            sim = build_simulation(
                wavelength_nm=wl_nm,
                array_count=cfg["array_count"],
                slab_length_um=cfg["slab_length_um"],
                slab_span_y_um=cfg["slab_span_y_um"],
                array_pitch_um=cfg["array_pitch_um"],
                output_pitch_um=cfg["output_pitch_um"],
                output_offset_um=cfg["output_offset_um"],
            )
            task_name = f"{cfg['label']}_{wl_nm:.1f}nm"
            task_id = web.upload(sim, task_name=task_name,
                                 folder_name=TASK_FOLDER, verbose=False)
            est = float(web.estimate_cost(task_id, verbose=False))
            total_est += est
            tasks.append(dict(cfg=cfg, wl_nm=wl_nm, sim=sim,
                              task_name=task_name, task_id=task_id, est=est))
            print(f"  {task_name}: {est:.4f} FC")

    print(f"\nTotal estimated cost: {total_est:.4f} FC")
    if total_est > MAX_CREDITS:
        raise RuntimeError(
            f"Estimated {total_est:.3f} FC exceeds budget {MAX_CREDITS} FC. "
            "Reduce configs or wavelengths."
        )

    # ── Phase 2: run all tasks (re-use already-uploaded task IDs) ─────────────
    rows: list[dict] = []
    for t in tasks:
        cfg      = t["cfg"]
        wl_nm    = t["wl_nm"]
        out_path = DATA_DIR / f"{t['task_name']}.hdf5"
        print(f"\nRunning {t['task_name']} …")
        sim_data = web.run(
            t["sim"], task_name=t["task_name"],
            folder_name=TASK_FOLDER, path=out_path, verbose=True,
        )
        fluxes              = extract_fluxes(sim_data)
        dom_frac, s2f, grade = routing_quality(fluxes)
        dom_out = int(np.argmax(fluxes)) + 1
        rows.append(dict(
            label          = cfg["label"],
            wavelength_nm  = wl_nm,
            array_count    = cfg["array_count"],
            slab_length_um = cfg["slab_length_um"],
            array_pitch_um = cfg["array_pitch_um"],
            output_pitch_um= cfg["output_pitch_um"],
            output_offset_um=cfg["output_offset_um"],
            estimated_cost = t["est"],
            dominant_output= dom_out,
            dominant_fraction=dom_frac,
            second_to_first= s2f,
            quality        = grade,
            out_1=fluxes[0], out_2=fluxes[1],
            out_3=fluxes[2], out_4=fluxes[3],
        ))
        print(f"  → dom_out={dom_out}, dom_frac={dom_frac:.3f}, "
              f"s2f={s2f:.3f}, quality={grade}")

    # ── Phase 3: save CSV ──────────────────────────────────────────────────────
    fieldnames = [
        "label", "wavelength_nm", "array_count", "slab_length_um",
        "array_pitch_um", "output_pitch_um", "output_offset_um",
        "estimated_cost", "dominant_output", "dominant_fraction",
        "second_to_first", "quality",
        "out_1", "out_2", "out_3", "out_4",
    ]
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)
    print(f"\nResults saved to {RESULTS_CSV}")

    # ── Phase 4: per-config summary ────────────────────────────────────────────
    import pandas as pd
    df = pd.DataFrame(rows)
    summary_lines = [
        "# AWG Improved Design Results",
        "",
        "## Improvement rationale",
        "Previous scans all used N=16 array arms, giving array-factor 3-dB BW = FSR/16 ≈ 1.2 nm.",
        "Channel spacing is 1.6 nm, so adjacent channels heavily overlap.",
        "N=24 reduces the 3-dB BW to ≈ 0.8 nm, well inside the channel spacing.",
        "A longer FPR (70 μm) further increases linear dispersion.",
        "",
        "## Quality rubric",
        "- good:    dom_frac ≥ 0.60, s2f ≤ 0.50",
        "- general: dom_frac ≥ 0.40, s2f ≤ 0.80",
        "- passing: dom_frac ≥ 0.30, s2f ≤ 0.95",
        "- poor:    below passing",
        "",
        "## Per-config results",
    ]
    for cfg in CONFIGS:
        sub = df[df["label"] == cfg["label"]]
        avg_dom = sub["dominant_fraction"].mean()
        min_dom = sub["dominant_fraction"].min()
        avg_s2f = sub["second_to_first"].mean()
        max_s2f = sub["second_to_first"].max()
        grades    = sub["quality"].tolist()
        agg_grade = ("passing"
                     if all(g in ("good", "general", "passing") for g in grades)
                        and sub["dominant_fraction"].min() >= 0.30
                     else "poor")
        summary_lines += [
            "",
            f"### {cfg['label']}",
            f"  N={cfg['array_count']}, FPR={cfg['slab_length_um']} μm, "
            f"array_pitch={cfg['array_pitch_um']}, "
            f"output_pitch={cfg['output_pitch_um']}, "
            f"offset={cfg['output_offset_um']}",
            f"  avg dom_frac={avg_dom:.4f}, min dom_frac={min_dom:.4f}",
            f"  avg s2f={avg_s2f:.4f},     max s2f={max_s2f:.4f}",
            "",
            "  | λ (nm) | dom_out | dom_frac | s2f | quality |",
            "  | ---: | ---: | ---: | ---: | --- |",
        ]
        for _, row in sub.sort_values("wavelength_nm").iterrows():
            summary_lines.append(
                f"  | {row.wavelength_nm:.1f} | {int(row.dominant_output)} "
                f"| {row.dominant_fraction:.4f} | {row.second_to_first:.4f} "
                f"| {row.quality} |"
            )

    # Comparison with best prior result
    summary_lines += [
        "",
        "## Comparison with prior best (N=16, FPR=55, 1.20/1.60/0.60)",
        "| Metric | Prior best | Best new config |",
        "| --- | --- | --- |",
    ]
    best_new = df.groupby("label")["dominant_fraction"].mean().idxmax()
    sub_new  = df[df["label"] == best_new]
    prior_avg_dom = 0.3683   # from seed_local_best in global opt
    prior_max_s2f = 0.9320
    new_avg_dom   = sub_new["dominant_fraction"].mean()
    new_max_s2f   = sub_new["second_to_first"].max()
    summary_lines += [
        f"| avg dom_frac (4-channel) | {prior_avg_dom:.4f} | {new_avg_dom:.4f} |",
        f"| max s2f (worst channel)  | {prior_max_s2f:.4f} | {new_max_s2f:.4f} |",
        f"| best new config label    | — | {best_new} |",
    ]

    SUMMARY_MD.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Summary saved to {SUMMARY_MD}")

    # ── Phase 5: plot ──────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, len(CONFIGS), figsize=(4.5 * len(CONFIGS), 4.2),
                             sharey=True)
    if len(CONFIGS) == 1:
        axes = [axes]
    colors = ["#0b3c5d", "#1d6f42", "#c07a00", "#8c2f39"]
    for ax, cfg in zip(axes, CONFIGS):
        sub = df[df["label"] == cfg["label"]].sort_values("wavelength_nm")
        x = sub["wavelength_nm"].values
        for i, col in enumerate(colors):
            ax.bar(x + (i - 1.5) * 0.25, sub[f"out_{i+1}"].values,
                   width=0.22, color=col, alpha=0.82, label=f"out_{i+1}")
        ax.set_title(f"{cfg['label']}\nN={cfg['array_count']}, FPR={cfg['slab_length_um']} μm",
                     fontsize=9)
        ax.set_xlabel("λ (nm)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Output flux (a.u.)", fontsize=8)
    axes[-1].legend(fontsize=7, frameon=False)
    plt.suptitle("Improved AWG Design: N=24 arms vs N=16 baseline",
                 fontsize=11, y=1.02)
    plt.tight_layout()
    fig.savefig(PLOT_PNG, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {PLOT_PNG}")
    print(f"\nTotal estimated cost used: {sum(t['est'] for t in tasks):.4f} FC")


if __name__ == "__main__":
    main()
