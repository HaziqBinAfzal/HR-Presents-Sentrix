# Changelog

All notable changes to Sentrix are documented here.

## [Unreleased]

### Planned
- Final RC acceptance testing against the release branch.
- Stable `v1.0.0` release after RC approval.

## [1.0.0-rc1] - 2026-08-06

### Added
- Complete Sentrix production-readiness baseline and branding cleanup.
- Email verification, resend flow, and verified-login enforcement.
- Secure ZIP extraction with traversal, symlink, nested archive, duplicate path, size, member-count, and compression-ratio protections.
- Owner-only access controls for analysis results and generated reports.
- Versioned Flask-Migrate/Alembic database baseline at revision `20260806_0001`.
- Database preflight utility that creates a timestamped backup and reports integrity, schema, row counts, and Alembic state.
- Automated tests for authentication, email verification, report authorization, production security configuration, database compatibility, archive security, and archive resource limits.
- Extractor benchmark utility and CI performance regression gate.
- GitHub Actions checks for Python 3.11 and 3.13, database migration round trips, code quality, high-severity security findings, extractor performance, and Docker image builds.

### Changed
- Production deployments now default to migration-managed schema changes instead of automatic table creation.
- Development and tests may still enable automatic creation through `DATABASE_AUTO_CREATE`.
- Authentication route wiring now consistently uses the verified-email handlers.
- UTC timestamp handling is compatible with current Python releases.
- Security-sensitive configuration is driven by environment variables.

### Security
- Production startup rejects a missing `SECRET_KEY`.
- Secure cookies and HSTS default to enabled when `APP_ENV=production`.
- Responses include CSP, frame denial, MIME protection, referrer policy, and permissions policy when security headers are enabled.
- Unverified users cannot log in, and verification tokens are invalid after an email-address change.
- ZIP archives are rejected above 5,000 members, 500 MB expanded size, 100 MB per member, or a 200:1 compression ratio.
- CI blocks syntax and undefined-name errors plus high-severity Bandit findings.

### Validation
- 31 automated tests pass locally and in CI.
- Alembic upgrade, downgrade-to-base, and re-upgrade are verified automatically.
- The production container build is verified in CI.
- A local 5,000-file benchmark completed extraction in approximately 2.8 seconds with about 6.4 MiB peak traced Python memory.

### Upgrade notes
- Existing populated SQLite databases created before Alembic must be backed up and inspected before being stamped to `20260806_0001`.
- Do not execute the baseline upgrade directly against an existing database whose application tables already match the current schema.

[Unreleased]: https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/compare/v1.0.0-rc1...HEAD
[1.0.0-rc1]: https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/releases/tag/v1.0.0-rc1
