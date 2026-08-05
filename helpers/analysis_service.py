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
from helpers.report_service import generate_html_report
from models import Analysis


def run_project_analysis(project, current_user):
    """Run the complete project analysis and save an Analysis record."""

    start_time = time.time()
    extract_folder = None

    try:
        project_folder = os.path.abspath(project.project_path)
        source_folder = os.path.join(project_folder, "source")
        upload_path = os.path.join(source_folder, project.stored_filename)

        if not os.path.isfile(upload_path):
            raise FileNotFoundError("Uploaded project file not found.")

        extract_folder = tempfile.mkdtemp(prefix="sentrix_")
        python_files = extract_project(upload_path, extract_folder)

        formatting_status = "Passed"
        pylint_scores = []
        pylint_issues = []
        pylint_output = []
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

            black_result = run_black(file_path)
            if black_result.get("status") != "Passed":
                formatting_status = black_result.get("status", "Failed")

            pylint_result = run_pylint(file_path)
            pylint_scores.append(float(pylint_result.get("score", 0.0) or 0.0))

            file_issues = pylint_result.get("issues", [])
            pylint_issues.extend(file_issues)

            for issue in file_issues:
                if isinstance(issue, dict):
                    pylint_output.append(
                        "\n".join(
                            [
                                str(issue.get("file", file_path)),
                                f"Line {issue.get('line', 'Unknown')}",
                                str(issue.get("type", "Unknown")),
                                str(issue.get("symbol", "Unknown")),
                                str(issue.get("message", "")),
                            ]
                        )
                    )
                else:
                    pylint_output.append(str(issue))

            radon_result = run_radon(file_path)
            if radon_result:
                complexity_rows.extend(radon_result)

        bandit_result = run_bandit(extract_folder)
        bandit_issues = bandit_result.get("issues", [])

        bandit_findings = []
        for issue in bandit_issues:
            if isinstance(issue, dict):
                bandit_findings.append(
                    "\n".join(
                        [
                            str(issue.get("severity", "Unknown")),
                            str(issue.get("file", "Unknown")),
                            f"Line {issue.get('line', 'Unknown')}",
                            f"Confidence: {issue.get('confidence', 'Unknown')}",
                            str(issue.get("issue", "")),
                        ]
                    )
                )
            else:
                bandit_findings.append(str(issue))

        radon_output = []
        for row in complexity_rows:
            if isinstance(row, dict):
                radon_output.append(
                    "\n".join(
                        [
                            str(row.get("function", row.get("name", "Unknown"))),
                            f"Grade: {row.get('grade', 'Unknown')}",
                            f"Complexity: {row.get('complexity', 0)}",
                        ]
                    )
                )
            else:
                radon_output.append(str(row))

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

        if max_complexity <= 5:
            complexity_level = "Low"
        elif max_complexity <= 10:
            complexity_level = "Medium"
        else:
            complexity_level = "High"

        ai_summary, recommendations = generate_ai_summary(
            average_score,
            int(bandit_result.get("count", 0) or 0),
            formatting_status,
            complexity_rows,
        )

        if recommendations is None:
            recommendations = []
        elif isinstance(recommendations, str):
            recommendations = [recommendations]

        security_count = int(bandit_result.get("count", len(bandit_issues)) or 0)
        security_penalty = min(security_count * 2, 30)
        overall_score = max(0, round((average_score * 10) - security_penalty, 2))
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
        }

    except Exception:
        db.session.rollback()
        raise

    finally:
        if extract_folder and os.path.isdir(extract_folder):
            shutil.rmtree(extract_folder, ignore_errors=True)
