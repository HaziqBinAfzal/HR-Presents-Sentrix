# Sentrix by HR-Presents

<p align="center">
  <img src="static/images/sentrix-electric-spark-wing.svg" alt="Sentrix Electric Wing" width="140">
</p>

<p align="center">
  <strong>Professional Python code quality, security, complexity, and reporting platform.</strong>
</p>

<p align="center">
  <a href="RELEASE_NOTES.md"><img src="https://img.shields.io/badge/release-v1.0.0--RC1-orange" alt="Release"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11--3.13-blue" alt="Python"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.x-black" alt="Flask"></a>
  <a href="https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/actions/workflows/ci.yml"><img src="https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

## New user? Start here

You do not need previous Flask experience.

Read the complete guide:

### [Open the Sentrix Beginner Localhost Guide](docs/BEGINNER_LOCALHOST_GUIDE.md)

It explains every step for Windows, Ubuntu/Linux, and macOS, including:

- Installing and checking Git
- Installing and checking Python
- Downloading Sentrix
- Selecting the correct permanent branch
- Creating and activating a virtual environment
- Installing dependencies
- Creating `.env`
- Starting localhost
- Registering the first account
- Uploading the first project
- Understanding reports
- Stopping and restarting Sentrix
- Updating to the latest version
- Fixing common beginner errors

The permanent source-of-truth branch is:

```text
production/sentrix-permanent
```

## Five-minute Linux/macOS start

```bash
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
git switch production/sentrix-permanent
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open in a browser:

```text
http://127.0.0.1:5000
```

## Five-minute Windows PowerShell start

```powershell
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
git switch production/sentrix-permanent
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open in a browser:

```text
http://127.0.0.1:5000
```

Do not type the localhost address as a PowerShell command. Paste it into Chrome, Edge, Firefox, Safari, or another browser.

## Running Sentrix again after restarting the computer

You only create the virtual environment and install dependencies during the first setup.

### Linux/macOS

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

Stop the local server with:

```text
Ctrl + C
```

---

## What Sentrix is

Sentrix is a Flask-based secure software analysis platform developed and maintained by **HR-Presents**. Authenticated users can upload Python files or ZIP projects, run multiple analyzers, review project-scoped findings, track analysis history, and generate professional security assessment reports.

Sentrix is designed for:

- Python developers
- Cybersecurity students
- Software engineering students
- Security analysts
- DevSecOps engineers
- Technical reviewers
- Academic project evaluation
- Secure code review and education

## Core features

### Accounts and workspace

- User registration
- Secure login and logout
- Password hashing
- Session management
- Password-reset tokens
- User profile and settings
- User-scoped projects, analyses, reviews, reports, and history

New users can sign in immediately. Mandatory email verification is not part of the finalized workflow.

### Python project analysis

- Python syntax validation
- Pylint code-quality analysis
- Bandit security scanning
- Radon complexity analysis
- Formatting and structural inspection
- Project metrics and metadata
- Optional operator-configured AI recommendations

Sentrix supports individual `.py` files and supported ZIP-based Python projects.

### Secure ZIP extraction

The extraction layer protects against:

- Path traversal
- Absolute paths
- Symlink members
- Duplicate normalized paths
- Nested archives
- Excessive archive members
- Oversized files
- Excessive expanded size
- Suspicious compression ratios

### Dashboard and history

Authenticated users can review:

- Total projects
- Total analyses
- Generated reports
- Recent activity
- Analysis results
- Downloadable reports
- Project and analysis history

Ownership checks prevent users from opening another user’s projects, results, or reports through direct URLs.

### Professional reports

Sentrix creates self-contained branded HTML reports suitable for browser review, printing, and saving as PDF.

The report includes:

- Executive summary
- Project profile
- Analysis methodology
- Code-quality findings
- Static security findings
- Complexity and maintainability information
- Raw scanner evidence
- Root-cause explanations
- Business and technical impact
- Severity interpretation
- Remediation and prevention guidance
- Project-specific standards mapping
- Project-specific security-control mapping

When the scanner provides a source location, the report can show the related file, line, or scanner rule. When evidence is missing, Sentrix does not invent a location.

### Standards represented in reports

Technical mappings may reference:

- OWASP Top 10
- OWASP ASVS
- CWE Top 25
- MITRE CAPEC and ATT&CK where applicable
- NIST SSDF
- NIST Cybersecurity Framework
- NIST SP 800-53
- CIS guidance
- SANS secure coding practices
- CERT secure coding standards
- PCI DSS where applicable
- ISO/IEC 27001 and ISO/IEC 27002
- SOC 2 security principles
- GDPR security requirements where applicable
- HIPAA security requirements where applicable

These mappings are technical guidance. They are not certification, legal advice, or proof of compliance.

### Top security controls

1. Secure authentication
2. Authorization and access control
3. Input validation
4. Output encoding
5. Cryptography
6. Secrets management
7. Logging and monitoring
8. Secure configuration management
9. Dependency and supply-chain security
10. Secure error handling

### Light and dark mode

The navigation bar includes a persistent day/night toggle. The selected theme is saved in the browser and remains active across pages and future visits.

---

## Basic user walkthrough

1. Start Sentrix with `python app.py`.
2. Open `http://127.0.0.1:5000` in a browser.
3. Select **Get Started** or **Register**.
4. Create an account.
5. Sign in.
6. Open **Upload**.
7. Select a `.py` file or supported ZIP project.
8. Start the analysis.
9. Review the Results page.
10. Open or download the professional report.
11. Use **Print / PDF** to save a PDF through the browser.
12. Open **History** later to review previous analyses.

For detailed explanations, read the [User Guide](docs/USER_GUIDE.md).

---

## Requirements

Recommended local environment:

- Python 3.11, 3.12, or 3.13
- Git
- `pip`
- A Python virtual environment
- Internet access during dependency installation
- SQLite for normal local development

Python 3.14 is not the documented support baseline.

## Environment setup

Copy `.env.example` to `.env`.

Linux/macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Important configuration areas include:

- Application environment
- `SECRET_KEY`
- Database URL
- Automatic local table creation
- Upload-size limits
- SMTP host and credentials
- Password-reset expiry
- Secure cookie settings
- Security headers
- Optional AI-provider configuration

Never commit `.env`, passwords, API keys, SMTP credentials, private keys, database credentials, or generated user data.

## Compile and test

Activate the virtual environment, then run:

```bash
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
python -m unittest discover -s tests -v
```

Focused tests:

```bash
python -m unittest tests.test_extractor_security -v
python -m unittest tests.test_report_content_enrichment -v
python -m unittest tests.test_report_project_mapping -v
```

A successful unittest run ends with:

```text
OK
```

## Updating to the latest permanent version

Stop Sentrix with `Ctrl + C`, then run:

```bash
git switch production/sentrix-permanent
git pull origin production/sentrix-permanent
pip install -r requirements.txt
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
python app.py
```

To make a local checkout exactly match the remote branch, the following commands are available, but they permanently discard uncommitted and untracked local work:

```bash
git fetch --all --prune
git switch production/sentrix-permanent
git reset --hard origin/production/sentrix-permanent
git clean -fd
```

Back up important files before using the destructive reset.

---

## Repository structure

```text
.
├── app.py                         # Flask application entry point
├── config.py                      # Environment-based configuration
├── database.py                    # Database compatibility export
├── extensions.py                  # Flask extension instances
├── forms.py                       # Web forms
├── models.py                      # SQLAlchemy models
├── requirements.txt               # Python dependencies
├── analyzer/
│   ├── ai.py                      # Optional AI support
│   ├── complexity.py              # Radon integration
│   ├── extractor.py               # Secure archive extraction
│   ├── formatter.py               # Formatting checks
│   ├── lint.py                    # Pylint integration
│   ├── security.py                # Bandit integration
│   ├── syntax.py                  # Python syntax checks
│   └── routes/                    # Flask blueprints and routes
├── helpers/
│   ├── report_enrichment.py       # Detailed report explanations
│   ├── report_project_mapping.py  # Evidence-aware standards mapping
│   └── report_service.py          # Report generation
├── templates/                     # HTML/Jinja pages
├── static/
│   ├── css/                       # Website styles
│   ├── images/                    # Sentrix branding assets
│   └── js/                        # Browser scripts
├── migrations/                    # Database migrations
├── tests/                         # Automated tests
├── docs/                          # User, installation, and technical guides
├── deploy/nginx/                  # Nginx deployment example
├── .github/workflows/ci.yml       # GitHub Actions validation
├── Dockerfile
├── docker-compose.yml
├── gunicorn.conf.py
├── CHANGELOG.md
├── RELEASE_NOTES.md
├── ROADMAP.md
├── SECURITY.md
├── CONTRIBUTING.md
└── CODE_OF_CONDUCT.md
```

---

## Technology stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Mail
- SQLAlchemy
- Alembic / Flask-Migrate
- Pylint
- Bandit
- Radon
- Bootstrap 5
- Font Awesome
- Chart.js
- Gunicorn
- Nginx
- Docker and Docker Compose
- GitHub Actions

## Docker

After reviewing and creating `.env`:

```bash
docker compose up --build
```

The included deployment assets are examples. Review storage, database, domains, HTTPS, permissions, health checks, and reverse-proxy settings before production use.

## Production deployment

Do not expose the Flask development server directly to the public internet.

A production deployment should include:

- Gunicorn or another supported WSGI server
- Nginx or an equivalent reverse proxy
- HTTPS
- Strong environment-managed secrets
- Secure cookies
- Migration-managed database changes
- Durable upload and report storage
- Centralized logs
- Monitoring and alerts
- Backup and restore procedures
- Request controls or rate limiting

Read [Deployment Guide](docs/DEPLOYMENT.md).

## Security notes

Sentrix uses layered protections including:

- Password hashing
- CSRF-protected forms
- Signed password-reset tokens
- Generic reset responses to reduce account enumeration
- Authenticated routes
- Owner-scoped project and report access
- Secure archive extraction
- Upload limits
- Environment-based secrets
- Security response headers
- Production cookie and HSTS options
- Escaping of project-derived report content

Static-analysis output requires human review. A clean scan does not prove a project is vulnerability-free, and a scanner finding does not automatically prove exploitability.

Read [SECURITY.md](SECURITY.md) before reporting a vulnerability.

## Generated and sensitive data

The following should not be committed:

- `.env`
- Local databases
- Uploaded projects
- Generated reports
- Corrected files
- Logs
- Caches
- Virtual environments
- Credentials and secret keys

Reports may contain project names, source locations, evidence, code excerpts, and security findings. Treat them as sensitive when analyzing private projects.

---

## Documentation index

### Beginner and user documentation

- [Complete Beginner Localhost Guide](docs/BEGINNER_LOCALHOST_GUIDE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Frequently Asked Questions](docs/FAQ.md)

### Technical and operational documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Administrator Guide](docs/ADMIN_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Guide](docs/SECURITY.md)
- [API and Route Guide](docs/API.md)
- [Release Checklist](docs/RELEASE_CHECKLIST.md)

### Project documents

- [Release Notes](RELEASE_NOTES.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

---

## Common first-run fixes

### `No module named flask`

Activate the virtual environment, then run:

```bash
pip install -r requirements.txt
```

### Port 5000 is already being used

Linux/macOS:

```bash
lsof -ti :5000 | xargs -r kill -9
python app.py
```

Windows:

```powershell
netstat -ano | findstr :5000
taskkill /PID YOUR_PID /F
python app.py
```

### PowerShell blocks activation

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### The browser shows an old version

1. Confirm the branch with `git branch --show-current`.
2. Pull the permanent branch.
3. Restart `python app.py`.
4. Hard-refresh the browser with `Ctrl + Shift + R`.

For more solutions, read [Troubleshooting Guide](docs/TROUBLESHOOTING.md).

---

## Branding

The permanent identity is:

```text
Sentrix
Presented by HR-Presents
```

The Electric Wing SVG in `static/images/` is the primary scalable brand asset.

## Developers

### Ruveeha Ashfaq

- GitHub: `ruveeha33`
- LinkedIn: `ruveeha-ashfaq-632b15378`

### Haziq Afzal

- GitHub: `HaziqBinAfzal`
- LinkedIn: `haziq-afzal-010b6636a`

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Changes should preserve:

- Sentrix branding
- Existing website structure and functionality
- User ownership boundaries
- Secure extraction controls
- Environment-based configuration
- Migration compatibility
- Automated tests
- Light and dark mode readability
- The finalized professional report structure

## License

No license should be assumed unless a license file is explicitly added. All rights remain with the repository owners and HR-Presents unless stated otherwise.

## Current source of truth

```text
production/sentrix-permanent
```

This branch contains the finalized working Sentrix application and its maintained documentation.
