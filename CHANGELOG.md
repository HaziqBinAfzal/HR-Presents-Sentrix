# Changelog

All notable changes to **Sentrix by HR-Presents** are documented here.

## [Unreleased]

No post-v1.0.0 changes are currently designated for release.

## [1.0.0] - 2026-08-08

### Final release

- Published **Sentrix v1.0.0** as the official final Windows customer release.
- Standardized `main` as the source-of-truth branch for the final release and future development.
- Published the compiled Windows customer package as `Sentrix-v1.0.0-Windows.zip`.
- Published the matching SHA-256 checksum file.
- Confirmed the final customer package contains `Runtime\Sentrix.exe` and its bundled runtime dependencies.
- Kept full project source code and developer documentation in the GitHub repository while excluding readable Sentrix project source from the customer ZIP.
- Finalized the Sentrix Electric Wing branding and customer-facing release documentation.

### Added

- User registration, login, logout, password hashing, sessions, profiles, and settings.
- Signed expiring password-reset tokens with SMTP delivery.
- User-scoped project, analysis, history, review, and report workflows.
- Secure ZIP extraction protections for traversal, absolute paths, symlinks, nested archives, duplicate normalized paths, member count, expanded size, per-member size, and compression ratio.
- Owner-only access controls for project results and generated reports.
- Python syntax validation.
- Pylint code-quality scanning.
- Bandit security scanning.
- Radon complexity analysis.
- Black formatting analysis.
- Formatting and structural analysis.
- Optional operator-configured AI-assisted recommendations.
- Database-backed dashboard and history metrics.
- Self-contained branded HTML reports suitable for printing and saving as PDF.
- Versioned Flask-Migrate/Alembic database baseline.
- Database preflight and compatibility utilities.
- Automated tests for authentication, authorization, reports, configuration, database compatibility, archive security, report enrichment, and project-specific mappings.
- GitHub Actions checks for compilation, tests, migration validation, security scanning, container builds, and the compiled Windows distribution.
- Docker, Docker Compose, Gunicorn, and Nginx deployment examples.
- Compiled Nuitka Windows customer edition requiring no separate Python installation.

### Changed

- Product branding standardized as **Sentrix — Presented by HR-Presents**.
- The Electric Wing became the primary brand asset.
- Production configuration became environment-driven.
- Production deployments default to migration-managed schema changes.
- Development and tests may explicitly enable automatic database creation.
- UTC timestamp handling aligned with current supported Python releases.
- Report content became more technical and educational while preserving the finalized visible structure.
- Project-specific standards and security-control mappings connect retained findings to scanner evidence, source locations, rules, risk context, and remediation guidance.
- Windows customer data is stored separately under `%LOCALAPPDATA%\Sentrix`.
- The final Windows customer package is source-free and includes bundled Pylint, Bandit, Black, and Radon functionality.

### Fixed

- Corrected dark-mode visibility across application and result components.
- Corrected report and results-page text that inherited light-theme colors.
- Prevented standards mappings from inventing project locations where evidence is unavailable.
- Prevented analyzer failures from being represented as fake zero scores.
- Corrected Windows compiled-web smoke testing for PowerShell compatibility.
- Finalized generated-report storage in the Sentrix data directory.

### Security

- Production startup rejects missing or unsafe secret configuration where enforced by application settings.
- Secure-cookie, HSTS, CSP, frame-denial, MIME-protection, referrer-policy, and permissions-policy options are available for production use.
- Password-reset responses are generic to reduce account enumeration.
- Successful password changes invalidate previously issued reset links.
- Cross-user access to projects, analyses, and reports is denied.
- Project-derived report content is escaped before HTML rendering.
- ZIP archives are checked against configured resource and path-safety limits.
- Customer builds reject readable Sentrix project source and development files before publication.

### Final Windows package

Official release asset:

```text
Sentrix-v1.0.0-Windows.zip
```

Official SHA-256:

```text
224d3c7cc161f5fce787931fc20aaaaacb9776be865e65769728ea09dd1ed4b0
```

Official release:

https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0

## [1.0.0-rc1] - 2026-08-06

Sentrix v1.0.0-RC1 was the release candidate preceding the final v1.0.0 Windows customer release.

[Unreleased]: https://github.com/HR-Presents/HR-Presents-Sentrix/compare/v1.0.0...main
[1.0.0]: https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0
[1.0.0-rc1]: https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0-rc1
