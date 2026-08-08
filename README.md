# Sentrix by HR-Presents

<p align="center">
  <img src="static/images/sentrix-electric-spark-wing.svg" alt="Sentrix Electric Wing" width="150">
</p>

<p align="center">
  <strong>Python code quality, security, complexity analysis, and professional reporting — in one local Windows application.</strong>
</p>

<p align="center">
  <a href="https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/releases/latest"><strong>⬇ Download Latest Sentrix for Windows</strong></a>
</p>

---

## Download Sentrix

**Normal users should download Sentrix from the Releases page. You do not need to clone this repository or install Python.**

### Step 1 — Open the latest release

Go to:

**[Latest Sentrix Release](https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/releases/latest)**

### Step 2 — Download the Windows ZIP

Under **Assets**, download:

```text
Sentrix-v1-Windows-Portable.zip
```

Do **not** download GitHub's automatically generated `Source code (zip)` or `Source code (tar.gz)` files unless you specifically want the source code.

### Step 3 — Extract the ZIP

Right-click the downloaded ZIP and choose:

```text
Extract All...
```

Extract it to a normal folder such as:

```text
Desktop\Sentrix
```

or:

```text
Documents\Sentrix
```

Do not run Sentrix directly from inside the ZIP preview.

### Step 4 — Start Sentrix

Open the extracted folder and double-click:

```text
Start Sentrix.bat
```

Sentrix includes its own Python 3.13 runtime and required dependencies. A separate Python installation is not required.

A Sentrix console window will open, then your browser should automatically open:

```text
http://127.0.0.1:5000
```

Keep the Sentrix console window open while using the application.

### Step 5 — Use Sentrix

1. Open Sentrix.
2. Register or sign in.
3. Open **Upload**.
4. Select a Python `.py` file or supported ZIP project.
5. Start the analysis.
6. Review the results.
7. Open or download the generated report.
8. Use **History** to return to previous analyses.

---

## What Sentrix Does

Sentrix is a local Python project analysis platform developed by **HR-Presents**. It combines multiple analysis tools into a single browser-based workspace running locally on your Windows computer.

### Included analysis

- **Pylint** — code quality and linting
- **Bandit** — Python security analysis
- **Radon** — complexity and maintainability analysis
- **Black** — formatting checks
- Python syntax validation
- Project metrics and structured findings
- Professional analysis reports

### Core product features

- Python file and ZIP project upload
- Secure project extraction
- Code-quality scoring
- Security findings
- Complexity analysis
- Formatting analysis
- User accounts and protected analysis history
- Downloadable reports
- Local operation at `127.0.0.1`
- Bundled Windows Python runtime

---

## Windows Requirements

For the portable Windows release you need:

- Windows 10 or Windows 11, 64-bit
- Enough free disk space for the extracted application and analysis data
- A modern browser such as Microsoft Edge, Google Chrome, or Firefox

You do **not** need:

- Python installed separately
- Git
- Visual Studio
- Docker
- Command-line setup
- A virtual environment

---

## Where Sentrix Stores User Data

Sentrix keeps runtime/user data in the Windows local application-data area rather than inside the application package.

Typical location:

```text
%LOCALAPPDATA%\Sentrix
```

This helps keep generated data separate from the portable application files.

Treat uploaded source projects and generated reports as sensitive if they contain private code or security findings.

---

## Troubleshooting

### Windows warns about the downloaded file

Because Sentrix is distributed as a downloaded application package, Windows or your browser may display a security prompt for an unfamiliar download.

Only run Sentrix if you downloaded it from the official **HR-Presents Sentrix GitHub Releases** page.

### `Start Sentrix.bat` does not start

Make sure you extracted the ZIP completely first. Do not launch it while browsing the ZIP archive itself.

### Port 5000 is already in use

Close any older Sentrix console window and start Sentrix again.

If another application is using port 5000, close that application before launching Sentrix.

### Browser does not open automatically

With the Sentrix console still running, open this address manually in your browser:

```text
http://127.0.0.1:5000
```

### Sentrix closes immediately

Run `Start Sentrix.bat` again and read the message shown in the console window. When reporting a problem, include the exact error text or a screenshot.

---

## Verify Your Download

Official releases may include a SHA-256 checksum file next to the ZIP.

On Windows PowerShell you can verify the downloaded ZIP with:

```powershell
Get-FileHash .\Sentrix-v1-Windows-Portable.zip -Algorithm SHA256
```

Compare the result with the SHA-256 value published with the release.

---

## Important Download Note

GitHub automatically shows two additional files on every tagged release:

```text
Source code (zip)
Source code (tar.gz)
```

Those are GitHub-generated source archives. They are **not the normal Windows customer download**.

For normal Windows use, download:

```text
Sentrix-v1-Windows-Portable.zip
```

---

## Security and Privacy

Sentrix is designed to run locally. Static-analysis results should still be reviewed by a human: a clean scan does not guarantee that a project contains no vulnerabilities, and a scanner finding does not automatically prove exploitability.

The secure ZIP extraction layer includes protections against unsafe archive behavior such as path traversal, nested archives, duplicate normalized paths, excessive archive expansion, oversized members, and suspicious compression ratios.

Never commit or publicly share private `.env` files, API keys, passwords, SMTP credentials, databases, uploaded customer projects, or generated reports containing sensitive source information.

See [SECURITY.md](SECURITY.md) for the project security policy.

---

## For Developers

The downloadable Windows ZIP is intended for customers and normal users.

Developers who want to inspect or contribute to the source can use this repository directly. The application is built with Python, Flask, SQLAlchemy, Pylint, Bandit, Radon, Black, Bootstrap, and related tooling.

Developer documentation is available under [`docs/`](docs/).

Useful project documents:

- [Release Notes](RELEASE_NOTES.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)

Automated validation is handled through GitHub Actions in `.github/workflows/`.

---

## HR-Presents

**Sentrix** is developed and presented by **HR-Presents**.

### Haziq Afzal

- GitHub: [HaziqBinAfzal](https://github.com/HaziqBinAfzal)
- LinkedIn: [haziq-afzal-010b6636a](https://www.linkedin.com/in/haziq-afzal-010b6636a/)

### Ruveeha Ashfaq

- GitHub: [ruveeha33](https://github.com/ruveeha33)
- LinkedIn: [ruveeha-ashfaq-632b15378](https://www.linkedin.com/in/ruveeha-ashfaq-632b15378/)

---

## Official Release

The official customer download is always published through GitHub Releases:

### **[Download the Latest Sentrix Release](https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/releases/latest)**

If this repository is transferred to another official HR-Presents GitHub account, GitHub repository redirects should continue directing existing repository links to the transferred repository.