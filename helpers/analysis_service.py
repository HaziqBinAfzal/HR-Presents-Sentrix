"""Sentrix project analysis orchestration."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time

from analyzer.engine import analyze_project
from analyzer.extractor import extract_project
from database import db
from helpers.report_service import generate_html_report
from models import Analysis


def _human_summary(payload: dict) -> str:
    summary = payload["summary"]
    sections = [
        summary["executive_summary"],
        "",
        f"Project Health Score: {summary['project_health_score']}/100",
        "",
        "Biggest Risks:",
        *[f"- {item}" for item in summary["biggest_risks"]],
        "",
        f"Security: {summary['security_summary']}",
        f"Code Quality: {summary['code_quality_summary']}",
        f"Maintainability: {summary['maintainability_summary']}",
    ]
    return "\n".join(sections)


def _recommendations(payload: dict) -> str:
    summary = payload["summary"]
    rows = ["Recommended Next Steps:"]
    rows.extend(f"{index}. {item}" for index, item in enumerate(summary["recommended_next_steps"], 1))
    if summary["prioritized_fixes"]:
        rows.extend(["", "Prioritized Fixes:"])
        rows.extend(f"- {item}" for item in summary["prioritized_fixes"])
    return "\n".join(rows)


def run_project_analysis(project, current_user):
    """Analyze every Python file in an uploaded project and persist structured results."""
    started_at = time.time()
    project_folder = os.path.abspath(project.project_path)
    upload_path = os.path.join(project_folder, "source", project.stored_filename)
    if not os.path.isfile(upload_path):
        raise FileNotFoundError("Uploaded project file not found.")

    extract_folder = tempfile.mkdtemp(prefix="sentrix_")
    try:
        extract_project(upload_path, extract_folder)
        payload = analyze_project(extract_folder)
        stats = payload["stats"]
        pylint = payload["pylint"]
        bandit = payload["bandit"]
        radon = payload["radon"]
        summary = payload["summary"]

        max_complexity = max(
            (item["complexity"] for item in radon["worst_functions"]),
            default=0,
        )
        complexity_level = "Low" if max_complexity <= 5 else "Medium" if max_complexity <= 10 else "High"
        formatting_status = "Needs attention" if pylint["counts"].get("convention", 0) else "Passed"

        analysis = Analysis(
            project_id=project.id,
            user_id=current_user.id,
            filename=project.original_filename,
            language="Python",
            overall_score=summary["project_health_score"],
            pylint_score=pylint["score"],
            security_count=sum(bandit["counts"].values()),
            formatting_status=formatting_status,
            complexity=complexity_level,
            analysis_duration=round(time.time() - started_at, 2),
            total_files=stats["python_files"],
            total_lines=stats["lines_of_code"],
            ai_summary=_human_summary(payload),
            recommendations=_recommendations(payload),
            pylint_output=json.dumps(pylint, ensure_ascii=False, indent=2),
            bandit_output=json.dumps(bandit, ensure_ascii=False, indent=2),
            radon_output=json.dumps(radon, ensure_ascii=False, indent=2),
            syntax_output=json.dumps(payload["syntax"], ensure_ascii=False, indent=2),
            issues_count=sum(pylint["counts"].values()),
            functions_count=stats["functions"],
            classes_count=stats["classes"],
            comments_count=stats["comment_lines"],
            blank_lines=stats["blank_lines"],
            status="Completed",
        )
        db.session.add(analysis)
        db.session.flush()
        analysis.report_path = generate_html_report(project, analysis, payload)
        db.session.commit()

        return {
            "analysis_id": analysis.id,
            "analysis": analysis,
            "quality": analysis.overall_score,
            "pylint_score": analysis.pylint_score,
            "issues": analysis.issues_count,
            "security": analysis.security_count,
            "complexity": analysis.complexity,
            "summary": analysis.ai_summary,
            "recommendations": summary["recommended_next_steps"],
            "engine": payload,
        }
    except Exception:
        db.session.rollback()
        raise
    finally:
        shutil.rmtree(extract_folder, ignore_errors=True)
