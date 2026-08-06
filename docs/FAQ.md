# Sentrix FAQ

## What is Sentrix?

Sentrix is a Flask-based platform for uploading Python projects, running multiple analysis tools, reviewing findings, and generating reports.

## Is RC1 production-ready?

RC1 is a release candidate, not an unconditional production approval. Complete the checklist in `RELEASE_NOTES.md` in the target environment before deployment.

## Does Sentrix execute uploaded code?

It should analyze source without executing the uploaded project. Operators and developers must verify every analyzer and helper preserves that boundary.

## Are AI recommendations required?

No. AI-assisted recommendations are optional and depend on configured provider credentials and availability. Static analysis results should remain usable when AI is disabled or unavailable.

## Can I trust every finding or suggested fix?

No automated analyzer is perfect. Validate findings, review diffs, run tests, and apply human judgment before changing production code.

## What files should I avoid uploading?

Do not upload secrets, `.env` files, private keys, credential stores, production databases, customer data, or unrelated proprietary material.

## Which database should I use?

SQLite is convenient for local or small single-instance use. A managed production database is preferable for higher concurrency, reliability, backups, and horizontal scaling.

## Why did my session or reset link stop working?

The signing secret may have changed, the token may have expired or been used, or the account state may have changed. Production installations need a stable `SECRET_KEY`.

## Why is email not arriving?

Check SMTP credentials, TLS settings, provider restrictions, sender policy, spam filtering, and application logs. Gmail commonly requires an application password when two-factor authentication is enabled.

## Does the repository include verified Docker support?

Not yet unless the exact release commit contains tested Docker and Compose files. Documentation describes the required production shape but does not replace implementation and verification.

## Is there a stable public REST API?

RC1 is primarily a server-rendered application. Internal routes are not a guaranteed versioned public API. See `docs/API.md`.

## How are reports protected?

Reports should be stored privately and downloaded only after authorization. Operators must verify storage permissions, retention, backups, and tenant isolation.

## How do I report a vulnerability?

Follow the private disclosure process in the repository-level `SECURITY.md`. Do not publish exploit details in a public issue.

## How should I upgrade?

Read release notes, back up data, test in staging, install dependencies, run reviewed migrations, deploy an immutable commit, perform smoke tests, and keep a rollback plan.

## Why are backup files listed as a release blocker?

Committed `.backup` or editor-save files create ambiguity about which implementation is authoritative and may preserve obsolete or sensitive code. They should be removed only after confirming they are not required.

## Where should production secrets live?

Use a secret manager or protected environment configuration. Never commit secrets to Git, bake them into images, or place them in public logs.
