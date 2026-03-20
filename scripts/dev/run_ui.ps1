$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = Join-Path $root "src"
$appPath = Join-Path $root "src\fund_direction_predictor\ui\app.py"

python -m streamlit run $appPath --server.port 8501
