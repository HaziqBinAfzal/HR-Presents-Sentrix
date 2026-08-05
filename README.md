# Sentrix

### Presented by HR-Presents

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Sentrix is an AI-assisted Python code intelligence and security review platform. It combines deterministic static analysis, security scanning, complexity measurement, formatting checks, project history, reviews, and downloadable reports in a single Flask application.

## Features

- Python project and source-file upload workflow
- Syntax, AST, lint, security, complexity, and maintainability analysis
- Integrated Sentrix AI Engine recommendations with no user API key required
- Pylint, Bandit, Radon, Black, `ast`, `tokenize`, and `pathlib` based inspection
- Dynamic dashboards, project history, reports, profile statistics, and reviews
- HTML, PDF, JSON, and Markdown report support
- Responsive Bootstrap interface for desktop, tablet, and mobile
- Authentication, password reset, user profiles, and activity tracking

## Architecture

Sentrix preserves a conventional Flask architecture:

```text
app.py                    Application factory and extension setup
config.py                 Environment-driven configuration
models.py                 SQLAlchemy data models
forms.py                  WTForms definitions
analyzer/                 Static-analysis modules and application routes
helpers/                  Upload, analysis, review, and report services
templates/                Jinja2 Bootstrap views
static/css/               Shared application styling
static/js/                Shared browser behavior
static/images/            Brand and interface assets
```

## Analysis Workflow

1. A signed-in developer uploads a Python file or supported project archive.
2. Sentrix safely validates and extracts the upload.
3. Source files are inspected with syntax parsing, AST traversal, token analysis, Pylint, Bandit, Radon, and Black.
4. Findings are normalized into quality, security, maintainability, complexity, best-practice, code-smell, performance, and architecture categories.
5. The Sentrix AI Engine produces plain-language explanations and prioritized recommendations from those deterministic findings.
6. Results are stored and exposed through the dashboard, history, profile, and downloadable reports.

## Technology Stack

- Python 3.11+
- Flask and Jinja2
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Mail
- Bootstrap 5
- Pylint
- Bandit
- Radon
- Black

## Requirements

- Python 3.11 or newer
- pip
- A virtual environment
- SQLite for local development or a supported production SQL database

## Installation

```bash
git clone https://github.com/HaziqBinAfzal/HR-Presents-Sentrix.git
cd HR-Presents-Sentrix
python -m venv venv
```

Activate the virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template and set secure values:

```bash
cp .env.example .env
```

Initialize the database by starting the application once, or use the configured migration workflow when migrations are present.

## Running

```bash
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

For production, set a strong `SECRET_KEY`, disable debug mode, configure a production database, and run behind a production WSGI server and reverse proxy.

## Report Generation

Sentrix reports are designed to include:

- Executive summary
- Overall quality score
- Security review
- Maintainability assessment
- Complexity analysis
- Best practices
- Code smells
- Performance suggestions
- Architecture suggestions
- AI recommendations

## Supported Languages

The current analysis engine is optimized for Python. The architecture allows additional language analyzers to be introduced without replacing the existing Flask application.

## Documentation

The in-application Documentation Center covers getting started, architecture, upload and analysis workflows, security scanning, the recommendation engine, database concepts, reports, troubleshooting, development, contribution, and roadmap guidance.

## Contribution Guide

1. Create a focused branch.
2. Preserve the existing Flask and Bootstrap architecture.
3. Add or update tests for behavioral changes.
4. Run syntax and application checks.
5. Open a pull request with a clear description of impact and validation.

## Roadmap

- Expanded analyzer test coverage
- Background analysis jobs for large projects
- Additional report export formats
- More granular project comparison views
- Additional language analyzers
- Deployment and observability documentation

## Contributors

Developed and maintained by **HR-Presents**.

## Support

Email: **supportsentrix@gmail.com**

## License

This project is licensed under the MIT License unless otherwise stated in the repository.
