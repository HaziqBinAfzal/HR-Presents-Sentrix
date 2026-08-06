"""Content-only report enrichment for Sentrix.

The helpers in this module add detailed technical and educational analysis inside
existing report sections. They do not define page order, navigation, headings,
layout, styling, charts, or branding.
"""

from __future__ import annotations

import re
from collections import Counter
from html import escape


def _text(value) -> str:
    return str(value or "").strip()


def _safe(value, fallback="Not available") -> str:
    value = _text(value)
    return escape(value or fallback)


def _contains(text: str, *terms: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _severity_counts(analysis) -> Counter:
    text = "\n".join(
        _text(getattr(analysis, field, None))
        for field in ("bandit_output", "pylint_output", "syntax_output", "radon_output")
    ).lower()
    counts = Counter()
    for level in ("critical", "high", "medium", "low"):
        counts[level.title()] = len(re.findall(rf"\b{level}\b", text))
    return counts


def _coverage_rows(analysis):
    security = _text(getattr(analysis, "bandit_output", None))
    quality = _text(getattr(analysis, "pylint_output", None))
    syntax = _text(getattr(analysis, "syntax_output", None))
    complexity = _text(getattr(analysis, "radon_output", None))
    combined = "\n".join((security, quality, syntax, complexity))

    checks = [
        ("Source code inspection", bool(security or quality or syntax), "Stored Bandit, Pylint, and syntax-check output is reviewed for unsafe constructs, coding defects, and structural failures."),
        ("Dangerous functions and imports", _contains(combined, "eval(", "exec(", "subprocess", "shell=true", "pickle", "yaml.load", "dangerous import"), "Potential execution, deserialization, shell, or import risks are identified from rule messages and source references retained by the scanners."),
        ("Secrets and credentials", _contains(combined, "password", "secret", "token", "api key", "credential", "private key", "aws", "azure", "google cloud", "jwt", "oauth", "ssh"), "Credential-like values are recognized from scanner evidence. Any confirmed exposure requires immediate revocation and rotation."),
        ("Injection and input handling", _contains(combined, "sql", "command injection", "xss", "ssrf", "xxe", "path traversal", "input validation", "output encoding"), "Findings are interpreted for untrusted-data flow into queries, commands, templates, network destinations, XML parsers, and filesystem paths."),
        ("Authentication and authorization", _contains(combined, "authentication", "authorization", "access control", "permission", "login", "session"), "Evidence is reviewed for missing identity checks, weak session handling, and unauthorized access paths."),
        ("Cryptography", _contains(combined, "md5", "sha1", "weak hash", "cipher", "random", "crypto", "encryption"), "Hashing, encryption, randomness, certificate, and key-management findings are interpreted against modern secure implementation expectations."),
        ("Error handling and logging", _contains(combined, "exception", "except", "logging", "debug", "traceback", "error handling"), "Broad exceptions, sensitive logs, debug exposure, and failure-handling quality are assessed from recorded static-analysis evidence."),
        ("Maintainability and complexity", bool(quality or complexity), "Pylint and Radon evidence supports interpretation of complexity, duplication indicators, code smells, readability, modularity, and technical debt."),
        ("Dependencies and supply chain", _contains(combined, "dependency", "package", "cve", "requirements", "deprecated library", "outdated"), "Only dependency evidence retained by the analysis is reported; absence of package inventory or CVE output is explicitly treated as insufficient evidence."),
        ("Configuration and deployment", _contains(combined, "dockerfile", "kubernetes", "github actions", "yaml", "json", "xml", "nginx", "apache", "flask", "django", "configuration", ".env"), "Configuration-related findings are interpreted across application, container, CI/CD, web-server, and framework configuration when evidence exists."),
    ]
    return checks


def executive_enrichment(project, analysis) -> str:
    counts = _severity_counts(analysis)
    security_count = int(getattr(analysis, "security_count", 0) or 0)
    issues_count = int(getattr(analysis, "issues_count", 0) or 0)
    overall_score = float(getattr(analysis, "overall_score", 0) or 0)
    return f"""
<h3>Technical interpretation</h3>
<p>Sentrix evaluates the retained static-analysis evidence for <strong>{_safe(getattr(project, 'project_name', None))}</strong> to identify security weaknesses, reliability concerns, maintainability risks, and secure-development gaps. The analysis combines syntax validation, Pylint quality rules, Bandit security rules, Radon complexity metrics, project metadata, and any generated recommendations available in the existing analysis record.</p>
<p>The current result records <strong>{security_count}</strong> security issue(s), <strong>{issues_count}</strong> quality issue(s), and an overall score of <strong>{overall_score:.1f}%</strong>. Recorded severity language includes {counts['Critical']} critical, {counts['High']} high, {counts['Medium']} medium, and {counts['Low']} low reference(s). These counts are contextual indicators rather than a replacement for exploitability validation.</p>
<p>For business stakeholders, unresolved findings can increase breach exposure, outage probability, remediation cost, delivery delay, compliance risk, and reputational damage. For engineers, the findings indicate where unsafe data flow, weak controls, excessive complexity, poor error handling, insecure configuration, or fragile design may reduce production reliability.</p>
<p>Severity should be interpreted using likely attack probability, exploit complexity, required privileges, user interaction, and potential confidentiality, integrity, and availability impact. Developers should confirm reachability and trust boundaries, correct the root cause, add regression tests, and rerun the analysis before release.</p>"""


def project_profile_enrichment(analysis) -> str:
    coverage = []
    for name, observed, detail in _coverage_rows(analysis):
        status = "Evidence observed" if observed else "No retained evidence"
        coverage.append(f"<tr><th>{escape(name)}</th><td><strong>{status}</strong> — {escape(detail)}</td></tr>")
    return f"""
<h3>Analysis scope and methodology</h3>
<p>The project profile defines the assessment boundary used to interpret all findings. File counts, lines of code, functions, classes, comments, language, duration, and complexity help reviewers understand scan scale, code concentration, and the likelihood that defects cluster in large or highly connected components.</p>
<table class="table">{''.join(coverage)}</table>
<p class="appendix-note">Sentrix reports only evidence available in the current analysis record. A missing finding does not prove that a control is implemented or that a vulnerability is absent. Runtime testing, threat modeling, manual review, dependency inventory validation, and environment inspection remain necessary for assurance.</p>"""


def recommendations_enrichment(analysis) -> str:
    security = _text(getattr(analysis, "bandit_output", None))
    quality = _text(getattr(analysis, "pylint_output", None))
    complexity = _text(getattr(analysis, "radon_output", None))
    combined = "\n".join((security, quality, complexity))
    guidance = [
        ("Root cause", "Trace each finding to the unsafe assumption, missing validation, weak control, obsolete API, excessive complexity, or insecure default that created it."),
        ("Risk and severity", "Prioritize issues that are remotely reachable, require little attacker effort, need no privileges, expose sensitive data, permit code execution, or threaten availability."),
        ("Secure implementation", "Apply parameterization, allow-list validation, contextual output encoding, least privilege, secure cryptography, safe parsing, explicit authorization, and defensive error handling as applicable."),
        ("Prevention", "Add focused unit and integration tests, security regression cases, code-review checks, CI scanning, dependency monitoring, secret scanning, and configuration validation."),
        ("Verification", "Rerun the relevant scanner, review the changed data flow, confirm the vulnerable path is no longer reachable, and retain evidence for audit or risk acceptance."),
    ]
    specialized = []
    if _contains(combined, "secret", "password", "token", "api key", "private key"):
        specialized.append("Immediately remove exposed secrets from source and history where practical, revoke and rotate them, then store replacements in an approved vault or protected environment variable.")
    if _contains(combined, "sql", "query", "injection"):
        specialized.append("Replace string-built queries with parameterized statements or ORM query APIs and validate authorization at the data-access boundary.")
    if _contains(combined, "subprocess", "shell=true", "exec(", "eval("):
        specialized.append("Eliminate shell interpretation and dynamic code execution for untrusted data; use fixed command argument arrays and strict allow-lists.")
    if _contains(combined, "pickle", "deserialize", "yaml.load"):
        specialized.append("Do not deserialize untrusted native objects; use safe loaders and simple data formats with schema validation.")
    if _contains(combined, "complexity", "too-many", "long method", "duplicate"):
        specialized.append("Refactor high-complexity units into cohesive functions or services while preserving behavior through tests and incremental changes.")
    special_html = "".join(f"<li>{escape(item)}</li>" for item in specialized) or "<li>Validate each recommendation against the actual code path and business context before implementation.</li>"
    rows = "".join(f"<tr><th>{escape(title)}</th><td>{escape(body)}</td></tr>" for title, body in guidance)
    return f"""
<h3>Senior-engineer remediation guidance</h3>
<table class="table">{rows}</table>
<h3>Finding-sensitive priorities</h3><ul class="recommendations">{special_html}</ul>
<p>Remediation improves security by removing exploitable behavior, reducing attack surface, increasing control consistency, and making future defects easier to detect. It also improves delivery speed and reliability by reducing technical debt and clarifying ownership of security-sensitive code.</p>"""


def quality_enrichment() -> str:
    return """
<h3>How to interpret code-quality analysis</h3>
<p>This section evaluates maintainability, readability, scalability, reusability, modularity, separation of concerns, coupling, cohesion, naming, organization, documentation, comments, duplicate logic, long methods, large classes, code smells, and refactoring opportunities. Pylint rules and syntax results identify concrete defects and conventions; Radon metrics provide complexity evidence.</p>
<p>Cyclomatic complexity estimates the number of independent execution paths and therefore the testing effort required to establish confidence. Highly complex code is more difficult to review, easier to break, and more likely to hide authorization, validation, exception-handling, or resource-lifecycle mistakes.</p>
<p>Clean Code, SOLID principles, and suitable design patterns should be applied to improve cohesion, reduce coupling, isolate responsibilities, and create testable interfaces. Changes should remain evidence-driven: refactor the smallest safe unit, preserve behavior, and verify CPU, memory, I/O, and concurrency effects with tests or profiling.</p>
<p>These metrics directly affect long-term maintenance, development speed, software reliability, production stability, and team collaboration. Clear, modular code lowers onboarding cost and makes security remediation safer and faster.</p>"""


def security_enrichment(analysis) -> str:
    rows = []
    for name, observed, detail in _coverage_rows(analysis):
        rows.append(f"<tr><th>{escape(name)}</th><td><strong>{'Relevant evidence' if observed else 'Not demonstrated'}</strong> — {escape(detail)}</td></tr>")
    controls = [
        ("Secure Authentication", "Protect identity verification, credentials, sessions, reset flows, and multi-factor controls."),
        ("Authorization & Access Control", "Enforce object- and function-level permission checks using least privilege and deny-by-default behavior."),
        ("Input Validation", "Validate type, length, format, range, and business rules before untrusted data reaches sensitive operations."),
        ("Output Encoding", "Apply context-specific encoding to prevent browser, template, command, and document injection."),
        ("Cryptography", "Use modern, reviewed algorithms and secure key generation, storage, rotation, and certificate validation."),
        ("Secrets Management", "Keep credentials out of source code and use managed vaults, protected variables, access controls, and rotation."),
        ("Logging & Monitoring", "Record security-relevant events without exposing secrets or personal data, and support alerting and investigation."),
        ("Secure Configuration Management", "Harden framework, container, server, CI/CD, and environment defaults and prevent debug exposure."),
        ("Dependency & Supply Chain Security", "Inventory direct and transitive packages, validate provenance, monitor CVEs, and upgrade safely."),
        ("Secure Error Handling", "Fail safely, avoid sensitive error disclosure, preserve auditability, and prevent broad exception suppression."),
    ]
    control_rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(detail)} Sentrix relates stored findings to this control when the scanner evidence is applicable.</td></tr>" for name, detail in controls)
    return f"""
<h3>Static security-analysis methodology</h3>
<p>Security analysis inspects source patterns and retained scanner messages for dangerous functions, hardcoded credentials, authentication and authorization weaknesses, missing input validation, unsafe output handling, SQL and command injection, XSS, SSRF, XXE, path traversal, insecure deserialization, unsafe file operations, race-condition indicators, memory-safety concerns where applicable, integer or buffer misuse indicators, weak exception handling, sensitive logging, cryptographic misuse, weak hashing, deprecated APIs, resource leaks, thread-safety concerns, and insecure object lifecycle behavior.</p>
<table class="table">{''.join(rows)}</table>
<h3>Top 10 security controls</h3><table class="table">{control_rows}</table>
<p>For every confirmed issue, developers should determine what the weakness means, how attacker-controlled data reaches it, which privileges and interactions are required, the likely confidentiality/integrity/availability impact, and the least disruptive secure implementation. Real exploitability depends on runtime context and must be validated.</p>"""


def complexity_enrichment() -> str:
    return """
<h3>Complexity, performance, and reliability interpretation</h3>
<p>Complexity findings identify code paths that may be difficult to reason about, test, secure, or change safely. Reviewers should look for deeply nested conditions, repeated branches, oversized functions, large classes, mixed responsibilities, duplicated logic, hidden state changes, and tight coupling.</p>
<p>High complexity can increase CPU work, memory retention, lock contention, thread-safety defects, resource leaks, and object-lifecycle errors when control flow becomes unclear. It also raises the probability that exceptional paths skip cleanup, authorization checks, validation, or logging.</p>
<p>Refactor incrementally into cohesive units with explicit inputs and outputs, bounded responsibilities, predictable lifecycle management, and focused tests. Measure performance bottlenecks before optimization and prefer clear algorithms and data structures over premature micro-optimization.</p>"""


def appendix_enrichment(analysis) -> str:
    standards = [
        ("OWASP Top 10", "Maps application-security findings to major web-application risk themes and secure coding practices."),
        ("OWASP ASVS", "Relates findings to verifiable application controls for architecture, authentication, sessions, access control, validation, cryptography, logging, and configuration."),
        ("CWE Top 25", "Associates common weakness classes with implementation-level defects where evidence supports the mapping."),
        ("MITRE ATT&CK / CAPEC", "Provides attack-technique and attack-pattern context when a finding supports a credible exploitation path."),
        ("NIST SSDF / CSF / SP 800-53", "Connects findings to secure-development, risk-management, protective-control, detection, and assurance practices."),
        ("CIS / SANS / CERT", "Relates secure configuration, coding, dependency, logging, and defensive-development practices to observed issues."),
        ("PCI DSS", "Applicable when payment-card data or payment systems are in scope; findings may affect secure development, access control, logging, and vulnerability management."),
        ("ISO/IEC 27001 and 27002", "Supports risk treatment and control guidance for secure development, access, cryptography, supplier security, operations, and incident readiness."),
        ("SOC 2", "Relates relevant findings to security, availability, confidentiality, processing integrity, and evidence expectations."),
        ("GDPR / HIPAA", "Applicable only when regulated personal or health data is processed; findings may affect confidentiality, integrity, access control, auditability, and breach risk."),
    ]
    standard_rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(detail)}</td></tr>" for name, detail in standards)
    return f"""
<h3>Standards and compliance interpretation</h3>
<table class="table">{standard_rows}</table>
<p>Compliance mapping is advisory and evidence-based. Sentrix does not certify compliance, determine legal applicability, or prove that organizational controls operate effectively. Each detected issue should be linked to the relevant requirement, documented with evidence, assigned an owner and priority, remediated or formally accepted, and retested.</p>
<h3>Risk assessment model</h3>
<p>Recommended prioritization considers attack probability, exploit complexity, privileges required, user interaction, confidentiality impact, integrity impact, availability impact, business disruption, financial exposure, regulatory consequences, and reputation damage. Critical and high-risk issues should normally be addressed before release; medium issues should be planned promptly; low issues should be corrected through normal engineering work unless context increases their impact.</p>
<h3>Educational guidance</h3>
<p>Each finding should be treated as a learning opportunity: understand why the weakness exists, how an attacker could exploit it, how secure coding prevents recurrence, and how the remediation changes the project’s risk profile. Real-world incidents commonly combine several individually moderate weaknesses, so reviewers should also consider attack chains and compensating controls.</p>"""
