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

## Overview

Sentrix is a Flask-based secure software analysis platform developed and maintained by **HR-Presents**. It allows authenticated users to upload a Python file or ZIP project, run multiple analyzers, review project-scoped findings, track analysis history, and generate professional security assessment reports.

The finalized Sentrix identity uses the **Electric Wing** logo throughout the application shell, favicon, social metadata, generated reports, and documentation. The permanent production branch is:

```text
production/sentrix-permanent
```

## Main capabilities

### User and account workflows

- User registration and secure login
- Password hashing and session management
- Logout and authenticated route protection
- User profile and account settings
- Signed, expiring password-reset links
- SMTP-based password-reset delivery
- User-scoped projects, analyses, reports, reviews, and history

Newly registered users can sign in immediately. Mandatory email verification is not part of the finalized workflow.

### Project analysis

Sentrix supports Python source files and ZIP-based Python projects. The analysis pipeline includes:

- Python syntax validation
- Pylint code-quality analysis
- Bandit security scanning
- Radon complexity measurements
- Formatting and structural inspection
- Project metadata and code metrics
- Optional operator-configured AI-assisted recommendations

The platform records analysis information such as project name, file count, line count, functions, classes, comments, duration, quality score, security findings, complexity, raw scanner output, recommendations, and report paths.

### Secure archive handling

ZIP extraction is hardened against common archive attacks, including:

- Path traversal
- Absolute paths
- Symlinks and unsafe members
- Duplicate normalized paths
- Nested archives
- Excessive member counts
- Oversized individual files
- Excessive expanded size
- Suspicious compression ratios

Upload and extraction limits are configurable and should be reviewed for the target deployment environment.

### Dashboard and history

Authenticated users receive a database-backed workspace containing:

- Project totals
- Analysis totals
- Generated report totals
- Recent project activity
- Analysis result access
- Downloadable reports
- Project and analysis history
- User ownership enforcement

Users cannot access another user's project, result, or report through direct object references.

### Professional reporting

Sentrix generates self-contained branded HTML reports suitable for browser review, printing, and saving as PDF.

The report preserves a consistent finalized structure while providing detailed technical and educational content, including:

- Executive summary
- Project profile and analysis methodology
- Code-quality findings
- Static security findings
- Complexity and maintainability findings
- Raw scanner evidence
- Root-cause explanations
- Business and technical impact
- Severity interpretation
- Secure remediation guidance
- Verification and prevention guidance
- Project-specific standards mapping
- Project-specific security-control mapping

Where scanner evidence contains a source location, the report can associate the issue with its affected file, line, or scanner rule. When evidence is insufficient, the report states that a project-specific location cannot safely be asserted instead of inventing one.

### Standards and security controls

Report interpretation may reference applicable security and compliance frameworks, including:

- OWASP Top 10
- OWASP ASVS
- CWE Top 25
- MITRE CAPEC and ATT&CK where applicable
- NIST SSDF
- NIST Cybersecurity Framework
- NIST SP 800-53
- CIS security guidance
- SANS secure coding practices
- CERT secure coding standards
- PCI DSS where applicable
- ISO/IEC 27001 and ISO/IEC 27002
- SOC 2 security principles
- GDPR security requirements where applicable
- HIPAA security requirements where applicable

These mappings are technical guidance and do not represent certification, legal advice, or proof of compliance.

The report also evaluates ten major security-control areas:

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

### Light and dark appearance

Sentrix includes a persistent light/dark mode toggle in the navigation bar. The selected mode is stored in the browser and remains active across navigation and future visits. The finalized dark mode covers headings, paragraphs, forms, tables, cards, dropdowns, accordions, results, report summaries, badges, and custom result components.

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

## Repository structure

```text
.
├── app.py                         # Flask application entry point
├── config.py                      # Environment-driven configuration
├── database.py                    # Database compatibility export
├── extensions.py                  # Flask extension instances
├── forms.py                       # Authentication and application forms
├── models.py                      # SQLAlchemy models
├── requirements.txt               # Python dependencies
├── analyzer/
│   ├── ai.py                      # Optional AI recommendation support
│   ├── complexity.py              # Radon integration
│   ├── extractor.py               # Secure project extraction
│   ├── formatter.py               # Formatting analysis
│   ├── lint.py                    # Pylint integration
│   ├── security.py                # Bandit integration
│   ├── syntax.py                  # Syntax validation
│   └── routes/                    # Application blueprints and routes
├── helpers/
│   ├── report_enrichment.py       # Enterprise report explanations
│   ├── report_project_mapping.py  # Project-specific standards/control evidence
│   └── report_service.py          # Report generation service
├── templates/                     # Jinja application pages
├── static/
│   ├── css/                       # Shared application styling
│   ├── images/                    # Sentrix branding assets
│   └── js/                        # Client-side scripts when present
├── migrations/                    # Versioned database migrations
├── tests/                         # Automated test suite
├── docs/                          # Operational and developer documentation
├── deploy/nginx/                  # Nginx deployment example
├── .github/workflows/ci.yml       # CI validation
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

## Requirements

Recommended local environment:

- Python 3.11 to 3.13
- `pip`
- A Python virtual environment
- SQLite for local development, or a configured production database
- Pylint, Bandit, and Radon installed from `requirements.txt`

Python 3.14 may work in some environments, but the documented and CI-targeted range should be treated as the supported baseline unless CI is expanded.

## Local installation on Linux or macOS

```bash
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
git fetch origin
git switch production/sentrix-permanent
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Local installation on Windows PowerShell

```powershell
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
git fetch origin
git switch production/sentrix-permanent
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Environment configuration

Copy `.env.example` to `.env` and configure values appropriate to the environment. Important settings include:

- `APP_ENV`
- `SECRET_KEY`
- `DATABASE_URL`
- `DATABASE_AUTO_CREATE`
- `MAX_CONTENT_LENGTH`
- SMTP host, port, username, password, sender, and TLS/SSL options
- Password-reset expiry
- Secure cookie settings
- Security-header settings
- Optional AI-provider configuration when enabled by the operator

Never commit `.env`, credentials, API keys, SMTP passwords, database secrets, private keys, or generated user data.

Production startup must use a strong stable `SECRET_KEY`. Do not rely on development defaults in a production environment.

## Database and migrations

Local development may use automatic table creation when explicitly enabled. Production deployments should use committed migrations.

Typical migration workflow:

```bash
flask db upgrade
```

Before applying migrations to an existing populated database:

1. Create a verified backup.
2. Inspect the existing schema.
3. Confirm the current migration revision.
4. Test the migration against a disposable copy.
5. Prepare a rollback and restore procedure.

Do not stamp or upgrade a legacy database without understanding whether its existing tables already match the migration baseline.

## Running tests

Activate the virtual environment and run:

```bash
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
python -m unittest discover -s tests -v
```

Focused report tests can be run with:

```bash
python -m unittest tests.test_report_content_enrichment -v
python -m unittest tests.test_report_project_mapping -v
```

Secure extraction tests can be run with:

```bash
python -m unittest tests.test_extractor_security -v
```

## Updating a local checkout to the permanent branch

Use the following when the local working copy should exactly match the permanent branch:

```bash
cd ~/HR-Presents-Sentrix
git fetch --all --prune
git switch production/sentrix-permanent
git reset --hard origin/production/sentrix-permanent
git clean -fd
```

`git reset --hard` and `git clean -fd` permanently remove uncommitted changes and untracked files.

## Docker

Build and start the configured services with:

```bash
docker compose up --build
```

Review `.env`, storage mounts, database configuration, reverse-proxy settings, health checks, and HTTPS termination before production use.

## Production deployment

A production deployment should use:

- Gunicorn or another supported production WSGI server
- Nginx or an equivalent reverse proxy
- HTTPS
- Secure cookies
- Strong secrets supplied through the environment
- Migration-managed database changes
- Durable storage for uploads and generated reports
- Centralized logging
- Monitoring and alerting
- Backup and restore procedures
- Rate limiting or upstream request controls where appropriate

The included deployment files are examples and must be reviewed for the target host, domain, certificate paths, user permissions, storage paths, and database service.

## Security model

Sentrix applies layered protections including:

- Password hashing
- CSRF-protected forms
- Signed password-reset tokens
- Generic password-reset responses to reduce account enumeration
- Authenticated route protection
- Owner-scoped project, analysis, and report access
- Secure archive extraction controls
- Upload limits
- Environment-based secrets
- Production configuration checks
- Security response headers where enabled
- Secure-cookie and HSTS options for production
- Escaping of project-derived report content

Static analysis results are indicators requiring developer review. A clean scan does not prove that a project is vulnerability-free, and a scanner finding does not automatically prove exploitability.

For vulnerability reporting and supported security procedures, read [SECURITY.md](SECURITY.md).

## Reports and generated data

Uploads, generated reports, corrected files, databases, environment files, logs, caches, and local runtime artifacts are excluded through `.gitignore` and `.dockerignore` where appropriate.

Generated reports may contain project names, source locations, scanner evidence, code excerpts, security findings, and remediation guidance. Treat them as potentially sensitive and apply appropriate access control, retention, storage, and deletion policies.

## Documentation

Additional documentation is available in:

- [Release notes](RELEASE_NOTES.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- `docs/` for installation, deployment, architecture, API, operations, troubleshooting, and user guidance

## Branding

The permanent application identity is:

```text
Sentrix
Presented by HR-Presents
```

Primary brand assets are stored in `static/images/`. The Electric Wing SVG is the preferred scalable source for the website shell, favicon, documentation, and generated reports.

## Developers

### Ruveeha Ashfaq

- GitHub: `ruveeha33`
- LinkedIn: `ruveeha-ashfaq-632b15378`

### Haziq Afzal

- GitHub: `HaziqBinAfzal`
- LinkedIn: `haziq-afzal-010b6636a`

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change. Contributions should preserve:

- Sentrix branding
- Existing user and report workflows
- User ownership boundaries
- Secure extraction controls
- Environment-driven configuration
- Migration compatibility
- Automated tests
- Light and dark mode readability
- The finalized professional report structure

## License

No license should be assumed unless a license file is explicitly added to the repository. All rights remain with the repository owners and HR-Presents unless stated otherwise.

## Status

The latest consolidated working version is maintained on:

```text
production/sentrix-permanent
```

This branch is the source of truth for the finalized Sentrix application and its current documentation.