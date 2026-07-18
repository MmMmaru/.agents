"""Optimize a circularly polarized single-layer patch antenna for GOALS.md item #2.

The script performs a bounded parameter sweep and selects the best candidate
that satisfies both:
- S11(2.4 GHz) < -10 dB
- AR(2.4 GHz) < 3 dB
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Candidate:
    """Represent one optimization candidate and its performance metrics."""

    patch_l_mm: float
    patch_w_mm: float
    corner_trim_mm: float
    feed_l_mm: float
    feed_offset_y_mm: float
    feed_w_mm: float
    feed_overlap_mm: float
    s11_db: float = math.nan
    ar_db: float = math.nan

    def score(self) -> float:
        """Compute penalty score; smaller is better, with hard target penalties."""

        s11_penalty = max(0.0, self.s11_db - (-10.0))
        ar_penalty = max(0.0, self.ar_db - 3.0)
        return s11_penalty * 3.0 + ar_penalty * 5.0

    def meets_targets(self) -> bool:
        """Return True when this candidate satisfies both electrical targets."""

        return self.s11_db < -10.0 and self.ar_db < 3.0


@dataclass
class OptimizeConfig:
    """Store reusable optimization settings and path configuration."""

    project_root: Path
    design_script: Path
    max_candidates: int
    visual_dir: Path


def _safe_float(value: object) -> float:
    """Convert value to float safely, returning NaN on parsing failure."""

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
    """Extract numeric Y-axis data from solution data object."""

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
    """Extract nearest metric sample from PyAEDT solution data at target frequency."""

    if solution_data is None:
        return math.nan

    try:
        sweep = solution_data.primary_sweep_values
        data = _extract_y_series(solution_data)
    except Exception:
        return math.nan

    if not sweep or not data:
        return math.nan

    best_index = min(
        range(len(sweep)),
        key=lambda idx: abs(_safe_float(sweep[idx]) - freq_ghz),
    )
    if best_index >= len(data):
        return math.nan
    return _safe_float(data[best_index])


def _freq_distance_to_target(freq_value: float, target_ghz: float) -> float:
    """Return nearest distance to target GHz after checking common unit scales."""

    candidates = [freq_value, freq_value / 1e3, freq_value / 1e6, freq_value / 1e9]
    return min(abs(item - target_ghz) for item in candidates)


def _extract_metric_from_report_csv(
    csv_path: Path,
    target_freq_ghz: float,
    y_hint: Optional[str] = None,
) -> float:
    """Parse exported report CSV and return Y metric closest to target frequency."""

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

    _, y_val = min(
        samples,
        key=lambda item: _freq_distance_to_target(item[0], target_freq_ghz),
    )
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
    """Create report, export CSV, and read metric near target frequency."""

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
    """Compute AR(dB) from LHCP/RHCP gains in dB."""

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


def _axial_ratio_boresight_from_report(hfss: object, project_dir: Path) -> float:
    """Extract boresight AR from direct HFSS expression dB(AxialRatioValue)."""

    report_name = "Rpt_Opt_AR_Boresight"
    created = hfss.post.create_report(
        expressions="dB(AxialRatioValue)",
        setup_sweep_name="Setup1 : LastAdaptive",
        report_category="Far Fields",
        context="FFSphere",
        primary_sweep_variable="Theta",
        variations={"Freq": ["2.4GHz"], "Phi": ["0deg"]},
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


def _candidate_grid() -> Iterable[Candidate]:
    """Yield candidates prioritized by distance to the current near-feasible baseline."""

    baseline = {
        "patch_l_mm": 29.2,
        "patch_w_mm": 29.2,
        "corner_trim_mm": 3.2,
        "feed_l_mm": 22.5,
        "feed_offset_y_mm": 4.0,
        "feed_w_mm": 3.0,
        "feed_overlap_mm": 0.6,
    }
    patch_l_values = [29.1, 29.2, 29.3, 29.4]
    patch_w_values = [29.1, 29.2, 29.3, 29.4]
    trim_values = [3.0, 3.1, 3.2, 3.3]
    feed_l_values = [22.2, 22.4, 22.6, 22.8]
    feed_off_y_values = [3.5, 4.0, 4.5]
    feed_w_values = [2.9, 3.0, 3.1]
    feed_overlap_values = [0.2, 0.4, 0.6, 0.8, 1.0]

    candidates = []
    for patch_l, patch_w, trim, feed_l, feed_off_y, feed_w, feed_overlap in itertools.product(
        patch_l_values,
        patch_w_values,
        trim_values,
        feed_l_values,
        feed_off_y_values,
        feed_w_values,
        feed_overlap_values,
    ):
        candidate = Candidate(
            patch_l_mm=patch_l,
            patch_w_mm=patch_w,
            corner_trim_mm=trim,
            feed_l_mm=feed_l,
            feed_offset_y_mm=feed_off_y,
            feed_w_mm=feed_w,
            feed_overlap_mm=feed_overlap,
        )
        distance = (
            abs(candidate.patch_l_mm - baseline["patch_l_mm"]) / 0.05
            + abs(candidate.patch_w_mm - baseline["patch_w_mm"]) / 0.05
            + abs(candidate.corner_trim_mm - baseline["corner_trim_mm"]) / 0.2
            + abs(candidate.feed_l_mm - baseline["feed_l_mm"]) / 0.2
            + abs(candidate.feed_offset_y_mm - baseline["feed_offset_y_mm"]) / 0.5
            + abs(candidate.feed_w_mm - baseline["feed_w_mm"]) / 0.2
            + abs(candidate.feed_overlap_mm - baseline["feed_overlap_mm"]) / 0.2
        )
        candidates.append((distance, candidate))

    for _, candidate in sorted(candidates, key=lambda item: item[0]):
        yield candidate


def evaluate_candidate(hfss: object, candidate: Candidate) -> Candidate:
    """Apply candidate variables, solve setup, and update candidate metrics."""

    hfss["patch_l"] = f"{candidate.patch_l_mm}mm"
    hfss["patch_w"] = f"{candidate.patch_w_mm}mm"
    hfss["trim"] = f"{candidate.corner_trim_mm}mm"
    hfss["feed_l"] = f"{candidate.feed_l_mm}mm"
    hfss["feed_off_y"] = f"{candidate.feed_offset_y_mm}mm"
    hfss["feed_w"] = f"{candidate.feed_w_mm}mm"
    hfss["feed_overlap"] = f"{candidate.feed_overlap_mm}mm"
    hfss.analyze_setup("Setup1")

    project_dir = Path(hfss.project_path).parent
    candidate.s11_db = _metric_from_report(
        hfss=hfss,
        report_name="Rpt_Opt_S11",
        expressions=["dB(S(P1,P1))", "dB(S(1,1))"],
        setup_sweep_name="Setup1 : Sweep1",
        target_freq_ghz=2.4,
        project_dir=project_dir,
    )
    candidate.ar_db = _axial_ratio_boresight_from_report(
        hfss=hfss,
        project_dir=project_dir,
    )
    return candidate


def run_optimization(config: OptimizeConfig) -> Dict[str, object]:
    """Run bounded sweep optimization on the design created by the design script."""

    try:
        from ansys.aedt.core import Hfss
    except ImportError as exc:
        raise RuntimeError(
            "PyAEDT is required. Install with: pip install pyaedt"
        ) from exc

    project_path = config.project_root / ".tmp" / "cp_patch_goal2.aedt"
    for csv_file in project_path.parent.glob("Rpt_*.csv"):
        try:
            csv_file.unlink()
        except OSError:
            pass
    hfss = None
    tried: List[Candidate] = []

    try:
        hfss = Hfss(
            project=str(project_path),
            design="CPPatch_2p4G",
            solution_type="Modal",
            non_graphical=True,
            new_desktop=True,
        )
        if "Setup1" not in hfss.setup_names:
            raise RuntimeError(
                "Setup1 is missing in project. Run the design script first to regenerate and save setup/sweep."
            )
        required_views = [
            config.visual_dir / "top_view.jpg",
            config.visual_dir / "isometric_view.jpg",
            config.visual_dir / "port_closeup.jpg",
        ]
        missing_views = [str(item) for item in required_views if not item.exists()]
        if missing_views:
            raise RuntimeError(
                "Baseline visual QA is missing. Export required views first: "
                + ", ".join(missing_views)
            )
        boundary_names = {item.name for item in getattr(hfss, "boundaries", [])}
        required_boundaries = {"Ground_Cond", "PatchFeed_Cond"}
        missing = required_boundaries - boundary_names
        if missing:
            raise RuntimeError(
                f"Missing conductor boundaries: {sorted(missing)}. "
                "Run the design script to rebuild explicit metal boundaries."
            )

        for index, candidate in enumerate(_candidate_grid()):
            if index >= config.max_candidates:
                break
            evaluated = evaluate_candidate(hfss, candidate)
            tried.append(evaluated)
            print(
                f"[{index + 1}] "
                f"L={evaluated.patch_l_mm:.2f} "
                f"W={evaluated.patch_w_mm:.2f} "
                f"trim={evaluated.corner_trim_mm:.2f} "
                f"feed={evaluated.feed_l_mm:.2f} "
                f"offY={evaluated.feed_offset_y_mm:.2f} "
                f"feedW={evaluated.feed_w_mm:.2f} "
                f"ovl={evaluated.feed_overlap_mm:.2f} "
                f"S11={evaluated.s11_db:.2f}dB "
                f"AR={evaluated.ar_db:.2f}dB"
            )

        if not tried:
            raise RuntimeError("No optimization candidates were evaluated.")

        best = min(tried, key=lambda item: item.score())
        return {
            "candidate_count": len(tried),
            "best_candidate": {
                "patch_l_mm": best.patch_l_mm,
                "patch_w_mm": best.patch_w_mm,
                "corner_trim_mm": best.corner_trim_mm,
                "feed_l_mm": best.feed_l_mm,
                "feed_offset_y_mm": best.feed_offset_y_mm,
                "feed_w_mm": best.feed_w_mm,
                "feed_overlap_mm": best.feed_overlap_mm,
                "s11_db": best.s11_db,
                "ar_db": best.ar_db,
                "meets_targets": best.meets_targets(),
            },
        }
    finally:
        if hfss is not None:
            hfss.release_desktop(close_projects=True)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line options for bounded optimization execution."""

    parser = argparse.ArgumentParser(
        description="Optimize the 2.4 GHz CP single-layer patch model."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=64,
        help="Maximum number of candidate points to evaluate.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Run optimization and print best candidate summary."""

    args = parse_args(argv)
    config = OptimizeConfig(
        project_root=args.project_root,
        design_script=args.project_root
        / "Antenna-design"
        / "cp_single_layer_patch_design.py",
        max_candidates=args.max_candidates,
        visual_dir=args.project_root / ".tmp" / "visual_qa",
    )
    result = run_optimization(config)
    print("Optimization summary:", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
