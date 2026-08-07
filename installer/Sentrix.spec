from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).parent.parent

hiddenimports = []
datas = []
binaries = []

for package in [
    "flask",
    "flask_login",
    "flask_mail",
    "flask_migrate",
    "flask_sqlalchemy",
    "flask_wtf",
    "sqlalchemy",
    "alembic",
    "jinja2",
    "wtforms",
    "email_validator",
    "reportlab",
    "openai",
    "bandit",
    "radon",
    "pylint",
    "flake8",
]:
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        hiddenimports += collect_submodules(package)

for folder in ["templates", "static", "migrations", "analyzer"]:
    source = ROOT / folder
    if source.exists():
        datas.append((str(source), folder))

for file_name in [".env.example", "README.md", "LICENSE", "LICENSE.md"]:
    source = ROOT / file_name
    if source.exists():
        datas.append((str(source), "."))

analysis = Analysis(
    [str(ROOT / "installer" / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="Sentrix",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
