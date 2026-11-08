# Abre JupyterLab con el notebook de exploracion.
# Carga la llave de Google Maps desde la variable de usuario de Windows (sin mostrarla).
$repo = Split-Path -Parent $PSScriptRoot
$env:GOOGLE_MAPS_API_KEY = [Environment]::GetEnvironmentVariable('GOOGLE_MAPS_API_KEY', 'User')
if (-not $env:GOOGLE_MAPS_API_KEY) { Write-Host "Aviso: no hay GOOGLE_MAPS_API_KEY; la seccion de Google Maps se saltara." }
Set-Location $repo
& "$repo\.venv\Scripts\jupyter.exe" lab "notebooks\00_mega_exploracion_google.ipynb"
