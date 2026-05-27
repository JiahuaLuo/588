from __future__ import annotations

import shutil
import subprocess
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "results" / "figures"
TABLES = ROOT / "results" / "tables"
HTML_OUT = ASSETS / "notebook_report.html"
DOCX_OUT = ROOT / "reports" / "EE588_HW3_Notebook_Report.docx"


def format_num(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def make_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>")
    body = "\n".join(body_rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def paragraph(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def bullets(items: list[str]) -> str:
    content = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f"<ul>{content}</ul>"


def image_block(filename: str, caption: str) -> str:
    return (
        '<div class="figure">'
        f'<img src="{escape(filename)}" alt="{escape(caption)}" />'
        f'<div class="caption">{escape(caption)}</div>'
        "</div>"
    )


def generate_plots() -> dict[str, str]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    available = []
    for name in ["neff_vs_width.png", "simplified_awg_geometry_layout.png"]:
        src = ASSETS / name
        if src.exists():
            available.append(name)
    return {"available": available}


def build_html() -> Path:
    figures = generate_plots()
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    width_df = pd.read_csv(TABLES / "waveguide_width_sweep_results.csv")
    params_df = pd.read_csv(TABLES / "awg_initial_parameters.csv")
    channel_df = pd.read_csv(TABLES / "awg_channel_plan.csv")
    lengths_df = pd.read_csv(TABLES / "awg_arrayed_waveguide_lengths.csv")

    selected = width_df.loc[width_df["width_um"].sub(0.50).abs().idxmin()]

    baseline_rows = [
        ["Core material", "Silicon (n = 3.48)"],
        ["Cladding material", "SiO2 (n = 1.44)"],
        ["Waveguide width", "0.50 um"],
        ["Waveguide height", "0.22 um"],
        ["Reference wavelength", "1.55 um"],
        ["Fundamental mode n_eff", format_num(selected["n_eff_mode0"])],
        ["Fundamental mode n_group", format_num(selected["n_group_mode0"])],
    ]

    sweep_rows = [
        [format_num(row.width_um, 2), format_num(row.n_eff_mode0), format_num(row.n_group_mode0)]
        for row in width_df.itertuples(index=False)
    ]

    selected_keys = [
        "channel_count",
        "center_wavelength",
        "channel_spacing",
        "target_fsr",
        "awg_order_m",
        "actual_fsr",
        "delta_length",
        "arrayed_waveguide_count",
        "suggested_fpr_length",
        "suggested_array_pitch",
        "suggested_output_pitch",
        "minimum_bend_radius",
    ]
    param_rows = [
        [row.parameter, format_num(row.value), row.unit]
        for row in params_df[params_df["parameter"].isin(selected_keys)].itertuples(index=False)
    ]

    channel_rows = [
        [
            str(int(row.channel_id)),
            format_num(row.center_wavelength_nm, 1),
            format_num(row.center_frequency_THz, 4),
            row.notes,
        ]
        for row in channel_df.itertuples(index=False)
    ]

    final_length = lengths_df["relative_length_um"].iloc[-1]

    sections = [
        '<h1 class="title">EE588 Homework 3: Notebook Results Summary for a 4-Channel C-Band AWG</h1>',
        '<p class="meta">Compiled from waveguide_mode.ipynb, waveguide_width_sweep.ipynb, and awg_initial_design.ipynb</p>',
        f'<p class="meta">Date: {date.today().isoformat()}</p>',
        "<h2>1. Report Objective</h2>",
        paragraph(
            "This document consolidates the main results from the project notebooks into a homework-style report. "
            "The goal is to show how the baseline silicon strip waveguide MODE study was extended into a width sweep "
            "and then translated into a first-pass 4-channel C-band AWG design."
        ),
        "<h2>2. Notebook Scope and Workflow</h2>",
        bullets(
            [
                "waveguide_mode.ipynb established a baseline MODE solution for a 500 nm x 220 nm silicon strip waveguide in SiO2.",
                "waveguide_width_sweep.ipynb scanned widths from 0.40 um to 0.60 um at 1550 nm to extract n_eff and n_group.",
                "awg_initial_design.ipynb converted the width-sweep result into channel targets, FSR, diffraction order, and array-length estimates for a simplified AWG.",
            ]
        ),
        "<h2>3. Baseline MODE Result</h2>",
        paragraph(
            "The baseline notebook confirms that the selected silicon strip waveguide supports a fundamental guided mode near 1550 nm. "
            "The 0.50 um width case is used as the reference design point because it is already represented in the initial MODE run "
            "and sits near the middle of the width sweep range."
        ),
        make_table(["Item", "Value"], baseline_rows),
        "<h2>4. Width Sweep Results</h2>",
        paragraph(
            "A low-cost MODE sweep was run at 1550 nm for widths from 0.40 um to 0.60 um. "
            "The results show a monotonic increase in effective index and a gradual decrease in group index as the waveguide becomes wider."
        ),
        make_table(["Width (um)", "n_eff", "n_group"], sweep_rows),
        paragraph(
            "Based on these trends, 0.50 um is a practical first-pass choice. "
            f"It matches the earlier baseline result, avoids the extremes of the scan range, and provides n_eff = {format_num(selected['n_eff_mode0'])} "
            f"and n_group = {format_num(selected['n_group_mode0'])} for subsequent AWG calculations."
        ),
        "<h2>5. AWG Initial Design Results</h2>",
        paragraph(
            "The AWG design notebook maps the single-waveguide results into a simplified 4-channel C-band demultiplexer target. "
            "The design uses a 1550 nm center wavelength and 1.6 nm channel spacing, which is approximately 200 GHz near 1550 nm."
        ),
        make_table(["Parameter", "Value", "Unit"], param_rows),
        make_table(["Channel", "Center Wavelength (nm)", "Frequency (THz)", "Notes"], channel_rows),
        paragraph(
            "The calculated path-length ladder grows in nearly uniform steps of about 30.99 um, reaching a relative difference of "
            f"{format_num(final_length, 2)} um by the final arm. This makes the geometry easy to interpret and suitable for a first-pass AWG layout."
        ),
    ]

    if figures["available"]:
        figure_rows = [[name, "Generated by the notebook and kept in project/tidy3d_awg_project/results/figures/"] for name in figures["available"]]
        sections.extend(
            [
                "<h2>6. Related Figure Files</h2>",
                paragraph(
                    "The notebook-produced figures are preserved alongside this report. They are listed here because the macOS textutil conversion path used for this DOCX did not embed local images reliably."
                ),
                make_table(["Figure File", "Location Note"], figure_rows),
            ]
        )

    sections.extend(
        [
            "<h2>7. Conclusions and Next Steps</h2>",
            bullets(
                [
                    "The notebook sequence provides a clean path from single-waveguide MODE analysis to AWG parameter estimation.",
                    "The 0.50 um waveguide width remains the recommended baseline because it balances continuity, moderate index values, and reportability.",
                    "The first-pass AWG target is a 4-channel C-band demultiplexer with channel centers at 1547.6, 1549.2, 1550.8, and 1552.4 nm.",
                    "The next project step should be to validate the simplified geometry and then decide whether to continue with low-cost approximations or move into device-level simulation.",
                ]
            ),
        ]
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>EE588 Homework 3 Notebook Report</title>
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
      font-size: 26pt;
      font-weight: normal;
      text-align: center;
      margin: 0 0 4pt 0;
    }}
    h2 {{
      font-size: 16pt;
      font-weight: normal;
      margin: 20pt 0 6pt 0;
    }}
    p {{
      margin: 0 0 8pt 0;
    }}
    p.meta {{
      text-align: center;
      color: #555555;
      margin: 0 0 8pt 0;
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
    }}
    th {{
      background: #f2f4f7;
      text-align: center;
      font-weight: bold;
    }}
    td:first-child {{
      text-align: left;
    }}
    td {{
      text-align: center;
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
    DOCX_OUT.parent.mkdir(parents=True, exist_ok=True)
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
    html = build_html()
    out = convert_to_docx(html)
    print(out)
