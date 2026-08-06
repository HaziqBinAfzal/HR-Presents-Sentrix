"""Content-only enterprise enrichment for the existing Sentrix report.

This module deliberately returns HTML fragments that are inserted into the
already-finalized report sections. It does not change navigation, section order,
headings, branding, styling, charts, tables, or report flow.
"""

from html import escape


def _safe(value, fallback="Not available"):
    text = str(value or "").strip()
    return escape(text or fallback)


def build_report_enrichment(project, analysis):
    security_count = int(getattr(analysis, "security_count", 0) or 0)
    issues_count = int(getattr(analysis, "issues_count", 0) or 0)
    overall_score = float(getattr(analysis, "overall_score", 0) or 0)
    project_name = _safe(getattr(project, "project_name", None))

    executive = f"""
<h3>Technical interpretation</h3>
<p>Sentrix evaluates retained static-analysis evidence for <strong>{project_name}</strong> using syntax validation, Pylint quality rules, Bandit security rules, Radon complexity metrics, project metadata, and generated recommendations. The current record contains <strong>{security_count}</strong> security issue(s), <strong>{issues_count}</strong> quality issue(s), and an overall score of <strong>{overall_score:.1f}%</strong>.</p>
<p>Severity should be interpreted using attack probability, exploit complexity, privileges required, user interaction, and confidentiality, integrity, availability, financial, operational, and reputation impact. Scanner output is evidence for review, not proof of exploitability or compliance.</p>
"""

    profile = """
<h3>Analysis scope and methodology</h3>
<p>The assessment inspects available source files, imports, functions, classes, configuration references, exception paths, logging behavior, data-flow indicators, and analyzer output. It evaluates secure coding, dangerous functions, secrets, authentication, authorization, validation, encoding, injection, unsafe deserialization, file handling, cryptography, dependency references, complexity, duplication, maintainability, performance, resource lifecycle, and concurrency indicators where evidence exists.</p>
<p class="appendix-note">Missing evidence is treated as insufficient coverage, not as proof that a weakness is absent. Runtime testing, threat modeling, manual review, dependency inventory validation, and deployment inspection remain necessary.</p>
"""

    recommendations = """
<h3>Senior-engineer remediation guidance</h3>
<table class="table">
<tr><th>Root cause</th><td>Trace each issue to the unsafe assumption, missing control, insecure default, obsolete API, weak design boundary, or excessive complexity that created it.</td></tr>
<tr><th>Risk explanation</th><td>Prioritize remotely reachable issues, low-complexity exploits, no-privilege paths, sensitive-data exposure, code execution, authentication bypass, and availability impact.</td></tr>
<tr><th>Secure implementation</th><td>Use parameterized queries, allow-list validation, contextual output encoding, least privilege, explicit authorization, modern cryptography, safe parsers, secure secret storage, and defensive error handling as applicable.</td></tr>
<tr><th>Prevention</th><td>Add focused tests, security regression cases, code-review checks, CI scanning, dependency monitoring, secret scanning, configuration validation, and documented risk acceptance.</td></tr>
<tr><th>Verification</th><td>Rerun the relevant scanner, verify the changed trust boundary and data flow, and retain evidence that the vulnerable behavior is no longer reachable.</td></tr>
</table>
"""

    quality = """
<h3>Code-quality interpretation</h3>
<p>This section evaluates maintainability, readability, scalability, reusability, modularity, separation of concerns, coupling, cohesion, naming, organization, documentation, comments, duplicate code, long methods, large classes, code smells, technical debt, refactoring opportunities, performance, memory efficiency, CPU efficiency, design patterns, SOLID principles, and Clean Code practices.</p>
<p>Cyclomatic complexity estimates independent execution paths and therefore testing effort. High complexity increases maintenance cost, slows delivery, reduces reliability, hides security checks, and makes production failures harder to diagnose.</p>
"""

    security = """
<h3>Static security-analysis interpretation</h3>
<p>Security analysis reviews dangerous functions and imports, hardcoded credentials, API keys, cloud keys, tokens, JWT secrets, OAuth credentials, SSH material, database passwords, certificates, private keys, authentication and authorization logic, input validation, output encoding, SQL injection, command injection, XSS, SSRF, XXE, path traversal, insecure deserialization, unsafe file handling, race conditions, weak cryptography, weak hashing, sensitive logging, error disclosure, resource leaks, and thread-safety or memory-safety indicators where applicable.</p>
<h3>Top 10 security controls</h3>
<table class="table">
<tr><th>Secure Authentication</th><td>Protect credentials, sessions, reset flows, verification, and identity checks.</td></tr>
<tr><th>Authorization & Access Control</th><td>Enforce least privilege, deny by default, and object- and function-level permissions.</td></tr>
<tr><th>Input Validation</th><td>Validate type, length, format, range, and business rules before sensitive operations.</td></tr>
<tr><th>Output Encoding</th><td>Apply context-specific encoding for browser, template, command, and document output.</td></tr>
<tr><th>Cryptography</th><td>Use modern reviewed algorithms with secure key generation, storage, and rotation.</td></tr>
<tr><th>Secrets Management</th><td>Keep secrets out of source and use protected variables or managed vaults with rotation.</td></tr>
<tr><th>Logging & Monitoring</th><td>Record security events without exposing secrets or personal data.</td></tr>
<tr><th>Secure Configuration</th><td>Harden framework, container, server, CI/CD, and environment defaults.</td></tr>
<tr><th>Dependency Security</th><td>Inventory direct and transitive packages, monitor CVEs, validate provenance, and upgrade safely.</td></tr>
<tr><th>Secure Error Handling</th><td>Fail safely, avoid sensitive disclosure, preserve auditability, and avoid broad exception suppression.</td></tr>
</table>
"""

    complexity = """
<h3>Complexity, performance, and reliability interpretation</h3>
<p>Review deeply nested conditions, repeated branches, oversized functions, large classes, duplicated logic, hidden state changes, tight coupling, cleanup paths, locks, resources, and object lifecycle. Refactor incrementally into cohesive units with explicit inputs, outputs, ownership, and focused tests. Measure bottlenecks before optimization.</p>
"""

    appendix = """
<h3>Standards and compliance interpretation</h3>
<table class="table">
<tr><th>OWASP Top 10 / ASVS</th><td>Maps web-application risks and verifiable controls for architecture, authentication, sessions, access control, validation, cryptography, logging, and configuration.</td></tr>
<tr><th>CWE Top 25 / MITRE CAPEC / ATT&CK</th><td>Relates implementation weaknesses to attack patterns and techniques where evidence supports a credible exploitation path.</td></tr>
<tr><th>NIST SSDF / CSF / SP 800-53</th><td>Connects findings to secure development, risk management, protective controls, detection, verification, and evidence retention.</td></tr>
<tr><th>CIS / SANS / CERT</th><td>Provides secure configuration, coding, dependency, logging, and defensive-development guidance.</td></tr>
<tr><th>PCI DSS / ISO 27001 / ISO 27002 / SOC 2</th><td>Highlights relevant secure development, access control, vulnerability management, supplier, operations, confidentiality, availability, and audit expectations.</td></tr>
<tr><th>GDPR / HIPAA</th><td>Applies only when regulated personal or health data is in scope; relevant findings may affect confidentiality, integrity, access control, auditability, and breach risk.</td></tr>
</table>
<p class="appendix-note">Mappings are educational guidance, not certification, legal advice, or proof that a control is implemented.</p>
"""

    return {
        "executive": executive,
        "profile": profile,
        "recommendations": recommendations,
        "quality": quality,
        "security": security,
        "complexity": complexity,
        "appendix": appendix,
    }
