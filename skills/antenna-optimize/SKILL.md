---
name: antenna-optimize
description: Use this skill when the user wants HFSS parametric sweeps or optimization loops (variables, parametrics, goals, result extraction) using the sibling PyAEDT references folder.
---

# Antenna Optimize Skill

## When to use
- User asks for parametric sweep or optimization in HFSS.
- User needs variable-driven design exploration and result comparison.
- User asks to automate scan/optimization and export results.

## Workflow
1. Read [`../references/files/INDEX.md`](../references/files/INDEX.md) and locate variable/setup/optimization refs.
2. Define design variables first ([`../references/files/21_variables.md`](../references/files/21_variables.md) reference).
3. Before any solve, confirm every tuned variable already exists in the active design variable table and is not just a stale name from an older model revision.
4. Reject candidate lists that include missing variables, derived aliases that are not meant to be tuned directly, or newly created orphan variables that do not drive the intended geometry.
5. Build sweep/optimization definitions ([`../references/files/22_design_xploration.md`](../references/files/22_design_xploration.md) reference).
6. Run analyze and export tabular/report results for decision making.
7. Always release HFSS/AEDT session at the end of optimization to prevent locked projects.
8. Run pre/post visual checks so optimization does not degrade geometry or port correctness.

## Example Scripts
- General bounded optimization example:
  [`../references/scripts/cp_single_layer_patch_optimize.py`](../references/scripts/cp_single_layer_patch_optimize.py)
- Single-parameter sweep with per-case persistence:
  [`../references/scripts/patch20g_param_study.py`](../references/scripts/patch20g_param_study.py)
- Remote visual QA before/after tuning:
  [`../references/scripts/patch20g_visual_qa.py`](../references/scripts/patch20g_visual_qa.py)
- Remote solved-data export example:
  [`../references/scripts/patch20g_export_dataset.py`](../references/scripts/patch20g_export_dataset.py)

## Execution mode guard
- If the user asks for direct tuning execution, perform optimization via terminal Python calls instead of creating new script files.
- Keep optimization outputs explicit in command results: tested candidates, objective values, and selected best candidate.
- Create files only when the user explicitly asks to persist code or reports.

## Mandatory teardown guard
- Wrap optimization execution with `try/finally` and always call `hfss.release_desktop(close_projects=True)` in `finally`.
- Avoid `release_desktop(close_on_exit=...)` unless the local PyAEDT version explicitly supports it.
- If process cleanup is incomplete, kill residual `ansysedt` and `ansyscl` processes and verify cleanup.

## Mandatory artifact retention guard
- Optimization runs must not accumulate historical probe files by default.
- If the user requests single-result retention, remove all other generated artifacts except the explicitly retained file(s).
- Keep debug/probe artifacts only when the user explicitly asks for diagnostics preservation.
- Include cleanup summary in final report: kept files, removed files, and post-cleanup folder listing.

## Mandatory visual optimization guard
- For baseline and best candidate, inspect model images (or user-provided images) and confirm:
  - excitation geometry is still valid,
  - feed/patch topology is unchanged unless intentionally optimized,
  - no invalid overlaps/gaps were introduced by variable changes.
- Reject a candidate if electrical objective improves but visual/physical validity fails.
- Optimization report must include both numeric metrics and visual sanity conclusion.
- If the user requests model confirmation, do not provide numeric-only confirmation; include explicit visual pass/fail evidence.

## Visual QA hard gate before tuning
- Do not start parametric sweep or optimization until baseline visual QA is completed.
- Baseline visual QA completion requires all three views:
  - `Top view`,
  - `Isometric view`,
  - `Port close-up`.
- If exact port close-up export is awkward in the current project, export the closest stable geometry-focused view and state the limitation explicitly instead of skipping geometry QA silently.
- If baseline visual evidence is missing, optimization execution is blocked and must be reported as incomplete.
- Every optimization report must include both:
  - baseline visual QA result,
  - best-candidate visual QA result.

## Remote batch sweep guard
- On `jzh_server1`, treat parametric sweeps as failure-prone long jobs.
- Persist one-case-at-a-time results and a traceback log; do not wait until the end to write artifacts.
- Treat `hfss.post.get_solution_data()` returning `False` as a report failure.
- Run one baseline solve before the first query in a fresh session.
- If a batch fails mid-run, resume from existing partial CSV/JSON when possible instead of discarding finished cases.
- If the project was updated since the previous tuning round, rebuild the tunable-variable list from the current model before launching a new search. Do not reuse older variable names blindly.

## Mandatory feedline optimization guard
- Include feedline-length variable in tuning candidates when feed excitation quality is user-reported as problematic.
- Do not accept candidate points that cause solver failure or invalid port geometry, even if partially improved at target frequency.
- When tuning `top_line_IYC_length` in direct-feed patch structures, co-optimize/update `Patch1_position_x` continuity constraint to prevent unintended feed-patch gap.
- Reject any candidate where feedline extends beyond substrate boundaries in top-view geometry.

## Mandatory boundary integrity guard
- Optimization is not allowed to proceed unless baseline model confirms explicit conductor boundaries on:
  - ground,
  - patch,
  - feedline.
- For 2D sheet-metal designs, material name is not a substitute for conductor boundary integrity.
- After variable updates, verify boundary assignments are still attached to the intended metal objects.
- Reject any candidate with missing, detached, or inconsistent conductor boundary assignments, even if numeric objectives improve.

## Mandatory output shape
- Provide script blocks in runnable order:
  1. Session and base setup
  2. Variable creation and constraints
  3. Parametric/optimization setup
  4. Solve and export
  5. Selection logic for best candidate
- Add a `Visual Validation` section:
  - baseline image check result,
  - best-candidate image check result,
  - any geometry/port risk notes.
- Include failure handling for variable, setup, and expression errors.

## Historical Mistakes Checklist
- Common failure 1: started optimization before baseline visual QA.
  - Prevention: block optimization unless `Top/Isometric/Port close-up` images exist.
- Common failure 2: trusted stale report files from previous runs.
  - Prevention: clear old report CSV files before new solve-and-evaluate loops.
- Common failure 3: accepted candidates with missing conductor boundaries.
  - Prevention: verify required boundary names before and during optimization.
- Common failure 4: optimized only one metric and regressed the other.
  - Prevention: use joint pass/fail gates for `S11` and `AR` on every candidate.
- Common failure 5: reused a variable name from an older model revision that no longer existed in the active design.
  - Prevention: read the current design variable table first and raise an error if any requested tuning variable is absent.

## Reference navigation
- Full index: [`../references/files/INDEX.md`](../references/files/INDEX.md)
- Optimization core files:
  - [`../references/files/21_variables.md`](../references/files/21_variables.md)
  - [`../references/files/22_design_xploration.md`](../references/files/22_design_xploration.md)
  - [`../references/files/19_solution_data.md`](../references/files/19_solution_data.md)
- Example scripts:
  - [`../references/scripts/cp_single_layer_patch_optimize.py`](../references/scripts/cp_single_layer_patch_optimize.py)
  - [`../references/scripts/patch20g_param_study.py`](../references/scripts/patch20g_param_study.py)
  - [`../references/scripts/patch20g_visual_qa.py`](../references/scripts/patch20g_visual_qa.py)
  - [`../references/scripts/patch20g_export_dataset.py`](../references/scripts/patch20g_export_dataset.py)
- Tuning experience:
  - [`../references/experience/cp_patch_goal2_tuning_experience.md`](../references/experience/cp_patch_goal2_tuning_experience.md)
