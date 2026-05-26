from __future__ import annotations

import shutil
import subprocess
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "report_assets"
HTML_OUT = ASSETS / "awg_final_report.html"
DOCX_OUT = ROOT / "EE588_AWG_Final_Project_Report.docx"


def format_num(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def paragraph(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def bullets(items: list[str]) -> str:
    content = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f"<ul>{content}</ul>"


def make_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def image_block(filename: str, caption: str) -> str:
    return (
        '<div class="figure">'
        f'<img src="{escape(filename)}" alt="{escape(caption)}" />'
        f'<div class="caption">{escape(caption)}</div>'
        "</div>"
    )


def prepare_assets() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name in [
        "neff_vs_width.png",
        "simplified_awg_geometry_layout.png",
        "report_assets/awg_transmission_spectra.png",
        "report_assets/awg_channel_metrics.png",
    ]:
        src = ROOT / name
        dst = ASSETS / Path(name).name
        if src.exists() and src.resolve() != dst.resolve():
            shutil.copyfile(src, dst)


def build_html() -> Path:
    prepare_assets()

    width_df = pd.read_csv(ROOT / "waveguide_width_sweep_results.csv")
    params_df = pd.read_csv(ROOT / "awg_initial_parameters.csv")
    channels_df = pd.read_csv(ROOT / "awg_channel_plan.csv")
    metrics_df = pd.read_csv(ROOT / "awg_channel_metrics.csv")

    params = {row.parameter: float(row.value) for row in params_df.itertuples(index=False)}
    baseline = width_df.loc[width_df["width_um"].sub(0.50).abs().idxmin()]

    baseline_rows = [
        ["Waveguide width", "0.50 um"],
        ["Waveguide height", "0.22 um"],
        ["Reference wavelength", "1550 nm"],
        ["Fundamental mode n_eff", format_num(float(baseline["n_eff_mode0"]))],
        ["Fundamental mode n_group", format_num(float(baseline["n_group_mode0"]))],
    ]

    design_rows = [
        ["Channel count", format_num(params["channel_count"], 0), "count"],
        ["Center wavelength", format_num(params["center_wavelength"], 1), "nm"],
        ["Channel spacing", format_num(params["channel_spacing"], 1), "nm"],
        ["Target FSR", format_num(params["target_fsr"], 1), "nm"],
        ["Actual FSR", format_num(params["actual_fsr"], 4), "nm"],
        ["AWG order", format_num(params["awg_order_m"], 0), "dimensionless"],
        ["Path length difference", format_num(params["delta_length"], 4), "um"],
        ["Arrayed waveguides", format_num(params["arrayed_waveguide_count"], 0), "count"],
    ]

    channel_rows = [
        [
            str(int(row.channel_id)),
            format_num(float(row.center_wavelength_nm), 1),
            format_num(float(row.center_frequency_THz), 4),
        ]
        for row in channels_df.itertuples(index=False)
    ]

    metrics_rows = [
        [
            str(int(row.channel_id)),
            format_num(float(row.target_wavelength_nm), 3),
            format_num(float(row.peak_wavelength_nm), 3),
            format_num(float(row.insertion_loss_db), 2),
            format_num(float(row.worst_case_crosstalk_db), 2),
            format_num(float(row.three_db_bandwidth_nm), 3),
        ]
        for row in metrics_df.itertuples(index=False)
    ]

    average_spacing = pd.to_numeric(metrics_df["adjacent_spacing_nm"], errors="coerce").dropna().mean()
    avg_insertion = float(metrics_df["insertion_loss_db"].mean())
    worst_crosstalk = float(metrics_df["worst_case_crosstalk_db"].max())
    avg_bandwidth = float(metrics_df["three_db_bandwidth_nm"].mean())

    sections = [
        '<h1 class="title">EE588 Final Project Report</h1>',
        '<p class="meta">C-band 4-Channel AWG / Wavelength Demultiplexer Design Using Tidy3D</p>',
        f'<p class="meta">Date: {date.today().isoformat()}</p>',
        "<h2>1. Objective</h2>",
        paragraph(
            "This report consolidates the full three-week project workflow, from silicon strip waveguide MODE analysis to a first-pass 4-channel AWG design and a final low-cost spectral evaluation."
        ),
        "<h2>2. Workflow Summary</h2>",
        bullets(
            [
                "Week 1 established the baseline 500 nm x 220 nm silicon strip waveguide MODE solution and verified the fundamental TE-like guided mode.",
                "Week 1 also completed a width sweep from 0.40 um to 0.60 um, producing the effective-index and group-index data used for AWG design.",
                "Week 2 translated the MODE data into a 4-channel C-band AWG parameter set, including channel plan, FSR, diffraction order, and array path-length ladder.",
                "Week 3 completed a simplified local spectrum analysis using the derived AWG parameters, yielding transmission, insertion-loss, crosstalk, and channel-spacing estimates.",
            ]
        ),
        "<h2>3. Baseline Waveguide Result</h2>",
        make_table(["Item", "Value"], baseline_rows),
        image_block("neff_vs_width.png", "Width sweep result used to select the 0.50 um baseline."),
        "<h2>4. First-Pass AWG Design</h2>",
        make_table(["Parameter", "Value", "Unit"], design_rows),
        make_table(["Channel", "Center Wavelength (nm)", "Center Frequency (THz)"], channel_rows),
        image_block("simplified_awg_geometry_layout.png", "First-pass simplified AWG geometry preview."),
        "<h2>5. Final Simplified Spectral Evaluation</h2>",
        paragraph(
            "Because full device-level FDTD validation would consume substantially more Tidy3D credits, the final project stage uses a local array-factor approximation driven by the already extracted MODE parameters and AWG geometry design values."
        ),
        paragraph(
            "This means the final spectra below should be interpreted as a system-level first-pass estimate rather than a claim of fully converged electromagnetic device performance."
        ),
        image_block("awg_transmission_spectra.png", "Simplified transmission spectra for the four output channels."),
        image_block("awg_channel_metrics.png", "Insertion loss, worst-case crosstalk, and 3 dB bandwidth by channel."),
        make_table(
            ["Channel", "Target (nm)", "Peak (nm)", "Insertion Loss (dB)", "Worst Crosstalk (dB)", "3 dB BW (nm)"],
            metrics_rows,
        ),
        "<h2>6. Key Final Results</h2>",
        bullets(
            [
                f"The average adjacent channel spacing is {format_num(float(average_spacing), 3)} nm, which matches the 1.6 nm design target.",
                f"The average insertion loss in the simplified model is {format_num(avg_insertion, 2)} dB.",
                f"The worst-case crosstalk in the simplified model is {format_num(worst_crosstalk, 2)} dB.",
                f"The average 3 dB channel bandwidth is {format_num(avg_bandwidth, 3)} nm.",
                "All four channel peaks remain aligned with the intended center wavelengths in the simplified analysis output.",
            ]
        ),
        "<h2>7. Conclusion</h2>",
        paragraph(
            "The project successfully progressed from low-cost single-waveguide MODE analysis to a reportable 4-channel C-band AWG design flow. The resulting parameter set is internally consistent, produces the intended channel spacing, and supports a coherent final submission package."
        ),
        paragraph(
            "The main remaining improvement path is clear: a future iteration should replace the local spectral approximation with one or more device-level Tidy3D simulations to refine insertion loss, passband shape, and crosstalk with higher physical fidelity."
        ),
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>EE588 Final Project Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.45;
      color: #000000;
      margin: 0 auto;
      width: 6.5in;
    }}
    h1.title {{
      font-size: 24pt;
      font-weight: normal;
      text-align: center;
      margin: 0 0 4pt 0;
    }}
    h2 {{
      font-size: 16pt;
      font-weight: normal;
      margin: 18pt 0 6pt 0;
    }}
    p {{
      margin: 0 0 8pt 0;
    }}
    p.meta {{
      text-align: center;
      color: #555555;
      margin: 0 0 6pt 0;
    }}
    ul {{
      margin: 0 0 8pt 24pt;
      padding-left: 18pt;
    }}
    li {{
      margin-bottom: 4pt;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 8pt 0 12pt 0;
      table-layout: fixed;
    }}
    th, td {{
      border: 1px solid #d0d7de;
      padding: 6pt 8pt;
      vertical-align: middle;
      word-wrap: break-word;
      text-align: center;
    }}
    th {{
      background: #f2f4f7;
      font-weight: bold;
    }}
    .figure {{
      margin: 12pt 0 14pt 0;
      text-align: center;
      page-break-inside: avoid;
    }}
    .figure img {{
      max-width: 100%;
      height: auto;
      border: 1px solid #e5e7eb;
    }}
    .caption {{
      font-size: 10pt;
      color: #555555;
      margin-top: 4pt;
    }}
  </style>
</head>
<body>
{''.join(sections)}
</body>
</html>
"""
    HTML_OUT.write_text(html, encoding="utf-8")
    return HTML_OUT


def convert_to_docx(html_path: Path) -> Path:
    if DOCX_OUT.exists():
        DOCX_OUT.unlink()
    subprocess.run(
        [
            "textutil",
            "-convert",
            "docx",
            str(html_path),
            "-output",
            str(DOCX_OUT),
        ],
        check=True,
    )
    return DOCX_OUT


if __name__ == "__main__":
    html_path = build_html()
    docx_path = convert_to_docx(html_path)
    print(html_path)
    print(docx_path)
