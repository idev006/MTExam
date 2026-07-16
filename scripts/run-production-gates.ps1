param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [int]$Requests = 500,
    [int]$Workers = 50
)

$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m ruff check backend tests poc
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe poc\security_smoke.py
& .\.venv\Scripts\python.exe poc\authenticated_load_smoke.py --url $BaseUrl --requests $Requests --workers $Workers
& .\.venv\Scripts\python.exe poc\device_acceptance_matrix.py > device-acceptance-matrix.json
Write-Host "Automated production gate checks completed; review external sign-offs and device matrix before Go."
