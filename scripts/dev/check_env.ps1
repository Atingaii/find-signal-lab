$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$files = @(
    "src\fund_direction_predictor\__init__.py",
    "src\fund_direction_predictor\settings.py",
    "src\fund_direction_predictor\api\main.py",
    "src\fund_direction_predictor\ui\app.py"
)

$paths = $files | ForEach-Object { Join-Path $root $_ }
python -m py_compile $paths

Write-Host "Python syntax check completed."
