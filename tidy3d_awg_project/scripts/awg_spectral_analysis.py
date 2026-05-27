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

ASSETS = ROOT / "results" / "figures"
TABLES = ROOT / "results" / "tables"
DOCS = ROOT / "docs"
SPECTRUM_CSV = TABLES / "awg_simplified_spectrum.csv"
METRICS_CSV = TABLES / "awg_channel_metrics.csv"
SUMMARY_MD = DOCS / "AWG_FINAL_RESULTS.md"
SPECTRA_PNG = ASSETS / "awg_transmission_spectra.png"
METRICS_PNG = ASSETS / "awg_channel_metrics.png"

# This is a local, low-cost approximation for the final project stage.
# It converts the existing MODE-derived AWG parameters into an array-factor
# spectrum model rather than claiming a full device-level FDTD result.
PEAK_TRANSMISSION_LINEAR = 10 ** (-3.0 / 10.0)
ENVELOPE_SIGMA_NM = 6.0


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    params_df = pd.read_csv(TABLES / "awg_initial_parameters.csv")
    channels_df = pd.read_csv(TABLES / "awg_channel_plan.csv")
    lengths_df = pd.read_csv(TABLES / "awg_arrayed_waveguide_lengths.csv")
    params = {row.parameter: float(row.value) for row in params_df.itertuples(index=False)}
    params["arrayed_waveguide_count"] = float(len(lengths_df))
    return params_df, channels_df, params


def array_factor(delta_lambda_nm: np.ndarray, fsr_nm: float, arm_count: int) -> np.ndarray:
    phi = 2.0 * np.pi * delta_lambda_nm / fsr_nm
    numerator = np.sin(arm_count * phi / 2.0)
    denominator = arm_count * np.sin(phi / 2.0)
    response = np.ones_like(delta_lambda_nm, dtype=float)
    valid = np.abs(denominator) > 1e-12
    response[valid] = (numerator[valid] / denominator[valid]) ** 2
    return response


def gaussian_envelope(delta_lambda_nm: np.ndarray, sigma_nm: float) -> np.ndarray:
    return np.exp(-0.5 * (delta_lambda_nm / sigma_nm) ** 2)


def build_spectrum(
    wavelengths_nm: np.ndarray,
    center_nm: float,
    fsr_nm: float,
    arm_count: int,
    peak_transmission: float,
) -> np.ndarray:
    delta_nm = wavelengths_nm - center_nm
    return peak_transmission * array_factor(delta_nm, fsr_nm, arm_count) * gaussian_envelope(delta_nm, ENVELOPE_SIGMA_NM)


def half_power_bandwidth_nm(wavelengths_nm: np.ndarray, transmission: np.ndarray, peak_index: int) -> float:
    half_power = transmission[peak_index] / 2.0
    left = peak_index
    while left > 0 and transmission[left] >= half_power:
        left -= 1
    right = peak_index
    while right < len(transmission) - 1 and transmission[right] >= half_power:
        right += 1
    return float(wavelengths_nm[right] - wavelengths_nm[left])


def save_spectrum_csv(wavelengths_nm: np.ndarray, channels_df: pd.DataFrame, transmissions: list[np.ndarray]) -> None:
    fieldnames = ["wavelength_nm"] + [f"out_{int(row.channel_id)}" for row in channels_df.itertuples(index=False)]
    with SPECTRUM_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx, wavelength_nm in enumerate(wavelengths_nm):
            row = {"wavelength_nm": float(wavelength_nm)}
            for out_idx, _ in enumerate(channels_df.itertuples(index=False), start=1):
                row[f"out_{out_idx}"] = float(transmissions[out_idx - 1][idx])
            writer.writerow(row)


def save_metrics_csv(rows: list[dict[str, float | str]]) -> None:
    fieldnames = [
        "channel_id",
        "target_wavelength_nm",
        "peak_wavelength_nm",
        "peak_transmission_linear",
        "peak_transmission_db",
        "insertion_loss_db",
        "adjacent_spacing_nm",
        "worst_case_crosstalk_db",
        "three_db_bandwidth_nm",
    ]
    with METRICS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_spectra(wavelengths_nm: np.ndarray, channels_df: pd.DataFrame, transmissions: list[np.ndarray]) -> None:
    ASSETS.mkdir(exist_ok=True)
    plt.figure(figsize=(8.4, 4.8))
    colors = ["#0b3c5d", "#1d6f42", "#c07a00", "#8c2f39"]
    for color, row, values in zip(colors, channels_df.itertuples(index=False), transmissions):
        plt.plot(
            wavelengths_nm,
            10.0 * np.log10(np.clip(values, 1e-12, None)),
            linewidth=2.0,
            color=color,
            label=f"Output {int(row.channel_id)} ({row.center_wavelength_nm:.1f} nm)",
        )
        plt.axvline(row.center_wavelength_nm, linestyle="--", linewidth=0.8, color=color, alpha=0.35)
    plt.ylim(-45, 0.5)
    plt.xlim(float(wavelengths_nm.min()), float(wavelengths_nm.max()))
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Transmission (dB)")
    plt.title("Simplified 4-Channel AWG Transmission Spectra")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    plt.savefig(SPECTRA_PNG, dpi=220)
    plt.close()


def plot_metrics(metrics_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.6))
    channels = metrics_df["channel_id"].astype(int).to_numpy()

    axes[0].bar(channels, metrics_df["insertion_loss_db"], color="#0b3c5d")
    axes[0].set_title("Insertion Loss")
    axes[0].set_xlabel("Channel")
    axes[0].set_ylabel("dB")
    axes[0].grid(True, axis="y", alpha=0.25)

    axes[1].bar(channels, metrics_df["worst_case_crosstalk_db"], color="#8c2f39")
    axes[1].set_title("Worst-Case Crosstalk")
    axes[1].set_xlabel("Channel")
    axes[1].set_ylabel("dB")
    axes[1].grid(True, axis="y", alpha=0.25)

    axes[2].bar(channels, metrics_df["three_db_bandwidth_nm"], color="#1d6f42")
    axes[2].set_title("3 dB Bandwidth")
    axes[2].set_xlabel("Channel")
    axes[2].set_ylabel("nm")
    axes[2].grid(True, axis="y", alpha=0.25)

    for axis in axes:
        axis.set_xticks(channels)

    fig.tight_layout()
    fig.savefig(METRICS_PNG, dpi=220)
    plt.close(fig)


def write_summary(params: dict[str, float], metrics_df: pd.DataFrame) -> None:
    spacing_values = pd.to_numeric(metrics_df["adjacent_spacing_nm"], errors="coerce").dropna()
    average_spacing_nm = float(spacing_values.mean()) if not spacing_values.empty else float("nan")
    avg_insertion_db = float(metrics_df["insertion_loss_db"].mean())
    max_insertion_db = float(metrics_df["insertion_loss_db"].max())
    avg_crosstalk_db = float(metrics_df["worst_case_crosstalk_db"].mean())
    worst_crosstalk_db = float(metrics_df["worst_case_crosstalk_db"].max())
    avg_bandwidth_nm = float(metrics_df["three_db_bandwidth_nm"].mean())

    lines = [
        "# Final Simplified AWG Results",
        "",
        "## Method",
        "",
        "This final-stage analysis uses a simplified local array-factor spectrum model calibrated by the existing Tidy3D MODE results and the first-pass AWG design parameters.",
        "It is intended as a low-cost system-level approximation for the course project and should not be interpreted as a substitute for a full Tidy3D device-level FDTD validation.",
        "",
        "## Inputs",
        "",
        f"- Center wavelength: {params['center_wavelength']:.1f} nm",
        f"- Channel spacing target: {params['channel_spacing']:.1f} nm",
        f"- Target FSR: {params['target_fsr']:.1f} nm",
        f"- AWG order: {params['awg_order_m']:.0f}",
        f"- Arrayed waveguide count: {params['arrayed_waveguide_count']:.0f}",
        f"- Path length difference: {params['delta_length']:.3f} um",
        "",
        "## Summary Metrics",
        "",
        f"- Average insertion loss: {avg_insertion_db:.2f} dB",
        f"- Worst insertion loss: {max_insertion_db:.2f} dB",
        f"- Average worst-case crosstalk: {avg_crosstalk_db:.2f} dB",
        f"- Worst-case crosstalk across all channels: {worst_crosstalk_db:.2f} dB",
        f"- Average 3 dB bandwidth: {avg_bandwidth_nm:.3f} nm",
        f"- Average adjacent channel spacing: {average_spacing_nm:.3f} nm",
        "",
        "## Channel Metrics",
        "",
        "| Channel | Target (nm) | Peak (nm) | Peak Tx (dB) | Insertion Loss (dB) | Crosstalk (dB) | 3 dB BW (nm) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in metrics_df.itertuples(index=False):
        lines.append(
            f"| {int(row.channel_id)} | {row.target_wavelength_nm:.3f} | {row.peak_wavelength_nm:.3f} | "
            f"{row.peak_transmission_db:.2f} | {row.insertion_loss_db:.2f} | {row.worst_case_crosstalk_db:.2f} | "
            f"{row.three_db_bandwidth_nm:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `results/tables/awg_simplified_spectrum.csv`",
            "- `results/tables/awg_channel_metrics.csv`",
            "- `results/figures/awg_transmission_spectra.png`",
            "- `results/figures/awg_channel_metrics.png`",
        ]
    )

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    _, channels_df, params = load_inputs()

    center_wavelength_nm = float(params["center_wavelength"])
    channel_spacing_nm = float(params["channel_spacing"])
    fsr_nm = float(params["actual_fsr"])
    arm_count = int(round(params["arrayed_waveguide_count"]))

    wavelengths_nm = np.linspace(center_wavelength_nm - 8.0, center_wavelength_nm + 8.0, 3201)
    transmissions = []
    metric_rows: list[dict[str, float | str]] = []
    peak_wavelengths = []

    for row in channels_df.itertuples(index=False):
        transmission = build_spectrum(
            wavelengths_nm=wavelengths_nm,
            center_nm=float(row.center_wavelength_nm),
            fsr_nm=fsr_nm,
            arm_count=arm_count,
            peak_transmission=PEAK_TRANSMISSION_LINEAR,
        )
        transmissions.append(transmission)

    for channel_index, row in enumerate(channels_df.itertuples(index=False)):
        transmission = transmissions[channel_index]
        peak_index = int(np.argmax(transmission))
        peak_wavelength_nm = float(wavelengths_nm[peak_index])
        peak_wavelengths.append(peak_wavelength_nm)
        peak_linear = float(transmission[peak_index])
        peak_db = float(10.0 * np.log10(max(peak_linear, 1e-12)))
        insertion_loss_db = float(-peak_db)

        other_peaks = []
        for other_index, other_transmission in enumerate(transmissions):
            if other_index == channel_index:
                continue
            other_peaks.append(float(other_transmission[peak_index]))
        worst_other = max(other_peaks)
        worst_case_crosstalk_db = float(10.0 * np.log10(max(worst_other / peak_linear, 1e-12)))

        metric_rows.append(
            {
                "channel_id": int(row.channel_id),
                "target_wavelength_nm": float(row.center_wavelength_nm),
                "peak_wavelength_nm": peak_wavelength_nm,
                "peak_transmission_linear": peak_linear,
                "peak_transmission_db": peak_db,
                "insertion_loss_db": insertion_loss_db,
                "adjacent_spacing_nm": "",
                "worst_case_crosstalk_db": worst_case_crosstalk_db,
                "three_db_bandwidth_nm": half_power_bandwidth_nm(wavelengths_nm, transmission, peak_index),
            }
        )

    for idx in range(len(peak_wavelengths) - 1):
        metric_rows[idx]["adjacent_spacing_nm"] = peak_wavelengths[idx + 1] - peak_wavelengths[idx]
    if metric_rows:
        metric_rows[-1]["adjacent_spacing_nm"] = ""

    metrics_df = pd.DataFrame(metric_rows)

    save_spectrum_csv(wavelengths_nm, channels_df, transmissions)
    save_metrics_csv(metric_rows)
    plot_spectra(wavelengths_nm, channels_df, transmissions)
    plot_metrics(metrics_df)
    write_summary(params, metrics_df)

    average_spacing = pd.to_numeric(metrics_df["adjacent_spacing_nm"], errors="coerce").dropna().mean()
    print("Simplified AWG spectral analysis completed.")
    print(f"Spectrum CSV: {SPECTRUM_CSV}")
    print(f"Metrics CSV: {METRICS_CSV}")
    print(f"Spectra plot: {SPECTRA_PNG}")
    print(f"Metrics plot: {METRICS_PNG}")
    print(f"Average insertion loss (dB): {metrics_df['insertion_loss_db'].mean():.3f}")
    print(f"Worst-case crosstalk (dB): {metrics_df['worst_case_crosstalk_db'].max():.3f}")
    print(f"Average adjacent spacing (nm): {average_spacing:.3f}")
    print(f"Nominal channel spacing target (nm): {channel_spacing_nm:.3f}")


if __name__ == "__main__":
    main()
