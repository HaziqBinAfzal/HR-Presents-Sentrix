# Sentrix by HR-Presents

<p align="center">
  <img src="static/images/sentrix-electric-spark-wing.svg" alt="Sentrix Electric Wing" width="150">
</p>

<p align="center">
  <strong>Python code quality, security, complexity analysis, and professional reporting — in one local Windows application.</strong>
</p>

<p align="center">
  <strong>✅ Sentrix v1.0.0 FINAL — Official Windows Release</strong>
</p>

---

## Sentrix v1.0.0

Sentrix is developed and presented by **HR-Presents**. The project includes the Windows application, source code, analysis modules, templates/static assets, documentation, build configuration, and project workflows.

### Commercial Source License

Sentrix and HR-Presents' original source code are proprietary commercial software. Paid copies that include source code are supplied under the **Sentrix Commercial Source License**.

**Read the full license:** [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)

The license permits an authorized purchaser to use Sentrix, inspect and modify the supplied source code, and use Sentrix for personal, educational, internal-business, freelance, and commercial project work.

Unless HR-Presents separately agrees in writing, purchase does **not** grant the right to resell, redistribute, publicly upload, sublicense, white-label, or sell Sentrix/source code as a competing standalone product.

Third-party libraries and components remain subject to their own licenses.

---

## Final Windows Release

The compiled Windows customer application is available from the official GitHub Release.

**[Sentrix v1.0.0 FINAL — Official Windows Customer Release](https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0)**

Under **Assets**, the compiled application is:

```text
Sentrix-v1.0.0-Windows.zip
```

### Start Sentrix

1. Download and fully extract the ZIP.
2. Open the extracted folder.
3. Double-click `Start Sentrix.bat`.
4. Keep the Sentrix console window open while using the application.
5. Sentrix opens locally at `http://127.0.0.1:5000`.

The compiled executable is located at:

```text
Runtime\Sentrix.exe
```

No separate Python installation is required for the compiled Windows application.

---

## What Sentrix Does

Sentrix is a local Python project analysis platform combining multiple analysis tools in a browser-based workspace.

### Included analysis

- **Pylint** — code quality and linting
- **Bandit** — Python security analysis
- **Radon** — complexity and maintainability analysis
- **Black** — formatting checks
- Python syntax validation
- Project metrics and structured findings
- Professional analysis reports

### Core features

- Python file and ZIP project upload
- Secure project extraction
- Code-quality scoring
- Security findings
- Complexity analysis
- Formatting analysis
- User accounts and protected analysis history
- Downloadable professional reports
- Local operation at `127.0.0.1`
- Compiled Windows distribution

---

## Windows Requirements

- Windows 10 or Windows 11, 64-bit
- Enough free disk space for the extracted application and analysis data
- A modern browser such as Microsoft Edge, Google Chrome, or Firefox

---

## User Data

Sentrix stores runtime and user data separately from the application package at:

```text
%LOCALAPPDATA%\Sentrix
```

Treat uploaded projects and generated reports as sensitive if they contain private code or security findings.

---

## Security and Privacy

Sentrix is designed to run locally. Static-analysis results should still be reviewed by a human: a clean scan does not guarantee that a project contains no vulnerabilities, and a scanner finding does not automatically prove exploitability.

Never commit or publicly share private `.env` files, API keys, passwords, SMTP credentials, databases, uploaded customer projects, or generated reports containing sensitive information.

See [SECURITY.md](SECURITY.md).

---

## Source Code and Documentation

The source-of-truth branch is `main`.

Developer documentation is available under [`docs/`](docs/).

Important project documents:

- [Commercial Source License](COMMERCIAL_LICENSE.md)
- [Release Notes](RELEASE_NOTES.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)

Automated validation and Windows builds are handled through GitHub Actions in `.github/workflows/`.

---

## Copyright and Licensing

Copyright (c) 2026 **HR-Presents**. All rights reserved.

HR-Presents' original Sentrix code, documentation, branding, Electric Wing artwork, and other original materials are proprietary. Authorized purchasers receive only the rights specifically granted by [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) or a separate written agreement from HR-Presents.

Third-party components remain governed by their respective licenses.

---

## HR-Presents

**Sentrix** is developed and presented by **HR-Presents**.

### Haziq Afzal

- GitHub: [HaziqBinAfzal](https://github.com/HaziqBinAfzal)
- LinkedIn: [haziq-afzal-010b6636a](https://www.linkedin.com/in/haziq-afzal-010b6636a/)

### Ruveeha Ashfaq

- GitHub: [ruveeha33](https://github.com/ruveeha33)
- LinkedIn: [ruveeha-ashfaq-632b15378](https://www.linkedin.com/in/ruveeha-ashfaq-632b15378/)
