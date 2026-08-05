# Sentrix Roadmap

This roadmap describes intended direction, not a promise of dates or guaranteed features.

## v1.0.0 — Stable production release

- Close every RC1 production-gate item.
- Add verified WSGI, reverse proxy, HTTPS, health-check, and process-management deployment assets.
- Add verified Docker and Docker Compose workflows or explicitly exclude container support.
- Complete automated tests for authentication, authorization, uploads, analysis, reports, exports, profile, and settings.
- Validate migrations, backups, restore, rollback, monitoring, and incident-response procedures.
- Remove obsolete and generated repository artifacts.
- Select and commit the project license.

## v1.1 — Reliability and maintainability

- Improve background handling for long-running analyses.
- Add richer operational metrics and structured logging.
- Increase analyzer isolation and failure recovery.
- Expand report formats and export validation.
- Improve accessibility and cross-browser testing.

## v1.2 — Team workflows

- Shared workspaces and clearer project roles.
- Review assignment and status workflows.
- Organization-level settings and audit events.
- Configurable retention and export policies.

## Future exploration

- Versioned public API after endpoint contracts and authentication are stabilized.
- Repository-provider integrations.
- Pluggable analyzer framework.
- Additional language support where analysis quality can be maintained.
- Enterprise identity, policy, and deployment features driven by validated demand.

## Prioritization principles

Security and data integrity come first, followed by reliability, usability, maintainability, and new features. Experimental capabilities must not be described as production-ready until they have tests, operational guidance, and failure-handling behavior.
