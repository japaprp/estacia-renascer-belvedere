param(
    [int]$Port = 8080,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$url = "http://127.0.0.1:$Port"

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $listener) {
    $pythonCmd = (Get-Command python -ErrorAction Stop).Source
    Start-Process -FilePath $pythonCmd -ArgumentList "-m", "http.server", $Port, "--bind", "127.0.0.1" -WorkingDirectory $projectRoot -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

if ($OpenBrowser) {
    Start-Process $url
}

Write-Host "Servidor local: $url"
