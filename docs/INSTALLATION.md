# Installation Guide

## Prerequisites

Use Python 3.11 or newer, Git, and an up-to-date package installer. Python 3.14 may expose compatibility issues in dependencies that have not yet declared support, so verify the exact interpreter in CI before treating it as supported.

## Get the source

```bash
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
```

For RC1 evaluation, check out the release branch or exact release tag.

## Create a virtual environment

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Debian/Ubuntu, install the operating-system package that provides `venv` if environment creation fails.

### macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

A Homebrew or python.org interpreter is recommended instead of modifying the system Python.

## Configure the environment

Copy `.env.example` to `.env`. At minimum, create a strong persistent `SECRET_KEY`. Configure `MAIL_USERNAME` and `MAIL_PASSWORD` for verification and password-recovery email. Configure `OPENAI_API_KEY` only when AI-assisted features are enabled.

Example development file:

```dotenv
SECRET_KEY=replace-with-a-long-random-value
DATABASE_URL=sqlite:///instance/database.db
MAIL_USERNAME=
MAIL_PASSWORD=
OPENAI_API_KEY=
```

Do not commit `.env`.

## Initialize and run

The current application creates missing tables on startup. That behavior is convenient locally but controlled migrations are required in production.

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## Smoke test

Confirm that the home page loads, registration and login forms render, a test project can be uploaded, an analysis finishes, results are visible only to the owning user, and a report/export can be generated. Test email flows only with a non-production test account.

## Docker and Compose

Container deployment is not considered verified until the repository includes and tests a `Dockerfile`, `.dockerignore`, Compose file, health checks, non-root runtime, persistent storage declarations, and production startup command. Do not invent local files from documentation alone.

## Upgrade installation

1. Back up the database and generated artifacts.
2. Read `CHANGELOG.md` and `RELEASE_NOTES.md`.
3. Pull the intended tag or commit.
4. Activate the environment and install updated dependencies.
5. Run and verify migrations when migration files are present.
6. Restart the service and complete smoke tests.
7. Keep a rollback package and tested backup available.

## Uninstallation

Stop the service, retain required backups, then remove the checkout and virtual environment. Removing the checkout may delete local SQLite databases and generated reports if they are stored inside it, so inspect storage paths first.
