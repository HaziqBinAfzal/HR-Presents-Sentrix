# Sentrix Roadmap

This roadmap describes the intended direction of **Sentrix by HR-Presents**. It is not a promise of dates or guaranteed features. Security, data integrity, reliability, compatibility, and evidence-based reporting take priority over feature expansion.

## Current finalized baseline

The latest consolidated application is maintained on:

```text
production/sentrix-permanent
```

The current baseline includes:

- Final Sentrix Electric Wing branding
- Registration, login, logout, profiles, settings, and password reset
- Immediate sign-in after registration without mandatory email verification
- User-scoped projects, analyses, history, reviews, and reports
- Secure Python file and ZIP-project uploads
- Syntax, Pylint, Bandit, Radon, formatting, and structural analysis
- Professional branded HTML reports
- Project-specific standards and security-control mappings
- Persistent light and dark modes
- Database migrations and compatibility handling
- Automated tests and CI configuration
- Docker, Docker Compose, Gunicorn, and Nginx deployment assets

## v1.0.0 — Stable production release

- Complete clean-checkout validation on supported Python versions.
- Confirm the entire automated test suite passes in CI.
- Validate database migration upgrade, downgrade, backup, and restore procedures.
- Validate Docker and non-container deployment paths.
- Verify HTTPS, reverse proxy, secure cookies, security headers, health checks, and process management.
- Complete accessibility and responsive-layout review.
- Complete cross-browser light/dark mode validation.
- Review all documentation commands against the release commit.
- Confirm no secrets, generated data, temporary files, or obsolete product branding remain in tracked files.
- Select and add an explicit project license when approved by the repository owners.
- Tag the exact approved release commit.

## v1.1 — Reliability and maintainability

- Improve background execution for large or long-running analyses.
- Add job state, retry behavior, cancellation, and failure recovery.
- Add structured application and audit logging.
- Add richer operational health and performance metrics.
- Improve analyzer isolation and timeout handling.
- Expand regression tests for reports, authorization, uploads, and dark mode.
- Improve database portability beyond local SQLite workflows.
- Reduce remaining compatibility shims after verified migrations.

## v1.2 — Reporting and secure-development workflows

- Add validated report export formats beyond printable HTML.
- Improve project-to-project and run-to-run comparison.
- Add remediation status and verification tracking.
- Add configurable report branding for approved deployments while preserving Sentrix attribution.
- Expand dependency inventory and transitive dependency analysis.
- Add stronger evidence normalization across scanner outputs.
- Improve standards mapping precision and control-level references.
- Add export retention and deletion policies.

## v1.3 — Team workflows

- Shared workspaces with explicit project roles.
- Review assignment and status workflows.
- Organization-level settings.
- Audit events for security-sensitive actions.
- Configurable retention and export policies.
- Team-level dashboards and reporting.
- Access-control tests for every organization and workspace boundary.

## Future exploration

- Versioned public API after endpoint contracts and authentication are stabilized.
- Git repository provider integrations.
- Pull-request and commit analysis workflows.
- Pluggable analyzer framework.
- Software bill of materials generation and validation.
- Additional language support where analysis quality can be maintained.
- Enterprise identity and policy integrations driven by validated demand.
- Deployment profiles for managed cloud environments.

## Prioritization principles

1. Protect user data and project source code.
2. Preserve authorization boundaries.
3. Avoid unsupported security or compliance claims.
4. Keep report evidence traceable to scanner output.
5. Maintain backward compatibility where safe.
6. Require tests for security-sensitive changes.
7. Keep the permanent branch clean and deployable.
8. Do not describe experimental features as production-ready.

Experimental capabilities must include documented limitations, operational guidance, tests, and failure-handling behavior before promotion into the stable product.
