# Sentrix by HR-Presents

<p align="center">
  <img src="static/images/sentrix-electric-spark-wing.svg" alt="Sentrix Electric Wing" width="150">
</p>

<p align="center">
  <strong>Python code quality, security, complexity analysis, and professional reporting — in one local Windows application.</strong>
</p>

<p align="center">
  <strong>✅ Sentrix v1.0.0 FINAL — Official Windows Customer Release</strong>
</p>

<p align="center">
  <a href="https://github.com/HR-Presents/HR-Presents-Sentrix/releases/latest"><strong>⬇ Download Sentrix v1.0.0 for Windows</strong></a>
</p>

---

## Final Windows Release

**Sentrix v1.0.0 is the final official Windows customer release.** Normal users should download the compiled package from GitHub Releases. You do not need to clone this repository, install Python, install Git, or have GitHub installed.

### Official download

Open the official release:

**[Sentrix v1.0.0 — Compiled Windows Customer Edition](https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0)**

Under **Assets**, download exactly:

```text
Sentrix-v1.0.0-Windows.zip
```

Do **not** download GitHub's automatically generated `Source code (zip)` or `Source code (tar.gz)` archives for normal customer use.

### Start Sentrix

1. Download `Sentrix-v1.0.0-Windows.zip`.
2. Right-click it and choose **Extract All...**.
3. Open the extracted `Sentrix-v1.0.0-Windows` folder.
4. Double-click:

```text
Start Sentrix.bat
```

5. Keep the Sentrix console window open while using the application.
6. Your browser should open automatically at:

```text
http://127.0.0.1:5000
```

The package contains the compiled application at:

```text
Runtime\Sentrix.exe
```

A separate Python installation is **not required**.

---

## Official Package Layout

```text
Sentrix-v1.0.0-Windows/
├── Start Sentrix.bat
├── README.txt
├── LICENSE.txt
└── Runtime/
    ├── Sentrix.exe
    ├── static/
    │   └── Sentrix Electric Wing branding assets
    └── compiled/runtime dependencies
```

The official customer package is compiled with Nuitka and intentionally excludes readable Sentrix project source files and development files such as project `.py` source, tests, `.git`, `.github`, and `requirements.txt`.

---

## Verify the Final Download

The official release also provides:

```text
Sentrix-v1.0.0-Windows.sha256.txt
```

Official final ZIP SHA-256:

```text
224d3c7cc161f5fce787931fc20aaaaacb9776be865e65769728ea09dd1ed4b0
```

Verify it in Windows PowerShell with:

```powershell
Get-FileHash .\Sentrix-v1.0.0-Windows.zip -Algorithm SHA256
```

The result must match the official checksum above.

---

## What Sentrix Does

Sentrix is a local Python project analysis platform developed by **HR-Presents**. It combines multiple analysis tools into a browser-based workspace running locally on Windows.

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
- Downloadable professional reports
- Local operation at `127.0.0.1`
- Compiled Windows customer distribution
- Pylint, Bandit, Black, and Radon functionality bundled with the compiled application

---

## Windows Requirements

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
- GitHub access to run the downloaded customer edition

---

## Where Sentrix Stores User Data

Sentrix stores runtime and user data separately from the application package at:

```text
%LOCALAPPDATA%\Sentrix
```

Treat uploaded projects and generated reports as sensitive if they contain private code or security findings.

---

## Troubleshooting

### Windows warns about the downloaded file

Windows or your browser may display a security prompt for an unfamiliar downloaded application. Only run Sentrix if you downloaded it from the official **HR-Presents Sentrix GitHub Release**.

### `Start Sentrix.bat` does not start

Make sure you extracted the ZIP completely first. Do not run Sentrix from inside the ZIP preview.

### Port 5000 is already in use

Close any older Sentrix console window and start Sentrix again. If another program is using port 5000, close it first.

### Browser does not open automatically

With the Sentrix console still running, manually open:

```text
http://127.0.0.1:5000
```

### Sentrix closes immediately

Run `Start Sentrix.bat` again and read the console message. Include the exact error text or a screenshot when reporting a problem.

---

## Security and Privacy

Sentrix is designed to run locally. Static-analysis results should still be reviewed by a human: a clean scan does not guarantee that a project contains no vulnerabilities, and a scanner finding does not automatically prove exploitability.

The secure ZIP extraction layer includes protections against unsafe archive behavior such as path traversal, nested archives, duplicate normalized paths, excessive archive expansion, oversized members, and suspicious compression ratios.

Never commit or publicly share private `.env` files, API keys, passwords, SMTP credentials, databases, uploaded customer projects, or generated reports containing sensitive source information.

See [SECURITY.md](SECURITY.md) for the project security policy.

---

## For Developers

The downloadable Windows ZIP is the **customer edition**. Developers who want the full source code and project documentation should use this repository directly.

The official source-of-truth branch for Sentrix v1.0.0 and future development is:

```text
main
```

Developer documentation is available under [`docs/`](docs/).

Useful project documents:

- [Release Notes](RELEASE_NOTES.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)

Automated validation and the compiled Windows release are handled through GitHub Actions in `.github/workflows/`.

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

## Official Final Release

### **[Download Sentrix v1.0.0 for Windows](https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0)**

For Windows customers, choose **`Sentrix-v1.0.0-Windows.zip`** under **Assets**. This is the final compiled customer package.