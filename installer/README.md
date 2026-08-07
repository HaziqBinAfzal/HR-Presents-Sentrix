# Sentrix Windows Installer

This directory builds Sentrix as a native Windows executable and wraps it in an Inno Setup installer.

## Output

`dist/windows/Sentrix-v1-Setup.exe`

The installer creates:

- `C:\Program Files\Sentrix\Sentrix.exe`
- Start Menu shortcut
- Optional Desktop shortcut
- Windows uninstaller entry
- Automatic launch after installation

The launcher starts the bundled Flask application on an available localhost port and opens the user's default browser when the application becomes ready. Runtime data and logs are stored under `%LOCALAPPDATA%\Sentrix` rather than the protected installation directory.

## Local build requirements

- Windows x64
- Python 3.13 x64 with the `py` launcher
- Inno Setup 6

Run from the repository root:

```powershell
./installer/build.ps1
```

## GitHub Actions

The `Build Windows Installer` workflow builds the same setup executable on `windows-latest` and uploads it as the `Sentrix-v1-Windows-Installer` artifact.

## Code signing

The current build is unsigned. Before commercial distribution, sign both `Sentrix.exe` and `Sentrix-v1-Setup.exe` with a trusted Windows code-signing certificate to reduce SmartScreen warnings and prove publisher identity.
