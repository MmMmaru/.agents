"""Export patch-20G simulation data on the remote HFSS host.

This script is intended to run on ``jzh_server1``. It avoids
``Hfss.get_antenna_data()`` because PyAEDT 0.25.1 with AEDT 2023.2
hits a far-field exporter bug for this project.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import scipy.io
from ansys.aedt.core import Hfss
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData
from ansys.aedt.core.visualization.advanced.farfield_visualization import export_pyaedt_antenna_metadata


PROJECT_PATH = Path(r"D:\PROJECT\nonuniform_array_demo2\hfss\planar_array.aedt")
DESIGN_NAME = "patch-20G"
SETUP_NAME = "Setup1"
SPHERE_NAME = "Infinite Sphere1"
OUTPUT_MAT_PATH = Path(r"D:\PROJECT\nonuniform_array_demo2\.temp\patch20g_dataset.mat")
OUTPUT_JSON_PATH = Path(r"D:\PROJECT\nonuniform_array_demo2\.temp\patch20g_dataset_summary.json")


def format_frequency_ghz(frequency_ghz: float) -> str:
    """Format one frequency value for AEDT."""

    return f"{float(frequency_ghz):.12g}GHz"


def build_uv_grid(theta_deg: np.ndarray, phi_deg: np.ndarray) -> np.ndarray:
    """Convert Theta/Phi sweep axes to the UV sample grid."""

    theta_grid, phi_grid = np.meshgrid(theta_deg, phi_deg, indexing="ij")
    theta_flat = theta_grid.reshape(-1)
    phi_flat = phi_grid.reshape(-1)
    u = np.sin(np.deg2rad(theta_flat)) * np.cos(np.deg2rad(phi_flat))
    v = np.sin(np.deg2rad(theta_flat)) * np.sin(np.deg2rad(phi_flat))
    return np.column_stack((u, v))


def main() -> None:
    """Run the full patch-20G solve and dataset export flow."""

    settings.use_grpc_api = None
    hfss = Hfss(
        project=str(PROJECT_PATH),
        design=DESIGN_NAME,
        solution_type="Modal",
        version="2023.2",
        non_graphical=True,
        new_desktop=False,
        close_on_exit=False,
        remove_lock=True,
    )
    try:
        hfss.analyze(setup=SETUP_NAME)

        s11_data = hfss.post.get_solution_data(
            expressions=["S(1:1,1:1)"],
            setup_sweep_name=hfss.nominal_sweep,
        )
        if s11_data is None:
            raise RuntimeError("Failed to query sweep frequencies from S(1:1,1:1).")

        raw_frequency_values = np.asarray(s11_data.primary_sweep_values, dtype=np.float64).reshape(-1)
        if raw_frequency_values.size == 0:
            raise RuntimeError("No sweep frequencies were returned by HFSS.")
        frequency_unit = s11_data.units_sweeps.get("Freq")
        if frequency_unit != "GHz":
            raise RuntimeError(f"Expected HFSS frequency unit 'GHz', got '{frequency_unit}'.")
        frequencies_ghz = raw_frequency_values.astype(np.float64)
        frequency_strings = [format_frequency_ghz(freq) for freq in frequencies_ghz]

        source_names = tuple(str(name) for name in hfss.excitation_names)
        if not source_names:
            raise RuntimeError("HFSS did not expose any excitation names.")
        active_port_names = tuple(name if name.endswith(":1") else f"{name}:1" for name in source_names)

        expressions = [
            f"S({source_name},{target_name})"
            for source_name in active_port_names
            for target_name in active_port_names
        ]
        s_data = hfss.post.get_solution_data(
            expressions=expressions,
            setup_sweep_name=hfss.nominal_sweep,
            variations={"Freq": frequency_strings},
        )
        if s_data is None:
            raise RuntimeError("Failed to query the full S-parameter matrix.")

        n_ports = len(active_port_names)
        n_freq = len(frequencies_ghz)
        s_matrix_complex = np.zeros((n_ports, n_ports, n_freq), dtype=np.complex128)
        for source_index, source_name in enumerate(active_port_names):
            for target_index, target_name in enumerate(active_port_names):
                expression = f"S({source_name},{target_name})"
                _, real_values = s_data.get_expression_data(expression=expression, formula="real")
                _, imag_values = s_data.get_expression_data(expression=expression, formula="imag")
                real_values = np.asarray(real_values, dtype=np.float64).reshape(-1)
                imag_values = np.asarray(imag_values, dtype=np.float64).reshape(-1)
                if real_values.size != n_freq or imag_values.size != n_freq:
                    raise RuntimeError(
                        f"Expression '{expression}' returned {real_values.size} real and "
                        f"{imag_values.size} imaginary samples, expected {n_freq}."
                    )
                s_matrix_complex[source_index, target_index, :] = real_values + 1j * imag_values

        if SPHERE_NAME not in [field_setup.name for field_setup in hfss.field_setups]:
            hfss.insert_infinite_sphere(
                phi_start=0,
                phi_stop=180,
                phi_step=5,
                theta_start=-180,
                theta_stop=180,
                theta_step=5,
                name=SPHERE_NAME,
            )

        export_folder = Path(hfss.working_directory) / "Setup1_Sweep-Infinite Sphere1"
        element_txt_path = export_folder / "element.txt"
        if not element_txt_path.is_file():
            export_ok = hfss.export_element_pattern(
                frequencies=frequency_strings,
                setup=hfss.nominal_sweep,
                sphere=SPHERE_NAME,
                variations={},
                element_name="element",
                output_dir=str(export_folder),
            )
            if not export_ok:
                raise RuntimeError("HFSS export_element_pattern returned False.")
        if not element_txt_path.is_file():
            raise RuntimeError(f"Missing exported element pattern index file: {element_txt_path}")

        metadata_path = Path(
            export_pyaedt_antenna_metadata(
                input_file=str(element_txt_path),
                output_dir=str(export_folder),
                variation="",
                model_info={},
                power={},
                touchstone_file="",
            )
        )
        if not metadata_path.is_file():
            raise RuntimeError(f"Failed to generate PyAEDT far-field metadata: {metadata_path}")

        farfield_data = FfdSolutionData(input_file=str(metadata_path))
        raw_farfield_store = getattr(farfield_data, "_FfdSolutionData__raw_data", None)
        if not isinstance(raw_farfield_store, dict) or not raw_farfield_store:
            raise RuntimeError("PyAEDT far-field metadata loader did not expose raw embedded pattern data.")

        ordered_source_names = list(farfield_data.all_element_names)
        if not ordered_source_names:
            raise RuntimeError("Far-field metadata does not contain any element names.")

        first_frequency_hz = float(farfield_data.frequencies[0])
        first_source_name = ordered_source_names[0]
        first_source_store = raw_farfield_store[first_source_name]
        if first_frequency_hz not in first_source_store:
            raise RuntimeError(f"Far-field store for '{first_source_name}' does not contain {first_frequency_hz} Hz.")
        first_frequency_store = first_source_store[first_frequency_hz]
        theta_deg = np.asarray(first_frequency_store["Theta"], dtype=np.float64).reshape(-1)
        phi_deg = np.asarray(first_frequency_store["Phi"], dtype=np.float64).reshape(-1)
        angles_uv = build_uv_grid(theta_deg=theta_deg, phi_deg=phi_deg)
        sample_count = angles_uv.shape[0]

        g_complex_all = np.zeros(
            (sample_count, 2, len(frequencies_ghz), len(ordered_source_names)),
            dtype=np.complex128,
        )
        for source_index, source_name in enumerate(ordered_source_names):
            source_store = raw_farfield_store.get(source_name)
            if not isinstance(source_store, dict):
                raise RuntimeError(f"Far-field store for source '{source_name}' is missing.")
            for frequency_index, frequency_hz in enumerate(farfield_data.frequencies):
                frequency_store = source_store.get(float(frequency_hz))
                if not isinstance(frequency_store, dict):
                    raise RuntimeError(
                        f"Far-field store for source '{source_name}' is missing {float(frequency_hz)} Hz."
                    )
                e_theta = np.asarray(frequency_store["rETheta"], dtype=np.complex128).reshape(-1)
                e_phi = np.asarray(frequency_store["rEPhi"], dtype=np.complex128).reshape(-1)
                if e_theta.size != sample_count or e_phi.size != sample_count:
                    raise RuntimeError("Far-field sample count changed across source/frequency slices.")
                g_complex_all[:, 0, frequency_index, source_index] = e_theta
                g_complex_all[:, 1, frequency_index, source_index] = e_phi

        scipy.io.savemat(
            OUTPUT_MAT_PATH,
            {
                "G_complex_all": g_complex_all,
                "S_matrix_complex": s_matrix_complex,
                "angles_uv": angles_uv,
                "Theta": theta_deg.reshape(-1, 1),
                "Phi": phi_deg.reshape(-1, 1),
                "frequencies_ghz": frequencies_ghz.reshape(-1, 1),
                "source_names": np.asarray(ordered_source_names, dtype=object).reshape(-1, 1),
            },
        )

        summary = {
            "project": hfss.project_name,
            "design": hfss.design_name,
            "nominal_sweep": hfss.nominal_sweep,
            "source_names": ordered_source_names,
            "frequencies_ghz": [float(value) for value in frequencies_ghz],
            "sample_count": int(sample_count),
            "g_complex_all_shape": list(g_complex_all.shape),
            "s_matrix_complex_shape": list(s_matrix_complex.shape),
            "export_folder": str(export_folder),
            "metadata_path": str(metadata_path),
            "output_mat_path": str(OUTPUT_MAT_PATH),
        }
        OUTPUT_JSON_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
    finally:
        hfss.release_desktop(close_projects=True, close_desktop=False)


if __name__ == "__main__":
    main()
