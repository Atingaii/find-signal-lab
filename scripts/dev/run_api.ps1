$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = Join-Path $root "src"

python -m uvicorn fund_direction_predictor.api.main:app --host 0.0.0.0 --port 8000 --reload
