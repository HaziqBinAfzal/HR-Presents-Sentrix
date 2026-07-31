def generate_ai_summary(
    pylint_score,
    security_count,
    formatting_status,
    complexity_rows,
):
    """
    Generate AI summary and recommendations.
    """

    summary = []

    recommendations = []

    # -----------------------------------------
    # Code Quality Summary
    # -----------------------------------------

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

    # -----------------------------------------
    # Security Summary
    # -----------------------------------------

    if security_count == 0:

        summary.append(
            "No security vulnerabilities were detected by Bandit."
        )

    else:

        summary.append(
            f"{security_count} potential security issue(s) were detected."
        )

    # -----------------------------------------
    # Formatting Summary
    # -----------------------------------------

    if formatting_status == "Passed":

        summary.append(
            "The project follows Black formatting."
        )

    else:

        summary.append(
            "The project requires formatting with Black."
        )

    # -----------------------------------------
    # Complexity Summary
    # -----------------------------------------

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

    # -----------------------------------------
    # Recommendations
    # -----------------------------------------

    if pylint_score < 8:

        recommendations.append(
            "Improve code quality by resolving the reported Pylint issues."
        )

    if security_count > 0:

        recommendations.append(
            f"Resolve the {security_count} security issue(s) detected by Bandit."
        )

    if formatting_status != "Passed":

        recommendations.append(
            "Run Black to ensure consistent code formatting."
        )

    if complexity_rows:

        high_complexity = [

            item

            for item in complexity_rows

            if item["grade"] in (
                "D",
                "E",
                "F"
            )
        ]

        if high_complexity:

            recommendations.append(
                "Refactor functions with high cyclomatic complexity."
            )

    if not recommendations:

        recommendations.append(
            "Excellent work! No major improvements are currently recommended."
        )

    return (
        " ".join(summary),
        recommendations
    )
