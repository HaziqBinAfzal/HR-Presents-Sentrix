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


def _recommendation_items(value):
    """Convert stored recommendation text into safe ordered-list items."""
    if not value:
        return ["Review the detailed findings and address the highest-risk items first."]

    items = []
    for raw_line in str(value).splitlines():
        line = raw_line.strip().lstrip("-•*0123456789. ").strip()
        if line:
            items.append(escape(line))

    return items or ["Review the detailed findings and address the highest-risk items first."]


def _health_status(score, security_count, issues_count):
    if score >= 85 and security_count == 0 and issues_count <= 5:
        return "Excellent", "health-excellent", "Strong quality with no significant security concerns detected."
    if score >= 70 and security_count <= 1:
        return "Good", "health-good", "Generally healthy, with a small number of improvements recommended."
    if score >= 50 and security_count < 5:
        return "Needs Attention", "health-warning", "Several findings should be reviewed before release."
    return "High Risk", "health-danger", "Significant quality or security concerns require prompt remediation."


def generate_html_report(project, analysis):
    """Generate a self-contained, branded, PDF-ready Sentrix HTML report."""
    reports_dir = os.path.join("uploads", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"sentrix_analysis_{analysis.id}.html"
    report_path = os.path.join(reports_dir, filename)

    security_count = int(getattr(analysis, "security_count", 0) or 0)
    issues_count = int(getattr(analysis, "issues_count", 0) or 0)
    overall_score = float(getattr(analysis, "overall_score", 0) or 0)
    pylint_score = float(getattr(analysis, "pylint_score", 0) or 0)
    recommendations = _recommendation_items(getattr(analysis, "recommendations", None))
    health_label, health_class, health_message = _health_status(
        overall_score,
        security_count,
        issues_count,
    )

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

    recommendation_html = "".join(f"<li>{item}</li>" for item in recommendations)
    logo_url = "/static/images/sentrix-electric-spark-wing.png?v=3"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sentrix Analysis Report - {_safe(project.project_name)}</title>
<style>
:root {{
    --primary: #1677ff;
    --primary-dark: #0f4fb8;
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
html {{ scroll-behavior: smooth; }}
body {{
    margin: 0;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    background: var(--background);
    color: var(--dark);
    line-height: 1.6;
}}
a {{ color: var(--primary-dark); text-decoration: none; }}
.report {{ max-width: 1120px; margin: 32px auto; padding: 0 24px 40px; }}
.cover {{
    min-height: 690px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(145deg, #08111f 0%, #15335d 62%, #1677ff 100%);
    color: white;
    border-radius: 22px;
    padding: 46px;
    box-shadow: 0 20px 56px rgba(15, 23, 42, .22);
}}
.brand {{ display:flex; align-items:center; gap:16px; font-size:30px; font-weight:800; letter-spacing:-.02em; }}
.brand img {{ width:86px; height:72px; object-fit:contain; border-radius:16px; }}
.brand small {{ display:block; font-size:10px; letter-spacing:.18em; opacity:.76; margin-top:3px; }}
.cover h1 {{ margin: 0 0 12px; font-size: 48px; line-height: 1.08; }}
.cover-subtitle {{ font-size: 20px; opacity: .88; max-width: 680px; }}
.cover-meta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 30px; }}
.cover-meta div {{ padding: 16px; border: 1px solid rgba(255,255,255,.2); border-radius: 13px; background: rgba(255,255,255,.08); }}
.cover-meta small {{ display: block; opacity: .72; margin-bottom: 3px; }}
.confidential {{ font-size: 12px; opacity: .72; }}
.actions {{ display: flex; justify-content: flex-end; gap: 10px; margin: 18px 0; }}
.button {{ border: 0; border-radius: 10px; padding: 11px 18px; font-weight: 700; cursor: pointer; }}
.button-primary {{ background: var(--primary); color: white; }}
.button-secondary {{ background: white; color: var(--dark); border: 1px solid var(--border); }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 22px 0; }}
.metric, .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; box-shadow: 0 8px 24px rgba(15, 23, 42, .05); }}
.metric {{ padding: 20px; }}
.metric-label {{ color: var(--muted); font-size: 13px; margin-bottom: 8px; }}
.metric-value {{ font-size: 27px; font-weight: 800; }}
.card {{ padding: 26px; margin-top: 18px; }}
.card h2 {{ margin: 0 0 18px; font-size: 22px; }}
.card h3 {{ margin: 22px 0 10px; font-size: 17px; }}
.section-kicker {{ color: var(--primary-dark); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }}
.table {{ width: 100%; border-collapse: collapse; }}
.table th, .table td {{ padding: 12px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
.table th {{ width: 220px; color: var(--muted); font-size: 13px; font-weight: 600; }}
.table tr:last-child th, .table tr:last-child td {{ border-bottom: 0; }}
.risk, .health {{ display: inline-flex; padding: 6px 11px; border-radius: 999px; font-size: 12px; font-weight: 800; }}
.risk-high, .health-danger {{ color: #991b1b; background: #fee2e2; }}
.risk-medium, .health-warning {{ color: #92400e; background: #fef3c7; }}
.risk-low, .health-good {{ color: #166534; background: #dcfce7; }}
.health-excellent {{ color: #075985; background: #e0f2fe; }}
.summary {{ background: var(--primary-soft); border-left: 4px solid var(--primary); padding: 18px; border-radius: 10px; }}
.health-panel {{ display: flex; justify-content: space-between; gap: 20px; align-items: center; padding: 18px; border-radius: 12px; background: #f8fafc; border: 1px solid var(--border); }}
.toc {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 28px; padding: 0; list-style: none; }}
.toc li {{ border-bottom: 1px dashed var(--border); padding: 8px 0; }}
.recommendations {{ margin: 0; padding-left: 22px; }}
.recommendations li {{ padding: 7px 0 7px 5px; }}
.output {{ margin: 0; padding: 18px; border-radius: 12px; background: #0b1220; color: #d8e4f4; white-space: pre-wrap; word-break: break-word; max-height: 520px; overflow: auto; font: 12px/1.65 "SFMono-Regular", Consolas, monospace; }}
.appendix-note {{ color: var(--muted); font-size: 13px; }}
.footer {{ color: var(--muted); font-size: 12px; text-align: center; margin-top: 26px; }}
.page-break {{ break-before: page; page-break-before: always; }}
.avoid-break {{ break-inside: avoid; page-break-inside: avoid; }}
@media (max-width: 820px) {{
    .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .cover {{ min-height: auto; }}
    .cover-meta, .toc {{ grid-template-columns: 1fr; }}
    .health-panel {{ align-items: flex-start; flex-direction: column; }}
}}
@media (max-width: 520px) {{
    .report {{ padding: 0 12px 24px; margin-top: 12px; }}
    .cover {{ padding: 28px; }}
    .cover h1 {{ font-size: 34px; }}
    .grid {{ grid-template-columns: 1fr; }}
    .table th, .table td {{ display: block; width: 100%; }}
    .table th {{ padding-bottom: 3px; border-bottom: 0; }}
}}
@media print {{
    @page {{ size: A4; margin: 14mm; }}
    body {{ background: white; print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
    .report {{ max-width: none; margin: 0; padding: 0; }}
    .cover {{ min-height: 252mm; border-radius: 0; box-shadow: none; }}
    .actions {{ display: none; }}
    .metric, .card {{ box-shadow: none; }}
    .output {{ max-height: none; overflow: visible; color: #111827; background: #f8fafc; border: 1px solid var(--border); }}
    a {{ color: inherit; }}
}}
</style>
</head>
<body>
<main class="report">
    <section class="cover">
        <div class="brand"><img src="{logo_url}" alt="Sentrix Electric Spark Wing"><span>Sentrix<small>PRESENTED BY HR-PRESENTS</small></span></div>
        <div>
            <div class="section-kicker" style="color:#b9d6ff;">Software assurance report</div>
            <h1>Project Analysis Report</h1>
            <p class="cover-subtitle">Quality, security, maintainability, and structural findings for {_safe(project.project_name)}.</p>
            <div class="cover-meta">
                <div><small>Project</small><strong>{_safe(project.project_name)}</strong></div>
                <div><small>Report ID</small><strong>SENTRIX-{analysis.id}</strong></div>
                <div><small>Language</small><strong>{_safe(analysis.language, 'Python')}</strong></div>
                <div><small>Generated</small><strong>{created_display}</strong></div>
            </div>
        </div>
        <div class="confidential">Confidential analysis output · Generated for the authenticated Sentrix workspace owner</div>
    </section>

    <div class="actions">
        <button class="button button-secondary" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})">Back to cover</button>
        <button class="button button-primary" onclick="window.print()">Print / Save as PDF</button>
    </div>

    <section class="card page-break">
        <div class="section-kicker">Document navigation</div>
        <h2>Contents</h2>
        <ol class="toc">
            <li><a href="#executive-summary">Executive Summary</a></li>
            <li><a href="#score-overview">Score Overview</a></li>
            <li><a href="#project-profile">Project Profile</a></li>
            <li><a href="#recommendations">Recommendations</a></li>
            <li><a href="#quality-findings">Quality Findings</a></li>
            <li><a href="#security-findings">Security Findings</a></li>
            <li><a href="#complexity-findings">Complexity Findings</a></li>
            <li><a href="#appendix">Appendix</a></li>
        </ol>
    </section>

    <section class="card" id="executive-summary">
        <div class="section-kicker">Assessment</div>
        <h2>Executive Summary</h2>
        <div class="health-panel">
            <div>
                <strong>Project Health</strong>
                <p style="margin:6px 0 0;color:var(--muted);">{health_message}</p>
            </div>
            <span class="health {health_class}">{health_label}</span>
        </div>
        <h3>Analysis summary</h3>
        <div class="summary">{_safe(getattr(analysis, 'ai_summary', None), 'No summary was generated for this analysis.')}</div>
    </section>

    <section class="grid" id="score-overview">
        <article class="metric avoid-break"><div class="metric-label">Overall Score</div><div class="metric-value">{overall_score:.1f}%</div></article>
        <article class="metric avoid-break"><div class="metric-label">Pylint Score</div><div class="metric-value">{pylint_score:.1f}/10</div></article>
        <article class="metric avoid-break"><div class="metric-label">Quality Issues</div><div class="metric-value">{issues_count}</div></article>
        <article class="metric avoid-break"><div class="metric-label">Security Risk</div><div class="metric-value"><span class="risk {risk_class}">{risk_label}</span></div></article>
    </section>

    <section class="card" id="project-profile">
        <div class="section-kicker">Scope</div>
        <h2>Project Profile</h2>
        <table class="table">
            <tr><th>Project</th><td>{_safe(project.project_name)}</td></tr>
            <tr><th>Original File</th><td>{_safe(project.original_filename)}</td></tr>
            <tr><th>Language</th><td>{_safe(analysis.language)}</td></tr>
            <tr><th>Status</th><td>{_safe(analysis.status)}</td></tr>
            <tr><th>Analysis Date</th><td>{created_display}</td></tr>
            <tr><th>Duration</th><td>{_safe(getattr(analysis, 'analysis_duration', None), '0')} seconds</td></tr>
            <tr><th>Total Files</th><td>{_safe(getattr(analysis, 'total_files', None), '0')}</td></tr>
            <tr><th>Total Lines</th><td>{_safe(getattr(analysis, 'total_lines', None), '0')}</td></tr>
        </table>
    </section>

    <section class="card" id="recommendations">
        <div class="section-kicker">Action plan</div>
        <h2>Recommendations</h2>
        <ol class="recommendations">{recommendation_html}</ol>
    </section>

    <section class="card" id="quality-findings">
        <div class="section-kicker">Static analysis</div>
        <h2>Quality Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'pylint_output', None))}</pre>
    </section>

    <section class="card" id="security-findings">
        <div class="section-kicker">Security review</div>
        <h2>Security Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'bandit_output', None))}</pre>
    </section>

    <section class="card" id="complexity-findings">
        <div class="section-kicker">Maintainability</div>
        <h2>Complexity Findings</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'radon_output', None))}</pre>
    </section>

    <section class="card" id="appendix">
        <div class="section-kicker">Appendix</div>
        <h2>Syntax and Structural Output</h2>
        <pre class="output">{_preformatted(getattr(analysis, 'syntax_output', None))}</pre>
    </section>

    <div class="footer"><img src="{logo_url}" alt="Sentrix Electric Spark Wing" style="width:44px;height:37px;object-fit:contain;vertical-align:middle;border-radius:8px;margin-right:8px">Sentrix · Presented by HR-Presents</div>
</main>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(html)

    return report_path
