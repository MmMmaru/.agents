# Axial Ratio Calculation Formula (Corrected)

## Why this note
This project previously mixed different AR definitions:
- direct HFSS report expression (`dB(AxialRatioValue)`),
- reconstructed AR from `GainLHCP/GainRHCP`.

Mixing these can produce inconsistent numbers.

## Authoritative definition
Axial ratio (AR) is the ratio of the major axis to the minor axis of the polarization ellipse:

- `AR_linear = E_major / E_minor`, with `AR_linear >= 1`
- `AR_dB = 20 * log10(AR_linear)`

For perfect circular polarization: `AR_linear = 1`, so `AR_dB = 0 dB`.
For linearly polarized limit: `AR -> infinity`.

## Project acceptance criterion
- Circular-polarization quality target: `AR_dB < 3 dB` (at required observation direction/frequency).

## HFSS usage rule (recommended)
When available, use HFSS direct AR expression:
- `dB(AxialRatioValue)`

This should be treated as the ground-truth metric for this project.

Recommended report context for this task:
- setup: `Setup1 : LastAdaptive`
- frequency: `2.4GHz`
- cut: `Phi=0deg`
- sweep: `Theta` (then read required angle, usually boresight `Theta=0deg`)

## If LHCP/RHCP components are used
Only use this when direct AR expression is unavailable.

Let `A = |E_RHCP|`, `B = |E_LHCP|` (field magnitudes), then:
- `AR_linear = (A + B) / |A - B|`
- `AR_dB = 20 * log10(AR_linear)`

Important:
- Do not use `|GainRHCP - GainLHCP|` directly as AR.
- If using power-like quantities in dB (`G_dB`), convert to field magnitude first:
  - `|E| proportional to sqrt(P)`
  - `A proportional to 10^(G_RHCP_dB/20)`
  - `B proportional to 10^(G_LHCP_dB/20)`

## Common mistakes to avoid
1. Comparing `Theta`-swept AR curve to a single-angle AR number without stating angle.
2. Mixing `Setup1:Sweep1` and `Setup1:LastAdaptive` without documenting the choice.
3. Using different AR formulas between baseline and optimization phases.

## Standardized extraction in this repo
Both design and optimization scripts should use the same AR metric path:
1. Create far-field report with `dB(AxialRatioValue)`.
2. Fix `Freq=2.4GHz`, `Phi=0deg`.
3. Read `Theta=0deg` point as boresight AR for optimization objective.

---

## Web references
- Ansys HFSS Help: Axial Ratio definition  
  https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v252/en/Subsystems/HFSS/Content/HFSS/AxialRatio.htm
- Antenna-Theory (engineering overview of AR and 3 dB CP criterion)  
  https://www.antenna-theory.com/definitions/axial.php
