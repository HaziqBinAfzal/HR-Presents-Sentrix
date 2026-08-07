$ErrorActionPreference = 'Stop'

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$InstallerDir = $PSScriptRoot
$BuildDir = Join-Path $Root 'build\windows'
$DistDir = Join-Path $Root 'dist\windows'
$VenvDir = Join-Path $BuildDir 'venv'
$Python = Join-Path $VenvDir 'Scripts\python.exe'
$Pip = Join-Path $VenvDir 'Scripts\pip.exe'

Write-Host '== Sentrix Windows build ==' -ForegroundColor Cyan
Write-Host "Repository: $Root"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw 'Python launcher (py.exe) was not found. Install Python 3.13 x64 for the build machine.'
}

New-Item -ItemType Directory -Force -Path $BuildDir, $DistDir | Out-Null

if (-not (Test-Path $Python)) {
    py -3.13 -m venv $VenvDir
}

& $Python -m pip install --upgrade pip wheel setuptools
& $Pip install -r (Join-Path $Root 'requirements.txt')
& $Pip install 'pyinstaller>=6.14,<7'

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root 'build\pyinstaller')
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root 'dist\Sentrix')
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $Root 'dist\Sentrix.exe')

Push-Location $Root
try {
    & $Python -m PyInstaller --clean --noconfirm --distpath (Join-Path $Root 'dist') --workpath (Join-Path $Root 'build\pyinstaller') (Join-Path $InstallerDir 'Sentrix.spec')
}
finally {
    Pop-Location
}

$AppExe = Join-Path $Root 'dist\Sentrix.exe'
if (-not (Test-Path $AppExe)) {
    throw "PyInstaller did not produce $AppExe"
}

Copy-Item -Force $AppExe (Join-Path $DistDir 'Sentrix.exe')

$Iscc = @(
    "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if (-not $Iscc) {
    throw 'Inno Setup 6 was not found. Install it on the build machine or use the GitHub Actions workflow.'
}

& $Iscc "/DSourceExe=$(Join-Path $DistDir 'Sentrix.exe')" "/DOutputDir=$DistDir" (Join-Path $InstallerDir 'Sentrix.iss')

$SetupExe = Join-Path $DistDir 'Sentrix-v1-Setup.exe'
if (-not (Test-Path $SetupExe)) {
    throw "Inno Setup did not produce $SetupExe"
}

Write-Host ''
Write-Host "Build complete: $SetupExe" -ForegroundColor Green
