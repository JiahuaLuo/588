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
import pandas as pd

try:
    from .awg_high_fidelity_validation import (
        ARRAY_COUNT,
        ARRAY_PITCH_UM,
        CHANNEL_WAVELENGTHS_NM,
        DELTA_LENGTH_UM,
        LAMBDA0_UM,
        NEFF0,
        NGROUP0,
        OUTPUT_Y_UM,
        SLAB_LENGTH_UM,
        array_y_positions,
        classify_routing_quality,
        neff_at_wavelength_um,
        routing_metrics,
    )
except ImportError:
    from awg_high_fidelity_validation import (
        ARRAY_COUNT,
        ARRAY_PITCH_UM,
        CHANNEL_WAVELENGTHS_NM,
        DELTA_LENGTH_UM,
        LAMBDA0_UM,
        NEFF0,
        NGROUP0,
        OUTPUT_Y_UM,
        SLAB_LENGTH_UM,
        array_y_positions,
        classify_routing_quality,
        neff_at_wavelength_um,
        routing_metrics,
    )


ASSETS = ROOT / "results" / "figures"
TABLES = ROOT / "results" / "tables"
DOCS = ROOT / "docs"
COARSE_RESULTS_CSV = TABLES / "awg_coarse_to_fine_candidates.csv"
COARSE_SUMMARY_MD = DOCS / "AWG_COARSE_TO_FINE_SUMMARY.md"
COARSE_SCAN_PNG = ASSETS / "awg_coarse_scan_ranking.png"
COARSE_CHANNEL_PNG = ASSETS / "awg_coarse_best_channels.png"

FPR_LENGTH_OPTIONS_UM = [50.0, 55.0, 60.0]
ARRAY_PITCH_OPTIONS_UM = [1.05, 1.10, 1.15, 1.20, 1.25]
OUTPUT_PITCH_OPTIONS_UM = [1.45, 1.50, 1.55, 1.60, 1.65]
OUTPUT_OFFSET_OPTIONS_UM = [0.45, 0.50, 0.55, 0.60, 0.65]
TOP_CANDIDATE_COUNT = 5
INPUT_PHASE_TILT_UM = 1.2


def phase_for_arm(arm_index: int, wavelength_um: float) -> float:
    beta = 2.0 * np.pi * neff_at_wavelength_um(wavelength_um, 0.0) / wavelength_um
    return float(beta * arm_index * DELTA_LENGTH_UM)


def output_positions(output_pitch_um: float, output_offset_um: float, output_count: int = 4) -> np.ndarray:
    out_indices = np.arange(output_count)
    out_center = (output_count - 1) / 2.0
    return (out_indices - out_center) * output_pitch_um + output_offset_um


def local_fluxes_for_config(
    wavelength_nm: float,
    array_pitch_um: float,
    output_pitch_um: float,
    output_offset_um: float,
    fpr_length_um: float,
) -> list[float]:
    wavelength_um = wavelength_nm / 1000.0
    k0 = 2.0 * np.pi / wavelength_um
    centered_indices = np.arange(ARRAY_COUNT) - (ARRAY_COUNT - 1) / 2.0
    arr_y = centered_indices * array_pitch_um
    out_y = output_positions(output_pitch_um=output_pitch_um, output_offset_um=output_offset_um)
    fluxes: list[float] = []

    for y_out in out_y:
        field = 0.0j
        for arm_index, (arm_position, y_arm) in enumerate(zip(centered_indices, arr_y)):
            paraxial_path = fpr_length_um + ((y_out - y_arm) ** 2) / (2.0 * fpr_length_um)
            geom_phase = k0 * (paraxial_path + INPUT_PHASE_TILT_UM * y_arm)
            array_phase = -phase_for_arm(int(arm_position), wavelength_um)
            aperture = np.exp(-0.5 * ((y_out - y_arm) / max(output_pitch_um, 1e-6)) ** 2)
            field += aperture * np.exp(1j * (geom_phase + array_phase))
        fluxes.append(float(np.abs(field) ** 2))
    return fluxes


def config_score(channel_rows: list[dict[str, float | str]]) -> float:
    dom = np.array([float(row["dominant_fraction"]) for row in channel_rows], dtype=float)
    s2f = np.array([float(row["second_to_first"]) for row in channel_rows], dtype=float)
    dominant_outputs = np.array([int(row["dominant_output"]) for row in channel_rows], dtype=float)
    center_bonus = float(channel_rows[len(channel_rows) // 2]["dominant_fraction"])
    wavelength_migration = dominant_outputs[-1] - dominant_outputs[0]
    nondecreasing_steps = np.sum(np.diff(dominant_outputs) >= 0)
    return float(
        dom.mean()
        - 0.28 * s2f.mean()
        + 0.32 * dom.min()
        - 0.12 * s2f.max()
        + 0.12 * center_bonus
        + 0.08 * wavelength_migration
        + 0.03 * nondecreasing_steps
    )


def build_candidate_rows() -> list[dict[str, float | str]]:
    all_rows: list[dict[str, float | str]] = []
    config_index = 0

    for fpr_length_um in FPR_LENGTH_OPTIONS_UM:
        for array_pitch_um in ARRAY_PITCH_OPTIONS_UM:
            for output_pitch_um in OUTPUT_PITCH_OPTIONS_UM:
                for output_offset_um in OUTPUT_OFFSET_OPTIONS_UM:
                    label = f"coarse_{config_index:03d}"
                    config_rows: list[dict[str, float | str]] = []
                    for wavelength_nm in CHANNEL_WAVELENGTHS_NM:
                        fluxes = local_fluxes_for_config(
                            wavelength_nm=wavelength_nm,
                            array_pitch_um=array_pitch_um,
                            output_pitch_um=output_pitch_um,
                            output_offset_um=output_offset_um,
                            fpr_length_um=fpr_length_um,
                        )
                        metrics = routing_metrics(fluxes)
                        row = {
                            "config_label": label,
                            "wavelength_nm": float(wavelength_nm),
                            "fpr_length_um": float(fpr_length_um),
                            "array_pitch_um": float(array_pitch_um),
                            "output_pitch_um": float(output_pitch_um),
                            "output_offset_um": float(output_offset_um),
                            "dominant_output": int(max(range(len(fluxes)), key=lambda idx: fluxes[idx]) + 1),
                            "dominant_fraction": metrics["dominant_fraction"],
                            "second_to_first": metrics["second_to_first"],
                            "quality": classify_routing_quality(metrics["dominant_fraction"], metrics["second_to_first"]),
                            "source_type": "coarse_local",
                            **{f"out_{idx}": float(fluxes[idx - 1]) for idx in range(1, 5)},
                        }
                        config_rows.append(row)

                    score = config_score(config_rows)
                    for row in config_rows:
                        row["coarse_score"] = score
                    all_rows.extend(config_rows)
                    config_index += 1

    return all_rows


def summarize_configs(results_df: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for cfg_label, cfg_df in results_df.groupby("config_label"):
        per_channel_qualities = list(cfg_df["quality"])
        summary_rows.append(
            {
                "config_label": cfg_label,
                "fpr_length_um": float(cfg_df["fpr_length_um"].iloc[0]),
                "array_pitch_um": float(cfg_df["array_pitch_um"].iloc[0]),
                "output_pitch_um": float(cfg_df["output_pitch_um"].iloc[0]),
                "output_offset_um": float(cfg_df["output_offset_um"].iloc[0]),
                "avg_dominant_fraction": float(cfg_df["dominant_fraction"].mean()),
                "min_dominant_fraction": float(cfg_df["dominant_fraction"].min()),
                "avg_second_to_first": float(cfg_df["second_to_first"].mean()),
                "max_second_to_first": float(cfg_df["second_to_first"].max()),
                "aggregate_quality": "general"
                if all(q in {"good", "general"} for q in per_channel_qualities)
                else ("passing" if all(q in {"good", "general", "passing"} for q in per_channel_qualities) else "poor"),
                "coarse_score": float(cfg_df["coarse_score"].iloc[0]),
            }
        )
    return pd.DataFrame(summary_rows).sort_values("coarse_score", ascending=False)


def write_results(rows: list[dict[str, float | str]]) -> None:
    COARSE_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "config_label",
        "wavelength_nm",
        "fpr_length_um",
        "array_pitch_um",
        "output_pitch_um",
        "output_offset_um",
        "dominant_output",
        "dominant_fraction",
        "second_to_first",
        "quality",
        "source_type",
        "coarse_score",
    ]
    fieldnames.extend([f"out_{idx}" for idx in range(1, 5)])
    with COARSE_RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_ranking(summary_df: pd.DataFrame) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    top_df = summary_df.head(12).copy()
    x = range(len(top_df))
    plt.figure(figsize=(10.0, 5.0))
    plt.bar(x, top_df["avg_dominant_fraction"], color="#0b3c5d", label="Average dominant fraction")
    plt.plot(x, top_df["min_dominant_fraction"], color="#1d6f42", marker="o", linewidth=1.8, label="Minimum dominant fraction")
    plt.plot(x, top_df["max_second_to_first"], color="#8c2f39", marker="s", linewidth=1.8, label="Maximum second/first")
    plt.xticks(list(x), top_df["config_label"], rotation=35, ha="right")
    plt.ylim(0, 1.05)
    plt.ylabel("Metric value")
    plt.title("Coarse Local Ranking Before 2D FDTD")
    plt.grid(True, axis="y", alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(COARSE_SCAN_PNG, dpi=220)
    plt.close()


def plot_best_channels(results_df: pd.DataFrame, best_label: str) -> None:
    subset = results_df[results_df["config_label"] == best_label].copy().sort_values("wavelength_nm")
    plt.figure(figsize=(8.0, 4.8))
    plt.plot(subset["wavelength_nm"], subset["dominant_fraction"], marker="o", linewidth=2.0, color="#1d6f42")
    plt.plot(subset["wavelength_nm"], subset["second_to_first"], marker="s", linewidth=2.0, color="#8c2f39")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Metric value")
    plt.title(f"Best Coarse Candidate Across 4 Channels: {best_label}")
    plt.grid(True, alpha=0.25)
    plt.legend(["Dominant fraction", "Second / first"], frameon=False)
    plt.tight_layout()
    plt.savefig(COARSE_CHANNEL_PNG, dpi=220)
    plt.close()


def write_summary(summary_df: pd.DataFrame, results_df: pd.DataFrame) -> None:
    COARSE_SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    best = summary_df.iloc[0]
    top_rows = summary_df.head(TOP_CANDIDATE_COUNT)
    lines = [
        "# AWG Coarse-to-Fine Screening Summary",
        "",
        "## Goal",
        "",
        "This stage performs a zero-credit local aperture-propagation scan before any 2D cloud FDTD runs.",
        "The purpose is not to replace FDTD, but to find the most promising parameter direction so the later cloud validation only touches a small shortlist.",
        "",
        "## Search Space",
        "",
        f"- FPR length candidates: {', '.join(f'{value:.2f}' for value in FPR_LENGTH_OPTIONS_UM)} um",
        f"- Array pitch candidates: {', '.join(f'{value:.2f}' for value in ARRAY_PITCH_OPTIONS_UM)} um",
        f"- Output pitch candidates: {', '.join(f'{value:.2f}' for value in OUTPUT_PITCH_OPTIONS_UM)} um",
        f"- Output offset candidates: {', '.join(f'{value:.2f}' for value in OUTPUT_OFFSET_OPTIONS_UM)} um",
        f"- Equivalent input phase tilt used in local model: {INPUT_PHASE_TILT_UM:.2f} um",
        "",
        "## Best Coarse Candidate",
        "",
        f"- Config label: `{best['config_label']}`",
        f"- FPR length: {best['fpr_length_um']:.2f} um",
        f"- Array pitch: {best['array_pitch_um']:.2f} um",
        f"- Output pitch: {best['output_pitch_um']:.2f} um",
        f"- Output offset: {best['output_offset_um']:.2f} um",
        f"- Average dominant fraction: {best['avg_dominant_fraction']:.4f}",
        f"- Minimum dominant fraction: {best['min_dominant_fraction']:.4f}",
        f"- Average second/first: {best['avg_second_to_first']:.4f}",
        f"- Maximum second/first: {best['max_second_to_first']:.4f}",
        "",
        "## Recommended 2D FDTD Shortlist",
        "",
        "| Config | FPR length | Array pitch | Output pitch | Offset | Avg dom frac | Min dom frac | Max second/first |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in top_rows.itertuples(index=False):
        lines.append(
            f"| {row.config_label} | {row.fpr_length_um:.2f} | {row.array_pitch_um:.2f} | {row.output_pitch_um:.2f} | "
            f"{row.output_offset_um:.2f} | {row.avg_dominant_fraction:.4f} | {row.min_dominant_fraction:.4f} | {row.max_second_to_first:.4f} |"
        )

    lines.extend(["", "## Best Candidate Per-Channel Results", "", "| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |", "| ---: | ---: | ---: | ---: | --- |"])
    best_rows = results_df[results_df["config_label"] == best["config_label"]].sort_values("wavelength_nm")
    for row in best_rows.itertuples(index=False):
        lines.append(
            f"| {row.wavelength_nm:.1f} | {int(row.dominant_output)} | {row.dominant_fraction:.4f} | {row.second_to_first:.4f} | {row.quality} |"
        )

    COARSE_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_candidate_rows()
    results_df = pd.DataFrame(rows)
    summary_df = summarize_configs(results_df)
    write_results(rows)
    plot_ranking(summary_df)
    plot_best_channels(results_df, str(summary_df.iloc[0]["config_label"]))
    write_summary(summary_df, results_df)
    print(f"Saved coarse candidate table to {COARSE_RESULTS_CSV}")
    print(f"Saved coarse summary to {COARSE_SUMMARY_MD}")


if __name__ == "__main__":
    main()
