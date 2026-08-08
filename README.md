# Sentrix by HR-Presents

<p align="center">
  <img src="static/images/sentrix-electric-spark-wing.svg" alt="Sentrix Electric Wing" width="150">
</p>

<p align="center">
  <strong>Python code quality, security, complexity analysis, and professional reporting — in one local Windows application.</strong>
</p>

<p align="center">
  <a href="https://github.com/HR-Presents/HR-Presents-Sentrix/releases/latest"><strong>⬇ Download Latest Sentrix for Windows</strong></a>
</p>

---

## Download Sentrix

**Normal users should download the compiled Windows customer edition from Releases. You do not need to clone this repository, install Python, or have GitHub installed.**

### Step 1 — Open the latest release

**[Latest Sentrix Release](https://github.com/HR-Presents/HR-Presents-Sentrix/releases/latest)**

### Step 2 — Download the customer ZIP

Under **Assets**, download:

```text
Sentrix-v1.0.0-Windows.zip
```

Do **not** download GitHub's automatically generated `Source code (zip)` or `Source code (tar.gz)` files for normal customer use.

### Step 3 — Extract the ZIP

Right-click the downloaded ZIP, choose **Extract All...**, and extract it to a normal folder such as:

```text
Desktop\Sentrix
```

Do not run Sentrix directly from inside the ZIP preview.

### Step 4 — Start Sentrix

Open the extracted folder and double-click:

```text
Start Sentrix.bat
```

The customer edition contains a compiled `Sentrix.exe` and its required runtime dependencies. **A separate Python installation is not required.**

A Sentrix console window will open, then your browser should automatically open:

```text
http://127.0.0.1:5000
```

Keep the Sentrix console window open while using the application.

### Step 5 — Use Sentrix

1. Register or sign in.
2. Open **Upload**.
3. Select a Python `.py` file or supported ZIP project.
4. Start the analysis.
5. Review code-quality, security, complexity, and formatting results.
6. Open or download the generated report.
7. Use **History** to return to previous analyses.

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
- Downloadable reports
- Local operation at `127.0.0.1`
- Compiled Windows customer distribution
- Pylint, Bandit, Black, and Radon functionality bundled with the compiled application

---

## Customer Edition

The official Windows customer package is built with Nuitka and distributed as:

```text
Sentrix-v1.0.0-Windows/
├── Start Sentrix.bat
├── README.txt
├── LICENSE.txt
└── Runtime/
    ├── Sentrix.exe
    └── compiled/runtime dependencies
```

The release workflow explicitly rejects readable Sentrix Python source and development files from the customer package. Files such as project `.py` source, `requirements.txt`, tests, `.git`, and `.github` are not intended to be included in the customer ZIP.

Compilation prevents customers from simply opening the distributed application as normal Python source. Like other compiled software, it should not be treated as absolute protection against expert reverse engineering.

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

Sentrix stores runtime/user data separately from the application package at:

```text
%LOCALAPPDATA%\Sentrix
```

Treat uploaded source projects and generated reports as sensitive if they contain private code or security findings.

---

## Verify Your Download

The official v1.0.0 release includes:

```text
Sentrix-v1.0.0-Windows.sha256.txt
```

You can verify the ZIP in Windows PowerShell with:

```powershell
Get-FileHash .\Sentrix-v1.0.0-Windows.zip -Algorithm SHA256
```

Official v1.0.0 customer ZIP SHA-256:

```text
224d3c7cc161f5fce787931fc20aaaaacb9776be865e65769728ea09dd1ed4b0
```

Compare the calculated value with the checksum file published beside the release asset.

---

## Troubleshooting

### Windows warns about the downloaded file

Because Sentrix is distributed as a downloaded application package, Windows or your browser may display a security prompt for an unfamiliar download. Only run Sentrix if you downloaded it from the official **HR-Presents Sentrix GitHub Releases** page.

### `Start Sentrix.bat` does not start

Make sure you extracted the ZIP completely first. Do not launch it while browsing the ZIP archive itself.

### Port 5000 is already in use

Close any older Sentrix console window and start Sentrix again. If another application is using port 5000, close that application first.

### Browser does not open automatically

With the Sentrix console still running, manually open:

```text
http://127.0.0.1:5000
```

### Sentrix closes immediately

Run `Start Sentrix.bat` again and read the console message. When reporting a problem, include the exact error text or a screenshot.

---

## Security and Privacy

Sentrix is designed to run locally. Static-analysis results should still be reviewed by a human: a clean scan does not guarantee that a project contains no vulnerabilities, and a scanner finding does not automatically prove exploitability.

The secure ZIP extraction layer includes protections against unsafe archive behavior such as path traversal, nested archives, duplicate normalized paths, excessive archive expansion, oversized members, and suspicious compression ratios.

Never commit or publicly share private `.env` files, API keys, passwords, SMTP credentials, databases, uploaded customer projects, or generated reports containing sensitive source information.

See [SECURITY.md](SECURITY.md) for the project security policy.

---

## For Developers

The downloadable Windows ZIP is intended for customers and normal users. Developers who want to inspect or contribute to the source can use this repository directly.

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

## Official Release

The official customer download is published through **HR-Presents** GitHub Releases:

### **[Download the Latest Sentrix Release](https://github.com/HR-Presents/HR-Presents-Sentrix/releases/latest)**

For Windows customers, choose **`Sentrix-v1.0.0-Windows.zip`** under **Assets**. Do not use GitHub's automatically generated source-code archives as the customer package.
