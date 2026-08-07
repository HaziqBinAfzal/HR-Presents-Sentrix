from bandit.core import config as bandit_config
from bandit.core import manager as bandit_manager


def run_bandit(path):
    """Run Bandit in-process so packaged Windows builds need no external CLI."""
    try:
        config = bandit_config.BanditConfig()
        manager = bandit_manager.BanditManager(
            config,
            "file",
            quiet=True,
        )
        manager.discover_files([path], recursive=True)
        manager.run_tests()

        issues = []
        for issue in manager.get_issue_list():
            issues.append(
                {
                    "file": getattr(issue, "fname", None),
                    "line": getattr(issue, "lineno", None),
                    "column": getattr(issue, "col_offset", None),
                    "severity": str(getattr(issue, "severity", "Unknown")),
                    "confidence": str(getattr(issue, "confidence", "Unknown")),
                    "issue": getattr(issue, "text", ""),
                    "test_id": getattr(issue, "test_id", None),
                    "test_name": getattr(issue, "test", None),
                    "code": getattr(issue, "get_code", lambda: "")(),
                }
            )

        output = "\n\n".join(
            f"{item['severity']} | {item['file']}:{item['line']} | {item['test_id']} | {item['issue']}"
            for item in issues
        )

        return {
            "count": len(issues),
            "issues": issues,
            "output": output,
        }
    except Exception as error:
        return {
            "count": 0,
            "issues": [],
            "output": f"Bandit analyzer error: {error}",
            "error": str(error),
        }
