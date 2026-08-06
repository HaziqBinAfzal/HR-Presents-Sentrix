import unittest
from types import SimpleNamespace

from helpers.report_project_mapping import render_security_controls, render_standards_mapping


class ReportProjectMappingTests(unittest.TestCase):
    def setUp(self):
        self.analysis = SimpleNamespace(
            bandit_output=(
                "app.py:42:5: B602 subprocess call with shell=True identified\n"
                "config.py:18:1: B105 Possible hardcoded password: 'example'\n"
            ),
            pylint_output="service.py:77:0: W0718: Catching too general exception Exception",
            syntax_output="",
            radon_output="",
        )

    def test_controls_include_project_evidence_location_and_fix(self):
        html = render_security_controls(self.analysis)
        self.assertIn("Related project evidence found", html)
        self.assertIn("app.py:42", html)
        self.assertIn("config.py:18", html)
        self.assertIn("How to fix", html)
        self.assertIn("Related error/evidence", html)

    def test_standards_include_project_relation_without_certification_claim(self):
        html = render_standards_mapping(self.analysis)
        self.assertIn("How it relates to this project", html)
        self.assertIn("Where", html)
        self.assertIn("not certification", html)

    def test_missing_evidence_does_not_invent_location(self):
        empty = SimpleNamespace(bandit_output="", pylint_output="", syntax_output="", radon_output="")
        html = render_security_controls(empty)
        self.assertIn("Not demonstrated by retained evidence", html)
        self.assertIn("No project-specific file or line can be asserted", html)


if __name__ == "__main__":
    unittest.main()
