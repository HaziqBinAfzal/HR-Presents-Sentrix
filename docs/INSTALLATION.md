# Sentrix Installation Guide

This guide explains how to install Sentrix locally. For a full first-time walkthrough with explanations for every command, read [BEGINNER_LOCALHOST_GUIDE.md](BEGINNER_LOCALHOST_GUIDE.md).

## Supported local setup

Use:

- Python 3.11, 3.12, or 3.13
- Git
- `pip`
- A Python virtual environment
- Windows PowerShell, Linux Terminal, or macOS Terminal

Python 3.14 is not the documented baseline. It may work, but some dependencies may not yet support it consistently.

## 1. Clone the repository

```bash
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
```

`git clone` downloads the repository. The `cd` command enters the project directory.

## 2. Select the permanent Sentrix branch

```bash
git fetch --all --prune
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
```

Confirm it:

```bash
git branch --show-current
```

Expected output:

```text
production/sentrix-permanent
```

## 3. Create and activate the virtual environment

Create the environment only once. Activate it again after every terminal or computer restart.

### Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Ubuntu/Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

A successful activation usually adds `(venv)` to the beginning of the terminal prompt.

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs Flask, SQLAlchemy, Pylint, Bandit, Radon, and the other packages required by Sentrix.

## 5. Create the environment file

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Ubuntu/Linux or macOS

```bash
cp .env.example .env
```

Do not commit `.env`. It may contain secrets and machine-specific configuration.

For localhost testing, review the development defaults. Production deployments must use a strong stable `SECRET_KEY`, secure database credentials, HTTPS, durable storage, and properly configured email settings.

## 6. Compile-check the project

```bash
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
```

No output normally means the check passed.

## 7. Start Sentrix

```bash
python app.py
```

Keep the terminal open and visit:

```text
http://127.0.0.1:5000
```

Paste this address into a web browser, not into PowerShell as a command.

## 8. Stop Sentrix

Return to the running terminal and press:

```text
Ctrl + C
```

## 9. Start it again later

### Windows PowerShell

```powershell
cd $HOME\HR-Presents-Sentrix
.\venv\Scripts\Activate.ps1
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
python app.py
```

### Ubuntu/Linux or macOS

```bash
cd ~/HR-Presents-Sentrix
source venv/bin/activate
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
python app.py
```

## 10. Run tests

```bash
python -m unittest discover -s tests -v
```

Focused tests:

```bash
python -m unittest tests.test_extractor_security -v
python -m unittest tests.test_report_content_enrichment -v
python -m unittest tests.test_report_project_mapping -v
```

## 11. Docker option

After creating `.env`, run:

```bash
docker compose up --build
```

Container deployment settings must be reviewed before production use, especially storage, database configuration, reverse-proxy settings, health checks, domain configuration, and HTTPS.

## 12. Updating an existing installation

Stop the server with `Ctrl + C`, then run:

```bash
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
pip install -r requirements.txt
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
python app.py
```

## 13. Common installation errors

### `No module named flask`

Activate the virtual environment and reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Port 5000 is already in use

Linux or macOS:

```bash
lsof -ti :5000 | xargs -r kill -9
python app.py
```

Windows PowerShell:

```powershell
netstat -ano | findstr :5000
taskkill /PID YOUR_PID /F
python app.py
```

### PowerShell will not activate the environment

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### The old version appears

```bash
git branch --show-current
git pull origin production/sentrix-permanent
git log -5 --oneline
```

Then restart the server and perform a hard browser refresh.

## 14. Related guides

- [Complete Beginner Localhost Guide](BEGINNER_LOCALHOST_GUIDE.md)
- [User Guide](USER_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Deployment](DEPLOYMENT.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
