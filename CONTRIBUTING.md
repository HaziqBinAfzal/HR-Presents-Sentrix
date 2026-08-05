# Contributing to Sentrix

Thank you for helping improve Sentrix. Contributions should protect user data, preserve existing workflows, and include enough evidence to review safely.

## Before contributing

- Search existing issues and pull requests.
- For large or behavior-changing work, open an issue describing the problem, proposed approach, risks, and migration impact.
- Never include secrets, real user data, generated uploads, databases, or private reports.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md).

## Development setup

1. Fork or clone the repository.
2. Create a virtual environment using a supported Python version.
3. Install `requirements.txt`.
4. Copy `.env.example` to `.env` and use development-only values.
5. Start the application and verify the baseline behavior before changing code.

See [docs/INSTALLATION.md](docs/INSTALLATION.md) and [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md).

## Branches and commits

Use focused branches such as `fix/upload-validation` or `feature/report-export`. Keep commits reviewable and use imperative messages, for example:

```text
fix: reject unsafe archive paths
```

Avoid mixing formatting-only changes with functional changes.

## Pull requests

A pull request should include:

- The user or operational problem being solved
- The implementation approach
- Security and data-migration impact
- Tests performed and results
- Screenshots for visible UI changes
- Rollback considerations
- Documentation updates

Do not claim production readiness without reproducible test or deployment evidence.

## Coding standards

- Prefer clear, small functions and explicit error handling.
- Keep route handlers thin; put reusable operations in services/helpers.
- Validate every user-controlled path, archive member, filename, form field, and identifier.
- Enforce ownership/authorization before returning or mutating resources.
- Do not log secrets, tokens, passwords, raw source code, or sensitive report content.
- Keep configuration environment-driven.
- Add type hints where they improve maintainability.

## Testing

At minimum, run tests covering the changed behavior. Changes to authentication, authorization, uploads, analysis, report generation, exports, settings, or migrations require negative-path tests as well as happy-path tests.

Recommended checks include unit tests, integration tests, linting, static analysis, dependency review, and a clean-install smoke test.

## Database changes

Use migrations for schema changes. Include upgrade and downgrade behavior where supported, explain data transformations, and test against a disposable copy of representative data. Never rely on `db.create_all()` as a substitute for controlled production migrations.

## Documentation

Update the README and relevant `/docs` pages whenever setup, configuration, behavior, routes, storage, security, or deployment changes.

## Security issues

Do not open a public issue for a suspected vulnerability. Follow [SECURITY.md](SECURITY.md).
