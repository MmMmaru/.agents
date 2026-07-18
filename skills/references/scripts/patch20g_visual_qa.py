"""Export baseline or candidate geometry snapshots for patch-20G.

This script is intended to run on ``jzh_server1`` with graphical AEDT enabled.
It captures top, isometric, and front views for a selected parameter set so
that geometry, feed, and port continuity can be checked before and after tuning.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ansys.aedt.core import Hfss
from ansys.aedt.core.generic.settings import settings


PROJECT_PATH = Path(r"D:\PROJECT\nonuniform_array_demo2\hfss\planar_array.aedt")
DESIGN_NAME = "patch-20G"
OUTPUT_DIR = Path(r"D:\PROJECT\nonuniform_array_demo2\.temp\patch20g_visual_qa")


def main() -> None:
    """Open the design, optionally apply variables, and export screenshots."""

    settings.use_grpc_api = None
    hfss = Hfss(
        project=str(PROJECT_PATH),
        design=DESIGN_NAME,
        solution_type="Modal",
        version="2023.2",
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        remove_lock=True,
    )
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        tag = os.environ.get("PATCH20G_QA_TAG", "baseline").strip() or "baseline"
        variable_json = os.environ.get("PATCH20G_QA_VARIABLES_JSON", "").strip()
        variables = json.loads(variable_json) if variable_json else {}
        if not isinstance(variables, dict):
            raise RuntimeError("PATCH20G_QA_VARIABLES_JSON must decode to a JSON object.")

        for variable_name, variable_value in variables.items():
            hfss[variable_name] = str(variable_value)

        object_names = set(hfss.modeler.object_names)
        selections = [
            name
            for name in ["Patch1", "Patch2", "port1", "port2", "substrate", "Ground", "gnd"]
            if name in object_names
        ]
        if not selections:
            selections = None

        image_paths = {
            "isometric": OUTPUT_DIR / f"{tag}_isometric.jpg",
            "top": OUTPUT_DIR / f"{tag}_top.jpg",
            "front": OUTPUT_DIR / f"{tag}_front.jpg",
        }
        for orientation, image_path in image_paths.items():
            hfss.post.export_model_picture(
                full_name=str(image_path),
                orientation=orientation,
                selections=selections,
                show_axis=True,
                show_grid=False,
                show_ruler=False,
                width=1800,
                height=1300,
            )

        summary = {
            "project": hfss.project_file,
            "design": hfss.design_name,
            "tag": tag,
            "variables": {key: str(value) for key, value in variables.items()},
            "selections": selections,
            "images": {key: str(path) for key, path in image_paths.items()},
            "exists": {key: path.is_file() for key, path in image_paths.items()},
        }
        summary_path = OUTPUT_DIR / f"{tag}_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
    finally:
        hfss.release_desktop(close_projects=True, close_desktop=False)


if __name__ == "__main__":
    main()
