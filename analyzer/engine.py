"""Structured multi-file Python analysis engine for Sentrix."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import tokenize
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", "__pycache__",
    "venv", ".venv", "env", ".env", "node_modules", "dist", "build",
    ".tox", ".nox", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "site-packages", "migrations", "vendor",
}

SEVERITY_ORDER = {"fatal": 0, "error": 1, "warning": 2, "refactor": 3, "convention": 4, "info": 5}
PYLINT_TYPES = {"fatal": "fatal", "error": "error", "warning": "warning", "refactor": "refactor", "convention": "convention", "info": "info"}
OWASP_BY_CWE = {
    "CWE-20": "A03:2021 Injection", "CWE-22": "A01:2021 Broken Access Control",
    "CWE-78": "A03:2021 Injection", "CWE-79": "A03:2021 Injection",
    "CWE-89": "A03:2021 Injection", "CWE-94": "A03:2021 Injection",
    "CWE-259": "A07:2021 Identification and Authentication Failures",
    "CWE-327": "A02:2021 Cryptographic Failures", "CWE-330": "A02:2021 Cryptographic Failures",
    "CWE-502": "A08:2021 Software and Data Integrity Failures",
    "CWE-611": "A05:2021 Security Misconfiguration",
}


@dataclass
class FileStats:
    path: str
    size_bytes: int
    lines: int
    blank_lines: int
    comment_lines: int
    code_lines: int
    functions: int
    classes: int


def _run(command: list[str], cwd: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(command, 127, "", str(exc))


def discover_python_files(root: str) -> tuple[list[Path], int]:
    root_path = Path(root).resolve()
    python_files: list[Path] = []
    total_files = 0
    for current_root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for name in files:
            if name.startswith("."):
                continue
            total_files += 1
            path = Path(current_root) / name
            if path.suffix.lower() == ".py":
                python_files.append(path)
    return sorted(python_files), total_files


def analyze_file_stats(path: Path, root: Path) -> tuple[FileStats, dict[str, Any] | None]:
    relative = str(path.relative_to(root))
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    blank = sum(1 for line in lines if not line.strip())
    comments = 0
    try:
        for token in tokenize.generate_tokens(iter(text.splitlines(True)).__next__):
            if token.type == tokenize.COMMENT:
                comments += 1
    except (tokenize.TokenError, IndentationError):
        comments = sum(1 for line in lines if line.lstrip().startswith("#"))

    functions = classes = 0
    syntax_error = None
    try:
        tree = ast.parse(text, filename=relative)
        functions = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
        classes = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    except SyntaxError as exc:
        line_text = lines[exc.lineno - 1] if exc.lineno and exc.lineno <= len(lines) else ""
        syntax_error = {
            "file": relative, "line": exc.lineno or 0, "column": exc.offset or 0,
            "message": exc.msg, "snippet": line_text.strip(),
            "suggestion": _syntax_suggestion(exc.msg), "severity": "error",
        }

    return FileStats(
        path=relative, size_bytes=len(raw), lines=len(lines), blank_lines=blank,
        comment_lines=comments, code_lines=max(0, len(lines) - blank - comments),
        functions=functions, classes=classes,
    ), syntax_error


def _syntax_suggestion(message: str) -> str:
    lower = message.lower()
    if "expected ':'" in lower:
        return "Add a colon at the end of the statement."
    if "unexpected indent" in lower or "unindent" in lower:
        return "Align this line with the surrounding indentation level."
    if "was never closed" in lower or "unterminated" in lower:
        return "Close the bracket, quote, or multiline string opened earlier."
    if "invalid syntax" in lower:
        return "Check the highlighted token and the previous line for a missing delimiter or operator."
    return "Review the highlighted line and the line immediately before it."


def run_pylint(project_root: str) -> dict[str, Any]:
    result = _run(["pylint", project_root, "--recursive=y", "--output-format=json", "--score=y"], timeout=180)
    issues: list[dict[str, Any]] = []
    try:
        payload = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        payload = []
    for item in payload:
        severity = PYLINT_TYPES.get(str(item.get("type", "info")).lower(), "info")
        issues.append({
            "tool": "pylint", "severity": severity,
            "file": item.get("path") or item.get("abspath") or "",
            "line": item.get("line", 0), "column": item.get("column", 0),
            "code": item.get("message-id", ""), "symbol": item.get("symbol", ""),
            "message": item.get("message", ""),
        })
    score = 10.0
    text_result = _run(["pylint", project_root, "--recursive=y", "--score=y", "--reports=n"], timeout=180)
    for line in (text_result.stdout + text_result.stderr).splitlines():
        if "rated at" in line:
            try:
                score = float(line.split("rated at", 1)[1].split("/10", 1)[0].strip())
            except ValueError:
                pass
    counts = Counter(issue["severity"] for issue in issues)
    issues.sort(key=lambda issue: (SEVERITY_ORDER.get(issue["severity"], 9), issue["file"], issue["line"]))
    return {"score": round(score, 2), "counts": dict(counts), "issues": issues, "top_issues": issues[:10], "available": result.returncode != 127}


def run_bandit(project_root: str) -> dict[str, Any]:
    result = _run(["bandit", "-r", project_root, "-f", "json", "-q"], timeout=180)
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    findings = []
    for item in payload.get("results", []):
        cwe_id = (item.get("issue_cwe") or {}).get("id")
        cwe = f"CWE-{cwe_id}" if cwe_id else None
        findings.append({
            "tool": "bandit", "severity": str(item.get("issue_severity", "LOW")).lower(),
            "confidence": str(item.get("issue_confidence", "LOW")).lower(),
            "file": item.get("filename", ""), "line": item.get("line_number", 0),
            "column": item.get("col_offset", 0), "test_id": item.get("test_id", ""),
            "message": item.get("issue_text", ""), "cwe": cwe,
            "owasp": OWASP_BY_CWE.get(cwe, "Review against OWASP Top 10"),
            "suggestion": item.get("more_info") or "Replace the risky construct with a validated, least-privilege alternative.",
        })
    counts = Counter(item["severity"] for item in findings)
    findings.sort(key=lambda item: ({"high": 0, "medium": 1, "low": 2}.get(item["severity"], 3), item["file"], item["line"]))
    return {"counts": {level: counts.get(level, 0) for level in ("high", "medium", "low")}, "findings": findings, "available": result.returncode != 127}


def run_radon(project_root: str) -> dict[str, Any]:
    cc_result = _run(["radon", "cc", project_root, "-j", "-s", "-a"], timeout=180)
    mi_result = _run(["radon", "mi", project_root, "-j", "-s"], timeout=180)
    hal_result = _run(["radon", "hal", project_root, "-j"], timeout=180)
    try:
        cc_payload = json.loads(cc_result.stdout or "{}")
    except json.JSONDecodeError:
        cc_payload = {}
    try:
        mi_payload = json.loads(mi_result.stdout or "{}")
    except json.JSONDecodeError:
        mi_payload = {}
    try:
        hal_payload = json.loads(hal_result.stdout or "{}")
    except json.JSONDecodeError:
        hal_payload = {}

    functions = []
    files = []
    for filename, blocks in cc_payload.items():
        file_complexities = []
        for block in blocks:
            row = {"file": filename, "name": block.get("name", "<module>"), "line": block.get("lineno", 0), "complexity": block.get("complexity", 0), "rank": block.get("rank", "A")}
            functions.append(row)
            file_complexities.append(row["complexity"])
        files.append({"file": filename, "average_complexity": round(sum(file_complexities) / len(file_complexities), 2) if file_complexities else 0, "max_complexity": max(file_complexities, default=0), "maintainability_index": (mi_payload.get(filename) or {}).get("mi", 0)})
    functions.sort(key=lambda row: row["complexity"], reverse=True)
    files.sort(key=lambda row: (row["max_complexity"], -row["maintainability_index"]), reverse=True)
    avg_cc = round(sum(row["complexity"] for row in functions) / len(functions), 2) if functions else 0
    avg_mi = round(sum(row["maintainability_index"] for row in files) / len(files), 2) if files else 100
    return {"average_cyclomatic_complexity": avg_cc, "average_maintainability_index": avg_mi, "halstead": hal_payload, "worst_functions": functions[:10], "worst_files": files[:10], "available": cc_result.returncode != 127}


def build_summary(stats: dict[str, Any], pylint: dict[str, Any], bandit: dict[str, Any], radon: dict[str, Any], syntax_errors: list[dict[str, Any]]) -> dict[str, Any]:
    security_penalty = bandit["counts"]["high"] * 12 + bandit["counts"]["medium"] * 5 + bandit["counts"]["low"] * 1.5
    syntax_penalty = min(25, len(syntax_errors) * 8)
    complexity_penalty = max(0, radon["average_cyclomatic_complexity"] - 5) * 2
    health = round(max(0, min(100, pylint["score"] * 10 - security_penalty - syntax_penalty - complexity_penalty)), 1)
    risks = []
    if bandit["counts"]["high"]:
        risks.append(f"{bandit['counts']['high']} high-severity security finding(s)")
    if syntax_errors:
        risks.append(f"{len(syntax_errors)} Python file(s) cannot be parsed")
    if pylint["counts"].get("error", 0) or pylint["counts"].get("fatal", 0):
        risks.append("Blocking Pylint errors are present")
    if radon["average_cyclomatic_complexity"] > 10:
        risks.append("Average cyclomatic complexity is high")
    prioritized = []
    prioritized.extend([f"Fix {item['file']}:{item['line']} — {item['message']}" for item in bandit["findings"][:5]])
    prioritized.extend([f"Correct syntax in {item['file']}:{item['line']} — {item['message']}" for item in syntax_errors[:3]])
    prioritized.extend([f"Resolve {item['code']} in {item['file']}:{item['line']} — {item['message']}" for item in pylint["top_issues"][:5]])
    return {
        "executive_summary": f"Sentrix analyzed {stats['python_files']} Python files and {stats['lines_of_code']} lines of code. The project health score is {health}/100.",
        "project_health_score": health,
        "biggest_risks": risks or ["No critical risks were detected by the available analyzers."],
        "security_summary": f"{bandit['counts']['high']} high, {bandit['counts']['medium']} medium, and {bandit['counts']['low']} low findings.",
        "code_quality_summary": f"Pylint score {pylint['score']}/10 with {sum(pylint['counts'].values())} findings.",
        "maintainability_summary": f"Average maintainability index {radon['average_maintainability_index']} and cyclomatic complexity {radon['average_cyclomatic_complexity']}.",
        "recommended_next_steps": ["Fix syntax and fatal errors first.", "Resolve high-severity security findings.", "Refactor the worst complexity hotspots.", "Address recurring Pylint warnings and conventions.", "Re-run Sentrix and compare trends."],
        "prioritized_fixes": prioritized[:10],
    }


def analyze_project(project_root: str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    python_files, total_files = discover_python_files(str(root))
    file_rows = []
    syntax_errors = []
    for path in python_files:
        stats, syntax_error = analyze_file_stats(path, root)
        file_rows.append(asdict(stats))
        if syntax_error:
            syntax_errors.append(syntax_error)
    total_size = sum(row["size_bytes"] for row in file_rows)
    stats = {
        "total_files": total_files, "python_files": len(python_files),
        "lines_of_code": sum(row["lines"] for row in file_rows),
        "code_lines": sum(row["code_lines"] for row in file_rows),
        "blank_lines": sum(row["blank_lines"] for row in file_rows),
        "comment_lines": sum(row["comment_lines"] for row in file_rows),
        "functions": sum(row["functions"] for row in file_rows),
        "classes": sum(row["classes"] for row in file_rows),
        "average_file_size": round(total_size / len(file_rows), 2) if file_rows else 0,
        "language_distribution": {"Python": len(python_files)}, "files": file_rows,
    }
    pylint = run_pylint(str(root))
    bandit = run_bandit(str(root))
    radon = run_radon(str(root))
    summary = build_summary(stats, pylint, bandit, radon, syntax_errors)
    return {"schema_version": 1, "stats": stats, "syntax": {"count": len(syntax_errors), "errors": syntax_errors}, "pylint": pylint, "bandit": bandit, "radon": radon, "summary": summary}
