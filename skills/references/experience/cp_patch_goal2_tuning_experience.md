# CP Patch Goal2 Tuning Experience

## Scope
Target from `GOALS.md` item #2:
- `S11@2.4GHz < -10 dB`
- `AR@2.4GHz < 3 dB`

Evaluation convention (standardized):
- AR expression: `dB(AxialRatioValue)`
- Context: `Setup1 : LastAdaptive`, `Freq=2.4GHz`, `Phi=0deg`, read `Theta=0deg`

## What worked
1. **AR can be reduced below 3 dB** by tuning:
   - `trim`
   - `feed_l`
   - `feed_off_y`
2. Example near-best AR points:
   - `(trim=3.2, feed_l=22.5, feed_off_y=4.0)` -> `AR ~ 2.24 dB`
   - `(trim=3.0, feed_l=22.6, feed_off_y=4.0)` -> `AR ~ 2.06 dB`

## What did not work
1. In current single-feed topology, **S11 remained around -9.2 dB to -9.6 dB** in local fine sweeps.
2. Fine changes in:
   - `feed_w`
   - `feed_overlap`
   improved AR in some cases but did not push S11 below `-10 dB`.

## Practical lessons
1. Keep AR and S11 optimization decoupled in phases:
   - Phase A: lock AR < 3 dB region.
   - Phase B: in that region, tune matching parameters only.
2. For this model, local tuning alone appears insufficient for S11 target crossing.
3. Next likely effective levers:
   - inset-feed depth as explicit variable,
   - small slot/notch in patch edge near feed for impedance match,
   - substrate/ground dimensions and feed transition refinement.

## Current best-known operating point
- `patch_l=29.2`
- `patch_w=29.2`
- `trim=3.0`
- `feed_l=22.6`
- `feed_off_y=4.0`
- `feed_w=3.0`
- `feed_overlap=0.6`
- `AR@2.4GHz (Theta=0) = 2.057 dB` (pass)
- `S11@2.4GHz = -9.197 dB` (near pass, but not pass)

## Recommendation for next iteration
Introduce one topology variable (inset depth or edge notch) before further dense local sweeps.
