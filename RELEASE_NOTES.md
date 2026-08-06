# Sentrix v1.0.0-RC1 Release Notes

**Release candidate date:** August 5, 2026  
**Target:** First production-oriented Sentrix release candidate

## Purpose

RC1 turns the current Sentrix repository into a reviewable release candidate with a complete documentation baseline and an explicit production-gating checklist. It does not conceal unverified areas: release readiness requires a clean installation, test execution, migration validation, deployment verification, security review, and backup/restore drill.

## Included product areas

- Authentication and account workflows
- Project upload and extraction
- Python syntax, lint, formatting, complexity, and security analysis
- Optional AI-assisted recommendations
- Project, analysis, review, and history views
- Profile and settings management
- Report and export services
- SMTP-backed account email flows

## Documentation delivered

- Main repository README
- Installation, user, administrator, developer, API, architecture, deployment, security, troubleshooting, and FAQ guides
- Changelog, roadmap, contribution guide, code of conduct, and security policy

## Production gate checklist

### Application

- [ ] Set `debug=False` and verify no development server is used.
- [ ] Provide a stable production `SECRET_KEY` through the environment.
- [ ] Confirm secure cookie settings behind HTTPS.
- [ ] Verify CSRF protection on all state-changing browser forms.
- [ ] Confirm authorization checks prevent cross-user resource access.
- [ ] Verify upload size, extension, archive traversal, and extraction limits.

### Data and migrations

- [ ] Verify every expected migration is committed and ordered correctly.
- [ ] Run upgrade and downgrade tests on disposable databases.
- [ ] Rehearse migration against a recent production-like backup.
- [ ] Document database ownership, retention, and restore objectives.

### Deployment

- [ ] Add and test a production WSGI server dependency.
- [ ] Add and test `Dockerfile` and Compose definitions, or formally exclude containers from RC1.
- [ ] Add and test Nginx and process supervisor examples.
- [ ] Configure HTTPS and redirect HTTP to HTTPS.
- [ ] Add health/readiness checks that do not expose secrets.
- [ ] Confirm generated files use durable storage with correct permissions.

### Quality

- [ ] Run tests from a clean checkout.
- [ ] Run linting and static analysis.
- [ ] Test registration, verification, login, logout, password recovery, upload, analysis, review, history, report, export, profile, and settings workflows.
- [ ] Verify documentation links and commands.
- [ ] Verify supported Python versions on Windows, Linux, and macOS.

### Repository hygiene

- [ ] Remove `*.backup`, `*.save`, editor files, caches, generated databases, and generated user artifacts after confirming they are obsolete.
- [ ] Confirm `.gitignore` covers secrets, virtual environments, caches, local databases, uploads, generated reports, and IDE files.
- [ ] Confirm no API keys, SMTP credentials, session secrets, or user data exist in Git history intended for distribution.
- [ ] Select and commit the intended license.

### Operations

- [ ] Configure centralized logs and retention.
- [ ] Configure monitoring for availability, errors, latency, storage, and database health.
- [ ] Validate backups and perform a restore drill.
- [ ] Document rollback, incident response, and responsible contacts.

## Known limitations

- The current repository still contains cleanup candidates and unverified deployment components.
- API behavior must be derived from and tested against actual registered routes; this RC1 documentation distinguishes web routes from a guaranteed versioned public API.
- AI recommendations depend on external provider availability, credentials, model behavior, and configured limits.
- SQLite is suitable for local and small single-instance use but is not the default recommendation for horizontally scaled production deployment.

## Promotion criteria

Promote RC1 to `v1.0.0` only after every release-blocking checklist item is complete, critical findings are resolved, deployment and rollback are rehearsed, and the exact release commit is tagged.
