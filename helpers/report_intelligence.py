"""Structured, evidence-aware context for Sentrix reports.

This module intentionally works with the existing Analysis model. It parses the
stored analyzer text into richer report objects without requiring a destructive
schema migration, keeping historical reports compatible.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    category: str
    title: str
    severity: str = "Info"
    confidence: str = "Not provided"
    file: str = "Not provided"
    line: str = "Not provided"
    rule_id: str = "Not provided"
    evidence: str = "No evidence snippet was recorded."
    impact: str = "Review the finding in the context of the affected code path."
    remediation: str = "Validate the finding and apply the least disruptive secure fix."
    standards: tuple[str, ...] = field(default_factory=tuple)


STANDARD_CATALOG = (
    "OWASP Top 10",
    "OWASP ASVS",
    "CWE Top 25",
    "NIST SSDF",
    "NIST CSF",
    "NIST SP 800-53",
    "CIS Controls",
    "CERT Secure Coding",
    "SANS Secure Coding",
    "ISO/IEC 27001",
    "ISO/IEC 27002",
    "SOC 2",
    "PCI DSS",
    "GDPR",
    "HIPAA",
)


def _blocks(value: object) -> list[list[str]]:
    text = str(value or "").strip()
    if not text:
        return []
    return [
        [line.strip() for line in block.splitlines() if line.strip()]
        for block in re.split(r"\n\s*\n", text)
        if block.strip()
    ]


def _line_number(lines: Iterable[str]) -> str:
    for line in lines:
        match = re.search(r"\bLine\s+([^:]+)", line, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Not provided"


def _confidence(lines: Iterable[str]) -> str:
    for line in lines:
        if line.lower().startswith("confidence:"):
            return line.split(":", 1)[1].strip().title()
    return "Not provided"


def _rule_id(lines: Iterable[str]) -> str:
    for line in lines:
        match = re.search(r"\b([A-Z]\d{3,4}|CWE-\d+|B\d{3}|[A-Z][A-Z0-9_-]{2,})\b", line)
        if match:
            return match.group(1)
    return "Not provided"


def _file_name(lines: list[str]) -> str:
    for line in lines:
        lowered = line.lower()
        if lowered.startswith(("line ", "confidence:", "severity:")):
            continue
        if "/" in line or "\\" in line or line.endswith(".py"):
            return line
    return "Not provided"


def _severity(lines: list[str], default: str = "Info") -> str:
    joined = " ".join(lines).lower()
    for level in ("critical", "high", "medium", "low"):
        if re.search(rf"\b{level}\b", joined):
            return level.title()
    return default


def _security_guidance(text: str) -> tuple[str, str, tuple[str, ...]]:
    lowered = text.lower()
    if any(term in lowered for term in ("password", "secret", "token", "api key", "credential")):
        return (
            "Exposed credentials can enable unauthorized access, lateral movement, or data disclosure.",
            "Remove the value from source control, rotate it, and load it from an approved secret manager or protected environment variable.",
            ("OWASP Top 10", "CWE Top 25", "NIST SSDF", "CIS Controls", "ISO/IEC 27001", "SOC 2"),
        )
    if any(term in lowered for term in ("subprocess", "shell=true", "command injection", "exec(", "eval(")):
        return (
            "Untrusted input reaching command or code execution can permit arbitrary execution in the application environment.",
            "Avoid shell interpretation, use argument arrays or allow-lists, and strictly validate any externally influenced value.",
            ("OWASP Top 10", "OWASP ASVS", "CWE Top 25", "CERT Secure Coding", "NIST SSDF"),
        )
    if any(term in lowered for term in ("sql", "injection", "query")):
        return (
            "Improper query construction may let an attacker alter database operations or access unauthorized records.",
            "Use parameterized queries or the ORM query API and keep user-controlled values out of query structure.",
            ("OWASP Top 10", "OWASP ASVS", "CWE Top 25", "PCI DSS", "NIST SSDF"),
        )
    if any(term in lowered for term in ("pickle", "deserialize", "yaml.load")):
        return (
            "Unsafe deserialization may construct attacker-controlled objects or trigger code execution.",
            "Use safe data formats and safe loaders; never deserialize untrusted native object streams.",
            ("OWASP Top 10", "CWE Top 25", "CERT Secure Coding", "NIST SSDF"),
        )
    return (
        "The finding may weaken application security if the affected path is reachable with attacker-controlled data.",
        "Confirm reachability, apply the scanner-specific fix, and add a regression test covering the vulnerable behavior.",
        ("OWASP Top 10", "NIST SSDF", "CIS Controls", "ISO/IEC 27001"),
    )


def parse_security_findings(value: object) -> list[Finding]:
    findings: list[Finding] = []
    for index, lines in enumerate(_blocks(value), start=1):
        evidence = lines[-1] if lines else "No evidence snippet was recorded."
        impact, remediation, standards = _security_guidance(" ".join(lines))
        findings.append(
            Finding(
                category="Security",
                title=evidence[:140] or f"Security finding {index}",
                severity=_severity(lines, "Medium"),
                confidence=_confidence(lines),
                file=_file_name(lines),
                line=_line_number(lines),
                rule_id=_rule_id(lines),
                evidence=evidence,
                impact=impact,
                remediation=remediation,
                standards=standards,
            )
        )
    return findings


def parse_quality_findings(value: object) -> list[Finding]:
    findings: list[Finding] = []
    for index, lines in enumerate(_blocks(value), start=1):
        evidence = lines[-1] if lines else "No evidence snippet was recorded."
        rule = _rule_id(lines)
        findings.append(
            Finding(
                category="Code Quality",
                title=evidence[:140] or f"Quality finding {index}",
                severity="Low",
                confidence="High",
                file=_file_name(lines),
                line=_line_number(lines),
                rule_id=rule,
                evidence=evidence,
                impact="Unresolved quality findings increase maintenance cost and can conceal defects in frequently changed code.",
                remediation="Apply the referenced lint rule, keep behavior unchanged, and add or update tests before refactoring broadly.",
                standards=("NIST SSDF", "CERT Secure Coding", "SANS Secure Coding", "ISO/IEC 27002"),
            )
        )
    return findings


def build_report_context(project, analysis) -> dict:
    security_findings = parse_security_findings(getattr(analysis, "bandit_output", None))
    quality_findings = parse_quality_findings(getattr(analysis, "pylint_output", None))
    all_findings = security_findings + quality_findings

    severity_counts = Counter(finding.severity for finding in all_findings)
    mapped_standards = Counter(
        standard for finding in all_findings for standard in finding.standards
    )
    standards = [
        {
            "name": standard,
            "status": "Mapped" if mapped_standards[standard] else "Insufficient evidence",
            "finding_count": mapped_standards[standard],
            "note": (
                "Mapped from one or more observed findings; this is guidance, not a compliance certification."
                if mapped_standards[standard]
                else "No finding-specific evidence was available to assess this framework in the current scan."
            ),
        }
        for standard in STANDARD_CATALOG
    ]

    total_findings = len(all_findings)
    high_impact = severity_counts["Critical"] + severity_counts["High"]
    if high_impact:
        executive_summary = (
            f"The analysis identified {total_findings} structured findings, including "
            f"{high_impact} high-impact item(s) requiring priority review."
        )
    elif total_findings:
        executive_summary = (
            f"The analysis identified {total_findings} structured findings. No critical or high-severity "
            "item was inferred from the stored scanner evidence, but validation and remediation remain necessary."
        )
    else:
        executive_summary = (
            "No structured finding evidence was stored for this analysis. The report therefore avoids asserting "
            "control coverage or a clean security posture."
        )

    return {
        "project_name": getattr(project, "project_name", "Not available"),
        "findings": all_findings,
        "security_findings": security_findings,
        "quality_findings": quality_findings,
        "severity_counts": dict(severity_counts),
        "standards": standards,
        "executive_summary": executive_summary,
        "developer_summary": (
            "Start with security findings and syntax failures, then resolve high-frequency lint rules and "
            "complexity hotspots. Verify each fix with focused tests and rerun the analysis before release."
        ),
        "methodology": (
            "Sentrix combines stored static-analysis evidence from Pylint, Bandit, syntax checks, Radon, "
            "formatting checks, and optional AI-generated guidance. Findings are normalized from the evidence "
            "available in the existing Analysis record; missing fields are explicitly marked as unavailable."
        ),
        "limitations": (
            "This report is a point-in-time static assessment. It does not prove exploitability, runtime safety, "
            "or regulatory compliance, and it does not replace manual review, dynamic testing, dependency "
            "inventory validation, threat modeling, or an independent audit."
        ),
    }
