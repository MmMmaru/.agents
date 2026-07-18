# Altium Designer Netlist Workflow Reference

## Scope

This reference captures a practical workflow for Altium Designer PCB scripting, especially net assignment after manually placing components. It is written from a real MSTR302 workflow where eight chips needed fixed nets `RF1..RF64` and `COM1..COM8`.

## Decide the Net Source

Before writing a script, decide where nets should originate:

- **Schematic-driven project**: create or edit schematic net labels, then run ECO/update PCB. This is safest for long-term design consistency.
- **External netlist import**: generate an Altium-supported netlist format and import/update through Altium.
- **PCB-native assignment**: use only when the project has no schematic source for these nets, or when the user explicitly wants PCB-only post-processing.

If PCB-native assignment is used, warn that a future schematic update can overwrite PCB-only nets.

## Safe PCB-Native Net Assignment

Use the PCB server current board:

```pascal
Board := PCBServer.GetCurrentPCBBoard;
If Board = Nil Then
Begin
    Raise('No active PCB document.');
End;
```

Find components by designator with a board iterator filtered by object type:

```pascal
Iterator := Board.BoardIterator_Create;
Iterator.AddFilter_ObjectSet(MkSet(eComponentObject));
Iterator.AddFilter_LayerSet(AllLayers);
```

Do not rely on `Iterator.AddFilter_Method(eProcessAll)` unless the target Altium environment proves the constant exists.

Find pads inside components with a group iterator filtered to `ePadObject`. Confirm the actual footprint pad names. For MSTR302, the useful mappings were:

| Port | BGA pad |
| --- | --- |
| RF1 | C17 |
| RF2 | E17 |
| RF3 | G17 |
| RF4 | J17 |
| RF5 | J1 |
| RF6 | G1 |
| RF7 | E1 |
| RF8 | C1 |
| COM | L9 |

If the user renamed pads to logical names, use `RF1..RF8` and `COM` instead.

Find or create nets as `IPCB_Net` objects. After creating a net, add it to the board.

Assign pad nets through primitive state methods, not direct property assignment:

```pascal
PCBServer.SendMessageToRobots(Pad.I_ObjectAddress, c_Broadcast, PCBM_BeginModify, c_NoEventData);
Pad.SetState_Net(Net);
Pad.SetState_InNet(True);
PCBServer.SendMessageToRobots(Pad.I_ObjectAddress, c_Broadcast, PCBM_EndModify, c_NoEventData);
Pad.GraphicallyInvalidate;
```

This is the critical step for interactive routing to inherit the net. Direct `Pad.Net := Net` can show a net in some UI paths while leaving the connection system stale; the next route can become `No Net`.

Wrap the full operation in:

```pascal
PCBServer.PreProcess;
Try
    { changes }
Finally
    PCBServer.PostProcess;
End;
```

## MSTR302 Fixed Net Naming Example

For eight manually placed chips named `U1..U8`:

- `U1` RF pads become `RF1..RF8`; `U1` COM becomes `COM1`.
- `U2` RF pads become `RF9..RF16`; `U2` COM becomes `COM2`.
- Continue through `U8`: `RF57..RF64`, `COM8`.

Formula:

```pascal
RFNetName := 'RF' + IntToStr((ChipIndex - 1) * 8 + RFIndex);
COMNetName := 'COM' + IntToStr(ChipIndex);
```

## Parser and API Pitfalls

### `ELSE expected` near `Raise Exception.Create`

Root cause: Altium DelphiScript is not full Delphi. `Raise Exception.Create('...')` can be parsed incorrectly. Use:

```pascal
Raise('message');
```

Prefer `Begin/End` after `If ... Then` when the following statement is a `Raise`, because it makes the script parser's control flow unambiguous.

### `Undeclared identifier eProcessAll`

Root cause: some Altium scripting environments do not expose this iterator method constant. It is not necessary when object type and layer filters are already present. Remove the method filter unless a local working example requires it.

### Route starts as `No Net`

Root cause candidates:

1. The script used `Pad.Net := Net` without `SetState_Net` and modification notifications.
2. The user clicked a different primitive, not the assigned pad.
3. The footprint pad name did not match the script's lookup name, so the intended pad was never assigned.
4. A schematic ECO or import flow overwrote PCB-only nets.

Debug in this order:

1. Re-run the assignment script and save the PCB.
2. Select the exact pad and inspect its net.
3. Start interactive routing from the pad copper, not adjacent geometry.
4. If routing still says `No Net`, add a diagnostic message after assignment that prints component designator, pad name, and net name for each successful binding.

## Workflow Lessons From the Incident

- Ask early whether the user wants placement, netlist import, pad assignment, or only a mapping table. These are different Altium workflows.
- Do not assume a PCB script that compiles in generic Delphi syntax will compile in Altium DelphiScript.
- Avoid writing `.PcbDoc` binaries directly. Prefer Altium scripts that run inside the editor.
- Do not trust property assignment alone for PCB server objects. Prefer `SetState_*` APIs and modification messages.
- Verify the acceptance behavior the user cares about. For net assignment, the real acceptance check is whether interactive routing inherits the assigned net.
- Keep project-specific mappings in the script or reference table, but keep the workflow skill generic enough for future Altium tasks.
