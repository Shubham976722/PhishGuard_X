
param(
    [string]$PythonExecutable
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path "$PSScriptRoot\..\..").Path

if ([string]::IsNullOrWhiteSpace($PythonExecutable)) {
    $PythonExecutable = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"
}

$LogDirectory = Join-Path $ProjectRoot "logs"

if (-not (Test-Path $PythonExecutable)) {
    throw "Python executable not found: $PythonExecutable"
}

New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss-fff"
$LogFile = Join-Path $LogDirectory "threat-feed-sync_$Timestamp.log"

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting threat-feed synchronization." |
    Out-File -FilePath $LogFile -Encoding utf8

$ExitCode = 1

Push-Location $ProjectRoot

try {
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        & $PythonExecutable -m backend.scripts.sync_threat_feeds 2>&1 |
            Out-File -FilePath $LogFile -Append -Encoding utf8

        $ExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }
}
catch {
    $_ | Out-File -FilePath $LogFile -Append -Encoding utf8
    $ExitCode = 1
}
finally {
    Pop-Location
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Exit code: $ExitCode" |
    Out-File -FilePath $LogFile -Append -Encoding utf8

exit $ExitCode
