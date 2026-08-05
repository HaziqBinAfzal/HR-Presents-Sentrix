import os
from html import escape


def _safe(value, fallback="Not available"):
    """Return an escaped value suitable for inclusion in the HTML report."""
    if value is None or value == "":
        return fallback
    return escape(str(value))


def _preformatted(value, fallback="No findings recorded."):
    text = fallback if value is None or value == "" else str(value)
    return escape(text)


def generate_html_report(project, analysis):
    """Generate a self-contained, print-friendly Sentrix HTML report."""
    reports_dir = os.path.join("uploads", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"sentrix_analysis_{analysis.id}.html"
    report_path = os.path.join(reports_dir, filename)

    security_count = int(getattr(analysis, "security_count", 0) or 0)
    overall_score = float(getattr(analysis, "overall_score", 0) or 0)

    if security_count >= 5 or overall_score < 50:
        risk_label = "High"
        risk_class = "risk-high"
    elif security_count >= 2 or overall_score < 75:
        risk_label = "Medium"
        risk_class = "risk-medium"
    else:
        risk_label = "Low"
        risk_class = "risk-low"

    created_at = getattr(analysis, "created_at", None)
    created_display = (
        created_at.strftime("%d %B %Y, %H:%M")
        if hasattr(created_at, "strftime")
        else _safe(created_at)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sentrix Analysis Report - {_safe(project.project_name)}</title>
<style>
:root {{
    --primary: #1677ff;
    --primary-soft: #eaf3ff;
    --dark: #0f172a;
    --muted: #64748b;
    --border: #dbe3ee;
    --surface: #ffffff;
    --background: #f4f7fb;
    --success: #15803d;
    --warning: #b45309;
    --danger: #dc2626;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    background: var(--background);
    color: var(--dark);
    line-height: 1.6;
}}
.report {{ max-width: 1120px; margin: 32px auto; padding: 0 24px 40px; }}
.header {{
    background: linear-gradient(135deg, #0f172a 0%, #16345f 65%, #1677ff 100%);
    color: white;
    border-radius: 20px;
    padding: 34px;
    box-shadow: 0 18px 50px rgba(15, 23, 42, .18);
}}
.brand {{ font-size: 28px; font-weight: 800; letter-spacing: -.02em; }}
.brand small {{ display: block; font-size: 10px; letter-spacing: .18em; opacity: .75; margin-top: 2px; }}
.header-grid {{ display: flex; justify-content: space-between; gap: 24px; align-items: flex-end; margin-top: 34px; }}
.header h1 {{ margin: 0 0 8px; font-size: 34px; }}
.header p {{ margin: 0; opacity: .82; }}
.report-id {{ text-align: right; font-size: 13px; opacity: .82; }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 22px 0; }}
.metric, .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
}}
.metric {{ padding: 20px; }}
.metric-label {{ color: var(--muted); font-size: 13px; margin-bottom: 8px; }}
.metric-value {{ font-size: 27px; font-weight: 800; }}
.card {{ padding: 24px; margin-top: 18px; }}
.card h2 {{ margin: 0 0 18px; font-size: 20px; }}
.table {{ width: 100%; border-collapse: collapse; }}
.table th, .table td {{ padding: 12px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
.table th {{ width: 220px; color: var(--muted); font-size: 13px; font-weight: 600; }}
.table tr:last-child th, .table tr:last-child td {{ border-bottom: 0; }}
.risk {{ display: inline-flex; padding: 6px 11px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.risk-high {{ color: #991b1b; background: #fee2e2; }}
.risk-medium {{ color: #92400e; background: #fef3c7; }}
.risk-low {{ color: #166534; background: #dcfce7; }}
.summary {{ background: var(--primary-soft); border-left: 4px solid var(--primary); padding: 18px; border-radius: 10px; }}
.output {{
    margin: 0;
    padding: 18px;
    border-radius: 12px;
    background: #0b1220;
    color: #d8e4f4;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 520px;
    overflow: auto;
    font: 12px/1.65 "SFMono-Regular", Consolas, monospace;
}}
.footer {{ color: var(--muted); font-size: 12px; text-align: center; margin-top: 26px; }}
.actions {{ display: flex; justify-content: flex-end; margin: 18px 0; }}
.print-button {{
    appearance: none;
    border: 0;
    border-radius: 10px;
    background: var(--primary);
    color: white;
    padding: 11px 18px;
    font-weight: 700;
    cursor: pointer;
}}
@media (max-width: 820px) {{
    .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .header-grid {{ display: block; }}
    .report-id {{ text-align: left; margin-top: 18px; }}
}}
@media (max-width: 520px) {{
    .report {{ padding: 0 12px 24px; margin-top: 12px; }}
    .header {{ padding: 24px; }}
    .header h1 {{ font-size: 27px; }}
    .grid {{ grid-template-columns: 1fr; }}
    .table th, .table td {{ display: block; width: 100%; }}
    .table th {{ padding-bottom: 3px; border-bottom: 0; }}
}}
@media print {{
    body {{ background: white; }}
    .report {{ max-width: none; margin: 0; padding: 0; }}
    .header, .metric, .card {{ box-shadow: none; }}
    .actions {{ display: none; }}
    .output {{ max-height: none; overflow: visible; color: #111827; background: #f8fafc; border: 1px solid var(--border); }}
}}
</style>
</head>
<body>
<main class="report">
    <section class="header">
        <div class="brand">🛡 Sentrix<small>PRESENTED BY HR-PRESENTS</small></div>
        <div class="header-grid">
            <div>
                <h1>Analysis Report</h1>
                <p>{_safe(project.project_name)} · {_safe(analysis.language)}</p>
            </div>
            <div class="report-id">
                Report ID: {analysis.id}<br>
                Generated: {created_display}
            </div>
        </div>
    </section>

    <div class="actions"><button class="print-button" onclick="window.print()">Print / Save as PDF</button></div>

    <section class="grid">
        <article class="metric"><div class="metric-label">Overall Score</div><div class="metric-value">{_safe(analysis.overall_score, '0')}%</div></article>
        <article class="metric"><div class="metric-label">Pylint Score</div><div class="metric-value">{_safe(analysis.pylint_score, '0')}/10</div></article>
        <article class="metric"><div class="metric-label">Security Issues</div><div class="metric-value">{security_count}</div></article>
        <article class="metric"><div class="metric-label">Risk Level</div><div class="metric-value"><span class="risk {risk_class}">{risk_label}</span></div></article>
    </section>

    <section class="card">
        <h2>Project Information</h2>
        <table class="table">
            <tr><th>Project</th><td>{_safe(project.project_name)}</td></tr>
            <tr><th>Original File</th><td>{_safe(project.original_filename)}</td></tr>
            <tr><th>Language</th><td>{_safe(analysis.language)}</td></tr>
            <tr><th>Status</th><td>{_safe(analysis.status)}</td></tr>
            <tr><th>Analysis Date</th><td>{created_display}</td></tr>
            <tr><th>Duration</th><td>{_safe(getattr(analysis, 'analysis_duration', None))}</td></tr>
        </table>
    </section>

    <section class="card">
        <h2>Code Metrics</h2>
        <table class="table">
            <tr><th>Total Files</th><td>{_safe(getattr(analysis, 'total_files', None), '0')}</td></tr>
            <tr><th>Total Lines</th><td>{_safe(getattr(analysis, 'total_lines', None), '0')}</td></tr>
            <tr><th>Functions</th><td>{_safe(getattr(analysis, 'functions_count', None), '0')}</td></tr>
            <tr><th>Classes</th><td>{_safe(getattr(analysis, 'classes_count', None), '0')}</td></tr>
            <tr><th>Comments</th><td>{_safe(getattr(analysis, 'comments_count', None), '0')}</td></tr>
            <tr><th>Blank Lines</th><td>{_safe(getattr(analysis, 'blank_lines', None), '0')}</td></tr>
            <tr><th>Complexity</th><td>{_safe(analysis.complexity)}</td></tr>
        </table>
    </section>

    <section class="card">
        <h2>Analysis Summary</h2>
        <div class="summary">{_safe(getattr(analysis, 'ai_summary', None), 'No summary was generated for this analysis.')}</div>
    </section>

    <section class="card">
        <h2>Syntax Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'syntax_output', None))}</pre>
    </section>

    <section class="card">
        <h2>Pylint Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'pylint_output', None))}</pre>
    </section>

    <section class="card">
        <h2>Security Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'bandit_output', None))}</pre>
    </section>

    <section class="card">
        <h2>Complexity Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'radon_output', None))}</pre>
    </section>

    <p class="footer">Generated by Sentrix · Presented and maintained by HR-Presents</p>
</main>
</body>
</html>
"""

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(html)

    return report_path
