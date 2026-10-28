param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonExe = (Get-Command python -ErrorAction Stop).Source
$ffmpegDirectory = Join-Path $PSScriptRoot '.tools\ffmpeg\ffmpeg-9.0.2-full_build\bin'
if (Test-Path -LiteralPath $ffmpegDirectory) { $env:PATH = "$ffmpegDirectory;$env:PATH" }
$env:PYTHONUTF8 = '1'
if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:8010' }
Write-Host 'Cappy Remake Studio: http://127.0.0.1:8010'
& $pythonExe -m remake_studio.cli --serve
exit $LASTEXITCODE
