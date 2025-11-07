@echo off
setlocal EnableExtensions

REM----------------------------------------------------------------------+
REM Removes local user accounts that have been inactive for 60 days or   |
REM longer while preserving the Healthspaces administrator account.      |
REM Usage:                                                               |
REM   remove_inactive_users.cmd            -> deletes matching accounts  |
REM   remove_inactive_users.cmd --dry-run  -> shows what would be done   |
REM----------------------------------------------------------------------+

set "MAX_AGE_DAYS=60"
set "EXCLUDE_USERS=Healthspaces Administrator Guest DefaultAccount WDAGUtilityAccount"

set "DRY_RUN_FLAG=0"
if /I "%~1"=="--dry-run" (
    set "DRY_RUN_FLAG=1"
    echo Running in DRY-RUN mode. No accounts will be deleted.
    echo.
)

where powershell >nul 2>&1
if errorlevel 1 (
    echo PowerShell is required but was not found on this system.
    exit /b 1
)

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass ^
    -Command ^
        "& {
            param(
                [int]$MaxAgeDays,
                [string]$ExclusionList,
                [int]$DryRunFlag
            )

            $threshold = (Get-Date).AddDays(-$MaxAgeDays)
            $exclusions = $ExclusionList -split '\s+' | Where-Object { $_ }
            $dryRun = $DryRunFlag -eq 1
            $computer = [ADSI]('WinNT://{0}' -f $env:COMPUTERNAME)
            $users = $computer.Children |
                Where-Object {
                    $_.SchemaClassName -eq 'user' -and $_.Name -notin $exclusions
                }

            foreach ($user in $users) {
                $lastActivity = $null

                try {
                    $rawLastLogin = $user.Properties.Item('LastLogin').Value
                    if ($rawLastLogin) {
                        $lastActivity = [datetime]$rawLastLogin
                    }
                } catch { }

                if (-not $lastActivity) {
                    try {
                        $ageSeconds = [int]$user.PasswordAge
                        if ($ageSeconds -gt 0) {
                            $lastActivity = (Get-Date).AddSeconds(-$ageSeconds)
                        }
                    } catch { }
                }

                if (-not $lastActivity) {
                    $lastActivity = Get-Date '1900-01-01'
                }

                if ($lastActivity -lt $threshold) {
                    $message = 'Removing user {0} (last activity: {1})' -f $user.Name, $lastActivity
                    if ($dryRun) {
                        Write-Host "[DRY-RUN] $message"
                        continue
                    }

                    Write-Host $message
                    $delete = Start-Process -FilePath 'net.exe' -ArgumentList @('user', $user.Name, '/delete') -NoNewWindow -PassThru -Wait

                    if ($delete.ExitCode -ne 0) {
                        Write-Warning ('Failed to remove user {0}. Exit code {1}' -f $user.Name, $delete.ExitCode)
                    }
                } else {
                    Write-Host ('Keeping user {0} (last activity: {1})' -f $user.Name, $lastActivity)
                }
            }
        }" ^
    %MAX_AGE_DAYS% ^
    "%EXCLUDE_USERS%" ^
    %DRY_RUN_FLAG%

endlocal

