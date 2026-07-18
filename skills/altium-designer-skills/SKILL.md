---
name: altium-designer-skills
description: Use when creating, reviewing, or debugging Altium Designer PCB scripts, PCB net assignment, pad-to-net binding, netlist import/export, or interactive routing that loses or fails to inherit net names.
---

# Altium Designer Skills

## Overview

Use Altium PCB scripts conservatively: treat the PCB server object model as the source of truth, and register every object mutation so interactive routing and DRC see the same nets as the property panel.

## Required Workflow

1. Identify whether the task is schematic-driven ECO, external netlist import, or PCB-native script assignment.
2. Inspect the target Altium script API version from working examples or current errors before relying on constants.
3. For PCB-native pad net assignment, find or create the `IPCB_Net`, then update pad state with modification notifications.
4. Verify in Altium by starting interactive routing from the assigned pad, not only by reading the pad property panel.
5. If routing starts as `No Net`, read `reference/netlist-workflow.md` before changing code.

## Net Assignment Pattern

Use this pattern for pad-to-net scripts:

```pascal
Procedure AssignPadNet(Board : IPCB_Board; Pad : IPCB_Pad; NetName : String);
Var
    Net : IPCB_Net;
Begin
    Net := RequireNet(Board, NetName);
    PCBServer.SendMessageToRobots(Pad.I_ObjectAddress, c_Broadcast, PCBM_BeginModify, c_NoEventData);
    Pad.SetState_Net(Net);
    Pad.SetState_InNet(True);
    PCBServer.SendMessageToRobots(Pad.I_ObjectAddress, c_Broadcast, PCBM_EndModify, c_NoEventData);
    Pad.GraphicallyInvalidate;
End;
```

Do not use `Pad.Net := Net` as the only update. It can leave Altium's connection system stale, so interactive routing may still start as `No Net`.

## Quick Reference

| Task | Preferred approach |
| --- | --- |
| No schematic, assign PCB nets | PCB script with `SetState_Net` and begin/end modify notifications |
| Schematic exists | Prefer schematic net labels and ECO/update PCB |
| Import a netlist | Generate Altium-supported netlist, then use Altium import/update flow |
| Debug parser errors | Assume DelphiScript differences first, not full Delphi support |
| Debug route losing net | Check pad object mutation registration and actual clicked primitive |

## Common Pitfalls

- `Raise Exception.Create(...)` is Delphi, not reliable Altium DelphiScript. Use `Raise('message')`.
- Some Altium script environments do not expose `eProcessAll`; do not depend on it for iterators.
- Pad names may be BGA ball IDs (`C17`) or logical names (`RF1`). Confirm the footprint naming before assigning nets.
- PCB-native nets can be overwritten by a later schematic ECO if the project is schematic-driven.
- Property panel net display is insufficient verification; interactive routing is the acceptance test.

## Reference

For the full workflow, incident review, and MSTR302 example, read `reference/netlist-workflow.md`.
