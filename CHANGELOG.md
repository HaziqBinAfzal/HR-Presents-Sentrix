# Changelog

All notable changes to **Sentrix by HR-Presents** are documented here.

## [Unreleased]

### Changed

- Consolidated the latest working application on `production/sentrix-permanent`.
- Completed the permanent Sentrix Electric Wing branding across the application shell, metadata, reports, favicon, and documentation.
- Added a persistent light and dark appearance toggle.
- Completed dark-mode contrast fixes across home, authentication, dashboard, upload, history, profile, settings, results, report summaries, cards, forms, tables, dropdowns, accordions, badges, and custom result components.
- Added a Professional Reports overview to the home page.
- Expanded existing report sections with enterprise-grade technical explanations while preserving the finalized report structure and styling.
- Added project-specific standards and security-control mappings that connect retained findings to scanner evidence, source locations, rules, risk context, and remediation guidance.
- Updated repository documentation and removed obsolete planning and invalid placeholder assets.

### Fixed

- Corrected dark-mode visibility for result status and date badges.
- Corrected report and results-page text that inherited light-theme colors.
- Prevented standards mappings from inventing project locations where evidence is unavailable.

### Removed

- Mandatory email-verification workflow. Newly registered users can sign in immediately.
- Obsolete frontend planning documents.
- Empty and invalid image placeholders.

## [1.0.0-rc1] - 2026-08-06

### Added

- Sentrix production-readiness baseline.
- User registration, login, logout, password hashing, sessions, profiles, and settings.
- Signed expiring password-reset tokens with SMTP delivery.
- User-scoped project, analysis, history, review, and report workflows.
- Secure ZIP extraction protections for traversal, absolute paths, symlinks, nested archives, duplicate normalized paths, member count, expanded size, per-member size, and compression ratio.
- Owner-only access controls for project results and generated reports.
- Python syntax validation.
- Pylint code-quality scanning.
- Bandit security scanning.
- Radon complexity analysis.
- Formatting and structural analysis.
- Optional operator-configured AI-assisted recommendations.
- Database-backed dashboard and history metrics.
- Self-contained branded HTML reports suitable for printing and saving as PDF.
- Versioned Flask-Migrate/Alembic database baseline.
- Database preflight and compatibility utilities.
- Automated tests for authentication, authorization, reports, configuration, database compatibility, archive security, report enrichment, and project-specific mappings.
- GitHub Actions checks for supported Python versions, compilation, tests, migration validation, security scanning, and container builds.
- Docker, Docker Compose, Gunicorn, and Nginx deployment examples.

### Changed

- Product branding was standardized as **Sentrix — Presented by HR-Presents**.
- The Electric Wing became the primary scalable brand asset.
- Production configuration became environment-driven.
- Production deployments default to migration-managed schema changes.
- Development and tests may explicitly enable automatic database creation.
- UTC timestamp handling was aligned with current supported Python releases.
- Report content became more technical and educational without changing the finalized visible structure.

### Security

- Production startup rejects a missing or unsafe secret configuration where enforced by the application settings.
- Secure-cookie, HSTS, CSP, frame-denial, MIME-protection, referrer-policy, and permissions-policy options are available for production use.
- Password-reset responses are generic to reduce account enumeration.
- Successful password changes invalidate previously issued reset links.
- Cross-user access to projects, analyses, and reports is denied.
- Project-derived report content is escaped before HTML rendering.
- ZIP archives are checked against configured resource and path-safety limits.
- CI validates syntax, tests, and selected security conditions.

### Validation

- Python compilation is supported through `compileall`.
- The automated test suite is available under `tests/`.
- Focused tests cover secure extraction and report behavior.
- Migration upgrade and downgrade workflows are included in CI where configured.
- Container builds are validated by the repository workflow where configured.

### Upgrade notes

- Existing populated databases must be backed up and inspected before migration changes are applied.
- Do not stamp or upgrade a legacy database without confirming whether its existing schema already matches the migration baseline.
- Use `production/sentrix-permanent` as the source-of-truth branch for the latest consolidated application.

[Unreleased]: https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/compare/v1.0.0-rc1...production/sentrix-permanent
[1.0.0-rc1]: https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/releases/tag/v1.0.0-rc1
