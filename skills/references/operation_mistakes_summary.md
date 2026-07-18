# Operation Mistakes Summary and Skill Improvements

## Main Mistakes Observed
1. Visual QA was skipped before reporting simulation/optimization results.
2. Direct 2D sheet conductor modeling was mixed with material-only reasoning.
3. Explicit conductor boundary checks were not enforced at optimization start.
4. Residual HFSS processes occasionally remained and could lock result files.
5. Some optimization iterations risked using stale exported report CSV files.

## Skill Improvements Applied
1. Added hard-gate visual QA rules in both design and optimize skills.
2. Added mandatory metal-boundary and boundary-integrity rules for 2D workflows.
3. Added historical mistakes checklists to both skill files for pre-run self-check.
4. Added process cleanup and stale-artifact prevention requirements.

## Current Enforcement in Runtime Scripts
1. Design script exports required visual QA images and validates setup before solve.
2. Optimization script blocks execution if visual evidence is missing.
3. Optimization script blocks execution if required conductor boundaries are missing.
4. Both scripts clear stale report CSV files before extracting new metrics.
