"""Backward-compatible Pylint wrapper backed by the Sentrix engine."""

from analyzer.engine import run_pylint as _run_pylint


def run_pylint(file_path):
    result = _run_pylint(file_path)
    return {
        "score": result["score"],
        "issues": result["issues"],
        "output": result,
        "counts": result["counts"],
        "top_issues": result["top_issues"],
    }
