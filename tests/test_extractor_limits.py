import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from analyzer.extractor import extract_project


class ExtractorLimitTests(unittest.TestCase):
    def _archive(self, root, entries):
        archive_path = Path(root) / "project.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in entries:
                archive.writestr(name, content)
        return archive_path

    def test_rejects_archive_over_member_limit(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(
                root,
                [(f"pkg/file_{index}.py", "VALUE = 1\n") for index in range(4)],
            )
            with patch("analyzer.extractor.MAX_ARCHIVE_MEMBERS", 3):
                with self.assertRaisesRegex(ValueError, "too many entries"):
                    extract_project(str(archive_path), str(Path(root) / "out"))

    def test_rejects_archive_over_total_uncompressed_limit(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(
                root,
                [("a.py", "A" * 40), ("b.py", "B" * 40)],
            )
            with patch("analyzer.extractor.MAX_ARCHIVE_UNCOMPRESSED_SIZE", 64):
                with self.assertRaisesRegex(ValueError, "500 MB safety limit"):
                    extract_project(str(archive_path), str(Path(root) / "out"))

    def test_rejects_single_member_over_limit(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(root, [("large.py", "X" * 65)])
            with patch("analyzer.extractor.MAX_SINGLE_MEMBER_SIZE", 64):
                with self.assertRaisesRegex(ValueError, "larger than 100 MB"):
                    extract_project(str(archive_path), str(Path(root) / "out"))

    def test_rejects_suspicious_compression_ratio(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(root, [("bomb.py", "A" * 10000)])
            with patch("analyzer.extractor.MAX_COMPRESSION_RATIO", 2):
                with self.assertRaisesRegex(ValueError, "suspicious compression ratio"):
                    extract_project(str(archive_path), str(Path(root) / "out"))

    def test_failed_extraction_removes_partial_output(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(
                root,
                [("good.py", "print('ok')\n"), ("../escape.py", "bad\n")],
            )
            output = Path(root) / "out"
            with self.assertRaises(ValueError):
                extract_project(str(archive_path), str(output))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
