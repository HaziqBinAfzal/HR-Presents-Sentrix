def generate_ai_summary(
    pylint_score,
    security_count,
    formatting_status,
    complexity_rows,
):
    """
    Generate a simple AI-style summary from analysis results.
    """

    summary = []

    if pylint_score >= 9:
        summary.append(
            "Excellent code quality was detected."
        )

    elif pylint_score >= 7:
        summary.append(
            "Overall code quality is good, with some improvements recommended."
        )

    else:
        summary.append(
            "The project has several code quality issues that should be addressed."
        )

    if security_count == 0:

        summary.append(
            "No security vulnerabilities were detected by Bandit."
        )

    else:

        summary.append(
            f"{security_count} potential security issue(s) were detected."
        )

    if formatting_status == "Passed":

        summary.append(
            "The project follows Black formatting."
        )

    else:

        summary.append(
            "The project requires formatting with Black."
        )

    if complexity_rows:

        highest = max(
            complexity_rows,
            key=lambda row: row["complexity"]
        )

        summary.append(
            f'The most complex function is "{highest["function"]}" '
            f'with complexity {highest["complexity"]} '
            f'and grade {highest["grade"]}.'
        )

    return " ".join(summary)
