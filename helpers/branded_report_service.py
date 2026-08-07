import os
import threading
from pathlib import Path

from helpers.report_service import generate_html_report as _generate_html_report


_REPORT_CWD_LOCK = threading.Lock()

ELECTRIC_SPARK_WING = """
<svg class="report-brand-mark" viewBox="0 0 96 72" role="img" aria-label="Sentrix Electric Spark Wing" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="reportWing" x1="8" y1="8" x2="88" y2="64" gradientUnits="userSpaceOnUse">
      <stop stop-color="#38bdf8"/>
      <stop offset="0.55" stop-color="#1677ff"/>
      <stop offset="1" stop-color="#818cf8"/>
    </linearGradient>
  </defs>
  <path d="M45 18 21 8l8 12-19-5 13 14-14-1 22 17 12-8-8-6 10 1Z" fill="url(#reportWing)"/>
  <path d="m51 18 24-10-8 12 19-5-13 14 14-1-22 17-12-8 8-6-10 1Z" fill="url(#reportWing)"/>
  <path d="M52 13 38 38h11l-7 22 22-30H53l8-17Z" fill="#ffffff"/>
</svg>
""".strip()


def _health(overall_score):
    score = float(overall_score or 0)
    if score >= 90:
        return "Excellent", "health-excellent"
    if score >= 75:
        return "Good", "health-good"
    if score >= 55:
        return "Needs Attention", "health-warning"
    return "High Risk", "health-danger"


def _security_risk(security_count):
    count = int(security_count or 0)
    if count >= 5:
        return "High", "risk-high"
    if count >= 2:
        return "Medium", "risk-medium"
    if count >= 1:
        return "Low", "risk-low"
    return "None", "risk-low"


def _replace_badge(html, css_prefix, labels, new_label, new_class):
    for old_label, old_class in labels:
        html = html.replace(
            f'<span class="{css_prefix} {old_class}">{old_label}</span>',
            f'<span class="{css_prefix} {new_class}">{new_label}</span>',
        )
    return html


def generate_html_report(project, analysis):
    """Generate a branded report inside the writable Sentrix data directory."""
    data_dir = Path(os.environ.get("SENTRIX_DATA_DIR", Path.cwd())).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    # The legacy report renderer still writes a relative uploads/reports path.
    # Serialize only that tiny cwd-sensitive section so simultaneous analyses
    # cannot send reports to each other's working directories.
    with _REPORT_CWD_LOCK:
        original_cwd = Path.cwd()
        try:
            os.chdir(data_dir)
            report_path = _generate_html_report(project, analysis)
        finally:
            os.chdir(original_cwd)

    path = Path(report_path)
    if not path.is_absolute():
        path = data_dir / path
    path = path.resolve()

    html = path.read_text(encoding="utf-8")

    html = html.replace(
        ".brand { font-size: 30px; font-weight: 800; letter-spacing: -.02em; }",
        ".brand { display:flex; align-items:center; gap:14px; font-size:30px; font-weight:800; letter-spacing:-.02em; }"
        ".report-brand-mark { width:76px; height:54px; flex:0 0 auto; }"
        ".brand-copy { display:block; }",
    )
    html = html.replace(
        '<div class="brand">🛡 Sentrix<small>PRESENTED BY HR-PRESENTS</small></div>',
        f'<div class="brand">{ELECTRIC_SPARK_WING}<span class="brand-copy">Sentrix<small>PRESENTED BY HR-PRESENTS</small></span></div>',
    )

    health_label, health_class = _health(getattr(analysis, "overall_score", 0))
    html = _replace_badge(
        html,
        "health",
        [
            ("Excellent", "health-excellent"),
            ("Good", "health-good"),
            ("Needs Attention", "health-warning"),
            ("High Risk", "health-danger"),
        ],
        health_label,
        health_class,
    )

    risk_label, risk_class = _security_risk(getattr(analysis, "security_count", 0))
    html = _replace_badge(
        html,
        "risk",
        [
            ("High", "risk-high"),
            ("Medium", "risk-medium"),
            ("Low", "risk-low"),
        ],
        risk_label,
        risk_class,
    )

    path.write_text(html, encoding="utf-8")
    return str(path)
