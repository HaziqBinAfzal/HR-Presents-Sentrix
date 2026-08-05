# Changelog

All notable changes to Sentrix are documented here. The format follows Keep a Changelog and the project intends to use Semantic Versioning after the first stable release.

## [Unreleased]

### Planned
- Complete automated test coverage for critical user journeys.
- Verify container images and Compose deployment.
- Complete migration and restore drills against production-like data.

## [1.0.0-RC1] - 2026-08-05

### Added
- Release-candidate documentation set for users, administrators, developers, API consumers, deployment, architecture, security, troubleshooting, and contribution workflows.
- Release notes, roadmap, code of conduct, security policy, and production verification checklist.
- Professional project overview, environment reference, architecture diagram, and installation guidance.

### Changed
- Reframed Sentrix documentation around the capabilities present in the repository.
- Marked Docker, CI, migration, and production verification work explicitly rather than claiming unverified readiness.

### Security
- Documented secret management, session hardening, upload controls, SMTP configuration, HTTPS, reverse-proxy controls, backups, incident response, and vulnerability reporting.

### Known release blockers
- Flask development mode remains enabled in the current entry point and must be disabled before production deployment.
- Backup and editor-save artifacts remain in the repository pending safe removal verification.
- Docker, Compose, Nginx, process-manager, and CI files require repository-level implementation and execution verification.
- A final license text has not yet been selected and committed.

[Unreleased]: https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/compare/v1.0.0-RC1...HEAD
[1.0.0-RC1]: https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/releases/tag/v1.0.0-RC1
