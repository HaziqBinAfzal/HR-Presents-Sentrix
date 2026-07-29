def generate_ai_summary(
    pylint_score,
    security_count,
    formatting_status,
    complexity_rows,
):
    """
    Generate an AI-style summary from the analysis results.
    """

    summary = []

    # --------------------------------------------------
    # Code Quality
    # --------------------------------------------------

    if pylint_score >= 9:

        summary.append(
            "Excellent code quality was detected with very few issues."
        )

    elif pylint_score >= 7:

        summary.append(
            "Overall code quality is good, although several improvements could make the project easier to maintain."
        )

    elif pylint_score >= 5:

        summary.append(
            "The project has moderate code quality issues that should be reviewed."
        )

    else:

        summary.append(
            "The project contains significant code quality problems and should be refactored."
        )

    # --------------------------------------------------
    # Security
    # --------------------------------------------------

    if security_count == 0:

        summary.append(
            "No security vulnerabilities were detected by Bandit."
        )

    elif security_count <= 5:

        summary.append(
            f"{security_count} potential security issue(s) were detected. Review them before deployment."
        )

    else:

        summary.append(
            f"{security_count} security issue(s) were detected. Immediate attention is recommended."
        )

    # --------------------------------------------------
    # Formatting
    # --------------------------------------------------

    if formatting_status == "Passed":

        summary.append(
            "The project follows Black formatting standards."
        )

    else:

        summary.append(
            "The project should be formatted with Black to improve consistency."
        )

    # --------------------------------------------------
    # Complexity
    # --------------------------------------------------

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

        if highest["grade"] in ("E", "F"):

            summary.append(
                "This function should be simplified to improve maintainability."
            )

    else:

        summary.append(
            "No significant function complexity was detected."
        )

    # --------------------------------------------------
    # Overall Recommendation
    # --------------------------------------------------

    if (
        pylint_score >= 8
        and security_count == 0
        and formatting_status == "Passed"
    ):

        summary.append(
            "Overall, the project is well structured and ready for further development."
        )

    else:

        summary.append(
            "Address the reported issues before using the project in production."
        )

    return " ".join(summary)
