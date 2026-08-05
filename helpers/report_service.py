"""Professional HTML report generation for Sentrix analyses."""

from __future__ import annotations

import html
import os
from pathlib import Path


def _escape(value) -> str:
    return html.escape(str(value or ""))


def _rows(items, columns):
    if not items:
        return f'<tr><td colspan="{len(columns)}">No findings.</td></tr>'
    return "".join(
        "<tr>" + "".join(f"<td>{_escape(item.get(key, ''))}</td>" for key, _ in columns) + "</tr>"
        for item in items
    )


def generate_html_report(project, analysis, payload=None):
    """Generate a print/PDF-ready Sentrix report with charts, tables and appendix."""
    payload = payload or {}
    stats = payload.get("stats", {})
    summary = payload.get("summary", {})
    pylint = payload.get("pylint", {})
    bandit = payload.get("bandit", {})
    radon = payload.get("radon", {})
    syntax = payload.get("syntax", {})

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"analysis_{analysis.id}.html"

    risks = "".join(f"<li>{_escape(item)}</li>" for item in summary.get("biggest_risks", []))
    next_steps = "".join(f"<li>{_escape(item)}</li>" for item in summary.get("recommended_next_steps", []))
    fixes = "".join(f"<li>{_escape(item)}</li>" for item in summary.get("prioritized_fixes", []))
    pylint_columns = [("severity", "Severity"), ("file", "File"), ("line", "Line"), ("code", "Code"), ("message", "Message")]
    security_columns = [("severity", "Severity"), ("file", "File"), ("line", "Line"), ("cwe", "CWE"), ("owasp", "OWASP"), ("message", "Finding")]
    complexity_columns = [("file", "File"), ("name", "Function"), ("line", "Line"), ("complexity", "Complexity"), ("rank", "Rank")]
    syntax_columns = [("file", "File"), ("line", "Line"), ("column", "Column"), ("message", "Error"), ("suggestion", "Suggested correction")]

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sentrix Analysis Report - {_escape(project.project_name)}</title>
<style>
:root{{--ink:#172033;--muted:#657089;--line:#dfe5ef;--brand:#4f46e5;--good:#16845b;--warn:#b7791f;--bad:#c53030;}}
*{{box-sizing:border-box}} body{{font-family:Inter,Arial,sans-serif;margin:0;color:var(--ink);background:#f5f7fb;line-height:1.5}}
.page{{max-width:1100px;margin:24px auto;background:white;padding:48px;box-shadow:0 8px 30px #15203a18}}
.cover{{min-height:680px;display:flex;flex-direction:column;justify-content:center;border-bottom:8px solid var(--brand)}}
h1{{font-size:46px;margin:0 0 12px}} h2{{margin-top:42px;border-bottom:2px solid var(--line);padding-bottom:8px}} h3{{margin-top:24px}}
.kicker{{text-transform:uppercase;letter-spacing:.14em;color:var(--brand);font-weight:700}} .muted{{color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} .card{{border:1px solid var(--line);border-radius:12px;padding:18px}}
.value{{font-size:30px;font-weight:800}} .bar{{height:12px;background:#e8ecf4;border-radius:9px;overflow:hidden}} .bar span{{display:block;height:100%;background:var(--brand)}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:12px}} th,td{{border:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}} th{{background:#f6f7fb}}
.badge{{display:inline-block;padding:3px 8px;border-radius:999px;background:#eef0ff;color:var(--brand);font-weight:700}}
.callout{{border-left:4px solid var(--brand);padding:14px 18px;background:#f7f7ff}}
@media print{{body{{background:white}} .page{{margin:0;max-width:none;box-shadow:none;padding:25mm}} .cover{{page-break-after:always}} h2{{page-break-after:avoid}} table{{page-break-inside:auto}} tr{{page-break-inside:avoid}}}}
@media(max-width:800px){{.page{{margin:0;padding:24px}}.grid{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><main class="page">
<section class="cover"><div class="kicker">Sentrix Code Intelligence</div><h1>Project Analysis Report</h1><h2 style="border:0;margin:0">{_escape(project.project_name)}</h2><p class="muted">Generated {_escape(analysis.created_at)} · {_escape(project.original_filename)}</p><div class="value">{_escape(analysis.overall_score)}/100</div><p>Project Health Score</p></section>

<h2>Executive Summary</h2><div class="callout">{_escape(summary.get('executive_summary', analysis.ai_summary))}</div>
<div class="grid" style="margin-top:18px">
<div class="card"><div class="muted">Python files</div><div class="value">{_escape(stats.get('python_files', analysis.total_files))}</div></div>
<div class="card"><div class="muted">Lines of code</div><div class="value">{_escape(stats.get('lines_of_code', analysis.total_lines))}</div></div>
<div class="card"><div class="muted">Pylint score</div><div class="value">{_escape(analysis.pylint_score)}/10</div></div>
<div class="card"><div class="muted">Security findings</div><div class="value">{_escape(analysis.security_count)}</div></div>
</div>
<h3>Biggest Risks</h3><ul>{risks or '<li>No critical risks detected.</li>'}</ul>

<h2>Project Overview</h2><table><tbody>
<tr><th>Total files</th><td>{_escape(stats.get('total_files'))}</td><th>Python files</th><td>{_escape(stats.get('python_files'))}</td></tr>
<tr><th>Code lines</th><td>{_escape(stats.get('code_lines'))}</td><th>Blank lines</th><td>{_escape(stats.get('blank_lines'))}</td></tr>
<tr><th>Comments</th><td>{_escape(stats.get('comment_lines'))}</td><th>Average file size</th><td>{_escape(stats.get('average_file_size'))} bytes</td></tr>
<tr><th>Functions</th><td>{_escape(stats.get('functions'))}</td><th>Classes</th><td>{_escape(stats.get('classes'))}</td></tr>
</tbody></table>

<h2>Score Cards</h2><div class="grid">
<div class="card"><span class="badge">Health</span><div class="value">{_escape(summary.get('project_health_score', analysis.overall_score))}</div><div class="bar"><span style="width:{max(0,min(100,float(analysis.overall_score or 0)))}%"></span></div></div>
<div class="card"><span class="badge">Security</span><div class="value">{_escape((bandit.get('counts') or {}).get('high', 0))}H / {_escape((bandit.get('counts') or {}).get('medium', 0))}M</div></div>
<div class="card"><span class="badge">Maintainability</span><div class="value">{_escape(radon.get('average_maintainability_index'))}</div></div>
<div class="card"><span class="badge">Complexity</span><div class="value">{_escape(radon.get('average_cyclomatic_complexity'))}</div></div>
</div>

<h2>Security Findings</h2><p>{_escape(summary.get('security_summary'))}</p><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in security_columns)}</tr></thead><tbody>{_rows(bandit.get('findings', []), security_columns)}</tbody></table>
<h2>Quality Findings</h2><p>{_escape(summary.get('code_quality_summary'))}</p><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in pylint_columns)}</tr></thead><tbody>{_rows(pylint.get('top_issues', []), pylint_columns)}</tbody></table>
<h2>Complexity Analysis</h2><p>{_escape(summary.get('maintainability_summary'))}</p><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in complexity_columns)}</tr></thead><tbody>{_rows(radon.get('worst_functions', []), complexity_columns)}</tbody></table>
<h2>Syntax Findings</h2><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in syntax_columns)}</tr></thead><tbody>{_rows(syntax.get('errors', []), syntax_columns)}</tbody></table>
<h2>AI Recommendations</h2><h3>Recommended Next Steps</h3><ol>{next_steps}</ol><h3>Prioritized Fixes</h3><ol>{fixes or '<li>No prioritized fixes.</li>'}</ol>
<h2>Appendix</h2><p>Analysis duration: {_escape(analysis.analysis_duration)} seconds. Tools: Pylint, Bandit, Radon, Python AST/tokenize. Results depend on installed analyzer versions and should be reviewed by a qualified engineer before production deployment.</p>
</main></body></html>"""
    report_path.write_text(document, encoding="utf-8")
    return os.fspath(report_path)
