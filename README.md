# Sentrix

**AI-powered code intelligence and security — presented by HR-Presents.**

Sentrix is a Flask-based SaaS platform for analyzing software projects, detecting defects and security vulnerabilities, measuring code quality, generating AI-assisted recommendations and fixes, and producing professional reports.

## Core capabilities

- Project upload and analysis history
- Syntax, lint, complexity, formatting and security analysis
- AI-assisted explanations, recommendations and remediation guidance
- Project health, security, maintainability and quality metrics
- Downloadable reporting workflows
- User registration, login, profiles and settings
- Dashboard statistics, project history and reviews
- Extensible analyzer and report-service architecture

## Technology stack

- Python and Flask
- Flask-SQLAlchemy and SQLAlchemy
- Flask-Login and Flask-WTF
- SQLite by default, configurable through `DATABASE_URL`
- OpenAI-compatible managed AI backend
- Bandit, Pylint, Flake8, Black and Radon
- Bootstrap, Chart.js and Font Awesome
- ReportLab for PDF generation

## Project structure

```text
Sentrix/
├── analyzer/               # Analysis engines and Flask routes
├── helpers/                # Upload, analysis, report and review services
├── static/                 # CSS, JavaScript and images
├── templates/              # Flask/Jinja user interface
├── uploads/                # Runtime project and report storage
├── app.py                  # Application factory and entry point
├── brand.py                # Central brand and official contact metadata
├── config.py               # Environment-driven configuration
├── database.py             # SQLAlchemy instance
├── extensions.py           # Flask extension instances
├── forms.py                # Validated web forms
├── models.py               # Database models
└── requirements.txt        # Python dependencies
```

## Quick start

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it using the command appropriate for your operating system.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the environment

Copy `.env.example` to `.env`, then set at minimum:

```env
SECRET_KEY=replace_with_a_long_random_secret
OPENAI_API_KEY=your_managed_backend_key
```

Sentrix deliberately uses a platform-managed AI backend. End users are not expected to provide their own API keys.

### 4. Start the application

```bash
python app.py
```

The default development address is `http://127.0.0.1:5000`.

## Configuration

| Variable | Purpose | Required |
|---|---|---:|
| `SECRET_KEY` | Session and CSRF signing | Yes |
| `DATABASE_URL` | SQLAlchemy database connection | No |
| `OPENAI_API_KEY` | Managed AI service credential | For AI features |
| `OPENAI_MODEL` | Selected AI model | No |
| `UPLOAD_FOLDER` | Runtime upload storage | No |
| `MAX_CONTENT_LENGTH` | Maximum upload size in bytes | No |
| `MAIL_USERNAME` | SMTP account | For email features |
| `MAIL_PASSWORD` | SMTP credential | For email features |
| `MAIL_DEFAULT_SENDER` | Sender identity | No |
| `SESSION_COOKIE_SECURE` | HTTPS-only session cookie | Production |

Never commit `.env`, production credentials, generated reports, uploaded projects, or database files.

## Database setup

The current application retains `db.create_all()` for compatibility. Production deployments should use Flask-Migrate/Alembic migrations for every schema change:

```bash
flask db upgrade
```

Database changes must be reviewed before deployment and backed up before destructive migrations.

## Security

Recommended production controls:

- Use a stable, randomly generated `SECRET_KEY`.
- Enable `SESSION_COOKIE_SECURE=1` behind HTTPS.
- Store all secrets in a managed secret store.
- Run uploads in isolated temporary directories.
- Validate extensions, MIME types, archive paths and extracted file sizes.
- Run analyzers with strict time, memory and process limits.
- Never execute uploaded project code.
- Restrict report and project access by authenticated owner.
- Keep Bandit, Flask, Werkzeug and other dependencies patched.

## Reports

Sentrix is being standardized around enterprise report exports containing project metadata, severity summaries, file and line references, root-cause analysis, recommendations, risk assessment, scores and prioritized action plans. Supported target formats are PDF, HTML, JSON and Markdown.

## Docker and deployment

For production deployment, run Sentrix behind a production WSGI server and reverse proxy. Do not use Flask's built-in development server. A production deployment should also provide:

- HTTPS termination
- Persistent database and report storage
- Managed secrets
- Background workers for long-running analysis
- Health checks and structured logging
- Database migrations during release
- Upload size and request time limits

## Troubleshooting

### Application fails with `SECRET_KEY is required`

Create `.env` from `.env.example` and add a stable random `SECRET_KEY`.

### AI analysis is unavailable

Confirm that the platform-level `OPENAI_API_KEY` and selected model are configured. Sentrix does not expose a BYOK workflow to end users.

### Reports or uploads cannot be written

Confirm that the runtime account has permission to create and write within the configured upload directory.

### Database schema errors

Back up the database and run the latest managed migrations. Avoid manually adding duplicate columns.

## Roadmap

- Complete Sentrix rebranding across all templates, reports and exports
- Fully dynamic dashboard, settings and project history
- Unified AI analysis result schema and score calculation
- Enterprise PDF, HTML, JSON and Markdown reports
- Integrated documentation center
- CI validation, security tests and deployment automation
- Multi-language analysis and scalable background processing

## Contributing

1. Create a branch from `main`.
2. Keep changes focused and backwards compatible.
3. Add or update tests.
4. Run formatting, linting, security and application checks.
5. Open a pull request describing the root cause, implementation and validation.

## Maintainers

- **Ruveeha Ashfaq** — [GitHub](https://github.com/ruveeha33) · [LinkedIn](https://www.linkedin.com/in/ruveeha-ashfaq-632b15378)
- **Haziq Afzal** — [GitHub](https://github.com/HaziqBinAfzal) · [LinkedIn](https://www.linkedin.com/in/haziq-afzal-010b6636a)

## Support

Email: **supportsentrix@gmail.com**

## License

No license file is currently included. Add an approved license before public distribution or third-party reuse.

---

© 2026 Sentrix. Presented by **HR-Presents**.
