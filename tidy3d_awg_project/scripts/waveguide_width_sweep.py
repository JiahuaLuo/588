import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tidy3d as td
import tidy3d.web as web
from tidy3d.constants import C_0


# =========================
# Basic sweep configuration
# =========================
# Sweep waveguide width while keeping height fixed.
WIDTHS_UM = [0.40, 0.45, 0.50, 0.55, 0.60]
CORE_THICKNESS_UM = 0.22
WAVELENGTH_UM = 1.55

# Refractive indices for a simple silicon strip waveguide model.
CORE_N = 3.48
CLAD_N = 1.44

# Keep the MODE simulation region modest to reduce cost.
SIM_SIZE_Y_UM = 4.0
SIM_SIZE_Z_UM = 3.0
MIN_STEPS_PER_WVL = 20
NUM_MODES = 4

# Output paths.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "mode_width_sweep"
CSV_PATH = PROJECT_ROOT / "results" / "tables" / "waveguide_width_sweep_results.csv"
PLOT_PATH = PROJECT_ROOT / "results" / "figures" / "neff_vs_width.png"


def build_materials():
    """Define cladding and core materials."""
    clad_medium = td.Medium(
        name="SiO2_cladding",
        permittivity=CLAD_N**2,
    )
    core_medium = td.Medium(
        name="Silicon_core",
        permittivity=CORE_N**2,
    )
    return clad_medium, core_medium


def build_waveguide(width_um, core_medium):
    """Create an infinitely long strip waveguide along the x direction."""
    return td.Structure(
        geometry=td.Box(size=[td.inf, width_um, CORE_THICKNESS_UM]),
        name=f"silicon_waveguide_{width_um:.2f}um",
        medium=core_medium,
    )


def build_mode_simulation(width_um):
    """Create a low-cost MODE simulation for one waveguide width."""
    clad_medium, core_medium = build_materials()
    waveguide = build_waveguide(width_um, core_medium)
    freq0 = C_0 / WAVELENGTH_UM

    sim = td.ModeSimulation(
        plane=td.Box(size=[0, SIM_SIZE_Y_UM, SIM_SIZE_Z_UM]),
        freqs=[freq0],
        mode_spec=td.ModeSpec(
            num_modes=NUM_MODES,
            group_index_step=True,
        ),
        size=[0, SIM_SIZE_Y_UM, SIM_SIZE_Z_UM],
        boundary_spec=td.BoundarySpec(
            x=td.Boundary.pml(),
            y=td.Boundary.pml(),
            z=td.Boundary.pml(),
        ),
        grid_spec=td.GridSpec.auto(
            min_steps_per_wvl=MIN_STEPS_PER_WVL,
            wavelength=WAVELENGTH_UM,
        ),
        medium=clad_medium,
        structures=[waveguide],
    )
    return sim


def extract_mode_results(sim_data):
    """Extract fundamental-mode effective index and optional group index."""
    modes = sim_data.modes_raw

    # The user requested explicit extraction from np.real(modes.n_complex).
    n_eff_all = np.real(modes.n_complex)
    n_eff_0 = float(n_eff_all.values[0, 0])

    n_group_0 = None
    if hasattr(modes, "n_group") and modes.n_group is not None:
        try:
            n_group_0 = float(modes.n_group.values[0, 0])
        except Exception:
            n_group_0 = None
    elif hasattr(modes, "n_group_raw") and modes.n_group_raw is not None:
        try:
            n_group_0 = float(modes.n_group_raw.values[0, 0])
        except Exception:
            n_group_0 = None

    return modes, n_eff_0, n_group_0


def save_results_csv(rows):
    """Write sweep results to a CSV file in the project root."""
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "width_um",
                "height_um",
                "wavelength_um",
                "n_eff_mode0",
                "n_group_mode0",
                "task_name",
                "hdf5_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def plot_neff_vs_width(rows):
    """Generate and save a simple neff vs width figure."""
    widths = [row["width_um"] for row in rows]
    neff_values = [row["n_eff_mode0"] for row in rows]

    plt.figure(figsize=(6, 4))
    plt.plot(widths, neff_values, marker="o", linewidth=1.8)
    plt.xlabel("Waveguide width (um)")
    plt.ylabel("Fundamental mode n_eff at 1.55 um")
    plt.title("n_eff vs Silicon Waveguide Width")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=200)
    plt.close()


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for width_um in WIDTHS_UM:
        sim = build_mode_simulation(width_um)

        width_label = f"{int(round(width_um * 1000)):03d}nm"
        task_name = f"silicon_strip_mode_width_{width_label}_1550nm"
        hdf5_path = DATA_DIR / f"waveguide_mode_width_{width_label}.hdf5"

        print(f"Running MODE sweep for width = {width_um:.2f} um")
        print(f"Task name: {task_name}")

        sim_data = web.run(
            sim,
            task_name=task_name,
            path=str(hdf5_path),
        )

        modes, n_eff_0, n_group_0 = extract_mode_results(sim_data)
        print("modes_raw extracted successfully")
        print(f"Fundamental mode n_eff = {n_eff_0:.6f}")
        if n_group_0 is not None:
            print(f"Fundamental mode n_group = {n_group_0:.6f}")
        else:
            print("Fundamental mode n_group not available in this result")

        rows.append(
            {
                "width_um": width_um,
                "height_um": CORE_THICKNESS_UM,
                "wavelength_um": WAVELENGTH_UM,
                "n_eff_mode0": n_eff_0,
                "n_group_mode0": n_group_0 if n_group_0 is not None else "",
                "task_name": task_name,
                "hdf5_path": str(hdf5_path.relative_to(PROJECT_ROOT)),
            }
        )

        # Keep a local variable named exactly as requested for readability.
        _ = modes

    save_results_csv(rows)
    plot_neff_vs_width(rows)

    print()
    print("Width sweep finished.")
    print(f"CSV saved to: {CSV_PATH}")
    print(f"Plot saved to: {PLOT_PATH}")
    print("This workflow uses MODE only, so the credit cost should stay much lower than FDTD.")


if __name__ == "__main__":
    main()
