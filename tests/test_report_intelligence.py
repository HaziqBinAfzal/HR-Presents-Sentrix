import unittest
from types import SimpleNamespace

from helpers.report_intelligence import (
    build_report_context,
    parse_quality_findings,
    parse_security_findings,
)
from helpers.report_sections import render_intelligence_sections


class ReportIntelligenceTests(unittest.TestCase):
    def test_security_finding_preserves_evidence_metadata(self):
        raw = "HIGH\n/app/main.py\nLine 42\nConfidence: HIGH\nB602 subprocess call with shell=True"
        finding = parse_security_findings(raw)[0]

        self.assertEqual(finding.severity, "High")
        self.assertEqual(finding.confidence, "High")
        self.assertEqual(finding.file, "/app/main.py")
        self.assertEqual(finding.line, "42")
        self.assertEqual(finding.rule_id, "B602")
        self.assertIn("command", finding.impact.lower())
        self.assertIn("OWASP Top 10", finding.standards)

    def test_quality_finding_is_structured(self):
        raw = "src/service.py\nLine 7\nconvention\nC0116\nMissing function or method docstring"
        finding = parse_quality_findings(raw)[0]

        self.assertEqual(finding.file, "src/service.py")
        self.assertEqual(finding.line, "7")
        self.assertEqual(finding.rule_id, "C0116")
        self.assertEqual(finding.confidence, "High")

    def test_missing_evidence_is_not_reported_as_compliant(self):
        project = SimpleNamespace(project_name="Demo")
        analysis = SimpleNamespace(bandit_output="", pylint_output="")
        context = build_report_context(project, analysis)

        self.assertEqual(context["findings"], [])
        self.assertTrue(
            all(item["status"] == "Insufficient evidence" for item in context["standards"])
        )
        self.assertIn("No structured finding evidence", context["executive_summary"])

    def test_rendered_sections_escape_scanner_output(self):
        project = SimpleNamespace(project_name="Demo")
        analysis = SimpleNamespace(
            bandit_output="HIGH\napp.py\nLine 1\nConfidence: HIGH\nB999 <script>alert(1)</script>",
            pylint_output="",
        )
        html = render_intelligence_sections(build_report_context(project, analysis))

        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("Standards and Compliance Mapping", html)


if __name__ == "__main__":
    unittest.main()
