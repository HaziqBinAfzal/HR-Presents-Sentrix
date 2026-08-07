"""Canonical scoring for Sentrix v1.

All numeric project-health values and labels must flow through this module.
The AI summary is intentionally non-scoring: generated prose must never change a
static-analysis score.
"""

from __future__ import annotations

import re
from collections import Counter


WEIGHTS = {
    "quality": 40.0,
    "security": 30.0,
    "maintainability": 15.0,
    "syntax": 10.0,
    "formatting": 5.0,
}


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, float(value)))


def security_score_from_issues(issues):
    """Return a severity-weighted 0-100 security score and normalized counts."""
    counts = Counter()
    for issue in issues or []:
        severity = str((issue or {}).get("severity", "low")).strip().lower()
        if severity not in {"high", "medium", "low"}:
            severity = "low"
        counts[severity] += 1

    penalty = counts["high"] * 25 + counts["medium"] * 10 + counts["low"] * 3
    return round(_clamp(100 - penalty), 1), {
        "high": counts["high"],
        "medium": counts["medium"],
        "low": counts["low"],
    }


def maintainability_score_from_complexities(complexities):
    """Translate measured cyclomatic complexity into a stable 0-100 score."""
    values = [max(0.0, float(value)) for value in complexities or []]
    if not values:
        return 100.0

    average = sum(values) / len(values)
    maximum = max(values)

    # A/B-range code keeps a high score. Increasing complexity degrades the
    # score smoothly; it never depends on file count or a hardcoded default.
    avg_penalty = max(0.0, average - 5.0) * 4.0
    max_penalty = max(0.0, maximum - 10.0) * 3.0
    return round(_clamp(100.0 - avg_penalty - max_penalty), 1)


def syntax_score_from_errors(error_count):
    return round(_clamp(100.0 - max(0, int(error_count or 0)) * 20.0), 1)


def formatting_score_from_status(status):
    normalized = str(status or "").strip().lower()
    if normalized == "disabled":
        return None
    if normalized == "passed":
        return 100.0
    if normalized in {"needs formatting", "needs attention"}:
        return 70.0
    if normalized:
        return 40.0
    return None


def final_rating(overall_score):
    score = float(overall_score or 0)
    if score >= 90:
        return "A+"
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def health_label(overall_score):
    score = float(overall_score or 0)
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 55:
        return "Needs Attention"
    return "High Risk"


def risk_level(severity_counts):
    counts = severity_counts or {}
    high = int(counts.get("high", 0) or 0)
    medium = int(counts.get("medium", 0) or 0)
    low = int(counts.get("low", 0) or 0)
    if high:
        return "High"
    if medium:
        return "Medium"
    if low:
        return "Low"
    return "None"


def calculate_scorecard(
    *,
    pylint_score=None,
    bandit_issues=None,
    complexities=None,
    syntax_error_count=0,
    formatting_status=None,
    enabled=None,
):
    """Calculate the one canonical Sentrix scorecard from completed analyzers."""
    enabled = enabled or {}
    components = {}

    if enabled.get("pylint", pylint_score is not None) and pylint_score is not None:
        components["quality"] = round(_clamp(float(pylint_score) * 10.0), 1)

    security_score, severity_counts = security_score_from_issues(bandit_issues)
    if enabled.get("bandit", True):
        components["security"] = security_score

    if enabled.get("radon", True):
        components["maintainability"] = maintainability_score_from_complexities(complexities)

    if enabled.get("syntax", True):
        components["syntax"] = syntax_score_from_errors(syntax_error_count)

    format_score = formatting_score_from_status(formatting_status)
    if enabled.get("black", format_score is not None) and format_score is not None:
        components["formatting"] = format_score

    total_weight = sum(WEIGHTS[name] for name in components)
    if not total_weight:
        raise ValueError("No completed analyzers were available for scoring.")

    overall = sum(components[name] * WEIGHTS[name] for name in components) / total_weight
    overall = round(_clamp(overall), 1)

    return {
        "overall_score": overall,
        "quality_score": components.get("quality"),
        "security_score": components.get("security"),
        "maintainability_score": components.get("maintainability"),
        "syntax_score": components.get("syntax"),
        "formatting_score": components.get("formatting"),
        "severity_counts": severity_counts,
        "security_findings": sum(severity_counts.values()),
        "risk_level": risk_level(severity_counts),
        "health_label": health_label(overall),
        "final_rating": final_rating(overall),
        "components": components,
    }


def _bandit_issues_from_output(output, fallback_count=0):
    """Recover severity evidence from persisted human-readable Bandit output."""
    issues = []
    text = str(output or "").strip()
    if text:
        for block in re.split(r"\n\s*\n", text):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            severity = lines[0].lower()
            if severity in {"high", "medium", "low"}:
                issues.append({"severity": severity})

    # Legacy records may only contain the count. Preserve their historical
    # count conservatively as low-severity evidence instead of inventing high
    # severity or silently returning a perfect security score.
    missing = max(0, int(fallback_count or 0) - len(issues))
    issues.extend({"severity": "low"} for _ in range(missing))
    return issues


def _complexities_from_output(output, level=None):
    values = []
    for match in re.finditer(r"Complexity\s*:\s*([0-9]+(?:\.[0-9]+)?)", str(output or ""), re.I):
        values.append(float(match.group(1)))
    if values:
        return values

    # Older records did not retain individual values. Map the stored level to
    # a representative boundary only for historical display compatibility.
    normalized = str(level or "").strip().lower()
    if normalized == "high":
        return [11.0]
    if normalized == "medium":
        return [8.0]
    if normalized == "low":
        return [5.0]
    return []


def scorecard_from_analysis(analysis):
    """Build display scores from one persisted Analysis record."""
    pylint_score = getattr(analysis, "pylint_score", None)
    pylint_output = str(getattr(analysis, "pylint_output", "") or "")
    issues_count = int(getattr(analysis, "issues_count", 0) or 0)

    # A zero score with zero findings and no Pylint output is the legacy
    # disabled/error shape. Do not present it as a real 0/10 result.
    pylint_available = not (
        float(pylint_score or 0) == 0.0 and issues_count == 0 and not pylint_output.strip()
    )

    bandit_issues = _bandit_issues_from_output(
        getattr(analysis, "bandit_output", ""),
        getattr(analysis, "security_count", 0),
    )
    complexities = _complexities_from_output(
        getattr(analysis, "radon_output", ""),
        getattr(analysis, "complexity", None),
    )
    syntax_output = str(getattr(analysis, "syntax_output", "") or "").strip()
    syntax_errors = len([line for line in syntax_output.splitlines() if line.strip()])

    scorecard = calculate_scorecard(
        pylint_score=float(pylint_score) if pylint_available else None,
        bandit_issues=bandit_issues,
        complexities=complexities,
        syntax_error_count=syntax_errors,
        formatting_status=getattr(analysis, "formatting_status", None),
        enabled={
            "pylint": pylint_available,
            "bandit": True,
            "radon": str(getattr(analysis, "complexity", "")).lower() != "disabled",
            "syntax": True,
            "black": str(getattr(analysis, "formatting_status", "")).lower() != "disabled",
        },
    )

    # overall_score is the persisted canonical result for newly generated
    # analyses. Keeping it here makes every surface exactly match the saved
    # scan while secondary scores and labels remain centrally derived.
    persisted_overall = getattr(analysis, "overall_score", None)
    if persisted_overall is not None:
        scorecard["overall_score"] = round(_clamp(float(persisted_overall)), 1)
        scorecard["health_label"] = health_label(scorecard["overall_score"])
        scorecard["final_rating"] = final_rating(scorecard["overall_score"])

    return scorecard
