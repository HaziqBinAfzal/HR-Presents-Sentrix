"""Project-specific standards and security-control mapping for Sentrix reports."""

from __future__ import annotations

import re
from html import escape


RULE_PATTERNS = (
    re.compile(r"(?P<file>[^\s:]+\.py):(?P<line>\d+)(?::\d+)?:\s*(?P<message>.+)"),
    re.compile(r">>\s*Issue:\s*\[(?P<rule>[^]]+)\]\s*(?P<message>.+)"),
)


def _text(value) -> str:
    return str(value or "").strip()


def _safe(value, fallback="Not available") -> str:
    text = _text(value)
    return escape(text or fallback)


def _all_evidence(analysis) -> str:
    return "\n".join(
        _text(getattr(analysis, field, None))
        for field in ("bandit_output", "pylint_output", "syntax_output", "radon_output")
    )


def _evidence_snippets(analysis, terms, limit=3):
    terms = tuple(term.lower() for term in terms)
    lines = [line.strip() for line in _all_evidence(analysis).splitlines() if line.strip()]
    matches = []
    for index, line in enumerate(lines):
        lowered = line.lower()
        if not any(term in lowered for term in terms):
            continue
        context = line
        if index and ("issue:" in lowered or line.startswith(">>")):
            previous = lines[index - 1]
            if previous not in context:
                context = f"{previous} | {context}"
        if context not in matches:
            matches.append(context[:420])
        if len(matches) >= limit:
            break
    return matches


def _location(snippets):
    locations = []
    for snippet in snippets:
        for pattern in RULE_PATTERNS:
            match = pattern.search(snippet)
            if not match:
                continue
            file_name = match.groupdict().get("file")
            line = match.groupdict().get("line")
            rule = match.groupdict().get("rule")
            if file_name:
                locations.append(f"{file_name}:{line}" if line else file_name)
            elif rule:
                locations.append(f"scanner rule {rule}")
    return ", ".join(dict.fromkeys(locations)) or "See the matching scanner entry in the Security, Quality, or Complexity Findings section."


def _mapping_row(analysis, title, terms, relation, fix):
    snippets = _evidence_snippets(analysis, terms)
    if snippets:
        evidence = "<br>".join(f"<code>{_safe(item)}</code>" for item in snippets)
        status = "Related project evidence found"
        where = _location(snippets)
    else:
        evidence = "No matching retained scanner message was found in this analysis."
        status = "Not demonstrated by retained evidence"
        where = "No project-specific file or line can be asserted from the current analysis record."
    return (
        f"<tr><th>{_safe(title)}</th><td>"
        f"<strong>Status:</strong> {_safe(status)}<br>"
        f"<strong>How it relates to this project:</strong> {_safe(relation)}<br>"
        f"<strong>Related error/evidence:</strong> {evidence}<br>"
        f"<strong>Where:</strong> {_safe(where)}<br>"
        f"<strong>How to fix:</strong> {_safe(fix)}"
        f"</td></tr>"
    )


def render_security_controls(analysis) -> str:
    controls = (
        ("Secure Authentication", ("authentication", "login", "password", "session", "credential", "token"), "Authentication-related findings indicate risk around identity verification, credential handling, login state, session protection, password reset, or verification flows.", "Use proven authentication libraries, strong password hashing, protected session cookies, rotation after login, rate limiting, secure reset tokens, and multi-factor authentication where appropriate."),
        ("Authorization & Access Control", ("authorization", "access control", "permission", "privilege", "unauthorized", "idor"), "Authorization findings show where authenticated users may reach data or actions outside their assigned role, ownership, or tenant boundary.", "Enforce server-side object and function authorization on every protected request, use deny-by-default policies, verify resource ownership, and add negative authorization tests."),
        ("Input Validation", ("input", "validation", "sql", "subprocess", "shell=true", "path traversal", "ssrf", "xxe", "pickle", "yaml.load"), "These findings relate to untrusted data entering queries, commands, files, parsers, URLs, or deserialization operations without sufficiently strict validation.", "Validate type, length, format, range, scheme, destination, and business rules using allow-lists; parameterize SQL; avoid shell interpretation; use safe parsers and canonicalized paths."),
        ("Output Encoding", ("xss", "cross-site", "escape", "markup", "template", "html"), "Output-related findings indicate that untrusted data may be rendered into HTML, templates, documents, logs, or commands without context-appropriate encoding.", "Use automatic template escaping, context-specific HTML/attribute/JavaScript/URL encoding, avoid unsafe HTML insertion, and add browser-focused regression tests."),
        ("Cryptography", ("md5", "sha1", "weak hash", "cipher", "random", "crypto", "encryption", "certificate"), "Cryptographic findings relate to weak algorithms, predictable randomness, certificate validation, insecure key handling, or unsuitable password hashing.", "Replace deprecated primitives with reviewed modern algorithms, use CSPRNGs, validated TLS, Argon2/bcrypt/scrypt/PBKDF2 for passwords, and managed key rotation."),
        ("Secrets Management", ("secret", "api key", "password", "token", "private key", "aws", "azure", "google cloud", "jwt", "oauth", "ssh"), "Secret-related evidence identifies credentials or key material that may be embedded in source, configuration, logs, or generated artifacts.", "Remove the secret, revoke and rotate it immediately, purge exposed history where practical, store replacements in a managed vault or protected environment variable, and enable automated secret scanning."),
        ("Logging & Monitoring", ("logging", "log", "debug", "traceback", "audit", "monitor"), "Logging findings relate to missing security visibility or exposure of credentials, personal data, stack traces, tokens, or internal details in logs.", "Log authentication, authorization, administrative, and security events with correlation IDs; redact sensitive fields; restrict log access; define alerts and retention policies."),
        ("Secure Configuration", ("debug", "configuration", "config", ".env", "dockerfile", "kubernetes", "github actions", "nginx", "apache", "yaml", "xml"), "Configuration evidence concerns insecure defaults, debug exposure, overly broad permissions, unsafe deployment settings, or weak CI/CD and container hardening.", "Disable debug mode, separate secrets from configuration, pin and validate CI actions, run containers as non-root, restrict network and filesystem permissions, and validate production settings in CI."),
        ("Dependency Security", ("dependency", "package", "requirements", "cve", "outdated", "deprecated", "library"), "Dependency findings indicate vulnerable, obsolete, unmaintained, untrusted, or weakly pinned direct or transitive packages.", "Generate a complete inventory/SBOM, run vulnerability and license scans, pin supported versions, review transitive changes, upgrade in tested increments, and replace abandoned packages."),
        ("Secure Error Handling", ("exception", "except", "error", "traceback", "raise", "pass"), "Error-handling evidence identifies broad exception suppression, sensitive disclosure, inconsistent cleanup, or failures that may bypass security checks and audit trails.", "Catch specific exceptions, fail closed, return generic user-facing errors, preserve structured internal diagnostics, guarantee cleanup with context managers/finally, and test failure paths."),
    )
    rows = "".join(_mapping_row(analysis, *control) for control in controls)
    return f"<h3>Top 10 security controls</h3><table class=\"table\">{rows}</table>"


def render_standards_mapping(analysis) -> str:
    standards = (
        ("OWASP Top 10 / OWASP ASVS", ("sql", "injection", "xss", "authentication", "authorization", "access control", "crypto", "secret", "ssrf", "xxe", "configuration", "logging"), "The project evidence is mapped to OWASP web-risk categories and ASVS verification areas such as access control, validation, cryptography, logging, secure configuration, and software integrity.", "Fix the underlying weakness first, then verify the relevant ASVS control with tests and documented evidence. For injection use parameterization and validation; for access control enforce server-side checks; for secrets rotate and move them to a vault."),
        ("CWE Top 25 / MITRE CAPEC / ATT&CK", ("cwe", "sql", "command", "xss", "path traversal", "deserialize", "credential", "privilege", "execution"), "Implementation errors are related to CWE weakness classes, CAPEC attack patterns, and ATT&CK techniques only where the retained evidence supports a plausible attacker action.", "Remove the vulnerable data flow or unsafe primitive, add trust-boundary validation and least privilege, and write regression tests that reproduce the attacker-controlled condition without causing harm."),
        ("NIST SSDF / CSF / SP 800-53", ("security", "vulnerability", "authentication", "authorization", "configuration", "dependency", "logging", "secret", "test"), "Findings relate to secure-development practices, risk identification, protective controls, vulnerability remediation, configuration management, audit logging, and verification evidence.", "Track each finding through ownership, priority, remediation, review, testing, and closure evidence; harden the affected control and integrate repeatable scanning into CI/CD."),
        ("CIS / SANS / CERT Secure Coding", ("dangerous", "eval", "exec", "subprocess", "shell=true", "pickle", "yaml.load", "debug", "logging", "dependency"), "The project evidence is evaluated against defensive coding, secure configuration, controlled execution, safe parsing, dependency hygiene, and operational logging guidance.", "Replace dangerous APIs with safe alternatives, minimize privileges, validate all external input, harden production defaults, and enforce the secure pattern through code review and automated checks."),
        ("PCI DSS / ISO 27001 / ISO 27002 / SOC 2", ("password", "credential", "access", "logging", "encryption", "dependency", "vulnerability", "configuration", "availability"), "Where payment, customer, or business-sensitive systems are in scope, these findings may affect access control, secure development, cryptography, vulnerability management, supplier risk, logging, confidentiality, and availability expectations.", "Correct the technical issue, document scope and risk, retain test and scan evidence, review access and change controls, and obtain formal audit validation where compliance is required."),
        ("GDPR / HIPAA", ("personal", "patient", "health", "pii", "password", "access", "encryption", "logging", "data", "credential"), "This mapping applies only if the affected project path processes regulated personal or health data. Related weaknesses may increase unauthorized disclosure, alteration, loss, or insufficient auditability.", "Minimize regulated data, enforce role-based access, encrypt data in transit and at rest where appropriate, redact logs, retain audit trails, remediate the underlying vulnerability, and complete a privacy/security impact review."),
    )
    rows = "".join(_mapping_row(analysis, *standard) for standard in standards)
    return (
        "<h3>Standards and compliance interpretation</h3>"
        f"<table class=\"table\">{rows}</table>"
        "<p class=\"appendix-note\">Mappings are evidence-based educational guidance, not certification, legal advice, or proof that a control is implemented. Where no matching project evidence is retained, the report explicitly avoids claiming compliance or non-compliance.</p>"
    )
