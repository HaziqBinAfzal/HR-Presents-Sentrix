# Sentrix v1.0.0-RC1 Release Notes

**Release candidate date:** August 6, 2026  
**Product:** Sentrix by HR-Presents  
**Permanent branch:** `production/sentrix-permanent`

## Release overview

Sentrix v1.0.0-RC1 is the consolidated production-oriented release candidate for the HR-Presents Python project analysis platform. It combines authenticated project analysis, secure archive handling, database-backed history, professional security reporting, project-specific standards interpretation, deployment assets, automated tests, and a finalized light/dark user interface.

The permanent application identity is **Sentrix — Presented by HR-Presents**, using the Electric Wing brand asset across the navigation, footer, favicon, metadata, documentation, and generated reports.

## Included product areas

- Registration, login, logout, sessions, password hashing, profiles, and settings
- Signed expiring password-reset links with SMTP delivery
- Immediate sign-in after registration; mandatory email verification is not used
- Python file and ZIP-project upload
- Secure ZIP extraction and resource controls
- Syntax, Pylint, Bandit, Radon, formatting, and structural analysis
- Optional operator-configured AI-assisted recommendations
- Dashboard, project history, analysis history, and reviews
- Owner-scoped results and report access
- Self-contained branded HTML reports
- Project-specific standards and security-control interpretation
- Persistent light and dark appearance modes
- Docker, Docker Compose, Gunicorn, Nginx, and GitHub Actions support

## Professional reporting

The finalized report structure remains visually consistent while containing deeper technical and educational analysis.

Reports may include:

- Executive summary and project health
- Scope and methodology
- Quality, security, and complexity findings
- Scanner evidence, rules, file names, and line numbers when available
- Root cause and exploitation context
- Business and technical impact
- Severity interpretation
- Secure implementation and remediation guidance
- Prevention and verification steps
- Standards and compliance interpretation
- Top ten security-control analysis

Standards guidance may reference OWASP Top 10, OWASP ASVS, CWE Top 25, MITRE CAPEC and ATT&CK where applicable, NIST SSDF, NIST CSF, NIST SP 800-53, CIS, SANS, CERT, PCI DSS, ISO/IEC 27001, ISO/IEC 27002, SOC 2, GDPR, and HIPAA.

Mappings are evidence-aware. When retained scanner output does not establish a project-specific relationship or location, Sentrix reports insufficient evidence instead of creating unsupported claims. Standards mapping is guidance and does not constitute certification or legal advice.

## Security controls represented

The reporting engine covers these principal control areas:

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

## Security protections

- Password hashing and authenticated sessions
- CSRF-protected browser forms
- Signed password-reset tokens
- Generic reset responses to reduce account enumeration
- User ownership checks for projects, analyses, and reports
- Report-content escaping
- Environment-based secrets and production configuration
- Secure-cookie and security-header options
- ZIP traversal, absolute-path, symlink, nested-archive, duplicate-path, member-count, expanded-size, per-member-size, and compression-ratio controls

Static analysis is an aid to secure development and does not prove that software is vulnerability-free. Findings require developer review and risk validation.

## User interface

The current interface includes:

- Finalized Sentrix navigation and branding
- Home, About, Contact, Dashboard, Upload, History, Profile, Settings, authentication, and results pages
- Professional Reports overview on the home page
- Persistent light/dark mode toggle
- Dark-mode readability across headings, paragraphs, cards, forms, tables, dropdowns, accordions, results, report summaries, and badges
- Responsive Bootstrap-based layouts

## Repository and deployment

The release includes:

- Environment template
- Versioned database migrations
- Automated unit tests
- Secure extraction tests
- Report enrichment and project-mapping tests
- GitHub Actions workflow
- Dockerfile
- Docker Compose configuration
- Gunicorn configuration
- Nginx deployment example
- Security, contribution, roadmap, release, and operational documentation

## Validation commands

```bash
python -m compileall -q app.py analyzer helpers forms.py models.py config.py tests
python -m unittest discover -s tests -v
```

Focused report validation:

```bash
python -m unittest tests.test_report_content_enrichment -v
python -m unittest tests.test_report_project_mapping -v
```

Focused extraction validation:

```bash
python -m unittest tests.test_extractor_security -v
```

## Local startup

```bash
python app.py
```

Default local address:

```text
http://127.0.0.1:5000
```

## Production requirements

Before production deployment:

- Set a strong stable `SECRET_KEY`
- Configure the production database and migrations
- Configure HTTPS
- Enable secure cookies and appropriate security headers
- Review SMTP settings
- Review upload and extraction limits
- Use a production WSGI server
- Configure reverse proxy limits and timeouts
- Use durable protected storage for uploads and reports
- Configure logging, monitoring, backups, retention, and restore procedures
- Test authorization and cross-user access controls
- Run the complete automated test suite

## Database upgrade guidance

Existing populated databases must be backed up and inspected before applying migration changes. Test upgrades against a disposable copy first. Do not stamp a legacy database unless its current schema and migration state are understood.

## Known limitations

- Optional AI recommendations depend on operator configuration and provider availability.
- Static scanners can produce false positives and false negatives.
- Compliance references are technical mappings, not certifications.
- SQLite is appropriate for local development and smaller single-instance deployments but may not suit horizontally scaled production use.
- Deployment examples must be adapted to the target domain, operating system, storage, database, certificates, and security requirements.

## Source of truth

The latest finalized and consolidated application is maintained on:

```text
production/sentrix-permanent
```

Use this branch when installing, validating, deploying, or continuing Sentrix development.
