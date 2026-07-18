"""Build and solve a circularly polarized single-layer patch antenna in HFSS.

This script targets GOALS.md pending item #2:
- Center frequency: 2.4 GHz
- Return loss target: S11 < -10 dB at 2.4 GHz
- Axial ratio target: AR < 3 dB at 2.4 GHz
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class DesignConfig:
    """Store all geometric and simulation parameters for the CP patch model."""

    project_path: Path
    design_name: str
    setup_name: str
    sweep_name: str
    center_freq_ghz: float
    substrate_name: str
    substrate_epsr: float
    substrate_tand: float
    substrate_thickness_mm: float
    board_l_mm: float
    board_w_mm: float
    patch_l_mm: float
    patch_w_mm: float
    corner_trim_mm: float
    feed_w_mm: float
    feed_l_mm: float
    feed_offset_y_mm: float
    air_margin_mm: float
    max_passes: int
    max_delta_s: float
    sweep_start_ghz: float
    sweep_stop_ghz: float
    sweep_points: int
    non_graphical: bool
    visual_dir: Path


def build_default_config(project_root: Path) -> DesignConfig:
    """Return a conservative baseline configuration for 2.4 GHz CP patch design."""

    return DesignConfig(
        project_path=project_root / ".tmp" / "cp_patch_goal2.aedt",
        design_name="CPPatch_2p4G",
        setup_name="Setup1",
        sweep_name="Sweep1",
        center_freq_ghz=2.4,
        substrate_name="FR4_epoxy",
        substrate_epsr=4.4,
        substrate_tand=0.02,
        substrate_thickness_mm=1.6,
        board_l_mm=80.0,
        board_w_mm=80.0,
        patch_l_mm=29.2,
        patch_w_mm=29.2,
        corner_trim_mm=3.2,
        feed_w_mm=3.0,
        feed_l_mm=22.0,
        feed_offset_y_mm=4.0,
        air_margin_mm=25.0,
        max_passes=12,
        max_delta_s=0.02,
        sweep_start_ghz=2.0,
        sweep_stop_ghz=2.8,
        sweep_points=321,
        non_graphical=True,
        visual_dir=project_root / ".tmp" / "visual_qa",
    )


def _reset_project_artifacts(project_path: Path) -> None:
    """Remove stale AEDT artifacts so every run starts from a clean project state."""

    sidecar_results = project_path.with_suffix(project_path.suffix + "results")
    sidecar_lock = project_path.with_suffix(project_path.suffix + ".lock")

    if project_path.exists():
        project_path.unlink()
    if sidecar_lock.exists():
        sidecar_lock.unlink()
    if sidecar_results.exists():
        shutil.rmtree(sidecar_results, ignore_errors=True)
    for csv_file in project_path.parent.glob("Rpt_*.csv"):
        try:
            csv_file.unlink()
        except OSError:
            pass


def _export_visual_qa_images(hfss: object, output_dir: Path) -> Dict[str, str]:
    """Export top/isometric/port-closeup images for mandatory visual QA evidence."""

    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = {
        "top": output_dir / "top_view.jpg",
        "isometric": output_dir / "isometric_view.jpg",
        "port_closeup": output_dir / "port_closeup.jpg",
    }

    # Try native model snapshot API first (requires graphical AEDT).
    try:
        hfss.post.export_model_picture(
            full_name=str(image_paths["top"]),
            orientation="top",
            show_axis=True,
            show_grid=True,
            show_ruler=True,
            show_region="Default",
        )
        hfss.post.export_model_picture(
            full_name=str(image_paths["isometric"]),
            orientation="isometric",
            show_axis=True,
            show_grid=True,
            show_ruler=True,
            show_region="Default",
        )
        hfss.post.export_model_picture(
            full_name=str(image_paths["port_closeup"]),
            orientation="right",
            selections=["Ground", "PortSheet", "Patch"],
            show_axis=True,
            show_grid=True,
            show_ruler=True,
            show_region=False,
        )
    except Exception:
        # Fallback to plot-based export for non-graphical environments.
        hfss.post.plot_model_obj(
            show=False,
            export_path=str(image_paths["top"]),
            view="xy",
            show_grid=True,
            show_bounding=True,
        )
        hfss.post.plot_model_obj(
            show=False,
            export_path=str(image_paths["isometric"]),
            view="isometric",
            show_grid=True,
            show_bounding=True,
        )
        hfss.post.plot_model_obj(
            objects=["Ground", "PortSheet", "Patch"],
            show=False,
            export_path=str(image_paths["port_closeup"]),
            view="yz",
            show_grid=True,
            show_bounding=True,
        )

    return {key: str(path) for key, path in image_paths.items()}


def _safe_float(value: object) -> float:
    """Convert a value to float and return NaN when conversion fails."""

    try:
        return float(value)
    except (TypeError, ValueError):
        if isinstance(value, str):
            match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", value)
            if match:
                try:
                    return float(match.group(0))
                except ValueError:
                    return math.nan
        return math.nan


def _extract_y_series(solution_data: object) -> list[float]:
    """Extract a numeric Y-data series from SolutionData in a version-tolerant way."""

    if solution_data is None:
        return []

    try:
        raw = solution_data.data_db()
    except Exception:
        return []

    if isinstance(raw, dict):
        if not raw:
            return []
        first_key = next(iter(raw.keys()))
        return [_safe_float(item) for item in raw[first_key]]
    return [_safe_float(item) for item in raw]


def _extract_metric_at_frequency(solution_data: object, freq_ghz: float) -> float:
    """Extract Y value nearest to target frequency from a PyAEDT solution data object."""

    if solution_data is None:
        return math.nan

    try:
        primary_sweep = solution_data.primary_sweep_values
        data_db = _extract_y_series(solution_data)
    except Exception:
        return math.nan

    if not primary_sweep or not data_db:
        return math.nan

    best_index = min(
        range(len(primary_sweep)),
        key=lambda index: abs(_safe_float(primary_sweep[index]) - freq_ghz),
    )
    if best_index >= len(data_db):
        return math.nan
    return _safe_float(data_db[best_index])


def _freq_distance_to_target(freq_value: float, target_ghz: float) -> float:
    """Return nearest distance to target GHz after checking common frequency units."""

    candidates = [freq_value, freq_value / 1e3, freq_value / 1e6, freq_value / 1e9]
    return min(abs(item - target_ghz) for item in candidates)


def _extract_metric_from_report_csv(
    csv_path: Path,
    target_freq_ghz: float,
    y_hint: Optional[str] = None,
) -> float:
    """Parse HFSS report CSV and return Y value closest to target frequency."""

    samples: list[tuple[float, float]] = []
    with csv_path.open("r", encoding="utf-8-sig", errors="ignore", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, [])
        x_idx = 0
        y_idx = 1
        if header:
            for index, name in enumerate(header):
                if "Freq" in name:
                    x_idx = index
                    break
            if y_hint:
                for index, name in enumerate(header):
                    if y_hint in name:
                        y_idx = index
                        break
            else:
                y_idx = len(header) - 1 if len(header) > 1 else 0

        for row in reader:
            if len(row) <= max(x_idx, y_idx):
                continue
            x_val = _safe_float(row[x_idx])
            y_val = _safe_float(row[y_idx])
            if math.isnan(x_val) or math.isnan(y_val):
                continue
            samples.append((x_val, y_val))

    if not samples:
        return math.nan

    x_val, y_val = min(
        samples,
        key=lambda item: _freq_distance_to_target(item[0], target_freq_ghz),
    )
    _ = x_val
    return y_val


def _metric_from_report(
    hfss: object,
    report_name: str,
    expressions: list[str],
    setup_sweep_name: str,
    target_freq_ghz: float,
    project_dir: Path,
    report_category: Optional[str] = None,
    context: Optional[str] = None,
    variations: Optional[dict] = None,
) -> float:
    """Create a report, export CSV, and extract metric value near target frequency."""

    for expression in expressions:
        created = hfss.post.create_report(
            expressions=expression,
            setup_sweep_name=setup_sweep_name,
            variations=variations,
            report_category=report_category,
            context=context,
            plot_name=report_name,
        )
        if not created:
            continue

        exported = hfss.post.export_report_to_csv(str(project_dir), report_name)
        if not exported:
            continue
        csv_path = project_dir / f"{report_name}.csv"
        if not csv_path.exists():
            continue
        metric = _extract_metric_from_report_csv(csv_path, target_freq_ghz, y_hint=expression)
        if not math.isnan(metric):
            return metric
    return math.nan


def _axial_ratio_from_lhcp_rhcp(gain_lhcp_db: float, gain_rhcp_db: float) -> float:
    """Compute axial ratio in dB from LHCP/RHCP gains in dB."""

    if math.isnan(gain_lhcp_db) or math.isnan(gain_rhcp_db):
        return math.nan

    p_lhcp = 10 ** (gain_lhcp_db / 10.0)
    p_rhcp = 10 ** (gain_rhcp_db / 10.0)
    e_major = math.sqrt(max(p_lhcp, p_rhcp))
    e_minor = math.sqrt(min(p_lhcp, p_rhcp))
    if abs(e_major - e_minor) < 1e-12:
        return math.inf
    ar_linear = (e_major + e_minor) / (e_major - e_minor)
    return 20.0 * math.log10(ar_linear)


def _axial_ratio_boresight_from_report(
    hfss: object,
    project_dir: Path,
    setup_name: str,
    freq_ghz: float,
) -> float:
    """Extract boresight AR from direct HFSS expression dB(AxialRatioValue)."""

    report_name = "Rpt_AR_Boresight"
    created = hfss.post.create_report(
        expressions="dB(AxialRatioValue)",
        setup_sweep_name=f"{setup_name} : LastAdaptive",
        report_category="Far Fields",
        context="FFSphere",
        primary_sweep_variable="Theta",
        variations={"Freq": [f"{freq_ghz}GHz"], "Phi": ["0deg"]},
        plot_name=report_name,
    )
    if not created:
        return math.nan

    exported = hfss.post.export_report_to_csv(str(project_dir), report_name)
    if not exported:
        return math.nan

    csv_path = project_dir / f"{report_name}.csv"
    if not csv_path.exists():
        return math.nan

    samples: list[tuple[float, float]] = []
    with csv_path.open("r", encoding="utf-8-sig", errors="ignore", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, [])
        theta_idx = 0
        ar_idx = len(header) - 1 if header else 1
        for i, col in enumerate(header):
            if "Theta" in col:
                theta_idx = i
            if "AxialRatio" in col:
                ar_idx = i
        for row in reader:
            if len(row) <= max(theta_idx, ar_idx):
                continue
            theta = _safe_float(row[theta_idx])
            ar_db = _safe_float(row[ar_idx])
            if math.isnan(theta) or math.isnan(ar_db):
                continue
            samples.append((theta, ar_db))

    if not samples:
        return math.nan
    return min(samples, key=lambda item: abs(item[0] - 0.0))[1]


def run_design(config: DesignConfig) -> Dict[str, float]:
    """Build geometry, solve the model, and return key performance metrics."""

    try:
        from ansys.aedt.core import Hfss
    except ImportError as exc:
        raise RuntimeError(
            "PyAEDT is required. Install with: pip install pyaedt"
        ) from exc

    config.project_path.parent.mkdir(parents=True, exist_ok=True)
    _reset_project_artifacts(config.project_path)
    hfss = None

    try:
        hfss = Hfss(
            project=str(config.project_path),
            design=config.design_name,
            solution_type="Modal",
            non_graphical=config.non_graphical,
            new_desktop=True,
        )

        # Define core design variables for reproducible geometry.
        hfss["sub_h"] = f"{config.substrate_thickness_mm}mm"
        hfss["board_l"] = f"{config.board_l_mm}mm"
        hfss["board_w"] = f"{config.board_w_mm}mm"
        hfss["patch_l"] = f"{config.patch_l_mm}mm"
        hfss["patch_w"] = f"{config.patch_w_mm}mm"
        hfss["trim"] = f"{config.corner_trim_mm}mm"
        hfss["feed_w"] = f"{config.feed_w_mm}mm"
        hfss["feed_l"] = f"{config.feed_l_mm}mm"
        hfss["feed_off_y"] = f"{config.feed_offset_y_mm}mm"
        hfss["feed_overlap"] = "0.6mm"

        # Create substrate, ground, and radiating patch.
        substrate = hfss.modeler.create_box(
            origin=["-board_l/2", "-board_w/2", "0mm"],
            sizes=["board_l", "board_w", "sub_h"],
            name="Substrate",
            material=config.substrate_name,
        )
        ground = hfss.modeler.create_rectangle(
            orientation="XY",
            origin=["-board_l/2", "-board_w/2", "0mm"],
            sizes=["board_l", "board_w"],
            name="Ground",
        )
        patch = hfss.modeler.create_rectangle(
            orientation="XY",
            origin=["-patch_l/2", "-patch_w/2", "sub_h"],
            sizes=["patch_l", "patch_w"],
            name="Patch",
        )

        # Trim opposite corners to excite two orthogonal modes for CP behavior.
        trim_a = hfss.modeler.create_rectangle(
            orientation="XY",
            origin=["patch_l/2-trim", "patch_w/2-trim", "sub_h"],
            sizes=["trim", "trim"],
            name="TrimA",
            material="copper",
        )
        trim_b = hfss.modeler.create_rectangle(
            orientation="XY",
            origin=["-patch_l/2", "-patch_w/2", "sub_h"],
            sizes=["trim", "trim"],
            name="TrimB",
            material="copper",
        )
        hfss.modeler.subtract(patch, [trim_a, trim_b], keep_originals=False)

        # Build a microstrip feed line on top metal layer.
        feed = hfss.modeler.create_rectangle(
            orientation="XY",
            origin=["-patch_l/2-feed_l+feed_overlap", "feed_off_y-feed_w/2", "sub_h"],
            sizes=["feed_l", "feed_w"],
            name="FeedLine",
        )
        hfss.modeler.unite([patch, feed])

        # Enforce explicit conductor boundaries for metal layers (2D sheet model).
        hfss.assign_perfecte_to_sheets(
            assignment=[ground.name],
            name="Ground_Cond",
            is_infinite_ground=False,
        )
        hfss.assign_perfecte_to_sheets(
            assignment=[patch.name],
            name="PatchFeed_Cond",
            is_infinite_ground=False,
        )

        # Create a local lumped port sheet at feed entrance.
        port_sheet = hfss.modeler.create_rectangle(
            orientation="YZ",
            origin=["-patch_l/2-feed_l+feed_overlap", "feed_off_y-feed_w/2", "0mm"],
            sizes=["feed_w", "sub_h"],
            name="PortSheet",
        )
        port = hfss.lumped_port(
            assignment=port_sheet.name,
            reference=ground.name,
            integration_line=hfss.AxisDir.ZNeg,
            name="P1",
        )
        if not port:
            raise RuntimeError("Failed to create lumped port P1.")

        # Create open-region radiation boundary with a frequency-aware airbox.
        hfss.create_open_region(
            frequency=f"{config.center_freq_ghz}GHz",
            boundary="Radiation",
        )

        # Configure driven setup and frequency sweep.
        setup = hfss.create_setup(
            name=config.setup_name,
            setup_type="HFSSDriven",
            Frequency=f"{config.center_freq_ghz}GHz",
            MaximumPasses=config.max_passes,
            MaxDeltaS=config.max_delta_s,
        )
        setup.create_frequency_sweep(
            unit="GHz",
            name=config.sweep_name,
            start_frequency=config.sweep_start_ghz,
            stop_frequency=config.sweep_stop_ghz,
            num_of_freq_points=config.sweep_points,
            sweep_type="Interpolating",
        )

        # Create far-field sphere for AR evaluation.
        hfss.insert_infinite_sphere(
            name="FFSphere",
            x_start=0,
            x_stop=360,
            x_step=2,
            y_start=-90,
            y_stop=90,
            y_step=2,
        )

        validation_lines, validation_ok = hfss.validate_full_design()
        print("Validation summary:", validation_ok)
        for line in validation_lines:
            print(line)
        if not validation_ok:
            raise RuntimeError("HFSS validation failed before solve.")

        solved = hfss.analyze_setup(config.setup_name)
        if not solved:
            raise RuntimeError("HFSS solve failed for Setup1. Model is not ready for tuning.")
        hfss.save_project()
        visual_images = _export_visual_qa_images(hfss, config.visual_dir)

        # Extract return loss around 2.4 GHz.
        setup_sweep = f"{config.setup_name} : {config.sweep_name}"
        s11_at_center = _metric_from_report(
            hfss=hfss,
            report_name="Rpt_S11_2p4",
            expressions=["dB(S(P1,P1))", "dB(S(1,1))"],
            setup_sweep_name=setup_sweep,
            target_freq_ghz=config.center_freq_ghz,
            project_dir=config.project_path.parent,
        )

        # Extract axial ratio directly from HFSS AR expression at boresight.
        ar_at_center = _axial_ratio_boresight_from_report(
            hfss=hfss,
            project_dir=config.project_path.parent,
            setup_name=config.setup_name,
            freq_ghz=config.center_freq_ghz,
        )

        return {
            "s11_db_at_2p4": s11_at_center,
            "ar_db_at_2p4": ar_at_center,
            "target_s11_db": -10.0,
            "target_ar_db": 3.0,
            "visual_top": visual_images["top"],
            "visual_isometric": visual_images["isometric"],
            "visual_port_closeup": visual_images["port_closeup"],
        }
    finally:
        if hfss is not None:
            hfss.release_desktop(close_projects=True)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line options for headless or GUI HFSS execution."""

    parser = argparse.ArgumentParser(
        description="Create and solve a 2.4 GHz single-layer circularly polarized patch in HFSS."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path used to place .tmp output project.",
    )
    parser.add_argument(
        "--graphical",
        action="store_true",
        help="Run HFSS in graphical mode for manual inspection.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Run design generation and print metric summary for GOALS verification."""

    args = parse_args(argv)
    config = build_default_config(args.project_root)
    config.non_graphical = not args.graphical
    metrics = run_design(config)
    print("Design metrics:", metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
