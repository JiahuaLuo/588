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
        build_simulation,
        classify_routing_quality,
        estimate_credit,
        extract_fluxes,
        routing_metrics,
        run_simulation,
    )


GLOBAL_RESULTS_CSV = ROOT / "results" / "tables" / "awg_hf_global_optimization_results.csv"
GLOBAL_SUMMARY_MD = ROOT / "docs" / "AWG_HF_GLOBAL_OPTIMIZATION_SUMMARY.md"
GLOBAL_SCAN_PNG = ASSETS / "awg_hf_global_optimization_scan.png"
GLOBAL_VERIFY_PNG = ASSETS / "awg_hf_global_optimization_channels.png"
COARSE_RESULTS_CSV = ROOT / "results" / "tables" / "awg_coarse_to_fine_candidates.csv"
GLOBAL_MAX_ESTIMATED_CREDITS = 1.8
COARSE_TOP_K = 5


def candidate_configs() -> list[dict[str, float | str]]:
    fallback = [
        {"label": "globscan_a", "array_pitch_um": 1.25, "output_pitch_um": 1.65, "output_offset_um": 0.50},
        {"label": "globscan_b", "array_pitch_um": 1.25, "output_pitch_um": 1.60, "output_offset_um": 0.55},
        {"label": "globscan_c", "array_pitch_um": 1.20, "output_pitch_um": 1.55, "output_offset_um": 0.55},
        {"label": "globscan_d", "array_pitch_um": 1.15, "output_pitch_um": 1.55, "output_offset_um": 0.60},
        {"label": "globscan_e", "array_pitch_um": 1.15, "output_pitch_um": 1.60, "output_offset_um": 0.65},
    ]
    if not COARSE_RESULTS_CSV.exists():
        return fallback

    coarse_df = pd.read_csv(COARSE_RESULTS_CSV)
    summary_rows = []
    for cfg_label, cfg_df in coarse_df.groupby("config_label"):
        summary_rows.append(
            {
                "label": cfg_label.replace("coarse_", "globscan_"),
                "array_pitch_um": float(cfg_df["array_pitch_um"].iloc[0]),
                "output_pitch_um": float(cfg_df["output_pitch_um"].iloc[0]),
                "output_offset_um": float(cfg_df["output_offset_um"].iloc[0]),
                "coarse_score": float(cfg_df["coarse_score"].iloc[0]),
            }
        )

    ranked = sorted(summary_rows, key=lambda item: item["coarse_score"], reverse=True)
    shortlisted = []
    seen_keys: set[tuple[float, float, float]] = set()
    for row in ranked:
        key = (
            round(float(row["array_pitch_um"]), 6),
            round(float(row["output_pitch_um"]), 6),
            round(float(row["output_offset_um"]), 6),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        shortlisted.append(row)
        if len(shortlisted) >= COARSE_TOP_K:
            break
    if shortlisted:
        return [
            {
                "label": str(row["label"]),
                "array_pitch_um": float(row["array_pitch_um"]),
                "output_pitch_um": float(row["output_pitch_um"]),
                "output_offset_um": float(row["output_offset_um"]),
            }
            for row in shortlisted
        ]
    return fallback


def global_score(avg_dom: float, avg_s2f: float, min_dom: float, max_s2f: float) -> float:
    return avg_dom - 0.30 * avg_s2f + 0.35 * min_dom - 0.12 * max_s2f


def aggregate_quality(per_channel_qualities: list[str]) -> str:
    if all(q == "good" for q in per_channel_qualities):
        return "good"
    if all(q in {"good", "general"} for q in per_channel_qualities) and any(q == "general" for q in per_channel_qualities):
        return "general"
    if all(q in {"good", "general", "passing"} for q in per_channel_qualities):
        return "passing"
    return "poor"


def existing_seed_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []

    baseline_path = ROOT / "results" / "tables" / "awg_high_fidelity_results.csv"
    if baseline_path.exists():
        baseline_df = pd.read_csv(baseline_path)
        baseline_df = baseline_df[baseline_df["label"].str.startswith("hf_4ch_")].copy()
        for row in baseline_df.itertuples(index=False):
            fluxes = [float(getattr(row, f"out_{idx}")) for idx in range(1, 5)]
            metrics = routing_metrics(fluxes)
            quality = classify_routing_quality(metrics["dominant_fraction"], metrics["second_to_first"])
            rows.append(
                {
                    "config_label": "seed_baseline",
                    "wavelength_nm": float(row.wavelength_nm),
                    "array_pitch_um": float(row.array_pitch_um),
                    "output_pitch_um": float(row.output_pitch_um),
                    "output_offset_um": float(row.output_offset_um),
                    "estimated_cost": float(row.estimated_cost),
                    "dominant_output": int(row.dominant_output),
                    "dominant_fraction": metrics["dominant_fraction"],
                    "second_to_first": metrics["second_to_first"],
                    "quality": quality,
                    "source_type": "cached",
                    **{f"out_{idx}": fluxes[idx - 1] for idx in range(1, 5)},
                }
            )

    opt_path = ROOT / "results" / "tables" / "awg_hf_optimization_results.csv"
    if opt_path.exists():
        opt_df = pd.read_csv(opt_path)
        opt_df = opt_df[opt_df["stage"] == "verify"].copy()
        same_cfg = opt_df[
            (opt_df["array_pitch_um"].round(6) == 1.2)
            & (opt_df["output_pitch_um"].round(6) == 1.6)
            & (opt_df["output_offset_um"].round(6) == 0.6)
        ]
        for row in same_cfg.itertuples(index=False):
            fluxes = [float(getattr(row, f"out_{idx}")) for idx in range(1, 5)]
            metrics = routing_metrics(fluxes)
            quality = classify_routing_quality(metrics["dominant_fraction"], metrics["second_to_first"])
            rows.append(
                {
                    "config_label": "seed_local_best",
                    "wavelength_nm": float(row.wavelength_nm),
                    "array_pitch_um": float(row.array_pitch_um),
                    "output_pitch_um": float(row.output_pitch_um),
                    "output_offset_um": float(row.output_offset_um),
                    "estimated_cost": float(row.estimated_cost),
                    "dominant_output": int(row.dominant_output),
                    "dominant_fraction": metrics["dominant_fraction"],
                    "second_to_first": metrics["second_to_first"],
                    "quality": quality,
                    "source_type": "cached",
                    **{f"out_{idx}": fluxes[idx - 1] for idx in range(1, 5)},
                }
            )

    return rows


def write_results(rows: list[dict[str, float | str]]) -> None:
    GLOBAL_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "config_label",
        "wavelength_nm",
        "array_pitch_um",
        "output_pitch_um",
        "output_offset_um",
        "estimated_cost",
        "dominant_output",
        "dominant_fraction",
        "second_to_first",
        "quality",
        "source_type",
    ]
    fieldnames.extend([f"out_{idx}" for idx in range(1, 5)])
    with GLOBAL_RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_configs(results_df: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for cfg_label, cfg_df in results_df.groupby("config_label"):
        per_channel_qualities = list(cfg_df["quality"])
        summary_rows.append(
            {
                "config_label": cfg_label,
                "array_pitch_um": float(cfg_df["array_pitch_um"].iloc[0]),
                "output_pitch_um": float(cfg_df["output_pitch_um"].iloc[0]),
                "output_offset_um": float(cfg_df["output_offset_um"].iloc[0]),
                "avg_dominant_fraction": float(cfg_df["dominant_fraction"].mean()),
                "min_dominant_fraction": float(cfg_df["dominant_fraction"].min()),
                "avg_second_to_first": float(cfg_df["second_to_first"].mean()),
                "max_second_to_first": float(cfg_df["second_to_first"].max()),
                "aggregate_quality": aggregate_quality(per_channel_qualities),
                "score": global_score(
                    float(cfg_df["dominant_fraction"].mean()),
                    float(cfg_df["second_to_first"].mean()),
                    float(cfg_df["dominant_fraction"].min()),
                    float(cfg_df["second_to_first"].max()),
                ),
            }
        )
    return pd.DataFrame(summary_rows).sort_values("score", ascending=False)


def plot_scan(summary_df: pd.DataFrame) -> None:
    plt.figure(figsize=(9.5, 4.8))
    x = range(len(summary_df))
    plt.bar(x, summary_df["avg_dominant_fraction"], color="#0b3c5d", label="Average dominant fraction")
    plt.plot(x, summary_df["min_dominant_fraction"], color="#1d6f42", marker="o", linewidth=1.8, label="Minimum dominant fraction")
    plt.plot(x, summary_df["max_second_to_first"], color="#8c2f39", marker="s", linewidth=1.8, label="Maximum second/first")
    plt.xticks(list(x), summary_df["config_label"], rotation=30, ha="right")
    plt.ylim(0, 1.05)
    plt.ylabel("Metric value")
    plt.title("Global 4-Channel Optimization Ranking")
    plt.grid(True, axis="y", alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(GLOBAL_SCAN_PNG, dpi=220)
    plt.close()


def plot_channels(results_df: pd.DataFrame, best_label: str) -> None:
    subset = results_df[results_df["config_label"] == best_label].copy().sort_values("wavelength_nm")
    plt.figure(figsize=(8.0, 4.8))
    plt.plot(subset["wavelength_nm"], subset["dominant_fraction"], marker="o", linewidth=2.0, color="#1d6f42")
    plt.plot(subset["wavelength_nm"], subset["second_to_first"], marker="s", linewidth=2.0, color="#8c2f39")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Metric value")
    plt.title(f"Best Global Config Across 4 Channels: {best_label}")
    plt.grid(True, alpha=0.25)
    plt.legend(["Dominant fraction", "Second / first"], frameon=False)
    plt.tight_layout()
    plt.savefig(GLOBAL_VERIFY_PNG, dpi=220)
    plt.close()


def write_summary(summary_df: pd.DataFrame, results_df: pd.DataFrame) -> None:
    GLOBAL_SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    best = summary_df.iloc[0]
    lines = [
        "# AWG High-Fidelity Global Optimization Summary",
        "",
        "## Goal",
        "",
        "This optimization prioritizes the full 4-channel average and worst-channel behavior rather than a single center wavelength.",
        "",
        "## Quality Rubric",
        "",
        "- good: dominant output fraction >= 0.60 and second/first <= 0.50",
        "- general: dominant output fraction >= 0.40 and second/first <= 0.80",
        "- passing: dominant output fraction >= 0.30 and second/first <= 0.95",
        "- poor: below the passing threshold",
        "",
        "## Best Global Configuration",
        "",
        f"- Config label: `{best['config_label']}`",
        f"- Array pitch: {best['array_pitch_um']:.2f} um",
        f"- Output pitch: {best['output_pitch_um']:.2f} um",
        f"- Output offset: {best['output_offset_um']:.2f} um",
        f"- Average dominant fraction: {best['avg_dominant_fraction']:.4f}",
        f"- Minimum dominant fraction: {best['min_dominant_fraction']:.4f}",
        f"- Average second/first: {best['avg_second_to_first']:.4f}",
        f"- Maximum second/first: {best['max_second_to_first']:.4f}",
        f"- Aggregate quality: {best['aggregate_quality']}",
        "",
        "## Configuration Ranking",
        "",
        "| Config | Array pitch | Output pitch | Offset | Avg dom frac | Min dom frac | Avg second/first | Max second/first | Aggregate quality |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for row in summary_df.itertuples(index=False):
        lines.append(
            f"| {row.config_label} | {row.array_pitch_um:.2f} | {row.output_pitch_um:.2f} | {row.output_offset_um:.2f} | "
            f"{row.avg_dominant_fraction:.4f} | {row.min_dominant_fraction:.4f} | {row.avg_second_to_first:.4f} | "
            f"{row.max_second_to_first:.4f} | {row.aggregate_quality} |"
        )

    lines.extend(["", "## Best Config Per-Channel Results", "", "| Wavelength (nm) | Dominant output | Dominant fraction | Second/first | Quality |", "| ---: | ---: | ---: | ---: | --- |"])
    best_rows = results_df[results_df["config_label"] == best["config_label"]].sort_values("wavelength_nm")
    for row in best_rows.itertuples(index=False):
        lines.append(
            f"| {row.wavelength_nm:.1f} | {int(row.dominant_output)} | {row.dominant_fraction:.4f} | {row.second_to_first:.4f} | {row.quality} |"
        )

    GLOBAL_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = existing_seed_rows()

    estimate_total = 0.0
    candidate_list = candidate_configs()
    for cfg in candidate_list:
        for wavelength_nm in CHANNEL_WAVELENGTHS_NM:
            sim = build_simulation(
                wavelength_nm=wavelength_nm,
                output_count=4,
                array_pitch_um=float(cfg["array_pitch_um"]),
                output_pitch_um=float(cfg["output_pitch_um"]),
                output_offset_um=float(cfg["output_offset_um"]),
                include_field_monitor=False,
            )
            _, est = estimate_credit(sim, f"{cfg['label']}_{wavelength_nm:.1f}nm")
            estimate_total += est

    print(f"Estimated global optimization cost: {estimate_total:.4f} FlexCredit")
    if estimate_total > min(MAX_TOTAL_ESTIMATED_CREDITS, GLOBAL_MAX_ESTIMATED_CREDITS):
        raise RuntimeError(
            f"Estimated cost {estimate_total:.4f} exceeds limit {min(MAX_TOTAL_ESTIMATED_CREDITS, GLOBAL_MAX_ESTIMATED_CREDITS):.4f}."
        )

    for cfg in candidate_list:
        for wavelength_nm in CHANNEL_WAVELENGTHS_NM:
            label = f"{cfg['label']}_{wavelength_nm:.1f}nm"
            sim = build_simulation(
                wavelength_nm=wavelength_nm,
                output_count=4,
                array_pitch_um=float(cfg["array_pitch_um"]),
                output_pitch_um=float(cfg["output_pitch_um"]),
                output_offset_um=float(cfg["output_offset_um"]),
                include_field_monitor=False,
            )
            out_path = DATA_DIR / f"{label}.hdf5"
            sim_data = run_simulation(sim, task_name=label, out_path=out_path)
            fluxes = extract_fluxes(sim_data, output_count=4)
            metrics = routing_metrics(fluxes)
            quality = classify_routing_quality(metrics["dominant_fraction"], metrics["second_to_first"])
            rows.append(
                {
                    "config_label": str(cfg["label"]),
                    "wavelength_nm": float(wavelength_nm),
                    "array_pitch_um": float(cfg["array_pitch_um"]),
                    "output_pitch_um": float(cfg["output_pitch_um"]),
                    "output_offset_um": float(cfg["output_offset_um"]),
                    "estimated_cost": "",
                    "dominant_output": int(max(range(len(fluxes)), key=lambda idx: fluxes[idx]) + 1),
                    "dominant_fraction": metrics["dominant_fraction"],
                    "second_to_first": metrics["second_to_first"],
                    "quality": quality,
                    "source_type": "new_run",
                    **{f"out_{idx}": fluxes[idx - 1] for idx in range(1, 5)},
                }
            )
            print(
                f"{label}: dominant_fraction={metrics['dominant_fraction']:.4f}, "
                f"second/first={metrics['second_to_first']:.4f}, quality={quality}"
            )

    results_df = pd.DataFrame(rows)
    summary_df = summarize_configs(results_df)
    write_results(rows)
    plot_scan(summary_df)
    plot_channels(results_df, str(summary_df.iloc[0]["config_label"]))
    write_summary(summary_df, results_df)
    print(f"Saved global optimization results to {GLOBAL_RESULTS_CSV}")
    print(f"Saved global optimization summary to {GLOBAL_SUMMARY_MD}")


if __name__ == "__main__":
    main()
