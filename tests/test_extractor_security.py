import tempfile
import unittest
import zipfile
from pathlib import Path

from analyzer.extractor import extract_project


class SecureExtractorTests(unittest.TestCase):
    def _archive(self, root, entries):
        archive_path = Path(root) / "project.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in entries:
                archive.writestr(name, content)
        return archive_path

    def test_extracts_valid_nested_python_project(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(
                root,
                [
                    ("project/app.py", "print('ok')\n"),
                    ("project/pkg/module.py", "VALUE = 1\n"),
                    ("project/README.md", "example\n"),
                ],
            )
            extract_folder = Path(root) / "extracted"

            files = extract_project(str(archive_path), str(extract_folder))

            self.assertEqual(len(files), 2)
            self.assertTrue(all(Path(path).is_file() for path in files))
            self.assertTrue(all(Path(path).suffix == ".py" for path in files))

    def test_rejects_parent_directory_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(root, [("../escape.py", "print('bad')\n")])

            with self.assertRaisesRegex(ValueError, "Unsafe ZIP archive path"):
                extract_project(str(archive_path), str(Path(root) / "extracted"))

            self.assertFalse((Path(root) / "escape.py").exists())

    def test_rejects_backslash_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(root, [("..\\escape.py", "print('bad')\n")])

            with self.assertRaisesRegex(ValueError, "Unsafe ZIP archive path"):
                extract_project(str(archive_path), str(Path(root) / "extracted"))

    def test_rejects_case_insensitive_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(
                root,
                [("src/App.py", "A = 1\n"), ("src/app.py", "A = 2\n")],
            )

            with self.assertRaisesRegex(ValueError, "duplicate file paths"):
                extract_project(str(archive_path), str(Path(root) / "extracted"))

    def test_rejects_nested_zip_archive(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(root, [("nested.zip", b"not-an-inner-zip")])

            with self.assertRaisesRegex(ValueError, "Nested ZIP archives"):
                extract_project(str(archive_path), str(Path(root) / "extracted"))

    def test_rejects_archive_without_python_files(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(root, [("README.md", "no Python here\n")])

            with self.assertRaisesRegex(ValueError, "No Python files"):
                extract_project(str(archive_path), str(Path(root) / "extracted"))

    def test_ignores_virtual_environment_directories(self):
        with tempfile.TemporaryDirectory() as root:
            archive_path = self._archive(
                root,
                [
                    ("app.py", "print('ok')\n"),
                    ("venv/lib/ignored.py", "print('ignore')\n"),
                ],
            )

            files = extract_project(
                str(archive_path),
                str(Path(root) / "extracted"),
            )

            self.assertEqual([Path(path).name for path in files], ["app.py"])


if __name__ == "__main__":
    unittest.main()
