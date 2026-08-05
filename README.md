# Sentrix

[![Release](https://img.shields.io/badge/release-v1.0.0--RC1-orange)](RELEASE_NOTES.md)
[![Python](https://img.shields.io/badge/python-3.11--3.13-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black)](https://flask.palletsprojects.com/)
[![CI](https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/actions/workflows/ci.yml/badge.svg)](https://github.com/HaziqBinAfzal/HR-Presents-Sentrix/actions/workflows/ci.yml)

Sentrix is a Flask-based Python project analysis platform by **HR-Presents**. It accepts Python projects, performs syntax, lint, complexity, formatting, security, and optional AI-assisted analysis, stores project and analysis history, and generates report artifacts.

> **Release status:** v1.0.0-RC1 remains a release candidate. Repository-level implementation and CI checks are being completed on `agent/sentrix-v1-production-completion`; environment-dependent SMTP, HTTPS, backup/restore, scale, and clean-machine deployment checks must still be performed before production promotion.

## Verified repository capabilities

- Registration, login, logout, password hashing, sessions, and user profiles
- Project upload and per-user project/analysis records
- Python syntax, Pylint, Bandit, Radon, formatting, and AI analysis modules
- Database-backed dashboard metrics and history queries
- Review model, forms, service references, and UI routes
- Dockerfile, Docker Compose, Gunicorn, Nginx, environment configuration, and documentation
- GitHub Actions validation for Python 3.11, 3.12, and 3.13 plus a production image build

## Production readiness matrix

| Area | Status | Evidence / remaining work |
|---|---|---|
| Authentication | Implemented | Registration, login/logout, password hashing and user-scoped records exist. |
| Email verification | Not implemented | SMTP is configured, but verification state, signed activation tokens, activation/resend routes, and templates are not yet present. |
| Forgot password | Partial | Forms/templates exist; the current route only displays a generic success message and does not send or consume reset tokens. |
| AI providers | Partial | OpenAI-oriented analysis exists. Gemini/Ollama switching, provider health checks, retries, and fallback behavior are not proven. |
| Report exports | Partial | Report storage/generation references exist. HTML, JSON, and PDF exports require route-level and artifact-level tests. |
| Dashboard metrics | Implemented, CI pending | Metrics query the database; CI must confirm the full application imports and routes render. |
| Reviews | Implemented, test pending | Model, forms, services, and route references exist; CRUD authorization tests are still required. |
| Notifications | Not verified | No complete notification delivery workflow has been established. |
| Settings | Partial | UI/routes exist; persistence and validation need automated tests. |
| Uploads | Partial | `.py` and `.zip` validation and a 100 MB ceiling exist; archive traversal, duplicate, cleanup, nested-folder, and stress tests remain. |
| Migrations | Not verified | Migration commands must be exercised against fresh and upgrade databases. |
| Docker | Implemented, CI pending | Dockerfile and Compose are present; CI builds the image, while clean-machine Compose startup still needs verification. |
| Production deployment | Configured, environment pending | Gunicorn and Nginx examples exist; HTTPS, DNS, proxy headers, static files, and production secrets require a real deployment test. |
| GitHub Actions | In progress | The previous RC run failed before creating jobs. The completion branch broadens CI to supported Python versions and agent branches. |
| Security headers | Not verified | CSP, HSTS, frame, referrer, and related response headers require implementation/audit. |
| CSRF | Framework enabled | Flask-WTF provides CSRF for FlaskForm submissions; every manual POST endpoint/template must still be audited. |
| Authorization | Partially verified | Key analysis/project lookups use `current_user.id`; complete cross-user route tests remain required. |
| Error handling | Partial | Upload and missing-record handling exists; dedicated 403/404/500 handlers and failure-path tests are still needed. |
| Performance | Not tested | Run 100 MB ZIP, 500/1,000-file, and concurrent-user tests outside CI. |
| Backup/restore | Documented, not tested | Restore a backup into a clean deployment and validate login, projects, analyses, and artifacts. |
| End-to-end flow | Not yet certified | Complete register → login → upload → analyze → recommendations → dashboard → report/export → history → logout testing. |

## Architecture

```mermaid
flowchart LR
    U[Browser] --> W[Flask application]
    W --> R[Main blueprint and routes]
    R --> S[Analysis, upload, review, report services]
    S --> A[Syntax / lint / complexity / security / AI analyzers]
    R --> D[(SQLAlchemy database)]
    S --> F[(Uploads and generated artifacts)]
    W --> M[SMTP mail service]
```

## Repository layout

```text
.
├── app.py
├── config.py
├── database.py
├── extensions.py
├── forms.py
├── models.py
├── analyzer/
├── helpers/
├── templates/
├── static/
├── migrations/
├── tests/
├── deploy/nginx/
├── Dockerfile
├── docker-compose.yml
├── gunicorn.conf.py
└── docs/
```

## Local installation

```bash
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open `http://127.0.0.1:5000`.

## Environment variables

| Variable | Required | Purpose |
|---|---:|---|
| `SECRET_KEY` | Production | Session and CSRF signing key |
| `DATABASE_URL` | Optional | SQLAlchemy URL; local SQLite is the default |
| `MAIL_SERVER` / `MAIL_PORT` | Email flows | SMTP endpoint |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | Email flows | SMTP credentials |
| `MAIL_DEFAULT_SENDER` | Email flows | Sender identity |
| `OPENAI_API_KEY` | AI features | Optional AI credential |
| `APP_ENV` | Recommended | `development`, `testing`, or `production` |
| `MAX_CONTENT_LENGTH` | Optional | Upload ceiling in bytes; default is 100 MB |

## Production deployment

Do not use Flask's development server in production. The intended topology is:

```text
Internet -> HTTPS Nginx reverse proxy -> Gunicorn -> Sentrix -> database/storage/SMTP
```

```bash
gunicorn --config gunicorn.conf.py 'app:create_app()'
```

Use production secrets, secure cookies, TLS, restricted storage permissions, tested migrations, monitoring, and verified backups. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Docker

```bash
docker compose build
docker compose up
```

The image build is covered by CI. Compose service startup, persistence, uploads, networking, and recovery must still be tested on a clean machine before the release is promoted.

## v1.0 promotion gate

Sentrix should be tagged `v1.0.0` only after all of the following are true:

1. CI passes on supported Python versions and the Docker image builds.
2. Password reset and email verification are implemented and tested, or explicitly removed from the advertised feature set.
3. Every user-facing route and POST form has functional, CSRF, and authorization coverage.
4. HTML, JSON, and PDF exports are generated and validated.
5. Fresh-install and upgrade migrations succeed.
6. Docker Compose and Gunicorn/Nginx deployments pass clean-machine smoke tests.
7. HTTPS and security headers are validated.
8. Backup and restore produce a working application.
9. The full end-to-end workflow succeeds.
10. A deliberate license is added, or the repository is clearly marked proprietary.

## Documentation

- [Installation](docs/INSTALLATION.md)
- [User guide](docs/USER_GUIDE.md)
- [Administrator guide](docs/ADMIN_GUIDE.md)
- [Developer guide](docs/DEVELOPER_GUIDE.md)
- [API reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Security](docs/SECURITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Release notes](RELEASE_NOTES.md)

## License and credits

Copyright © HR-Presents and contributors. No open-source license should be inferred until the repository owner adds the intended `LICENSE` text.

Sentrix is developed and maintained by HR-Presents.
