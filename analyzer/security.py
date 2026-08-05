"""Backward-compatible Bandit wrapper backed by the Sentrix engine."""

import json

from analyzer.engine import run_bandit as _run_bandit


def run_bandit(path):
    result = _run_bandit(path)
    issues = [
        {
            "file": item["file"],
            "line": item["line"],
            "severity": item["severity"].upper(),
            "confidence": item["confidence"].upper(),
            "issue": item["message"],
            "cwe": item["cwe"],
            "owasp": item["owasp"],
            "suggestion": item["suggestion"],
        }
        for item in result["findings"]
    ]
    return {
        "count": len(issues),
        "issues": issues,
        "output": json.dumps(result, ensure_ascii=False, indent=2),
        "counts": result["counts"],
    }
