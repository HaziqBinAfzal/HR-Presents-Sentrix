# Sentrix Deployment Guide

## Deployment principles

Deploy an immutable reviewed commit, keep secrets outside source control, terminate TLS, run a production WSGI server, isolate writable storage, execute migrations exactly once, and maintain tested backup and rollback procedures.

## Required production settings

At minimum configure:

```env
APP_ENV=production
SECRET_KEY=<long-random-secret>
DATABASE_URL=<production-database-url>
DATABASE_AUTO_CREATE=0
SESSION_COOKIE_SECURE=1
REMEMBER_COOKIE_SECURE=1
HSTS_ENABLED=1
PREFERRED_URL_SCHEME=https
```

Email verification and password reset additionally require:

```env
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USE_SSL=0
MAIL_USERNAME=<smtp-user>
MAIL_PASSWORD=<smtp-password>
MAIL_DEFAULT_SENDER=<verified-sender>
SUPPORT_EMAIL=<support-address>
```

Optional controls include `MAX_CONTENT_LENGTH`, `SESSION_LIFETIME_MINUTES`, `EMAIL_VERIFICATION_MAX_AGE`, `PASSWORD_RESET_MAX_AGE`, `CONTENT_SECURITY_POLICY`, `PERMISSIONS_POLICY`, `REFERRER_POLICY`, and `HSTS_MAX_AGE`.

Never commit real secrets or place them in container images, shell history, or reverse-proxy configuration.

## Recommended Linux topology

```text
Nginx :443 -> Gunicorn 127.0.0.1:8000 -> Sentrix
                                      -> managed database or durable SQLite volume
                                      -> private durable upload/report storage
                                      -> SMTP
```

## Installation and startup

```bash
git checkout <reviewed-release-tag>
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run migrations before starting application workers:

```bash
APP_ENV=production DATABASE_AUTO_CREATE=0 flask --app app db upgrade
APP_ENV=production DATABASE_AUTO_CREATE=0 flask --app app db current
```

The expected RC1 revision is:

```text
20260806_0001 (head)
```

Start with Gunicorn:

```bash
gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 120 'app:create_app()'
```

Worker count and timeout must be validated under the target workload.

## Existing databases created before Alembic

Do not run the baseline upgrade directly against a populated database that already contains Sentrix tables.

1. Stop application writes.
2. Run the preflight utility:

```bash
python scripts/database_preflight.py
```

3. Confirm `Integrity check: ok`, no expected tables are missing, and preserve the reported backup.
4. Verify the schema matches revision `20260806_0001`.
5. Stamp without recreating tables:

```bash
APP_ENV=production DATABASE_AUTO_CREATE=0 flask --app app db stamp 20260806_0001
```

6. Confirm:

```bash
APP_ENV=production DATABASE_AUTO_CREATE=0 flask --app app db current
```

## Backup and restore

For SQLite, stop writes and create a consistent backup with the SQLite backup API or the included preflight utility. Back up the database together with persistent project, report, corrected-output, and diff folders.

Before a restore:

1. Stop application workers.
2. Preserve the failed database and writable folders for investigation.
3. Restore the database and matching file-storage snapshot.
4. Run `PRAGMA integrity_check` for SQLite or the database platform's equivalent.
5. Run `flask --app app db current`.
6. Start one application instance and perform smoke tests before scaling up.

Never treat an untested copy operation as a verified backup strategy.

## Nginx example

```nginx
server {
    listen 80;
    server_name sentrix.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sentrix.example.com;

    ssl_certificate /etc/letsencrypt/live/sentrix.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sentrix.example.com/privkey.pem;

    client_max_body_size 100m;

    location /static/ {
        alias /opt/sentrix/static/;
        access_log off;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Trust forwarded headers only from a controlled proxy.

## Docker

The CI workflow builds the production image on every relevant push and pull request. At runtime, provide secrets through the deployment platform, mount durable database/upload storage, and run migrations as a separate one-time deployment step before starting multiple containers.

Do not expose the database publicly. Do not allow multiple application replicas to race the migration command.

## Rollout

1. Confirm all GitHub Actions jobs are green.
2. Back up database and persistent files.
3. Deploy the reviewed image or commit to staging.
4. Run migrations once.
5. Verify registration, verification email, login, upload, hostile ZIP rejection, analysis, report download, authorization isolation, and logout.
6. Deploy to production.
7. Monitor application errors, SMTP failures, disk usage, database health, and request latency.

## Rollback

Rollback the application only when the database revision remains compatible. If a migration changed data or schema incompatibly, follow the reviewed downgrade procedure or restore the matched database and file-storage backup.
