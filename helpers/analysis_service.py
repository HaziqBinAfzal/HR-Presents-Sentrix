import os
import time
import shutil
import tempfile
import ast

from database import db

from models import Analysis
from analyzer.syntax import check_syntax
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

    pylint_output = []

    complexity_rows = []

    total_lines = 0

    blank_lines = 0

    comments_count = 0

    functions_count = 0

    classes_count = 0

    # -----------------------------------------
    # Run project analyzers
    # -----------------------------------------

    syntax_errors = []

    for file in python_files:

    # -----------------------------------------
    # Count file statistics
    # -----------------------------------------

        try:

             with open(file, "r", encoding="utf-8") as source:

                 lines = source.readlines()

             total_lines += len(lines)

             for line in lines:

                 stripped = line.strip()

                 if not stripped:

                     blank_lines += 1

                 elif stripped.startswith("#"):

                     comments_count += 1

                 elif stripped.startswith("def "):

                     functions_count += 1

                 elif stripped.startswith("class "):

                     classes_count += 1

        except Exception:

            pass

    # -----------------------------------------
    # Black
    # -----------------------------------------
    
    syntax = check_syntax(file)

    if not syntax["valid"]:

        syntax_errors.append({

            "file": file,

            "line": syntax["line"],

            "message": syntax["message"]

        })

        

    with open(
        file,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        source = f.readlines()

    total_lines += len(source)

    for line in source:

        stripped = line.strip()

        if not stripped:

            blank_lines += 1

        elif stripped.startswith("#"):

            comments_count += 1

    try:

        tree = ast.parse(
            "".join(source)
        )

        for node in ast.walk(tree):

            if isinstance(
                node,
                ast.FunctionDef
            ):

                functions_count += 1

            elif isinstance(
                node,
                ast.ClassDef
            ):

                classes_count += 1

    except Exception:

        pass


    black = run_black(file)

    black = run_black(file)

    if black["status"] != "Passed":

        formatting_status = black["status"]

    # -----------------------------------------
    # Pylint
    # -----------------------------------------

    pylint_result = run_pylint(file)

    pylint_scores.append(
        pylint_result["score"]
    )

    pylint_issues.extend(
        pylint_result["issues"]
    )

    pylint_output.append(

        "\n".join(

            [

                f"{issue['file']}"

                f"\nLine {issue['line']}"

                f"\n{issue['type']}"

                f"\n{issue['symbol']}"

                f"\n{issue['message']}"

                for issue in pylint_result["issues"]

            ]

       )

    )

    # -----------------------------------------
    # Radon
    # -----------------------------------------

    complexity_rows.extend(
        run_radon(file)
    )
    bandit_result = run_bandit(
        extract_folder
    )

    # -----------------------------------------
    # Store detailed outputs
    # -----------------------------------------

    bandit_output = bandit_result["output"]

    bandit_findings = "\n\n".join(

        [

            f"{issue['severity']}"

            f"\n{issue['file']}"

            f"\nLine {issue['line']}"

            f"\nConfidence : {issue['confidence']}"

            f"\n{issue['issue']}"

            for issue in bandit_result["issues"]

        ]

    )
    
    radon_output = "\n\n".join(

        [

            f"{row['function']}"

            f"\nGrade : {row['grade']}"

            f"\nComplexity : {row['complexity']}"

            for row in complexity_rows

        ]

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

<<<<<<< HEAD
    if complexity_rows:
        max_complexity = max(
            row["complexity"] for row in complexity_rows
        )
=======
    highest_grade = "A"

    for row in complexity_rows:

        grade = row["grade"]

        if grade > highest_grade:

            highest_grade = grade

    if highest_grade in ("A", "B"):

        complexity_level = "Low"

    elif highest_grade == "C":

        complexity_level = "Medium"
>>>>>>> c93460b (Complete Milestone 1 analysis engine)

        if max_complexity <= 5:
            complexity_level = "Low"
        elif max_complexity <= 10:
            complexity_level = "Medium"
        else:
            complexity_level = "High"
    else:
<<<<<<< HEAD
        complexity_level = "Low"
=======

        complexity_level = "High"
>>>>>>> c93460b (Complete Milestone 1 analysis engine)
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

        syntax_output="\n".join(
            [
                f"{i['file']} : Line {i['line']} : {i['message']}"
                for i in syntax_errors
            ]
        ),


        total_files=len(python_files),

        total_lines=total_lines,

        analysis_duration=analysis_duration,

        ai_summary=ai_summary,

        recommendations="\n".join(recommendations),

        pylint_output="\n\n".join(pylint_output),

        bandit_output=bandit_findings,

        radon_output=radon_output,

        issues_count=len(pylint_issues),

        functions_count=functions_count,

        classes_count=classes_count,

        comments_count=comments_count,

        blank_lines=blank_lines,

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

