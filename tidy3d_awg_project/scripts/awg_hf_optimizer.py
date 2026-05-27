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
import pandas as pd

try:
    from .awg_high_fidelity_validation import (
        ASSETS,
        CHANNEL_WAVELENGTHS_NM,
        DATA_DIR,
        MAX_TOTAL_ESTIMATED_CREDITS,
        ROOT,
        TASK_FOLDER,
        build_simulation,
        classify_routing_quality,
        estimate_credit,
        extract_fluxes,
        routing_metrics,
        run_simulation,
    )
except ImportError:
    from awg_high_fidelity_validation import (
        ASSETS,
        CHANNEL_WAVELENGTHS_NM,
        DATA_DIR,
        MAX_TOTAL_ESTIMATED_CREDITS,
        ROOT,
        TASK_FOLDER,
        build_simulation,
        classify_routing_quality,
        estimate_credit,
        extract_fluxes,
        routing_metrics,
        run_simulation,
    )


OPT_RESULTS_CSV = ROOT / "results" / "tables" / "awg_hf_optimization_results.csv"
OPT_SUMMARY_MD = ROOT / "docs" / "AWG_HF_OPTIMIZATION_SUMMARY.md"
OPT_PLOT_PNG = ASSETS / "awg_hf_optimization_scan.png"
VERIFY_PLOT_PNG = ASSETS / "awg_hf_optimization_verification.png"
TARGET_WAVELENGTH_NM = 1550.8
MAX_OPTIMIZATION_ESTIMATED_CREDITS = 1.2


def optimization_score(dominant_fraction: float, second_to_first: float) -> float:
    return dominant_fraction - 0.35 * second_to_first


def candidate_configs() -> list[dict[str, float | str]]:
    return [
        {"label": "optscan_baseline", "array_pitch_um": 1.50, "output_pitch_um": 2.00, "output_offset_um": 0.00},
        {"label": "optscan_a", "array_pitch_um": 1.30, "output_pitch_um": 1.80, "output_offset_um": 0.30},
        {"label": "optscan_b", "array_pitch_um": 1.20, "output_pitch_um": 1.70, "output_offset_um": 0.40},
        {"label": "optscan_c", "array_pitch_um": 1.20, "output_pitch_um": 1.60, "output_offset_um": 0.60},
        {"label": "optscan_d", "array_pitch_um": 1.15, "output_pitch_um": 1.55, "output_offset_um": 0.70},
        {"label": "optscan_e", "array_pitch_um": 1.10, "output_pitch_um": 1.50, "output_offset_um": 0.80},
        {"label": "optscan_f", "array_pitch_um": 1.05, "output_pitch_um": 1.45, "output_offset_um": 0.90},
        {"label": "optscan_g", "array_pitch_um": 1.00, "output_pitch_um": 1.40, "output_offset_um": 1.00},
        {"label": "optscan_h", "array_pitch_um": 1.00, "output_pitch_um": 1.35, "output_offset_um": 1.10},
    ]


def write_results(rows: list[dict[str, float | str]]) -> None:
    OPT_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "stage",
        "label",
        "wavelength_nm",
        "array_pitch_um",
        "output_pitch_um",
        "output_offset_um",
        "estimated_cost",
        "dominant_output",
        "dominant_fraction",
        "second_to_first",
        "quality",
        "score",
    ]
    fieldnames.extend([f"out_{idx}" for idx in range(1, 5)])
    with OPT_RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_scan(results_df: pd.DataFrame) -> None:
    ASSETS.mkdir(exist_ok=True)
    scan_df = results_df[results_df["stage"] == "scan"].copy()
    scan_df = scan_df.sort_values("score", ascending=False)

    plt.figure(figsize=(9.0, 4.8))
    x = range(len(scan_df))
    plt.bar(x, scan_df["dominant_fraction"], color="#0b3c5d", label="Dominant fraction")
    plt.plot(x, scan_df["second_to_first"], color="#8c2f39", marker="o", linewidth=1.8, label="Second / first")
    plt.xticks(list(x), scan_df["label"], rotation=30, ha="right")
    plt.ylim(0, 1.05)
    plt.ylabel("Metric value")
    plt.title("FDTD Optimization Scan at 1550.8 nm")
    plt.grid(True, axis="y", alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(OPT_PLOT_PNG, dpi=220)
    plt.close()


def plot_verification(results_df: pd.DataFrame) -> None:
    verify_df = results_df[results_df["stage"] == "verify"].copy()
    plt.figure(figsize=(8.0, 4.8))
    plt.plot(verify_df["wavelength_nm"], verify_df["dominant_fraction"], marker="o", linewidth=2.0, color="#1d6f42")
    plt.plot(verify_df["wavelength_nm"], verify_df["second_to_first"], marker="s", linewidth=2.0, color="#8c2f39")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Metric value")
    plt.title("Best-Config Verification Across 4 Channels")
    plt.grid(True, alpha=0.25)
    plt.legend(["Dominant fraction", "Second / first"], frameon=False)
    plt.tight_layout()
    plt.savefig(VERIFY_PLOT_PNG, dpi=220)
    plt.close()


def write_summary(results_df: pd.DataFrame) -> None:
    OPT_SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    scan_df = results_df[results_df["stage"] == "scan"].copy().sort_values("score", ascending=False)
    verify_df = results_df[results_df["stage"] == "verify"].copy().sort_values("wavelength_nm")
    best = scan_df.iloc[0]

    lines = [
        "# AWG High-Fidelity Optimization Summary",
        "",
        "## Quality Rubric",
        "",
        "- good: dominant output fraction >= 0.60 and second/first <= 0.50",
        "- general: dominant output fraction >= 0.40 and second/first <= 0.80",
        "- passing: dominant output fraction >= 0.30 and second/first <= 0.95",
        "- poor: anything below the passing threshold",
        "",
        "Dominant output fraction measures how much of the detected output flux stays in the strongest port.",
        "Second/first measures how close the second-strongest port is to the strongest one, so lower is better.",
        "",
        "## Best Scan Result",
        "",
        f"- Best configuration: `{best['label']}`",
        f"- Array pitch: {best['array_pitch_um']:.2f} um",
        f"- Output pitch: {best['output_pitch_um']:.2f} um",
        f"- Output offset: {best['output_offset_um']:.2f} um",
        f"- Dominant output fraction at {best['wavelength_nm']:.1f} nm: {best['dominant_fraction']:.4f}",
        f"- Second/first ratio at {best['wavelength_nm']:.1f} nm: {best['second_to_first']:.4f}",
        f"- Quality classification: {best['quality']}",
        "",
        "## Full Scan Ranking",
        "",
        "| Label | Array pitch (um) | Output pitch (um) | Offset (um) | Dominant fraction | Second/first | Quality |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for row in scan_df.itertuples(index=False):
        lines.append(
            f"| {row.label} | {row.array_pitch_um:.2f} | {row.output_pitch_um:.2f} | {row.output_offset_um:.2f} | "
            f"{row.dominant_fraction:.4f} | {row.second_to_first:.4f} | {row.quality} |"
        )

    lines.extend(["", "## Best-Config Verification", "", "| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |", "| ---: | ---: | ---: | ---: | --- |"])

    for row in verify_df.itertuples(index=False):
        lines.append(
            f"| {row.wavelength_nm:.1f} | {int(row.dominant_output)} | {row.dominant_fraction:.4f} | {row.second_to_first:.4f} | {row.quality} |"
        )

    OPT_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_row(stage: str, label: str, wavelength_nm: float, cfg: dict[str, float | str], estimated_cost: float, fluxes: list[float]) -> dict[str, float | str]:
    metrics = routing_metrics(fluxes)
    row = {
        "stage": stage,
        "label": label,
        "wavelength_nm": wavelength_nm,
        "array_pitch_um": float(cfg["array_pitch_um"]),
        "output_pitch_um": float(cfg["output_pitch_um"]),
        "output_offset_um": float(cfg["output_offset_um"]),
        "estimated_cost": estimated_cost,
        "dominant_output": int(max(range(len(fluxes)), key=lambda idx: fluxes[idx]) + 1),
        "dominant_fraction": metrics["dominant_fraction"],
        "second_to_first": metrics["second_to_first"],
        "quality": classify_routing_quality(metrics["dominant_fraction"], metrics["second_to_first"]),
        "score": optimization_score(metrics["dominant_fraction"], metrics["second_to_first"]),
    }
    for idx in range(4):
        row[f"out_{idx+1}"] = float(fluxes[idx])
    return row


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, float | str]] = []
    estimated_runs: list[tuple[str, dict[str, float | str], float]] = []
    total_estimated_cost = 0.0

    for cfg in candidate_configs():
        sim = build_simulation(
            wavelength_nm=TARGET_WAVELENGTH_NM,
            output_count=4,
            delta_temp_k=0.0,
            array_pitch_um=float(cfg["array_pitch_um"]),
            output_pitch_um=float(cfg["output_pitch_um"]),
            output_offset_um=float(cfg["output_offset_um"]),
            include_field_monitor=False,
        )
        task_name = str(cfg["label"])
        _, estimate = estimate_credit(sim, task_name)
        total_estimated_cost += estimate
        estimated_runs.append((task_name, cfg, estimate))
        print(f"Estimated cost for {task_name}: {estimate:.4f} FlexCredit")

    verification_estimate = 0.0
    probe_sim = build_simulation(
        wavelength_nm=CHANNEL_WAVELENGTHS_NM[0],
        output_count=4,
        array_pitch_um=float(candidate_configs()[0]["array_pitch_um"]),
        output_pitch_um=float(candidate_configs()[0]["output_pitch_um"]),
        output_offset_um=float(candidate_configs()[0]["output_offset_um"]),
    )
    _, probe_estimate = estimate_credit(probe_sim, "optverify_probe")
    verification_estimate = probe_estimate * len(CHANNEL_WAVELENGTHS_NM)
    total_estimated_cost += verification_estimate

    print(f"Estimated verification cost for best config: {verification_estimate:.4f} FlexCredit")
    print(f"Total estimated optimization cost: {total_estimated_cost:.4f} FlexCredit")
    if total_estimated_cost > min(MAX_TOTAL_ESTIMATED_CREDITS, MAX_OPTIMIZATION_ESTIMATED_CREDITS):
        raise RuntimeError(
            f"Estimated optimization cost {total_estimated_cost:.4f} exceeds limit "
            f"{min(MAX_TOTAL_ESTIMATED_CREDITS, MAX_OPTIMIZATION_ESTIMATED_CREDITS):.4f}."
        )

    scan_rows: list[dict[str, float | str]] = []
    for task_name, cfg, estimate in estimated_runs:
        sim = build_simulation(
            wavelength_nm=TARGET_WAVELENGTH_NM,
            output_count=4,
            delta_temp_k=0.0,
            array_pitch_um=float(cfg["array_pitch_um"]),
            output_pitch_um=float(cfg["output_pitch_um"]),
            output_offset_um=float(cfg["output_offset_um"]),
            include_field_monitor=False,
        )
        out_path = DATA_DIR / f"{task_name}.hdf5"
        sim_data = run_simulation(sim, task_name=task_name, out_path=out_path)
        fluxes = extract_fluxes(sim_data, output_count=4)
        row = make_row("scan", task_name, TARGET_WAVELENGTH_NM, cfg, estimate, fluxes)
        scan_rows.append(row)
        rows.append(row)
        print(
            f"{task_name}: dominant_fraction={row['dominant_fraction']:.4f}, "
            f"second/first={row['second_to_first']:.4f}, quality={row['quality']}"
        )

    best_row = max(scan_rows, key=lambda item: (float(item["score"]), float(item["dominant_fraction"]), -float(item["second_to_first"])))
    best_cfg = {
        "array_pitch_um": float(best_row["array_pitch_um"]),
        "output_pitch_um": float(best_row["output_pitch_um"]),
        "output_offset_um": float(best_row["output_offset_um"]),
    }
    print(f"Best config from scan: {best_cfg}")

    for wavelength_nm in CHANNEL_WAVELENGTHS_NM:
        label = f"optverify_{wavelength_nm:.1f}nm"
        sim = build_simulation(
            wavelength_nm=wavelength_nm,
            output_count=4,
            delta_temp_k=0.0,
            array_pitch_um=best_cfg["array_pitch_um"],
            output_pitch_um=best_cfg["output_pitch_um"],
            output_offset_um=best_cfg["output_offset_um"],
            include_field_monitor=False,
        )
        out_path = DATA_DIR / f"{label}.hdf5"
        sim_data = run_simulation(sim, task_name=label, out_path=out_path)
        fluxes = extract_fluxes(sim_data, output_count=4)
        row = make_row("verify", label, wavelength_nm, best_cfg, probe_estimate, fluxes)
        rows.append(row)
        print(
            f"{label}: dominant_fraction={row['dominant_fraction']:.4f}, "
            f"second/first={row['second_to_first']:.4f}, quality={row['quality']}"
        )

    results_df = pd.DataFrame(rows)
    write_results(rows)
    plot_scan(results_df)
    plot_verification(results_df)
    write_summary(results_df)
    print(f"Saved optimization results to {OPT_RESULTS_CSV}")
    print(f"Saved optimization summary to {OPT_SUMMARY_MD}")


if __name__ == "__main__":
    main()
