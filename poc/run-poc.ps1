$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Project virtual environment was not found at $python"
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    Write-Host "`n== $Label =="
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

Push-Location $projectRoot
try {
    Invoke-Checked "Ruff" { & $python -m ruff check . }
    Invoke-Checked "Executable POC tests" { & $python -m pytest -m poc }
    Invoke-Checked "Remaining backend tests" { & $python -m pytest -m "not poc" }

    Push-Location (Join-Path $projectRoot "frontend")
    try {
        Invoke-Checked "Vue TypeScript check" { & npm.cmd run type-check }
        Invoke-Checked "Vite production build" { & npm.cmd run build }
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}

Write-Host "`nMTExam technology POC passed."
