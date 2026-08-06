# Sentrix Beginner Localhost Guide

This guide is written for people who have never run a Python or Flask project before. Follow the steps in order and do not skip a command unless the guide says it is optional.

Sentrix runs locally in your web browser at:

```text
http://127.0.0.1:5000
```

Running locally means the website is started on your own computer. It is not automatically published to the internet.

---

## 1. What you need before starting

You need:

- A Windows, Ubuntu/Linux, or macOS computer
- Internet access for the first installation
- Git
- Python 3.11, 3.12, or 3.13
- A terminal application
- At least 1 GB of free disk space

You do not need to install Flask, Bandit, Pylint, or Radon separately. They are installed from `requirements.txt` later.

---

## 2. Check whether Git is installed

Open a terminal.

### Windows

Open **PowerShell**:

1. Press the Windows key.
2. Type `PowerShell`.
3. Open **Windows PowerShell** or **Terminal**.

Run:

```powershell
git --version
```

### Ubuntu/Linux or macOS

Open **Terminal** and run:

```bash
git --version
```

A successful result looks similar to:

```text
git version 2.45.2
```

If the command is not recognized, install Git first.

- Windows: install Git from the official Git for Windows installer.
- Ubuntu/Debian: install the `git` package using your system package manager.
- macOS: install the Apple command-line tools or Git through Homebrew.

Close and reopen the terminal after installing Git.

---

## 3. Check whether Python is installed

### Windows PowerShell

Try:

```powershell
py --version
```

If that does not work, try:

```powershell
python --version
```

### Ubuntu/Linux or macOS

Run:

```bash
python3 --version
```

A supported result looks like:

```text
Python 3.11.x
Python 3.12.x
Python 3.13.x
```

Python 3.14 is not the documented baseline. Use Python 3.11–3.13 for the most predictable setup.

When installing Python on Windows, enable the installer option named **Add Python to PATH**.

---

## 4. Download Sentrix from GitHub

Choose a folder where you want to keep the project. Your home directory is fine.

### Windows PowerShell

```powershell
cd $HOME
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
```

### Ubuntu/Linux or macOS

```bash
cd ~
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
```

What these commands do:

- `cd` changes the current terminal folder.
- `git clone` downloads the repository.
- `cd HR-Presents-Sentrix` enters the downloaded project folder.

Check your current folder:

### Windows

```powershell
Get-Location
```

### Linux or macOS

```bash
pwd
```

The path should end with:

```text
HR-Presents-Sentrix
```

---

## 5. Switch to the permanent Sentrix branch

The finalized working version is maintained on:

```text
production/sentrix-permanent
```

Run:

```bash
git fetch --all --prune
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
```

These same Git commands work in PowerShell, Linux Terminal, and macOS Terminal.

Confirm the branch:

```bash
git branch --show-current
```

Expected result:

```text
production/sentrix-permanent
```

---

## 6. Create a virtual environment

A virtual environment keeps Sentrix packages separate from other Python projects.

Create it only once. You activate it again whenever you reopen the terminal or restart the computer.

### Windows PowerShell

```powershell
py -m venv venv
```

If `py` is unavailable but `python` works:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

### Ubuntu/Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

When activation succeeds, the terminal usually begins with:

```text
(venv)
```

Example:

```text
(venv) user@computer:~/HR-Presents-Sentrix$
```

---

## 7. Upgrade pip

Run:

```bash
python -m pip install --upgrade pip
```

`pip` is the tool Python uses to install packages.

---

## 8. Install Sentrix dependencies

Run:

```bash
pip install -r requirements.txt
```

This installs Flask and the other packages required by Sentrix.

The installation can take several minutes. Keep the terminal open until it finishes.

A warning about a newer pip version is not usually an error. A red traceback or a line beginning with `ERROR` must be resolved.

Verify Flask is installed:

```bash
python -c "import flask; print(flask.__version__)"
```

Verify the active Python belongs to the virtual environment:

### Windows

```powershell
where.exe python
```

### Linux or macOS

```bash
which python
```

The path should include the project’s `venv` folder.

---

## 9. Create the local environment file

Sentrix includes `.env.example`, which is a safe configuration template. Copy it to `.env`.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Ubuntu/Linux or macOS

```bash
cp .env.example .env
```

The `.env` file is for local settings and secrets. Do not upload it to GitHub.

For a basic localhost test, keep the default development values unless the application reports that a required value is missing.

For production, always use a long random `SECRET_KEY` and properly configured database, email, HTTPS, and storage settings.

---

## 10. Check the project before starting it

Run:

```bash
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
```

No output means the compilation check passed.

If Python prints an error, read the filename and line number in the message before continuing.

---

## 11. Start Sentrix

Run:

```bash
python app.py
```

A successful startup looks similar to:

```text
* Running on http://127.0.0.1:5000
```

Keep this terminal open. Closing it stops the local website.

Open a browser and visit:

```text
http://127.0.0.1:5000
```

Do not type the address as a PowerShell command. Paste it into Chrome, Edge, Firefox, Safari, or another browser.

---

## 12. Create your first Sentrix account

1. Open the Sentrix home page.
2. Select **Get Started** or **Register**.
3. Enter the requested account details.
4. Submit the registration form.
5. Open the login page.
6. Sign in using the account you created.

New users can sign in immediately. Mandatory email verification is not part of the finalized workflow.

---

## 13. Analyze your first Python project

1. Sign in.
2. Open **Upload** or **New Analysis**.
3. Select a `.py` file or supported ZIP project.
4. Enter the requested project information.
5. Start the analysis.
6. Wait for syntax, quality, security, and complexity checks to complete.
7. Open the Results page.

Sentrix may display:

- Syntax findings
- Pylint quality findings
- Bandit security findings
- Radon complexity information
- Project metrics
- Recommendations
- A professional report

Scanner findings require developer review. A finding is not automatically proof of a real exploitable vulnerability, and a clean scan is not proof that a project is completely secure.

---

## 14. Open and understand the report

The professional report can include:

- Executive summary
- Project scope
- Analysis methodology
- Quality and security findings
- Evidence and source locations when available
- Severity explanations
- Business and technical impact
- Remediation guidance
- Security standards mapping
- Top security controls mapping
- Raw scanner output

Use **Print / PDF** to print the report or save it as a PDF through the browser.

Standards mappings are technical guidance. They do not represent formal certification or legal advice.

---

## 15. Use light and dark mode

Use the moon or sun icon in the navigation bar.

- Moon icon: switch to dark mode.
- Sun icon: return to light mode.

The selected mode is saved in the browser.

---

## 16. Stop Sentrix

Return to the terminal running `python app.py` and press:

```text
Ctrl + C
```

This stops the local Flask server.

---

## 17. Run Sentrix again after restarting your computer

You do not need to clone the repository or recreate the virtual environment again.

### Ubuntu/Linux or macOS

```bash
cd ~/HR-Presents-Sentrix
source venv/bin/activate
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
python app.py
```

### Windows PowerShell

```powershell
cd $HOME\HR-Presents-Sentrix
.\venv\Scripts\Activate.ps1
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 18. Update to the latest Sentrix version

First stop the running server with `Ctrl + C`.

Then run:

```bash
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
pip install -r requirements.txt
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
python app.py
```

This preserves normal tracked local changes only when Git can merge them safely. Beginners should avoid editing application files in the same checkout used for updates.

To force the local repository to exactly match the permanent branch, use the destructive reset instructions in the main README only after backing up anything important.

---

## 19. Run the automated tests

Stop the website first, or open a second terminal and activate the same virtual environment.

Run:

```bash
python -m unittest discover -s tests -v
```

A passing test ends with:

```text
OK
```

Focused tests:

```bash
python -m unittest tests.test_extractor_security -v
python -m unittest tests.test_report_content_enrichment -v
python -m unittest tests.test_report_project_mapping -v
```

---

## 20. Common beginner problems

### Problem: `git` is not recognized

Cause: Git is not installed or the terminal was opened before installation finished.

Fix:

1. Install Git.
2. Close the terminal.
3. Open a new terminal.
4. Run `git --version` again.

### Problem: `python` or `py` is not recognized

Cause: Python is not installed or was not added to PATH.

Fix:

1. Install Python 3.11–3.13.
2. Enable **Add Python to PATH** on Windows.
3. Restart the terminal.
4. Run the version command again.

### Problem: `No module named flask`

Cause: The virtual environment is not active or dependencies were not installed.

Fix:

```bash
pip install -r requirements.txt
```

Also verify that `(venv)` appears in the terminal.

### Problem: PowerShell says script execution is disabled

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

This changes the policy only for the current PowerShell session.

### Problem: `Address already in use` or port 5000 is busy

#### Ubuntu/Linux or macOS

```bash
lsof -ti :5000 | xargs -r kill -9
python app.py
```

#### Windows PowerShell

Find the process:

```powershell
netstat -ano | findstr :5000
```

Use the PID shown in the final column:

```powershell
taskkill /PID YOUR_PID /F
```

Then run:

```powershell
python app.py
```

### Problem: Browser says it cannot connect

Check that:

- The terminal still shows the Flask server running.
- You opened `http://127.0.0.1:5000` in the browser.
- No startup traceback appeared.
- Another program is not blocking port 5000.

### Problem: `requirements.txt` installation fails

Run:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Also confirm you are using Python 3.11–3.13.

### Problem: changes do not appear in the browser

Perform a hard refresh:

```text
Windows/Linux: Ctrl + Shift + R
macOS: Command + Shift + R
```

Then restart the Flask server.

### Problem: the wrong or old version appears

Run:

```bash
git branch --show-current
git log -5 --oneline
git status
```

The branch should be:

```text
production/sentrix-permanent
```

---

## 21. Useful commands to remember

Show the current branch:

```bash
git branch --show-current
```

Show changed files:

```bash
git status
```

Show recent commits:

```bash
git log -5 --oneline
```

Activate the environment on Linux/macOS:

```bash
source venv/bin/activate
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Start Sentrix:

```bash
python app.py
```

Stop Sentrix:

```text
Ctrl + C
```

Leave the virtual environment:

```bash
deactivate
```

---

## 22. Safety notes

- Never commit `.env`.
- Never upload real passwords, private keys, API keys, customer code, or confidential reports to a public repository.
- Use test projects while learning.
- Back up the database before destructive Git resets or migrations.
- Do not expose the Flask development server directly to the public internet.
- Use Gunicorn, Nginx, HTTPS, secure environment configuration, durable storage, and operational monitoring for production deployment.

---

## 23. Where to continue

After Sentrix is running, read:

- [User Guide](USER_GUIDE.md)
- [Installation Guide](INSTALLATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Security Guide](SECURITY.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Developer Guide](DEVELOPER_GUIDE.md)

The permanent source of truth is:

```text
production/sentrix-permanent
```
