"""Run a single-parameter HFSS study for patch-20G on jzh_server1."""

from __future__ import annotations

import csv
import json
import traceback
from pathlib import Path

import numpy as np
from ansys.aedt.core import Hfss
from ansys.aedt.core.generic.settings import settings


PROJECT_PATH = Path(r"D:\PROJECT\nonuniform_array_demo2\hfss\planar_array.aedt")
DESIGN_NAME = "patch-20G"
SETUP_NAME = "Setup1"
OUTPUT_DIR = Path(r"D:\PROJECT\nonuniform_array_demo2\.temp\patch20g_param_study")
SUMMARY_PATH = OUTPUT_DIR / "summary.json"
DETAIL_PATH = OUTPUT_DIR / "detailed_results.json"
CSV_PATH = OUTPUT_DIR / "summary_table.csv"
PROGRESS_LOG_PATH = OUTPUT_DIR / "progress.log"
ERROR_LOG_PATH = OUTPUT_DIR / "error.log"
TARGET_FREQUENCY_GHZ = 20.0
REFERENCE_IMPEDANCE_OHM = 50.0
SWEEP_PLAN = {
    "w1": ["3.9mm", "4.1mm", "4.3mm", "4.5mm", "4.7mm"],
    "w2": ["3.7mm", "3.9mm", "4.1mm", "4.3mm", "4.5mm"],
    "ls": ["1.6mm", "1.8mm", "2.0mm", "2.2mm", "2.4mm"],
    "ws": ["1.6mm", "1.8mm", "2.0mm", "2.2mm", "2.4mm"],
}


def complex_series(solution_data, expression: str) -> np.ndarray:
    """Return one complex-valued report expression."""

    _, real_values = solution_data.get_expression_data(expression=expression, formula="real")
    _, imag_values = solution_data.get_expression_data(expression=expression, formula="imag")
    return np.asarray(real_values, dtype=np.float64) + 1j * np.asarray(imag_values, dtype=np.float64)


def s_to_z(s11: np.ndarray, z0: float) -> np.ndarray:
    """Convert reflection coefficient to input impedance."""

    denominator = 1.0 - s11
    if np.any(np.isclose(np.abs(denominator), 0.0)):
        raise RuntimeError("Encountered singular S11 to Zin conversion.")
    return z0 * (1.0 + s11) / denominator


def db20(values: np.ndarray) -> np.ndarray:
    """Convert complex magnitude to dB."""

    magnitude = np.maximum(np.abs(values), 1e-15)
    return 20.0 * np.log10(magnitude)


def index_of_frequency(frequencies_ghz: np.ndarray, target_ghz: float) -> int:
    """Return the sweep index for the target frequency."""

    index = int(np.argmin(np.abs(frequencies_ghz - target_ghz)))
    if abs(float(frequencies_ghz[index]) - target_ghz) > 1e-9:
        raise RuntimeError(f"Target frequency {target_ghz} GHz is not present in the solved sweep.")
    return index


def find_best_match_frequency(frequencies_ghz: np.ndarray, s11_db: np.ndarray) -> tuple[float, float]:
    """Return the frequency and dB of the best S11 point."""

    best_index = int(np.argmin(s11_db))
    return float(frequencies_ghz[best_index]), float(s11_db[best_index])


def log_progress(message: str) -> None:
    """Append one progress line."""

    print(message, flush=True)
    with PROGRESS_LOG_PATH.open("a", encoding="utf-8") as progress_file:
        progress_file.write(message + "\n")


def collect_case_metrics(hfss: Hfss) -> dict:
    """Solve one case and collect S-parameter plus impedance metrics."""

    hfss.analyze(setup=SETUP_NAME)
    solution_data = hfss.post.get_solution_data(
        expressions=[
            "S(1:1,1:1)",
            "S(2:1,2:1)",
            "S(1:1,2:1)",
            "S(2:1,1:1)",
        ],
        setup_sweep_name=hfss.nominal_sweep,
    )
    if not solution_data:
        raise RuntimeError("Failed to read S-parameter solution data.")

    frequencies_ghz = np.asarray(solution_data.primary_sweep_values, dtype=np.float64).reshape(-1)
    if frequencies_ghz.size == 0:
        raise RuntimeError("The solved case did not return any frequency points.")

    s11 = complex_series(solution_data, "S(1:1,1:1)")
    s22 = complex_series(solution_data, "S(2:1,2:1)")
    s12 = complex_series(solution_data, "S(1:1,2:1)")
    s21 = complex_series(solution_data, "S(2:1,1:1)")
    if not all(series.size == frequencies_ghz.size for series in [s11, s22, s12, s21]):
        raise RuntimeError("S-parameter sample count mismatch.")

    s11_db = db20(s11)
    s22_db = db20(s22)
    s21_db = db20(s21)
    s12_db = db20(s12)
    z11 = s_to_z(s11, REFERENCE_IMPEDANCE_OHM)
    z22 = s_to_z(s22, REFERENCE_IMPEDANCE_OHM)
    target_index = index_of_frequency(frequencies_ghz, TARGET_FREQUENCY_GHZ)
    best_s11_frequency_ghz, best_s11_db = find_best_match_frequency(frequencies_ghz, s11_db)
    best_s22_frequency_ghz, best_s22_db = find_best_match_frequency(frequencies_ghz, s22_db)

    return {
        "target_frequency_ghz": TARGET_FREQUENCY_GHZ,
        "s11_db_at_target": float(s11_db[target_index]),
        "s22_db_at_target": float(s22_db[target_index]),
        "s21_db_at_target": float(s21_db[target_index]),
        "s12_db_at_target": float(s12_db[target_index]),
        "z11_real_ohm_at_target": float(np.real(z11[target_index])),
        "z11_imag_ohm_at_target": float(np.imag(z11[target_index])),
        "z22_real_ohm_at_target": float(np.real(z22[target_index])),
        "z22_imag_ohm_at_target": float(np.imag(z22[target_index])),
        "best_s11_frequency_ghz": best_s11_frequency_ghz,
        "best_s11_db": best_s11_db,
        "best_s22_frequency_ghz": best_s22_frequency_ghz,
        "best_s22_db": best_s22_db,
        "frequencies_ghz": frequencies_ghz.tolist(),
        "s11_db": s11_db.tolist(),
        "s22_db": s22_db.tolist(),
        "s21_db": s21_db.tolist(),
        "s12_db": s12_db.tolist(),
        "z11_real_ohm": np.real(z11).tolist(),
        "z11_imag_ohm": np.imag(z11).tolist(),
        "z22_real_ohm": np.real(z22).tolist(),
        "z22_imag_ohm": np.imag(z22).tolist(),
    }


def write_summary_csv(case_rows: list[dict]) -> None:
    """Write the compact tabular summary."""

    fieldnames = [
        "parameter",
        "value",
        "s11_db_at_20ghz",
        "s22_db_at_20ghz",
        "s21_db_at_20ghz",
        "z11_real_ohm_at_20ghz",
        "z11_imag_ohm_at_20ghz",
        "best_s11_frequency_ghz",
        "best_s11_db",
        "best_s22_frequency_ghz",
        "best_s22_db",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in case_rows:
            writer.writerow(row)


def main() -> None:
    """Execute the parameter study."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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
        baseline_values = {name: str(hfss[name]) for name in SWEEP_PLAN}
        hfss.analyze(setup=SETUP_NAME)
        freq_probe = hfss.post.get_solution_data(
            expressions=["S(1:1,1:1)"],
            setup_sweep_name=hfss.nominal_sweep,
        )
        if not freq_probe:
            raise RuntimeError("Failed to query baseline frequency sweep values.")
        frequencies_ghz = np.asarray(freq_probe.primary_sweep_values, dtype=np.float64).reshape(-1)
        if frequencies_ghz.size == 0:
            raise RuntimeError("No frequency points were returned.")
        frequency_unit = freq_probe.units_sweeps.get("Freq")
        if frequency_unit != "GHz":
            raise RuntimeError(f"Expected sweep unit GHz but got {frequency_unit!r}.")
        PROGRESS_LOG_PATH.write_text("", encoding="utf-8")
        ERROR_LOG_PATH.write_text("", encoding="utf-8")
        log_progress(f"Baseline values: {baseline_values}")
        detailed_results: dict[str, list[dict]] = {}
        case_rows: list[dict] = []
        for parameter_name, candidate_values in SWEEP_PLAN.items():
            detailed_results[parameter_name] = []
            for candidate_value in candidate_values:
                log_progress(f"CASE_START {parameter_name}={candidate_value}")
                hfss[parameter_name] = candidate_value
                metrics = collect_case_metrics(hfss)
                case_record = {
                    "parameter": parameter_name,
                    "value": candidate_value,
                    "baseline_value": baseline_values[parameter_name],
                    "metrics": metrics,
                }
                detailed_results[parameter_name].append(case_record)
                case_rows.append(
                    {
                        "parameter": parameter_name,
                        "value": candidate_value,
                        "s11_db_at_20ghz": metrics["s11_db_at_target"],
                        "s22_db_at_20ghz": metrics["s22_db_at_target"],
                        "s21_db_at_20ghz": metrics["s21_db_at_target"],
                        "z11_real_ohm_at_20ghz": metrics["z11_real_ohm_at_target"],
                        "z11_imag_ohm_at_20ghz": metrics["z11_imag_ohm_at_target"],
                        "best_s11_frequency_ghz": metrics["best_s11_frequency_ghz"],
                        "best_s11_db": metrics["best_s11_db"],
                        "best_s22_frequency_ghz": metrics["best_s22_frequency_ghz"],
                        "best_s22_db": metrics["best_s22_db"],
                    }
                )
                DETAIL_PATH.write_text(json.dumps(detailed_results, indent=2), encoding="utf-8")
                write_summary_csv(case_rows)
                log_progress(f"CASE_DONE {parameter_name}={candidate_value} S11@20={metrics['s11_db_at_target']:.2f}dB")
            hfss[parameter_name] = baseline_values[parameter_name]

        write_summary_csv(case_rows)
        summary = {
            "project": hfss.project_file,
            "design": hfss.design_name,
            "setup": SETUP_NAME,
            "nominal_sweep": hfss.nominal_sweep,
            "baseline_values": baseline_values,
            "target_frequency_ghz": TARGET_FREQUENCY_GHZ,
            "reference_impedance_ohm": REFERENCE_IMPEDANCE_OHM,
            "sweep_plan": SWEEP_PLAN,
            "summary_table_csv": str(CSV_PATH),
            "detail_json": str(DETAIL_PATH),
        }
        SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        DETAIL_PATH.write_text(json.dumps(detailed_results, indent=2), encoding="utf-8")
        log_progress("STUDY_COMPLETE")
        print(json.dumps(summary, indent=2), flush=True)
    finally:
        hfss.release_desktop(close_projects=True, close_desktop=False)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ERROR_LOG_PATH.write_text(traceback.format_exc(), encoding="utf-8")
        raise
