# Sentrix Deployment Guide

## Deployment principles

Deploy an immutable reviewed commit, keep secrets outside source control, terminate TLS, use a production WSGI server, isolate writable storage, run controlled migrations, and maintain tested rollback and restore procedures.

## Recommended Linux topology

```text
Nginx :443 -> Gunicorn 127.0.0.1:8000 -> Sentrix
                                      -> PostgreSQL or managed database
                                      -> private durable file storage
                                      -> SMTP and optional AI provider
```

## Production environment

Set at least `SECRET_KEY`, `DATABASE_URL`, mail credentials when email flows are enabled, and optional AI credentials. Protect the environment file with operating-system permissions. Do not place credentials in Nginx configuration, process command history, container images, or repository files.

## Gunicorn

Install and pin Gunicorn in the production dependency set before declaring the command supported. A typical factory command is:

```bash
gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 120 'app:create_app()'
```

Worker count and timeout must be load-tested. In-process analysis may require longer timeouts but increasing them is not a substitute for moving long-running work to background workers.

## systemd example

Create a dedicated unprivileged service account and adjust paths:

```ini
[Unit]
Description=Sentrix web application
After=network.target

[Service]
User=sentrix
Group=sentrix
WorkingDirectory=/opt/sentrix
EnvironmentFile=/etc/sentrix/sentrix.env
ExecStart=/opt/sentrix/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 120 'app:create_app()'
Restart=on-failure
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Validate this example in the target distribution before use.

## Nginx reverse proxy example

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

Trust forwarded headers only from the controlled proxy and configure Flask accordingly before relying on them for security decisions.

## SSL/HTTPS

Use a trusted certificate authority, automate renewal, redirect HTTP to HTTPS, monitor expiry, enable secure cookies, and consider HSTS after confirming every subdomain and dependency supports HTTPS. Test renewal and reload behavior.

## Database migrations

Take a backup, stop or drain writes when required, run the exact reviewed migration, verify schema and critical queries, then start the new application version. Never allow multiple instances to race migrations.

## Docker

A production container should use a supported Python base, create a non-root user, install pinned dependencies, copy only required files, avoid embedding secrets, expose the internal application port, run Gunicorn, and provide a health check. A `.dockerignore` should exclude `.git`, virtual environments, caches, local databases, uploads, reports, tests not needed at runtime, and secrets.

## Docker Compose

A verified Compose deployment should define the application, production database, health checks, named volumes, restart policy, environment references, and isolated networks. Do not expose the database publicly. Use Compose for a controlled single-host deployment, not as an automatic substitute for backup, monitoring, TLS, and orchestration.

RC1 does not claim container deployment is complete until those files are committed and tested.

## Rollout and rollback

Deploy to staging, run smoke tests, take backups, deploy the immutable release, run migrations once, verify health and user journeys, and monitor errors. Roll back the application only when the database remains backward-compatible; otherwise follow the tested migration rollback or restore plan.

## Production verification

Verify registration, login, logout, email verification, password reset, project upload, hostile archive rejection, analysis, results, history, reports, exports, profile, settings, authorization isolation, TLS, logging, monitoring, backups, restore, and restart behavior.
