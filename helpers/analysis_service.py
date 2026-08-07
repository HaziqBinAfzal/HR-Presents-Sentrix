import ast
import os
import shutil
import tempfile
import time

from analyzer.ai import generate_ai_summary
from analyzer.complexity import run_radon
from analyzer.extractor import extract_project
from analyzer.formatter import run_black
from analyzer.lint import run_pylint
from analyzer.security import run_bandit
from analyzer.syntax import check_syntax
from database import db
from helpers.branded_report_service import generate_html_report
from models import Analysis
from settings_models import UserSettings


def _format_pylint_issue(issue, file_path):
    if isinstance(issue, dict):
        return "\n".join(
            [
                str(issue.get("file", file_path)),
                f"Line {issue.get('line', 'Unknown')}",
                str(issue.get("type", "Unknown")),
                str(issue.get("symbol", "Unknown")),
                str(issue.get("message", "")),
            ]
        )
    return str(issue)


def _format_bandit_issue(issue):
    if isinstance(issue, dict):
        return "\n".join(
            [
                str(issue.get("severity", "Unknown")),
                str(issue.get("file", "Unknown")),
                f"Line {issue.get('line', 'Unknown')}",
                f"Confidence: {issue.get('confidence', 'Unknown')}",
                str(issue.get("issue", "")),
            ]
        )
    return str(issue)


def _format_radon_row(row):
    if isinstance(row, dict):
        return "\n".join(
            [
                str(row.get("function", row.get("name", "Unknown"))),
                f"Grade: {row.get('grade', 'Unknown')}",
                f"Complexity: {row.get('complexity', 0)}",
            ]
        )
    return str(row)


def run_project_analysis(project, current_user):
    """Run a Sentrix analysis using the current user's saved preferences."""

    start_time = time.time()
    extract_folder = None
    preferences = UserSettings.for_user(current_user.id)

    try:
        project_folder = os.path.abspath(project.project_path)
        source_folder = os.path.join(project_folder, "source")
        upload_path = os.path.join(source_folder, project.stored_filename)

        if not os.path.isfile(upload_path):
            raise FileNotFoundError("Uploaded project file not found.")

        extract_folder = tempfile.mkdtemp(prefix="sentrix_")
        python_files = extract_project(upload_path, extract_folder)

        if not python_files:
            raise ValueError("No Python files were found in the uploaded project.")

        formatting_status = "Disabled" if not preferences.enable_black else "Passed"
        pylint_scores = []
        pylint_issues = []
        pylint_output = []
        pylint_errors = []
        complexity_rows = []
        syntax_errors = []

        total_lines = 0
        blank_lines = 0
        comments_count = 0
        functions_count = 0
        classes_count = 0

        for file_path in python_files:
            try:
                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore",
                ) as source_file:
                    source_lines = source_file.readlines()

                total_lines += len(source_lines)

                for line in source_lines:
                    stripped = line.strip()
                    if not stripped:
                        blank_lines += 1
                    elif stripped.startswith("#"):
                        comments_count += 1

                try:
                    tree = ast.parse("".join(source_lines))
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            functions_count += 1
                        elif isinstance(node, ast.ClassDef):
                            classes_count += 1
                except SyntaxError:
                    pass

            except OSError:
                pass

            syntax_result = check_syntax(file_path)
            if not syntax_result.get("valid", False):
                syntax_errors.append(
                    {
                        "file": file_path,
                        "line": syntax_result.get("line"),
                        "message": syntax_result.get("message", "Unknown syntax error"),
                    }
                )

            if preferences.enable_black:
                black_result = run_black(file_path)
                if black_result.get("error"):
                    raise RuntimeError(
                        f"Black analyzer failed for {os.path.basename(file_path)}: "
                        f"{black_result.get('error')}"
                    )
                if black_result.get("status") != "Passed":
                    formatting_status = black_result.get("status", "Failed")

            if preferences.enable_pylint:
                pylint_result = run_pylint(file_path)
                if pylint_result.get("error"):
                    pylint_errors.append(
                        f"{os.path.basename(file_path)}: {pylint_result.get('error')}"
                    )
                    continue

                score_value = pylint_result.get("score")
                if score_value is None:
                    pylint_errors.append(
                        f"{os.path.basename(file_path)}: Pylint returned no score."
                    )
                    continue

                pylint_scores.append(float(score_value))
                file_issues = pylint_result.get("issues", [])
                pylint_issues.extend(file_issues)
                pylint_output.extend(
                    _format_pylint_issue(issue, file_path) for issue in file_issues
                )

            if preferences.enable_radon:
                radon_result = run_radon(file_path)
                if radon_result:
                    complexity_rows.extend(radon_result)

        if pylint_errors:
            raise RuntimeError(
                "Pylint analyzer failed instead of producing a valid score. "
                + " | ".join(pylint_errors[:5])
            )

        if preferences.enable_pylint and len(pylint_scores) != len(python_files):
            raise RuntimeError(
                "Pylint did not return a valid result for every Python file."
            )

        if preferences.enable_bandit:
            bandit_result = run_bandit(extract_folder)
            if bandit_result.get("error"):
                raise RuntimeError(
                    f"Bandit analyzer failed: {bandit_result.get('error')}"
                )
        else:
            bandit_result = {"count": 0, "issues": [], "output": ""}

        bandit_issues = bandit_result.get("issues", [])
        bandit_findings = [_format_bandit_issue(issue) for issue in bandit_issues]
        radon_output = [_format_radon_row(row) for row in complexity_rows]

        average_score = (
            round(sum(pylint_scores) / len(pylint_scores), 2)
            if pylint_scores
            else 0.0
        )

        numeric_complexities = [
            float(row.get("complexity", 0) or 0)
            for row in complexity_rows
            if isinstance(row, dict)
        ]
        max_complexity = max(numeric_complexities) if numeric_complexities else 0

        if not preferences.enable_radon:
            complexity_level = "Disabled"
        elif max_complexity <= 5:
            complexity_level = "Low"
        elif max_complexity <= 10:
            complexity_level = "Medium"
        else:
            complexity_level = "High"

        security_count = int(bandit_result.get("count", len(bandit_issues)) or 0)

        if preferences.enable_ai:
            ai_summary, recommendations = generate_ai_summary(
                average_score,
                security_count,
                formatting_status,
                complexity_rows,
            )
        else:
            ai_summary = "AI summary generation was disabled in your Sentrix settings."
            recommendations = []

        if recommendations is None:
            recommendations = []
        elif isinstance(recommendations, str):
            recommendations = [recommendations]

        quality_base = average_score * 10 if preferences.enable_pylint else 100.0
        security_penalty = min(security_count * 2, 30) if preferences.enable_bandit else 0
        syntax_penalty = min(len(syntax_errors) * 5, 30)
        overall_score = max(0, round(quality_base - security_penalty - syntax_penalty, 2))
        analysis_duration = round(time.time() - start_time, 2)

        analysis = Analysis(
            project_id=project.id,
            user_id=current_user.id,
            filename=project.original_filename,
            language="Python",
            overall_score=overall_score,
            pylint_score=average_score,
            security_count=security_count,
            formatting_status=formatting_status,
            complexity=complexity_level,
            syntax_output="\n".join(
                f"{item['file']} : Line {item['line']} : {item['message']}"
                for item in syntax_errors
            ),
            total_files=len(python_files),
            total_lines=total_lines,
            analysis_duration=analysis_duration,
            ai_summary=ai_summary,
            recommendations="\n".join(recommendations),
            pylint_output="\n\n".join(pylint_output),
            bandit_output="\n\n".join(bandit_findings),
            radon_output="\n\n".join(radon_output),
            issues_count=len(pylint_issues),
            functions_count=functions_count,
            classes_count=classes_count,
            comments_count=comments_count,
            blank_lines=blank_lines,
            status="Completed",
        )

        db.session.add(analysis)
        db.session.commit()

        if preferences.auto_generate_report:
            report_path = generate_html_report(project, analysis)
            analysis.report_path = report_path
            db.session.commit()

        return {
            "analysis_id": analysis.id,
            "analysis": analysis,
            "quality": overall_score,
            "pylint_score": average_score,
            "issues": len(pylint_issues),
            "security": security_count,
            "complexity": complexity_level,
            "summary": ai_summary,
            "recommendations": recommendations,
            "preferences": {
                "black": preferences.enable_black,
                "pylint": preferences.enable_pylint,
                "bandit": preferences.enable_bandit,
                "radon": preferences.enable_radon,
                "ai": preferences.enable_ai,
                "auto_generate_report": preferences.auto_generate_report,
            },
        }

    except Exception:
        db.session.rollback()
        raise

    finally:
        if extract_folder and os.path.isdir(extract_folder):
            shutil.rmtree(extract_folder, ignore_errors=True)
