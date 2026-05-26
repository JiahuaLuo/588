from __future__ import annotations

import csv
import math
import os
from pathlib import Path

MPLCONFIGDIR = Path(__file__).resolve().parent / ".mplconfig"
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tidy3d as td
import tidy3d.web as web
from tidy3d.constants import C_0


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "report_assets"
DATA_DIR = ROOT / "data" / "high_fidelity_awg"
RESULTS_CSV = ROOT / "awg_high_fidelity_results.csv"
SUMMARY_MD = ROOT / "AWG_HIGH_FIDELITY_SUMMARY.md"
SPECTRA_PNG = ASSETS / "awg_high_fidelity_transmission.png"

CHANNEL_WAVELENGTHS_NM = [1547.6, 1549.2, 1550.8, 1552.4]
MAX_TOTAL_ESTIMATED_CREDITS = 4.0
TASK_FOLDER = "ee588_awg"

# Material and baseline device values.
CORE_N = 3.48
CLAD_N = 1.44
WG_WIDTH_UM = 0.50
WG_HEIGHT_UM = 0.22
LAMBDA0_UM = 1.55
NEFF0 = 2.444579740420668
NGROUP0 = 4.051219463271623
DELTA_LENGTH_UM = 30.990668646375973

# Output-FPR validation geometry.
ARRAY_COUNT = 16
ARRAY_PITCH_UM = 1.5
OUTPUT_Y_UM = [-3.0, -1.0, 1.0, 3.0]
INPUT_STUB_UM = 8.0
SLAB_LENGTH_UM = 55.0
OUTPUT_STUB_UM = 14.0
SLAB_SPAN_Y_UM = 34.0
SIM_SIZE_Z_UM = 0.0
PML_MARGIN_X_UM = 5.0
PML_MARGIN_Y_UM = 3.0
MIN_STEPS_PER_WVL = 18


def neff_at_wavelength_um(wavelength_um: float, delta_temp_k: float = 0.0) -> float:
    # Use n_group = n_eff - lambda * dn_eff/dlambda to build a local linear model.
    dneff_dlambda = (NEFF0 - NGROUP0) / LAMBDA0_UM
    neff = NEFF0 + dneff_dlambda * (wavelength_um - LAMBDA0_UM)
    dneff_dtemp = 1.86e-4
    return float(neff + dneff_dtemp * delta_temp_k)


def array_y_positions(array_count: int = ARRAY_COUNT, array_pitch_um: float = ARRAY_PITCH_UM) -> np.ndarray:
    indices = np.arange(array_count)
    center = (array_count - 1) / 2.0
    return (indices - center) * array_pitch_um


def phase_for_arm(arm_index: int, wavelength_um: float, delta_temp_k: float = 0.0) -> float:
    beta = 2.0 * np.pi * neff_at_wavelength_um(wavelength_um, delta_temp_k) / wavelength_um
    return float(beta * arm_index * DELTA_LENGTH_UM)


def build_simulation(
    wavelength_nm: float,
    output_count: int = 4,
    delta_temp_k: float = 0.0,
    array_pitch_um: float = ARRAY_PITCH_UM,
    output_pitch_um: float = 2.0,
    output_offset_um: float = 0.0,
    include_field_monitor: bool = False,
) -> td.Simulation:
    wavelength_um = wavelength_nm / 1000.0
    freq0 = C_0 / wavelength_um
    fwidth = freq0 / 80.0

    # Use a 2D effective-index device model to keep the cloud FDTD cost tractable.
    clad = td.Medium(name="SiO2_eff", permittivity=CLAD_N**2)
    core = td.Medium(name="strip_eff", permittivity=neff_at_wavelength_um(wavelength_um, delta_temp_k) ** 2)

    arr_y = array_y_positions(array_pitch_um=array_pitch_um)
    out_indices = np.arange(output_count)
    out_center = (output_count - 1) / 2.0
    out_y = (out_indices - out_center) * output_pitch_um + output_offset_um

    x_array_center = -SLAB_LENGTH_UM / 2.0
    x_output_start = SLAB_LENGTH_UM / 2.0
    x_output_end = x_output_start + OUTPUT_STUB_UM
    sim_size_x = INPUT_STUB_UM + SLAB_LENGTH_UM + OUTPUT_STUB_UM + 2.0 * PML_MARGIN_X_UM
    sim_size_y = SLAB_SPAN_Y_UM + 2.0 * PML_MARGIN_Y_UM

    structures: list[td.Structure] = [
        td.Structure(
            geometry=td.Box(center=(0.0, 0.0, 0.0), size=(SLAB_LENGTH_UM, SLAB_SPAN_Y_UM, td.inf)),
            medium=core,
            name="slab_fpr",
        )
    ]

    for idx, y_um in enumerate(arr_y):
        structures.append(
            td.Structure(
                geometry=td.Box(
                    center=(x_array_center - INPUT_STUB_UM / 2.0, float(y_um), 0.0),
                    size=(INPUT_STUB_UM, WG_WIDTH_UM, td.inf),
                ),
                medium=core,
                name=f"array_stub_{idx:02d}",
            )
        )

    for idx, y_um in enumerate(out_y):
        structures.append(
            td.Structure(
                geometry=td.Box(
                    center=(x_output_start + OUTPUT_STUB_UM / 2.0, float(y_um), 0.0),
                    size=(OUTPUT_STUB_UM, WG_WIDTH_UM, td.inf),
                ),
                medium=core,
                name=f"output_wg_{idx+1}",
            )
        )

    sources: list[td.ModeSource] = []
    source_plane_x = x_array_center - INPUT_STUB_UM * 0.55
    for arm_index, y_um in enumerate(arr_y):
        phase = phase_for_arm(arm_index, wavelength_um, delta_temp_k)
        sources.append(
            td.ModeSource(
                name=f"src_{arm_index:02d}",
                center=(source_plane_x, float(y_um), 0.0),
                size=(0.0, 1.2, td.inf),
                source_time=td.GaussianPulse(freq0=freq0, fwidth=fwidth, phase=phase),
                direction="+",
                mode_spec=td.ModeSpec(num_modes=1, target_neff=neff_at_wavelength_um(wavelength_um, delta_temp_k)),
                mode_index=0,
            )
        )

    monitors: list[td.FluxMonitor | td.FieldMonitor] = []
    flux_plane_x = x_output_start + OUTPUT_STUB_UM * 0.65
    for idx, y_um in enumerate(out_y):
        monitors.append(
            td.FluxMonitor(
                name=f"out_{idx+1}",
                center=(flux_plane_x, float(y_um), 0.0),
                size=(0.0, 1.4, td.inf),
                freqs=[freq0],
            )
        )

    if include_field_monitor:
        monitors.append(
            td.FieldMonitor(
                name="field_xy",
                center=(0.0, 0.0, 0.0),
                size=(SLAB_LENGTH_UM + 10.0, SLAB_SPAN_Y_UM + 4.0, 0.0),
                freqs=[freq0],
                fields=["Ex", "Ey", "Hz"],
            )
        )

    sim = td.Simulation(
        center=(0.0, 0.0, 0.0),
        size=(sim_size_x, sim_size_y, SIM_SIZE_Z_UM),
        run_time=1.5e-12,
        medium=clad,
        structures=structures,
        sources=sources,
        monitors=monitors,
        boundary_spec=td.BoundarySpec(
            x=td.Boundary.pml(),
            y=td.Boundary.pml(),
            z=td.Boundary.periodic(),
        ),
        grid_spec=td.GridSpec.auto(min_steps_per_wvl=MIN_STEPS_PER_WVL, wavelength=wavelength_um),
        shutoff=1e-5,
    )
    return sim


def estimate_credit(sim: td.Simulation, task_name: str) -> tuple[str, float]:
    task_id = web.upload(sim, task_name=task_name, folder_name=TASK_FOLDER, verbose=False)
    estimate = web.estimate_cost(task_id, verbose=False)
    return task_id, float(estimate)


def run_simulation(sim: td.Simulation, task_name: str, out_path: Path) -> td.SimulationData:
    return web.run(sim, task_name=task_name, folder_name=TASK_FOLDER, path=out_path, verbose=True)


def extract_fluxes(sim_data: td.SimulationData, output_count: int = 4) -> list[float]:
    values = []
    for idx in range(output_count):
        flux = sim_data[f"out_{idx+1}"].flux
        values.append(float(np.real(np.array(flux)).reshape(-1)[0]))
    return values


def save_results(rows: list[dict[str, float | str]]) -> None:
    fieldnames = [
        "label",
        "wavelength_nm",
        "temperature_shift_K",
        "output_count",
        "array_pitch_um",
        "output_pitch_um",
        "output_offset_um",
        "estimated_cost",
        "dominant_output",
    ]
    fieldnames.extend([f"out_{idx}" for idx in range(1, 9)])
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_results(results_df: pd.DataFrame) -> None:
    ASSETS.mkdir(exist_ok=True)
    plt.figure(figsize=(8.0, 4.8))
    baseline = results_df[results_df["label"].str.startswith("hf_4ch_")]
    for idx, color in zip(range(4), ["#0b3c5d", "#1d6f42", "#c07a00", "#8c2f39"]):
        plt.plot(
            baseline["wavelength_nm"],
            baseline[f"out_{idx+1}"],
            marker="o",
            linewidth=1.8,
            color=color,
            label=f"Output {idx+1}",
        )
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Output flux (a.u.)")
    plt.title("High-Fidelity Output-FPR Validation")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(SPECTRA_PNG, dpi=220)
    plt.close()


def write_summary(results_df: pd.DataFrame) -> None:
    lines = [
        "# AWG High-Fidelity Validation Summary",
        "",
        "This file summarizes the cloud-run Tidy3D validation of the simplified AWG output FPR stage.",
        "The model is more physical than the local array-factor script because it uses actual FDTD propagation through the slab/output section, while still avoiding the full 2 mm-scale array-arm meander geometry.",
        "",
        "## Baseline 4-Channel Runs",
        "",
    ]

    baseline = results_df[results_df["label"].str.startswith("hf_4ch_")]
    for row in baseline.itertuples(index=False):
        flux_values = [getattr(row, f"out_{idx}") for idx in range(1, int(row.output_count) + 1)]
        flux_text = ", ".join(f"{float(val):.4g}" for val in flux_values if val == val)
        lines.append(
            f"- {row.wavelength_nm:.1f} nm -> dominant output {int(row.dominant_output)}; fluxes = [{flux_text}]"
        )

    lines.extend(["", "## Stretch-Goal Attempts", ""])
    for prefix, desc in [
        ("stretch_8ch_", "8-channel aperture/output layout"),
        ("stretch_temp_", "temperature dependence"),
        ("stretch_opt_", "pitch/offset optimization"),
    ]:
        subset = results_df[results_df["label"].str.startswith(prefix)]
        if subset.empty:
            lines.append(f"- {desc}: not run.")
            continue
        lines.append(f"- {desc}:")
        for row in subset.itertuples(index=False):
            lines.append(
                f"  - {row.label}: {row.wavelength_nm:.1f} nm, dominant output {int(row.dominant_output)}, "
                f"estimated cost {row.estimated_cost:.4f}"
            )

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, float | str]] = []

    baseline_configs = [
        {"label": f"hf_4ch_{wl:.1f}nm", "wavelength_nm": wl, "delta_temp_k": 0.0, "output_count": 4, "array_pitch_um": 1.5, "output_pitch_um": 2.0, "output_offset_um": 0.0}
        for wl in CHANNEL_WAVELENGTHS_NM
    ]
    stretch_configs = [
        {"label": "stretch_8ch_1550.0nm", "wavelength_nm": 1550.0, "delta_temp_k": 0.0, "output_count": 8, "array_pitch_um": 1.3, "output_pitch_um": 1.5, "output_offset_um": 0.0},
        {"label": "stretch_temp_1560.0nm_plus40K", "wavelength_nm": 1550.8, "delta_temp_k": 40.0, "output_count": 4, "array_pitch_um": 1.5, "output_pitch_um": 2.0, "output_offset_um": 0.0},
        {"label": "stretch_opt_1550.8nm", "wavelength_nm": 1550.8, "delta_temp_k": 0.0, "output_count": 4, "array_pitch_um": 1.2, "output_pitch_um": 1.6, "output_offset_um": 0.6},
    ]
    all_configs = baseline_configs + stretch_configs

    estimated_tasks: list[tuple[dict[str, float | str], td.Simulation, str, float]] = []
    total_estimated = 0.0

    for idx, cfg in enumerate(all_configs):
        sim = build_simulation(
            wavelength_nm=float(cfg["wavelength_nm"]),
            output_count=int(cfg["output_count"]),
            delta_temp_k=float(cfg["delta_temp_k"]),
            array_pitch_um=float(cfg["array_pitch_um"]),
            output_pitch_um=float(cfg["output_pitch_um"]),
            output_offset_um=float(cfg["output_offset_um"]),
            include_field_monitor=(idx == 0),
        )
        task_name = str(cfg["label"])
        task_id, estimate = estimate_credit(sim, task_name)
        total_estimated += estimate
        estimated_tasks.append((cfg, sim, task_id, estimate))
        print(f"Estimated cost for {task_name}: {estimate:.4f} FlexCredit")

    print(f"Total estimated cost: {total_estimated:.4f} FlexCredit")
    if total_estimated > MAX_TOTAL_ESTIMATED_CREDITS:
        raise RuntimeError(
            f"Estimated total cost {total_estimated:.4f} exceeds limit {MAX_TOTAL_ESTIMATED_CREDITS:.4f}. "
            "Tighten the geometry or reduce the run set before submitting."
        )

    for cfg, sim, task_id, estimate in estimated_tasks:
        _ = task_id
        output_count = int(cfg["output_count"])
        out_path = DATA_DIR / f"{cfg['label']}.hdf5"
        sim_data = run_simulation(sim, task_name=str(cfg["label"]), out_path=out_path)
        fluxes = extract_fluxes(sim_data, output_count=output_count)
        dominant_output = int(np.argmax(fluxes) + 1)
        row = {
            "label": cfg["label"],
            "wavelength_nm": float(cfg["wavelength_nm"]),
            "temperature_shift_K": float(cfg["delta_temp_k"]),
            "output_count": output_count,
            "array_pitch_um": float(cfg["array_pitch_um"]),
            "output_pitch_um": float(cfg["output_pitch_um"]),
            "output_offset_um": float(cfg["output_offset_um"]),
            "estimated_cost": estimate,
            "dominant_output": dominant_output,
        }
        for idx in range(8):
            row[f"out_{idx+1}"] = fluxes[idx] if idx < len(fluxes) else ""
        rows.append(row)
        print(f"Completed {cfg['label']}: dominant output = {dominant_output}, fluxes = {fluxes[:4]}")

    results_df = pd.DataFrame(rows)
    save_results(rows)
    plot_results(results_df)
    write_summary(results_df)
    print(f"Saved results to {RESULTS_CSV}")
    print(f"Saved summary to {SUMMARY_MD}")
    print(f"Saved plot to {SPECTRA_PNG}")


if __name__ == "__main__":
    main()
