from pathlib import Path

from analyzer.engine import analyze_file_stats, build_summary, discover_python_files


def test_discovery_ignores_generated_and_dependency_directories(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "ignored.py").write_text("raise RuntimeError\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").write_text("pass\n", encoding="utf-8")

    files, total_files = discover_python_files(str(tmp_path))

    assert [path.name for path in files] == ["main.py", "tests.py"]
    assert total_files == 2


def test_file_statistics_and_syntax_diagnostic(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("# comment\n\ndef broken()\n    return 1\n", encoding="utf-8")

    stats, syntax_error = analyze_file_stats(source, Path(tmp_path))

    assert stats.lines == 4
    assert stats.blank_lines == 1
    assert stats.comment_lines == 1
    assert syntax_error["file"] == "broken.py"
    assert syntax_error["line"] == 3
    assert "colon" in syntax_error["suggestion"].lower()


def test_health_summary_prioritizes_security_and_syntax():
    stats = {"python_files": 3, "lines_of_code": 120}
    pylint = {
        "score": 8.0,
        "counts": {"error": 1, "warning": 2},
        "top_issues": [{"code": "E0001", "file": "a.py", "line": 2, "message": "failure"}],
    }
    bandit = {
        "counts": {"high": 1, "medium": 1, "low": 0},
        "findings": [{"file": "a.py", "line": 4, "message": "unsafe call"}],
    }
    radon = {"average_cyclomatic_complexity": 7, "average_maintainability_index": 71}
    syntax = [{"file": "b.py", "line": 8, "message": "expected ':'"}]

    summary = build_summary(stats, pylint, bandit, radon, syntax)

    assert summary["project_health_score"] < 80
    assert summary["biggest_risks"]
    assert summary["prioritized_fixes"][0].startswith("Fix a.py:4")
