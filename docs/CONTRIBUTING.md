# Documentation Contribution Guide

The canonical project contribution policy is [`../CONTRIBUTING.md`](../CONTRIBUTING.md). This page adds documentation-specific guidance.

## Documentation standards

- Describe only behavior verified in the repository or clearly label future/target behavior.
- Keep commands copyable and state the operating system or shell when it matters.
- Never include real credentials, private data, internal hostnames, or user source code.
- Link related guides using repository-relative links.
- Explain security and rollback implications for operational procedures.
- Use exact release names and dates where ambiguity would be harmful.

## Required updates

Update documentation when a change affects setup, environment variables, routes, permissions, analysis behavior, report formats, storage, migrations, deployment, security controls, or supported platforms.

## Review checklist

- Links resolve from GitHub.
- Commands match committed files and dependencies.
- Feature claims are supported by code and tests.
- Examples use placeholders rather than secrets.
- Headings are navigable and terminology is consistent.
- Release-specific limitations remain visible.
