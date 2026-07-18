---
name: antenna-design
description: Use this skill when the user wants end-to-end HFSS antenna design workflows (build geometry, assign boundaries/excitations, create setup/sweeps, solve, and collect reports) using the sibling PyAEDT references folder.
---

# Antenna Design Skill

## When to use
- User asks to build or modify an HFSS antenna model.
- User needs a reproducible design flow from project open to solved results.
- User asks for boundary/excitation/setup scripting in PyAEDT.

## Workflow
1. Start from [`../references/files/INDEX.md`](../references/files/INDEX.md) and map the request to the 7-step flow.
2. For each step, open only the needed reference file(s) under [`../references/files/`](../references/files/).
3. Use APIs from these references to produce executable PyAEDT scripts.
4. Prefer minimal robust calls over large helper wrappers.
5. Always close HFSS/AEDT sessions at the end of execution to avoid project lock and process leaks.
6. Run a visual QA loop on geometry/port/boundary screenshots before finalizing results.

## Execution mode guard
- If the user asks for direct execution (for example "directly call Python"), run Python in terminal immediately instead of creating script files.
- Only generate `.py` files when the user explicitly asks for file deliverables.
- When executing directly, still keep the same 6-step runnable order in the command/session output.

## Mandatory teardown guard
- After design/solve/report steps, always release HFSS in a `finally` block.
- Use version-safe API call: `hfss.release_desktop(close_projects=True)`.
- Do not pass `close_on_exit` to `release_desktop` unless version support is verified.
- If residual `ansysedt` or `ansyscl` processes remain after release, terminate them and re-check process list.

## Mandatory artifact retention guard
- Default behavior: keep output minimal and deterministic; do not leave probe/debug projects unless explicitly requested.
- When the user specifies a keep-list (for example only one `.aedt` file), delete all non-listed generated artifacts:
  - `.aedtresults/`, `.pyaedt/`, `.lock`, temporary CSV/log files, probe projects.
- Perform cleanup after successful teardown so files are not locked by AEDT.
- Before completion, report:
  - retained artifacts,
  - removed artifact count,
  - remaining top-level files in the output folder.

## Mandatory visual QA guard
- The agent must inspect model images (user-provided or self-exported) and explicitly report geometry/port issues before claiming completion.
- If a screenshot is not available, export at least:
  - isometric overview,
  - top view,
  - port close-up with excitation sheet/integration line.
- If API-based export is unavailable, use manual screenshot capture and continue QA.
- Visual QA is blocking: do not claim "done" until visual checks pass or issues are reported with fixes.
- Visual QA evidence is mandatory in every "model confirmation" response:
  - image source used,
  - pass/fail status,
  - issue list with confidence,
  - concrete PyAEDT/HFSS fix actions.
- If only one isometric image is available and port geometry is ambiguous, result must be `VISUAL_QA = FAIL (insufficient evidence)` and the agent must request/export the required extra views.

## Visual QA hard gate for direct execution
- For direct terminal execution, numeric simulation output alone is never sufficient for completion.
- Before any "design complete", "optimization complete", or target pass/fail statement, the agent must:
  1. export or capture `Top view`, `Isometric view`, and `Port close-up`,
  2. inspect those images,
  3. include explicit `VISUAL_QA = PASS|FAIL` in the response.
- If image export fails, the run is considered incomplete and must be reported as blocked until image evidence is available.
- Do not continue to optimization stage when the baseline model has not passed visual QA checks.

## Visual QA checklist
- Port placement:
  - Port sheet must be at the intended excitation plane, not stretched along the feed trace.
  - Port must correctly connect signal conductor and reference conductor across the dielectric path.
  - Integration direction must be physically meaningful for the chosen port type.
- Feed and patch connectivity:
  - Feed trace must connect to patch as intended (direct/inset/coupled), with no accidental gap/overlap.
  - Trace width transition near patch edge must be intentional.
- Stackup and region sanity:
  - Patch/ground/substrate alignment must be consistent in XY and Z.
  - Air/radiation region clearance should be sufficient around radiating edges.
- Boundary and far-field sanity:
  - Radiation/open region should enclose the full antenna structure.
  - Far-field setup should be compatible with boundary and solved setup.

## Mandatory port and feedline correction guard
- If the user reports port/feedline errors, the agent must:
  1. rebuild or replace the excitation definition (not only retune unrelated variables),
  2. explicitly set and verify feedline-length variable,
  3. run at least one post-fix solve check before claiming success.
- Reject any model state where the port visually spans along the feedline instead of a local excitation cross-section.
- If feedline length is changed for direct-feed patch topology, enforce feed-patch continuity:
  - `Patch1_position_x = top_line_IYC_position_x + top_line_IYC_length` (or equivalent geometric constraint),
  - unless the user explicitly requests inset/coupled/gap-fed topology.
- Enforce feedline-on-substrate constraint:
  - feedline projection must not exceed substrate/ground projection,
  - update substrate origin/length expressions when feedline/patch continuity updates would otherwise push feed outside the board.

## Mandatory metal boundary guard
- Ground, patch, and feed conductors must have explicit electromagnetic boundary definition.
- Do not rely on conductor material assignment alone for final sign-off.
- For 2D sheet metal modeling, do not treat "copper material assigned" as a validity check.
- In 2D topology, boundary assignment is the primary electromagnetic definition for conductors.
- For sheet-based metal topology, explicitly assign conductor boundary (for example `Perfect E`) to:
  - ground metal sheet,
  - patch metal sheet,
  - feedline metal sheet.
- If a non-PEC conductor model is intentionally used, the response must explicitly state:
  - which boundary/model replaces `Perfect E`,
  - why it is physically appropriate for the current target.
- Any run without explicit metal boundary confirmation must be reported as incomplete.

## Image-first debugging mode
- If the user provides an image, first perform visual diagnosis from that image before changing parameters.
- Output must include:
  - suspected issue list,
  - confidence level per issue (high/medium/low),
  - direct fix actions mapped to HFSS/PyAEDT operations.

## Prompt hint for visual confirmation
Use this fixed prompt pattern before declaring model correctness:

`Visual confirmation checklist (must pass all):`
1. `Top view` reviewed: feed-patch connection and overlap/gap status.
2. `Port close-up` reviewed: port cross-section, reference conductor, and integration direction.
3. `Isometric view` reviewed: stackup alignment and radiation region enclosure.
4. If any item is missing/ambiguous, output `FAIL` and list required new screenshots.

## Mandatory output shape
- Provide script blocks in runnable order:
  1. Desktop/HFSS init
  2. Geometry
  3. Boundary and excitation
  4. Setup and sweep
  5. Solve
  6. Post-processing export/report
- Add a `Visual QA` section:
  - image evidence used,
  - detected issues,
  - fixes applied or recommended.
- Include a short troubleshooting section for likely failures.

## Historical Mistakes Checklist
- Common failure 1: reported numeric results without visual QA evidence.
  - Prevention: do not report completion unless three required views exist and are reviewed.
- Common failure 2: left residual HFSS processes and locked project files.
  - Prevention: always verify no `ansysedt/ansyscl` process remains after teardown.
- Common failure 3: treated 2D conductor material labels as sufficient.
  - Prevention: require explicit conductor boundary assignment and boundary-name verification.
- Common failure 4: changed feedline parameters without checking feed-patch continuity/substrate containment.
  - Prevention: run topology checks (gap/overlap and board containment) before solve sign-off.

## Reference navigation
- Full index: [`../references/files/INDEX.md`](../references/files/INDEX.md)
- Core start points:
  - [`../references/files/01_hfss.md`](../references/files/01_hfss.md)
  - [`../references/files/13_solve_setup.md`](../references/files/13_solve_setup.md)
  - [`../references/files/18_post_hfss.md`](../references/files/18_post_hfss.md)
