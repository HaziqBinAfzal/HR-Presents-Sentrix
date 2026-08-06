# Sentrix v1.0.0-rc1 Release Checklist

## Source and branch

- [ ] The release commit is on `release/v1.0.0-rc1`.
- [ ] The working tree is clean.
- [ ] No temporary trigger files, local databases, backups, secrets, or editor artifacts are tracked.
- [ ] `CHANGELOG.md` matches the release scope.
- [ ] The release tag will use `v1.0.0-rc1`.

## Automated validation

- [ ] Python 3.11 validation is green.
- [ ] Python 3.13 validation is green.
- [ ] Python quality and security is green.
- [ ] Alembic migration round trip is green.
- [ ] Extractor performance guard is green.
- [ ] Production container build is green.
- [ ] Full local unit suite passes.
- [ ] Project compilation passes.

## Database

- [ ] A fresh database upgrades to `20260806_0001 (head)`.
- [ ] Upgrade, downgrade to base, and re-upgrade complete successfully.
- [ ] Existing databases are backed up before stamping or upgrading.
- [ ] Existing user, project, analysis, review, and settings records remain intact.
- [ ] A restore drill has been completed with matching persistent file storage.

## Authentication and email

- [ ] Registration creates an unverified user.
- [ ] Verification email delivery works with production SMTP.
- [ ] Valid verification links verify the account.
- [ ] Verification links become invalid after an email-address change.
- [ ] Unverified users cannot log in.
- [ ] Verified users can log in and log out.
- [ ] Password-reset email and token expiry work.
- [ ] Resend responses do not disclose whether an account exists.

## Upload, analysis, and reports

- [ ] A normal Python file can be analyzed.
- [ ] A normal nested ZIP project can be analyzed.
- [ ] Traversal, symlink, duplicate-path, nested-ZIP, oversized, and suspicious-ratio archives are rejected.
- [ ] A project at the accepted member boundary completes within operational limits.
- [ ] Reports are generated and downloadable by their owner.
- [ ] Another user cannot access reports or results they do not own.
- [ ] Missing report files fail safely.

## Production security

- [ ] `APP_ENV=production` is set.
- [ ] `SECRET_KEY` is long, random, and stored outside source control.
- [ ] `DATABASE_AUTO_CREATE=0` is set.
- [ ] HTTPS is enabled at the trusted reverse proxy.
- [ ] Session and remember-me cookies are secure and HTTP-only.
- [ ] HSTS is enabled only after HTTPS is fully verified.
- [ ] CSP, frame denial, MIME protection, referrer policy, and permissions policy are present.
- [ ] Upload and proxy body-size limits agree.
- [ ] Writable database/upload/report paths are private and durable.

## Operations

- [ ] Database and persistent files are backed up together.
- [ ] SMTP failures are monitored.
- [ ] Application errors and worker restarts are monitored.
- [ ] Disk usage is monitored for uploads, reports, backups, and logs.
- [ ] Health and smoke tests run after deployment.
- [ ] Rollback criteria and the restore procedure are documented for the operator.

## Release procedure

1. Merge the reviewed completion branch into `release/v1.0.0-rc1`.
2. Wait for all release-branch CI jobs to pass.
3. Run the final smoke-test checklist in staging.
4. Create annotated tag `v1.0.0-rc1` at the approved commit.
5. Publish GitHub release notes from `CHANGELOG.md`.
6. Deploy the exact tagged artifact to the RC environment.
7. Record acceptance results and unresolved RC issues before promoting to `v1.0.0`.
