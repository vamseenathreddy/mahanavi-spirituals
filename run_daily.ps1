# run_daily.ps1
#
# Wrapper for unattended daily runs via Windows Task Scheduler's wake
# timer. Task Scheduler wakes the laptop and starts THIS script at a
# fixed time (e.g. 5:00 AM); this script then:
#   1. Waits a RANDOM delay so the actual post happens at a varying time
#      within the window, not the identical second every day.
#   2. Runs the real pipeline.
#   3. Shuts the laptop back down.
#
# Logs its own actions to run_daily.log, SEPARATE from the app's own
# data\logs\mahanavi.log -- if the laptop never actually woke up, or Task
# Scheduler never fired, there will be NO entry in run_daily.log at all,
# which is itself the diagnostic: check this file first when troubleshooting
# a missed day, before digging into the app's internal logs.
#
# Usage (normal unattended run):
#   powershell -ExecutionPolicy Bypass -File run_daily.ps1
#
# Usage (testing -- skips the random wait and the shutdown, so you can
# watch it run without losing your session):
#   powershell -ExecutionPolicy Bypass -File run_daily.ps1 -TestMode

param(
    [switch]$TestMode,
    [int]$WindowMinutes = 30
)

$ErrorActionPreference = "Stop"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$LogFile = Join-Path $ScriptDir "run_daily.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp | $Message" | Add-Content -Path $LogFile -Encoding utf8
}

Write-Log "=== run_daily.ps1 started (TestMode=$TestMode) ==="

try {
    if ($TestMode) {
        Write-Log "TestMode: skipping random delay and shutdown."
    } else {
        $delaySeconds = Get-Random -Minimum 0 -Maximum ($WindowMinutes * 60)
        Write-Log "Waiting $delaySeconds seconds (random within a $WindowMinutes-minute window) before running."
        Start-Sleep -Seconds $delaySeconds
    }

    $pyStdoutLog = Join-Path $ScriptDir "run_daily_python_stdout.log"
    Write-Log "Running: python -m mahanavi.main --run-now (its own output goes to $pyStdoutLog and data\logs\mahanavi.log)"
    python -m mahanavi.main --run-now *> $pyStdoutLog
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Log "Pipeline finished with exit code 0 (success)."
    } else {
        Write-Log "Pipeline finished with NON-ZERO exit code $exitCode -- check data\logs\mahanavi.log for details."
    }
} catch {
    Write-Log "UNHANDLED ERROR in wrapper script: $($_.Exception.Message)"
} finally {
    if ($TestMode) {
        Write-Log "TestMode: NOT shutting down. === run_daily.ps1 finished ==="
    } else {
        Write-Log "Shutting down in 60 seconds. Press Ctrl+C now to cancel if you're watching this."
        Write-Log "=== run_daily.ps1 finished ==="
        shutdown /s /t 60 /c "Mahanavi Spirituals: daily run complete, shutting down."
    }
}