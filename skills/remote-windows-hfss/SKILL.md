---
name: remote-windows-hfss
description: Use this skill when running commands, Python scripts, PyAEDT, or HFSS jobs on remote Windows servers through SSH, especially jzh_server1 and jzh_server2.
---

# Remote Windows HFSS Skill

## When To Use
- The task needs SSH execution on a Windows server.
- The task runs Python, PyAEDT, AEDT, or HFSS remotely.
- The task needs background execution and log inspection for long-running simulations.
- The task involves debugging remote quoting, PowerShell, or shell syntax failures.

## Verified Server Facts
`jzh_server1` was checked on 2026-04-29.

- Host alias: `jzh_server1`
- Hostname: `JZHServer001004`
- Remote shell: Windows PowerShell 5.1
- Python: `Python 3.12.2`
- pip: `pip 24.0`
- PyAEDT: `ansys.aedt.core 0.25.1`
- AEDT install root: `C:\Program Files\AnsysEM\v232`

`jzh_server2` was checked on 2026-11-13.

- Host alias: `jzh_server2` (`~/.ssh/config`), user `徐容圣`, port 22
- IP: `121.248.55.219` (campus DHCP, it changes; previous `121.248.52.34`)
- Hostname: `DESKTOP-9BH6DAG`, Windows 11 Pro, i7-13700K (16 cores), 64 GB RAM
- Remote shell: Windows PowerShell 5.1
- AEDT: `D:\Program Files\AnsysEM\v241` (2024.1, the one in use) and `C:\Program Files\AnsysEM\v221`
- Project root: `D:\PROJECT\nonuniform_array` (branch `rotate`), HFSS project `hfss\center_fed_CP2022.aedt`
- Python: project venv `D:\PROJECT\nonuniform_array\.venv` (Python 3.12.4 from `D:\anaconda`, PyAEDT 0.25.1, pywin32). `python` on PATH is only the WindowsApps stub; always call the venv interpreter by absolute path.
- Claude Code 2.1.318 at `%APPDATA%\npm\claude.cmd`, logged in. Persistent `claude remote-control` instances run as scheduled tasks (at logon, interactive session) through `D:\PROJECT\.claude_rc\start_claude_rc.ps1 -WorkDir <dir> -Name <name>`, which restarts the process if it exits; logs in `D:\PROJECT\.claude_rc\logs`. Current tasks: `claude_remote_control` (`D:\PROJECT\nonuniform_array`, name `jzh_server2`) and `claude_remote_control_demo2` (`D:\PROJECT\nonuniform_array_demo2`, name `jzh_server2_demo2`). Add another folder by registering one more task with the same launcher.

### jzh_server2 IP changed
- The newest IP is the first entry (`MRU0`) of the local RDP history: `Get-ItemProperty "HKCU:\Software\Microsoft\Terminal Server Client\Default"`.
- Confirm it is the same machine before trusting it: `ssh-keyscan -t ed25519 <new ip>` must match the old IP's key in `~/.ssh/known_hosts`. Then update `HostName` in `~/.ssh/config`.
- If ssh reports `Bad owner or permissions on .ssh/config`, the file inherited a `CodexSandboxUsers` ACL. Fix: `icacls "$env:USERPROFILE\.ssh\config" /inheritance:r /grant:r "$($env:USERNAME):F" "SYSTEM:F" "Administrators:F"`.

### jzh_server2: reading results from the AEDT GUI the user has open
- The user usually keeps the project open in the AEDT GUI (RDP session), so the project is locked. Do not open a second AEDT on it and do not kill the GUI.
- An SSH session cannot COM-attach to the GUI (different Windows session). Run the Python script inside the interactive session instead: register a scheduled task with `New-ScheduledTaskPrincipal -LogonType Interactive`, action `.venv\Scripts\pythonw.exe -u <script>`, start it, poll a done-marker file, then delete the task.
- In the script attach with `win32com.client.Dispatch("Ansoft.ElectronicsDesktop").GetAppDesktop()`; compare the `ansysedt.exe` PID list before/after to make sure no new AEDT was spawned.
- Embedded element patterns for all ports export without touching sources: `design.GetModule("RadField").ExportElementPatternToFile([...])` per frequency (64 ports took about 10 s per frequency). FFD rows are theta-outer, phi-inner; fields are in the global frame with position phase included.
- Sphere properties are not readable through `GetPropertyValue`; read `FarFieldSetups` and element `UDMRotate`/`UDMMove` placements from the `.aedt` text.
- Finished solve status is readable without AEDT from `<project>.aedtresults\<design>.results\*.profile` and `*.EMConvData`.
- Never run recursive `Get-ChildItem` over `D:\` or the `.aedtresults` tree (hundreds of GB); it times out.

## Core Rules
- Treat the remote shell as Windows PowerShell, not Bash.
- Use local PowerShell `-EncodedCommand` wrappers for non-trivial SSH commands.
- Prefer `scp` for pushing local scripts to the remote host. Avoid inline `Get-Content ... -Raw` relays when local/remote PowerShell behavior is uncertain.
- Store temporary scripts, stdout logs, stderr logs, and probe files under `.temp`.
- For long HFSS solves, use `Start-Process` with redirected logs and `-WindowStyle Hidden`.
- If the user corrects the target host mid-task, stop using the old host immediately. Do not launch, stop, probe, or clean up any additional process on the old host unless the user explicitly asks for that follow-up.
- In Python scripts, write comments in English only.
- Raise errors for failed prerequisites instead of silently falling back.
- Always release AEDT sessions in `finally` with `hfss.release_desktop(close_projects=True)`.
- When extracting S-parameter results, never blindly use the first entry in `existing_analysis_sweeps`. Inspect the available sweep names, prefer the explicit solved sweep over `LastAdaptive` or table-only entries, and verify the returned frequency axis has more than one point before reporting minima or bandwidth conclusions.
- On `jzh_server1`, inspect `hfss.working_directory` before building export paths. For AEDT projects opened through PyAEDT, this path can already include the active design leaf such as `...\planar_array.pyaedt\patch-20G`.
- For batch parametric studies, do not wait until the end to write outputs. Persist one-case-at-a-time progress, partial JSON/CSV, and a traceback log so remote failures leave usable evidence.
- For any multi-case HFSS batch, reset the full intended variable state before every case. Do not let a case inherit design-variable values left by the previous case in the same project/session.
- If a case list stores only partial overrides, merge each case against a trusted baseline-variable dictionary first, then apply the merged full state for that case.
- The trusted baseline-variable dictionary must come from a pristine source project, not from a search copy that earlier cases may already have modified and saved.
- After fixing baseline-reset logic or after suspecting project-state contamination, regenerate fresh project copies from the pristine source before resuming batch solves.
- When the pristine source is an `.aedt` text project, prefer parsing the design-variable block directly for the baseline instead of launching AEDT just to read baseline variables.
- Do not run multiple PyAEDT solve-and-query batches concurrently against the same host/project session. On one host, serialize HFSS jobs so each batch owns its AEDT session and project copy until it finishes.
- Treat `hfss.post.get_solution_data()` returning `False` the same as a failed query. Do not assume it returns only `None` on failure.
- Before the first report query in a new batch script, run a baseline solve or verify that solved data already exists. Some `jzh_server1` HFSS sessions return `False` for unsolved report requests instead of raising.
- If a multi-case script fails mid-run, first inspect partial result files and the last completed case before rerunning. Do not discard already solved cases.

## Correct SSH Pattern
Use an encoded PowerShell command to avoid nested quote corruption.

```powershell
$script = @'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
Write-Output 'SSH_OK'
hostname
$PSVersionTable.PSVersion.ToString()
python --version
python -m pip --version
'@
$enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($script))
ssh jzh_server1 powershell -NoProfile -EncodedCommand $enc
```

## Correct PyAEDT Check
Do not use Bash heredoc syntax on the remote Windows host. Write a temporary Python file under `.temp`, then execute it.

```powershell
$script = @'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$tempDir = 'D:\PROJECT\hfss\.temp'
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$checkPath = Join-Path $tempDir 'check_pyaedt_env.py'
@"
try:
    import ansys.aedt.core as pyaedt
    print('PYAEDT_OK')
    print(getattr(pyaedt, '__version__', 'NO_VERSION_ATTR'))
except Exception as exc:
    raise RuntimeError('PyAEDT import failed: ' + repr(exc))
"@ | Set-Content -Path $checkPath -Encoding UTF8
python $checkPath
Get-ChildItem 'C:\Program Files\AnsysEM', 'C:\Program Files\ANSYS Inc' -Directory -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
'@
$enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($script))
ssh jzh_server1 powershell -NoProfile -EncodedCommand $enc
```

## Correct Long-Running HFSS Pattern
Run long jobs in the background and inspect logs instead of blocking the local terminal.

```powershell
$script = @'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$tempDir = 'D:\PROJECT\hfss\.temp'
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$stdoutPath = Join-Path $tempDir 'run.stdout.log'
$stderrPath = Join-Path $tempDir 'run.stderr.log'
Remove-Item $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
$p = Start-Process -FilePath python `
    -ArgumentList '-u', 'D:\PROJECT\hfss\.temp\your_script.py' `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -WindowStyle Hidden `
    -PassThru
Write-Output "PID=$($p.Id)"
Start-Sleep -Seconds 20
Write-Output "RUNNING=$(-not $p.HasExited)"
if (Test-Path $stderrPath) {
    Write-Output 'STDERR_BEGIN'
    Get-Content $stderrPath
    Write-Output 'STDERR_END'
}
if (Test-Path $stdoutPath) {
    Write-Output 'STDOUT_HEAD_BEGIN'
    Get-Content $stdoutPath -TotalCount 120
    Write-Output 'STDOUT_HEAD_END'
}
'@
$enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($script))
ssh jzh_server1 powershell -NoProfile -EncodedCommand $enc
```

## Reusable Success Flow
For `jzh_server1`, prefer this order when the task is HFSS execution plus data extraction:

1. Push the local script with `scp`.
2. Run a lightweight probe first if the environment or project path is uncertain.
3. Run baseline solve before the first `get_solution_data()` call in a new batch script.
4. For long studies, write `progress.log`, partial JSON/CSV, and `error.log` after each case.
5. Reuse successful far-field exports when available instead of re-exporting.

Verified reusable scripts:
- Visual QA: [`../references/scripts/patch20g_visual_qa.py`](../references/scripts/patch20g_visual_qa.py)
- Dataset export with FFD reuse: [`../references/scripts/patch20g_export_dataset.py`](../references/scripts/patch20g_export_dataset.py)

Recommended sync pattern:

```powershell
scp .temp\patch20g_visual_qa.py jzh_server1:D:/PROJECT/nonuniform_array_demo2/.temp/patch20g_visual_qa.py
scp .temp\patch20g_export_dataset.py jzh_server1:D:/PROJECT/nonuniform_array_demo2/.temp/patch20g_export_dataset.py
```

## Wrong Pattern: Bash Heredoc
This is wrong because `jzh_server1` runs Windows PowerShell, not Bash.

```powershell
ssh jzh_server1 powershell -NoProfile -Command "python - <<'PY'
print('hello')
PY"
```

Typical failure:

```text
Redirection operator is missing a file specification.
The '<' operator is reserved for future use.
```

Root cause:
- `<<'PY'` is Bash heredoc syntax.
- Windows PowerShell parses `<` before Python starts.

## Failure Handling
- If SSH fails, record the exact SSH error before changing commands.
- If Python fails, run `python --version` and `python -m pip --version` remotely.
- If PyAEDT import fails, raise an error and record the import traceback.
- On `jzh_server2`, if PyAEDT tries to load `C:\Program Files\build_output\64Release\PyDesktopPlugin.dll` and that file does not exist, treat it as an environment setup problem. Locate the actual `PyDesktopPlugin.dll` under the installed Ansys tree, set `DesktopPluginPyAEDT` explicitly, and raise an error if the DLL cannot be found.
- If AEDT launch hangs, inspect stdout/stderr logs and remote `ansysedt` or `ansyscl` process state.
- Do not remove `.lock` files unless the owning AEDT process is confirmed dead.
- If a remote batch script exits without visible stderr, add explicit `traceback` logging in the script itself and persist progress after each case before rerunning.
- If a batch candidate result looks unexpectedly good or bad, first verify whether the script reset all tunable variables before that case. Do not trust later cases in a batch that only applied delta overrides on top of a mutated project state.
- If a solve completes but the follow-up report query fails with gRPC/solution-type errors such as `InvokeAedtObjMethod`, `GetSolutionType`, or missing `default_solution`, suspect concurrent PyAEDT access to the same AEDT session or project copy first. Stop overlapping jobs on that host, use a fresh project copy, and rerun serially on that machine.
- If a remote Python process exits during `hfss.analyze()` without Python traceback, do not immediately change the tuning logic. First run a minimal foreground probe on the same project with marker-file logging and `faulthandler` enabled to separate solver/process crash from script bugs.
- If `hfss.get_antenna_data()` or `FfdSolutionDataExporter.export_farfield()` fails after logging `Exporting embedded element patterns...`, check whether the exporter already created `element.txt`, `element_*.ffd`, and `pyaedt_antenna_metadata.json` under `<working_directory>\Setup1_Sweep-<sphere>`.
- On `jzh_server1` with `AEDT 2023.2` and `PyAEDT 0.25.1`, the far-field exporter can partially succeed and then fail in PyAEDT post-processing with errors such as `AttributeError("'FfdSolutionDataExporter' object has no attribute 'post'")` or VTK/OpenGL initialization failures. Treat the FFD files as the source of truth and continue by parsing the exported files directly instead of rerunning the fragile wrapper.
- For this environment, prefer reusing an existing successful FFD export over calling `export_element_pattern()` again. Repeated exporter calls can fail even when the previously generated `element.txt` and `.ffd` files remain valid.
- On `jzh_server2`, if the Python runtime lives under a non-ASCII user-profile path such as `C:\Users\徐容圣\...`, do not rely on scheduled tasks or shell contexts that may reinterpret that path. Prefer launching the batch from a normal user PowerShell session with an explicit absolute `python.exe` path and inherited environment variables.
- After starting a background batch on `jzh_server2`, verify success with both checks: the batch `progress.log` must contain `CASE_START`, and the remote process table must still show the expected `python` and `ansysedt/ansyscl` processes a short time later. If only `CASE_START` exists but no live process remains, treat the launch as failed and do not assume the host is still computing.
- For `jzh_server2` launcher scripts stored on disk, do not hardcode a non-ASCII user-profile path literal such as `C:\Users\徐容圣\...` inside the `.ps1` file. Resolve the runtime path dynamically at execution time from `$env:USERPROFILE`, `where.exe python`, or an ASCII-only parent path probe, then validate it with `Test-Path` before launch.
- For remote background HFSS batches on both `jzh_server1` and `jzh_server2`, an immediate `CASE_START` plus a briefly live process table is not sufficient evidence. Re-check after a multi-minute window and require at least one of these before trusting the batch: `CASE_DONE`, `summary.json`, `best.json`, or continued live `python`/`ansysedt` processes. If the host later has only the initial startup logs and no live processes, classify the batch as a silent launch failure.
- If a remote batch dies during AEDT startup with stdout ending around `Launching AEDT server with gRPC transport mode` and no traceback in `stderr` or `error.log`, do not keep relaunching the same background pattern as if it were healthy. Record the silent-startup failure, stop trusting that batch lane, and switch the host to a foreground single-case probe or another explicitly instrumented minimal reproduction.
- When a PowerShell batch wrapper launches Python or PyAEDT on a remote Windows host, do not invoke the native executable inline under `$ErrorActionPreference = "Stop"` if the child may write warnings or info lines to stderr. Use `Start-Process -Wait -PassThru` with explicit `-RedirectStandardOutput` and `-RedirectStandardError` files, then inspect the exit code yourself. Otherwise PowerShell can convert benign native stderr output into terminating errors and kill the batch before HFSS finishes.
- On a remote Windows host accessed through `ssh ... powershell`, never use a blanket `Get-Process powershell ... | Stop-Process` cleanup inside the same remote script. That can terminate the current shell hosting the SSH command and abort the probe immediately. Restrict solver cleanup to `python`, `ansysedt`, and `ansyscl`, or target known stale child PIDs explicitly.
