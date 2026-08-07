$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Root = (Resolve-Path $PSScriptRoot).Path
$Runtime = Join-Path $Root '.sentrix-runtime'
$Python = Join-Path $Runtime 'python.exe'
$GetPip = Join-Path $Runtime 'get-pip.py'
$Ready = Join-Path $Runtime '.dependencies-ready'
$Logs = Join-Path $Root 'logs'
$StdOut = Join-Path $Logs 'sentrix-out.log'
$StdErr = Join-Path $Logs 'sentrix-error.log'
$PythonVersion = '3.13.14'
$PythonZip = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
$GetPipUrl = 'https://bootstrap.pypa.io/get-pip.py'

function Write-Step([string]$Text) {
    Write-Host "`n>> $Text" -ForegroundColor Cyan
}

function Test-Port([int]$Port) {
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

function Get-FreePort {
    foreach ($candidate in 5000..5010) {
        if (Test-Port $candidate) { return $candidate }
    }
    throw 'Sentrix could not find a free local port between 5000 and 5010.'
}

Clear-Host
Write-Host '========================================' -ForegroundColor DarkCyan
Write-Host '              SENTRIX v1' -ForegroundColor Cyan
Write-Host '        Portable Windows Edition' -ForegroundColor Gray
Write-Host '========================================' -ForegroundColor DarkCyan
Write-Host 'First launch requires an internet connection.' -ForegroundColor DarkGray

New-Item -ItemType Directory -Force -Path $Logs | Out-Null

if (-not (Test-Path $Python)) {
    Write-Step 'Preparing private Python runtime (first launch only)'
    New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
    $zip = Join-Path $env:TEMP 'sentrix-python.zip'
    Invoke-WebRequest -UseBasicParsing -Uri $PythonZip -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $Runtime -Force
    Remove-Item $zip -Force -ErrorAction SilentlyContinue

    $pth = Get-ChildItem $Runtime -Filter 'python*._pth' | Select-Object -First 1
    if (-not $pth) { throw 'Python runtime configuration file was not found.' }
    $lines = Get-Content $pth.FullName
    $lines = $lines | ForEach-Object { if ($_ -eq '#import site') { 'import site' } else { $_ } }
    if ($lines -notcontains 'Lib\site-packages') { $lines += 'Lib\site-packages' }
    Set-Content -Path $pth.FullName -Value $lines -Encoding ASCII

    Invoke-WebRequest -UseBasicParsing -Uri $GetPipUrl -OutFile $GetPip
    & $Python $GetPip --disable-pip-version-check
    if ($LASTEXITCODE -ne 0) { throw 'pip installation failed.' }
}

$env:PATH = "$Runtime;$Runtime\Scripts;$env:PATH"
$env:PYTHONUTF8 = '1'
$env:APP_ENV = 'development'
$env:HOST = '127.0.0.1'
$env:FLASK_DEBUG = '0'

if (-not (Test-Path $Ready)) {
    Write-Step 'Installing Sentrix components (first launch only)'
    & $Python -m pip install --disable-pip-version-check --no-warn-script-location -r (Join-Path $Root 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Sentrix dependency installation failed.' }
    Set-Content -Path $Ready -Value (Get-Date).ToString('o') -Encoding ASCII
}

$Port = Get-FreePort
$env:PORT = [string]$Port
$Url = "http://127.0.0.1:$Port"

Write-Step "Starting Sentrix at $Url"
Remove-Item $StdOut, $StdErr -Force -ErrorAction SilentlyContinue

$process = Start-Process -FilePath $Python -ArgumentList @((Join-Path $Root 'app.py')) -WorkingDirectory $Root -PassThru -WindowStyle Hidden -RedirectStandardOutput $StdOut -RedirectStandardError $StdErr

$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    if ($process.HasExited) { break }
    try {
        Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2 | Out-Null
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
    Write-Host "`nSentrix did not start correctly." -ForegroundColor Red
    Write-Host "Error log: $StdErr" -ForegroundColor Yellow
    if (Test-Path $StdErr) { Get-Content $StdErr -Tail 30 }
    exit 1
}

Start-Process $Url
Write-Host "`nSentrix is running." -ForegroundColor Green
Write-Host "Browser: $Url" -ForegroundColor White
Write-Host 'Keep this window open while using Sentrix.' -ForegroundColor Yellow
Write-Host 'Press Ctrl+C or close this window when finished.' -ForegroundColor DarkGray

try {
    Wait-Process -Id $process.Id
} finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
}
