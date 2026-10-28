param(
    [Parameter(Mandatory=$true)][string]$Text,
    [string]$Output = "output/omnivoice/preview.wav",
    [int]$Steps = 16,
    [double]$Speed = 1.0
)
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$taskPython = Join-Path $taskRoot ".tools/omnivoice-env/Scripts/python.exe"
& $taskPython (Join-Path $taskRoot "scripts/omnivoice_narrate.py") --text $Text --output $Output --steps $Steps --speed $Speed
exit $LASTEXITCODE
