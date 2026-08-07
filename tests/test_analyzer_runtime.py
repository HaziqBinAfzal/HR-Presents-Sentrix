import tempfile
import unittest
from pathlib import Path

from analyzer.lint import run_pylint
from analyzer.security import run_bandit


class AnalyzerRuntimeTests(unittest.TestCase):
    def test_pylint_reports_findings_for_bad_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "poor_sample.py"
            path.write_text(
                "import os\n\n"
                "def BAD_NAME(x):\n"
                "    unused = 1\n"
                "    return x\n",
                encoding="utf-8",
            )

            result = run_pylint(str(path))

            self.assertNotIn("error", result)
            self.assertIsInstance(result.get("issues"), list)
            self.assertGreater(len(result["issues"]), 0)
            self.assertGreaterEqual(float(result["score"]), 0.0)
            self.assertLessEqual(float(result["score"]), 10.0)

    def test_bandit_clean_scan_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "clean_sample.py"
            path.write_text("value = 1\n", encoding="utf-8")

            result = run_bandit(temp_dir)

            self.assertNotIn("error", result)
            self.assertIsInstance(result.get("issues"), list)
            self.assertEqual(result.get("count"), len(result["issues"]))


if __name__ == "__main__":
    unittest.main()
