import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from helpers.report_service import generate_html_report


class ReportContentEnrichmentTests(unittest.TestCase):
    def test_existing_structure_and_headings_are_preserved(self):
        project = SimpleNamespace(
            id=7,
            project_id="project-7",
            project_name="Example",
            original_filename="example.zip",
        )
        analysis = SimpleNamespace(
            id=11,
            language="Python",
            status="completed",
            created_at=None,
            analysis_duration=2.5,
            total_files=3,
            total_lines=120,
            functions_count=8,
            classes_count=2,
            comments_count=12,
            blank_lines=18,
            complexity="Moderate",
            security_count=1,
            issues_count=4,
            overall_score=78,
            pylint_score=8.4,
            ai_summary="Summary",
            recommendations="Use parameterized queries",
            syntax_output="No syntax errors",
            pylint_output="C0103 invalid-name",
            bandit_output="Severity: Medium\nConfidence: High\nSQL injection risk",
            radon_output="Average complexity: B",
            formatting_status="checked",
        )

        with tempfile.TemporaryDirectory() as directory, patch("helpers.report_service.os.path.join") as join:
            report_path = os.path.join(directory, "sentrix_analysis_11.html")
            join.side_effect = lambda *parts: report_path if parts[-1].endswith(".html") else os.path.join(directory, *parts[1:])
            generated = generate_html_report(project, analysis)
            with open(generated, encoding="utf-8") as report:
                html = report.read()

        expected_headings = [
            "Executive Summary",
            "Project Profile",
            "Prioritized Recommendations",
            "Syntax and Pylint Findings",
            "Security Findings",
            "Complexity Findings",
            "Appendix",
        ]
        positions = [html.index(heading) for heading in expected_headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Top 10 security controls", html)
        self.assertIn("Standards and compliance interpretation", html)
        self.assertIn("OWASP Top 10", html)
        self.assertIn("Dependency &amp; Supply Chain Security", html)


if __name__ == "__main__":
    unittest.main()
