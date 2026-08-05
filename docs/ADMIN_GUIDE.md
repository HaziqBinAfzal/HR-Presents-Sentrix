# Sentrix Administrator Guide

## Responsibilities

Administrators are responsible for secure configuration, deployment, database and file storage, SMTP, backups, migrations, monitoring, incident response, upgrades, and access control. Application defaults are not a substitute for an operating policy.

## Production configuration

Provide secrets through a protected environment or secret manager. Use a stable high-entropy `SECRET_KEY`; changing it invalidates existing signed sessions and tokens. Set an explicit `DATABASE_URL`, SMTP credentials, provider credentials, storage locations, upload limits, and environment label.

Disable debug mode. Do not expose the Flask development server. Use HTTPS and configure secure session cookies after confirming proxy headers are handled safely.

## Database operations

Use a managed or separately administered relational database for multi-instance or business-critical deployments. SQLite is acceptable for local and small single-process installations but requires careful backup and locking expectations.

Treat migration files as release artifacts. Before each upgrade:

1. Back up the database.
2. Test the migration on representative data.
3. Record expected duration and locking behavior.
4. Define rollback criteria.
5. Verify row counts and critical workflows after migration.

The current startup path calls `db.create_all()`. This does not safely replace migrations for existing schemas.

## Storage and permissions

Uploads, extracted projects, generated reports, corrected files, and diffs can contain sensitive source code. Store them outside a public web root, use least-privilege ownership, isolate tenants at the application layer, monitor capacity, and include required artifacts in backup policy.

## Mail configuration

Sentrix currently targets SMTP with TLS. Use an application password or service credential, not a personal primary password. Restrict sender identity, test verification and reset emails, monitor delivery failures, and rotate credentials after suspected exposure.

## Health checks

A liveness check should prove the process responds. A readiness check may verify required dependencies such as the database and writable storage without exposing credentials or internal details. Keep expensive analysis and email tests out of frequent health probes.

## Monitoring and logging

Monitor request errors, authentication failures, analysis failures, queue or processing latency where applicable, database connectivity, mail delivery, disk usage, report generation, dependency health, and certificate expiry. Use structured logs with request correlation. Never log passwords, reset tokens, API keys, session cookies, or full private source files.

## Backups

Define recovery point and recovery time objectives. Back up the database, configuration references, and durable generated artifacts. Encrypt backups, separate them from the application host, restrict access, test restoration regularly, and document how application and database versions are matched.

## Updating

Read release notes, verify dependency and Python compatibility, back up data, deploy to staging, run migrations, complete smoke tests, deploy using a controlled rollout, and retain rollback capability. Avoid in-place unreviewed edits on production hosts.

## Session management

Use HTTPS-only cookies in production, HTTP-only cookies, an appropriate SameSite policy, limited session lifetime, and server-side invalidation strategy where required. Revoke or invalidate sessions after account compromise, secret rotation, or major authorization changes.

## Disaster recovery

Maintain a written procedure covering incident declaration, service isolation, credential rotation, clean infrastructure provisioning, database and file restoration, integrity verification, DNS/proxy restoration, user communication, and post-incident review.

## Production checklist

Complete every item in `RELEASE_NOTES.md`, including tests, migrations, TLS, reverse proxy, process supervision, backups, restore drill, repository hygiene, and license selection. A release candidate is not production-approved until those controls are verified in the target environment.
