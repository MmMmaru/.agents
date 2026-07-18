# Goal 2 Execution Guide (Circularly Polarized Single-Layer Patch)

## Target
- Goal source: `GOALS.md` item #2 (`[pending]`)
- Frequency: `2.4 GHz`
- Electrical acceptance:
  - `S11(2.4GHz) < -10 dB`
  - `AR(2.4GHz) < 3 dB`

## Added Scripts
- Design build and baseline solve:
  - `Antenna-design/cp_single_layer_patch_design.py`
- Bounded optimization sweep:
  - `Antenna-optimize/cp_single_layer_patch_optimize.py`

## Step-by-Step
1. Build baseline model and solve:
```powershell
python E:\PROJECT\Autohfss\Antenna-design\cp_single_layer_patch_design.py --project-root E:\PROJECT\Autohfss
```
2. Run optimization candidates:
```powershell
python E:\PROJECT\Autohfss\Antenna-optimize\cp_single_layer_patch_optimize.py --project-root E:\PROJECT\Autohfss --max-candidates 64
```
3. Confirm final metrics from the printed summary:
- `best_candidate.s11_db`
- `best_candidate.ar_db`
- `best_candidate.meets_targets`

## Output Location
- HFSS project:
  - `E:\PROJECT\Autohfss\.tmp\cp_patch_goal2.aedt`

## Notes
- Both scripts use `try/finally` and always call `release_desktop(close_projects=True)`.
- If PyAEDT is missing, install it first:
```powershell
pip install pyaedt
```
- If AR expression differs by AEDT version, validate the AR expression string in HFSS report window and align it in both scripts.
