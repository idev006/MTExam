param(
    [string]$Database = "data/mtexam.db",
    [string]$OutputDirectory = "backups"
)

$ErrorActionPreference = "Stop"
$dbPath = [IO.Path]::GetFullPath($Database)
$outPath = [IO.Path]::GetFullPath($OutputDirectory)
if (-not (Test-Path -LiteralPath $dbPath)) { throw "SQLite database not found: $dbPath" }
New-Item -ItemType Directory -Force -Path $outPath | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$target = Join-Path $outPath "mtexam-$stamp.db"
Copy-Item -LiteralPath $dbPath -Destination $target
Get-FileHash -Algorithm SHA256 -LiteralPath $target | Set-Content -LiteralPath "$target.sha256"
Write-Output "Backup created: $target"
