import unittest
from types import SimpleNamespace

from helpers.scoring import calculate_scorecard, scorecard_from_analysis


class ScoringConsistencyTests(unittest.TestCase):
    def test_all_enabled_analyzers_contribute(self):
        card = calculate_scorecard(
            pylint_score=8.0,
            bandit_issues=[{"severity": "HIGH"}, {"severity": "LOW"}],
            complexities=[2, 7, 12],
            syntax_error_count=1,
            formatting_status="Needs Formatting",
            enabled={
                "pylint": True,
                "bandit": True,
                "radon": True,
                "syntax": True,
                "black": True,
            },
        )
        self.assertEqual(
            set(card["components"]),
            {"quality", "security", "maintainability", "syntax", "formatting"},
        )
        self.assertGreater(card["overall_score"], 0)
        self.assertLess(card["overall_score"], 100)
        self.assertEqual(card["security_findings"], 2)
        self.assertEqual(card["risk_level"], "Medium")

    def test_disabled_analyzer_is_excluded_not_zeroed(self):
        with_pylint_disabled = calculate_scorecard(
            pylint_score=None,
            bandit_issues=[],
            complexities=[2],
            syntax_error_count=0,
            formatting_status="Passed",
            enabled={
                "pylint": False,
                "bandit": True,
                "radon": True,
                "syntax": True,
                "black": True,
            },
        )
        self.assertIsNone(with_pylint_disabled["quality_score"])
        self.assertEqual(with_pylint_disabled["overall_score"], 100.0)

    def test_security_score_is_severity_weighted(self):
        low = calculate_scorecard(
            pylint_score=10,
            bandit_issues=[{"severity": "LOW"}],
            complexities=[1],
            formatting_status="Passed",
        )
        high = calculate_scorecard(
            pylint_score=10,
            bandit_issues=[{"severity": "HIGH"}],
            complexities=[1],
            formatting_status="Passed",
        )
        self.assertGreater(low["security_score"], high["security_score"])
        self.assertEqual(low["risk_level"], "Low")
        self.assertEqual(high["risk_level"], "Low")  # v1 risk threshold is count-based

    def test_persisted_analysis_uses_same_display_logic(self):
        analysis = SimpleNamespace(
            overall_score=82.5,
            pylint_score=8.4,
            security_count=2,
            formatting_status="Passed",
            complexity="Medium",
            pylint_output="x.py\nLine 1\nwarning\nunused-import\nUnused import",
            issues_count=1,
            bandit_output=(
                "HIGH\nx.py\nLine 2\nConfidence: HIGH\nUnsafe call\n\n"
                "LOW\nx.py\nLine 3\nConfidence: MEDIUM\nWeak pattern"
            ),
            radon_output="func\nGrade: B\nComplexity: 7",
            syntax_output="",
        )
        card = scorecard_from_analysis(analysis)
        self.assertEqual(card["overall_score"], 82.5)
        self.assertEqual(card["quality_score"], 84.0)
        self.assertEqual(card["risk_level"], "Medium")
        self.assertEqual(card["health_label"], "Good")
        self.assertEqual(card["final_rating"], "B")

    def test_legacy_zero_with_no_findings_is_not_real_quality_zero(self):
        analysis = SimpleNamespace(
            overall_score=75,
            pylint_score=0,
            security_count=0,
            formatting_status="Passed",
            complexity="Low",
            pylint_output="",
            issues_count=0,
            bandit_output="",
            radon_output="func\nGrade: A\nComplexity: 1",
            syntax_output="",
        )
        card = scorecard_from_analysis(analysis)
        self.assertIsNone(card["quality_score"])
        self.assertEqual(card["overall_score"], 75.0)


if __name__ == "__main__":
    unittest.main()
