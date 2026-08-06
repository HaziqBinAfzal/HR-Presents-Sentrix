# Sentrix Security Guide

This guide covers implementation and operations. Vulnerability reporting is defined in the repository-level `SECURITY.md`.

## Threat model

Sentrix processes untrusted accounts, form input, uploaded archives, source code, filenames, analyzer output, external AI responses, database records, email links, and generated files. Risks include account takeover, insecure direct object reference, archive traversal, resource exhaustion, command injection, unsafe rendering, secret exposure, malicious report content, and dependency compromise.

## Authentication

Use strong password hashing through maintained framework primitives, rate-limit login and password-reset attempts, avoid account enumeration, expire verification/reset tokens, and invalidate tokens after use. Sensitive account changes should require recent authentication where appropriate.

## Authorization

Every project, analysis, report, review, history item, export, profile, and setting operation must enforce ownership or an explicit role. Use ownership-filtered queries instead of loading by ID and checking later. Return a non-revealing 404 or 403 consistently.

## Sessions and CSRF

Use a persistent high-entropy secret, HTTP-only cookies, secure cookies under HTTPS, an appropriate SameSite policy, limited lifetimes, and CSRF protection for state-changing browser requests. Never accept a session identifier from a URL.

## Upload security

- Enforce request and per-file size limits.
- Allow only required formats and inspect content rather than trusting extensions.
- Generate server-side storage names.
- Reject absolute paths, `..` traversal, symlink escape, device files, and unsafe archive members.
- Limit extracted file count, total expanded bytes, nesting, and processing time.
- Store uploads outside the public web root.
- Isolate analyzer processes where feasible.
- Remove temporary files reliably.

## Analyzer execution

Do not execute uploaded projects. Invoke tools with argument arrays rather than shell strings, enforce timeouts and memory/CPU limits, capture bounded output, and handle individual tool failures. A tool crash or timeout must not become a clean result.

## AI integrations

Send only the minimum permitted content, disclose provider use to operators, configure timeouts and cost limits, protect credentials, and treat responses as untrusted suggestions. Never allow model output to bypass authorization, execute commands, or modify files without review and tests.

## Reports and exports

Authorize the source record before generation and download. Escape untrusted content, prevent formula injection in spreadsheet-compatible exports, avoid predictable public URLs, set safe content types, and define retention and deletion behavior.

## Secrets

Keep `.env`, API keys, SMTP credentials, database passwords, certificates, and signing keys outside Git. Rotate exposed secrets and audit history. Development fallback secrets must not silently reach production.

## Dependencies and supply chain

Pin or constrain dependencies deliberately, review update notes, scan known vulnerabilities, use trusted package indexes, protect CI credentials, generate reproducible artifacts, and retain dependency/license records. Static analysis tools also process hostile input and must be patched.

## Headers and proxy

Deploy behind HTTPS and add suitable security headers, including content-type protection, frame restrictions, referrer policy, and a tested Content Security Policy. Trust proxy headers only from known infrastructure.

## Logging and privacy

Log security-relevant events with timestamps and request identifiers, but exclude passwords, tokens, cookies, credentials, private source content, and sensitive report bodies. Restrict log access and define retention.

## Incident response

Contain affected systems, preserve evidence, rotate credentials, invalidate sessions/tokens, identify affected data and users, patch and test, restore from trusted sources when needed, communicate responsibly, and perform a post-incident review.
