import os
import re
import threading
from pathlib import Path

from helpers.report_service import generate_html_report as _generate_html_report
from helpers.scoring import scorecard_from_analysis


_REPORT_CWD_LOCK = threading.Lock()

ELECTRIC_SPARK_WING = """
<svg class="report-brand-mark" viewBox="0 0 180 120" role="img" aria-label="Sentrix Electric Spark Wing" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="reportWing" x1="18" y1="16" x2="146" y2="104" gradientUnits="userSpaceOnUse"><stop stop-color="#2496ff"/><stop offset="0.48" stop-color="#1677ff"/><stop offset="1" stop-color="#0754dc"/></linearGradient></defs>
  <g fill="url(#reportWing)"><path d="M84 40 59 31 17 13c6 20 18 37 37 50L31 58c9 13 22 23 39 29l-20 1c9 9 20 15 34 18l14-36-14-30Z"/><path d="M91 47 113 33l16-25-4 28 26-17-17 31 24-5-34 25-17 36 3-29H91l13-30H91Z"/><path d="M83 63 65 58l15 12-10 4 17 9 8-22-12 2Z" opacity=".94"/></g>
</svg>
""".strip()


def _replace_badge(html, css_prefix, labels, new_label, new_class):
    for old_label, old_class in labels:
        html = html.replace(
            f'<span class="{css_prefix} {old_class}">{old_label}</span>',
            f'<span class="{css_prefix} {new_class}">{new_label}</span>',
        )
    return html


def _health_class(label):
    return {"Excellent":"health-excellent","Good":"health-good","Needs Attention":"health-warning","High Risk":"health-danger"}[label]


def _risk_class(label):
    return {"High":"risk-high","Medium":"risk-medium","Low":"risk-low","None":"risk-low"}[label]


def _metric(label, value):
    return f'<article class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></article>'


def generate_html_report(project, analysis):
    """Generate HTML/print-PDF output from the same canonical scorecard as the UI."""
    data_dir = Path(os.environ.get("SENTRIX_DATA_DIR", Path.cwd())).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
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
        '<div class="brand">🛡 Sentrix<small>PRESENTED BY HR-PRESENTS</small></div>',
        f'<div class="brand"><div class="brand-logo">{ELECTRIC_SPARK_WING}</div><span>Sentrix<small>PRESENTED BY HR-PRESENTS</small></span></div>',
    )

    card = scorecard_from_analysis(analysis)
    health_label = card["health_label"]
    risk_label = card["risk_level"]
    html = _replace_badge(html,"health",[("Excellent","health-excellent"),("Good","health-good"),("Needs Attention","health-warning"),("High Risk","health-danger")],health_label,_health_class(health_label))
    html = _replace_badge(html,"risk",[("High","risk-high"),("Medium","risk-medium"),("Low","risk-low"),("None","risk-low")],risk_label,_risk_class(risk_label))

    quality = "N/A" if card["quality_score"] is None else f'{card["quality_score"]:.1f}%'
    security = "N/A" if card["security_score"] is None else f'{card["security_score"]:.1f}%'
    maintainability = "N/A" if card["maintainability_score"] is None else f'{card["maintainability_score"]:.1f}%'
    syntax = "N/A" if card["syntax_score"] is None else f'{card["syntax_score"]:.1f}%'
    metrics = (
        '<section class="grid" id="score-overview">'
        + _metric("Overall Score", f'{card["overall_score"]:.1f}%')
        + _metric("Code Quality", quality)
        + _metric("Security Score", security)
        + _metric("Maintainability", maintainability)
        + _metric("Syntax Score", syntax)
        + _metric("Final Rating", card["final_rating"])
        + _metric("Risk Level", risk_label)
        + _metric("Security Findings", str(card["security_findings"]))
        + '</section>'
    )
    html = re.sub(
        r'<section class="grid" id="score-overview">.*?</section>',
        metrics,
        html,
        count=1,
        flags=re.DOTALL,
    )

    path.write_text(html, encoding="utf-8")
    return str(path)
