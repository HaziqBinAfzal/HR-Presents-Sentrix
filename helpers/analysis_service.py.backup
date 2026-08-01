import os
import time
import shutil
import tempfile

from database import db

from models import Analysis

from helpers.report_service import generate_html_report
from analyzer.extractor import extract_project
from analyzer.formatter import run_black
from analyzer.lint import run_pylint
from analyzer.complexity import run_radon
from analyzer.security import run_bandit
from analyzer.ai import generate_ai_summary


def run_project_analysis(
    project,
    current_user,
):
    """
    Runs the complete project analysis
    and saves the Analysis object.
    """

    start_time = time.time()

    # -----------------------------------------
    # Locate uploaded file
    # -----------------------------------------

    project_folder = os.path.abspath(
        project.project_path
    )

    source_folder = os.path.join(
        project_folder,
        "source"
    )

    upload_path = os.path.join(
        source_folder,
        project.stored_filename
    )

    if not os.path.isfile(upload_path):

        raise FileNotFoundError(
            "Uploaded project file not found."
        )

    # -----------------------------------------
    # Temporary extraction folder
    # -----------------------------------------

    extract_folder = tempfile.mkdtemp(
        prefix="codesentinel_"
    )

    python_files = extract_project(
        upload_path,
        extract_folder
    )

    formatting_status = "Passed"

    pylint_scores = []

    pylint_issues = []

    complexity_rows = []


# -----------------------------------------
    # Run project analyzers
    # -----------------------------------------

    for file in python_files:

        black = run_black(file)

        if black["status"] != "Passed":
            formatting_status = black["status"]

        pylint_result = run_pylint(file)

        pylint_scores.append(
            pylint_result["score"]
        )

        pylint_issues.extend(
            pylint_result["issues"]
        )

        complexity_rows.extend(
            run_radon(file)
        )

    bandit_result = run_bandit(
        extract_folder
    )

    # -----------------------------------------
    # Calculate average pylint score
    # -----------------------------------------

    average_score = 0

    if pylint_scores:

        average_score = round(
            sum(pylint_scores) /
            len(pylint_scores),
            2
        )

    # -----------------------------------------
    # AI Summary
    # -----------------------------------------

    ai_summary, recommendations = generate_ai_summary(
        average_score,
        bandit_result["count"],
        formatting_status,
        complexity_rows,
    )

    # -----------------------------------------
    # Complexity Level
    # -----------------------------------------

    if len(complexity_rows) <= 10:
        complexity_level = "Low"

    elif len(complexity_rows) <= 30:
        complexity_level = "Medium"

    else:
        complexity_level = "High"

    # -----------------------------------------
    # Overall Score
    # -----------------------------------------

    security_penalty = min(
        bandit_result["count"] * 2,
        30
    )

    overall_score = max(
        0,
        round(
            average_score * 10 -
            security_penalty,
            2
        )
    )

    analysis_duration = round(
        time.time() - start_time,
        2
    )

    # -----------------------------------------
    # Save Analysis
    # -----------------------------------------

    analysis = Analysis(

        project_id=project.id,

        user_id=current_user.id,

        filename=project.original_filename,

        language="Python",

        overall_score=overall_score,

        pylint_score=average_score,

        security_count=bandit_result["count"],

        formatting_status=formatting_status,

        complexity=complexity_level,

        total_files=len(python_files),

        total_lines=0,

        analysis_duration=analysis_duration,

        ai_summary=ai_summary,

        recommendations="\n".join(recommendations),

        status="Completed"
    )


    db.session.add(analysis)
    db.session.commit()

    report_path = generate_html_report(
        project,
        analysis
    )

    analysis.report_path = report_path
    db.session.commit()

    shutil.rmtree(extract_folder)

    return {
        "analysis_id": analysis.id,
        "analysis": analysis,
        "quality": overall_score,
        "pylint_score": average_score,
        "issues": len(pylint_issues),
        "security": bandit_result["count"],
        "complexity": complexity_level,
        "summary": ai_summary,
        "recommendations": recommendations,
    }

