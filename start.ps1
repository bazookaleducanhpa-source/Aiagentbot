$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python virtual environment.' }
}
& '.venv/Scripts/python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Could not install dependencies.' }
Write-Host 'Dreamforge Studio: http://127.0.0.1:8000'
& '.venv/Scripts/python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000
