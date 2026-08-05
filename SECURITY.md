# Security Policy

## Supported versions

Until the first stable release, security fixes are applied to the active release-candidate branch and then carried into the next release. Old development snapshots are not supported.

## Reporting a vulnerability

Do not disclose exploitable details in a public issue, discussion, pull request, screenshot, or log. Contact the repository owner privately through the contact information on the GitHub profile and include:

- A clear description of the issue
- Affected component and version/commit
- Reproduction steps or a minimal proof of concept
- Potential impact
- Suggested mitigation, when available

Remove real credentials, private source code, personal data, and destructive payloads. Allow maintainers reasonable time to investigate and coordinate a fix before public disclosure.

## Response process

Maintainers should acknowledge receipt, reproduce and assess severity, define containment and remediation, prepare tests, coordinate disclosure, and publish upgrade guidance. Timelines depend on complexity and risk; no report is considered accepted until maintainers confirm it.

## Security baseline for operators

- Use a long, stable `SECRET_KEY` from a secret manager or protected environment.
- Run with debug mode disabled.
- Terminate HTTPS at a trusted reverse proxy and set secure cookie behavior.
- Restrict database, upload, report, and backup permissions.
- Use application-specific SMTP credentials and rotate them when exposed.
- Keep dependencies and the operating system patched.
- Back up data and test restoration.
- Enforce size, type, path, and archive extraction controls for uploaded projects.
- Keep generated artifacts outside publicly served paths unless access is authorized.
- Centralize logs without recording secrets, passwords, session tokens, or private source code.

## Scope boundaries

AI-provider behavior, SMTP providers, operating systems, databases, proxies, and third-party libraries have their own security responsibilities. Sentrix operators must configure and monitor those systems according to their vendors' guidance.
