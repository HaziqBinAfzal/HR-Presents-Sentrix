"""HTML renderers for additive Sentrix report intelligence sections."""

from __future__ import annotations

from html import escape


def _safe(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return escape(str(value))


def _finding_cards(findings, empty_message):
    if not findings:
        return f'<div class="evidence-empty">{escape(empty_message)}</div>'

    cards = []
    for finding in findings:
        standards = ", ".join(finding.standards) or "No mapping available"
        severity_class = f"severity-{finding.severity.lower()}"
        cards.append(
            f"""
<article class="finding-card">
  <div class="finding-head"><div><span class="finding-category">{_safe(finding.category)}</span><h3>{_safe(finding.title)}</h3></div><span class="severity {severity_class}">{_safe(finding.severity)}</span></div>
  <table class="table compact-table">
    <tr><th>File</th><td>{_safe(finding.file)}</td><th>Line</th><td>{_safe(finding.line)}</td></tr>
    <tr><th>Rule ID</th><td>{_safe(finding.rule_id)}</td><th>Confidence</th><td>{_safe(finding.confidence)}</td></tr>
  </table>
  <h4>Evidence</h4><pre class="evidence">{_safe(finding.evidence)}</pre>
  <div class="finding-grid"><div><h4>Impact</h4><p>{_safe(finding.impact)}</p></div><div><h4>Remediation</h4><p>{_safe(finding.remediation)}</p></div></div>
  <p class="mapping-note"><strong>Standards mapping:</strong> {_safe(standards)}</p>
</article>"""
        )
    return "".join(cards)


def render_intelligence_sections(context):
    mapped = []
    for item in context["standards"]:
        status_class = "mapped" if item["status"] == "Mapped" else "insufficient"
        mapped.append(
            f"<tr><td>{_safe(item['name'])}</td><td><span class=\"mapping-status {status_class}\">{_safe(item['status'])}</span></td><td>{item['finding_count']}</td><td>{_safe(item['note'])}</td></tr>"
        )

    counts = context["severity_counts"]
    return f"""
<section class="card" id="methodology"><div class="section-kicker">Evidence model</div><h2>Methodology and Scope</h2><p>{_safe(context['methodology'])}</p><div class="summary"><strong>Assessment limitation:</strong> {_safe(context['limitations'])}</div></section>
<section class="card" id="risk-assessment"><div class="section-kicker">Security intelligence</div><h2>Risk Assessment</h2><div class="risk-matrix"><div><span>Critical</span><strong>{counts.get('Critical', 0)}</strong></div><div><span>High</span><strong>{counts.get('High', 0)}</strong></div><div><span>Medium</span><strong>{counts.get('Medium', 0)}</strong></div><div><span>Low</span><strong>{counts.get('Low', 0)}</strong></div><div><span>Informational</span><strong>{counts.get('Info', 0)}</strong></div></div><h3>Evidence-based executive interpretation</h3><p>{_safe(context['executive_summary'])}</p><h3>Developer summary</h3><p>{_safe(context['developer_summary'])}</p></section>
<section class="card" id="structured-security"><div class="section-kicker">Finding detail</div><h2>Structured Security Findings</h2>{_finding_cards(context['security_findings'], 'No structured security evidence was recorded. This does not establish that the project is vulnerability-free.')}</section>
<section class="card" id="structured-quality"><div class="section-kicker">Finding detail</div><h2>Structured Code Quality Findings</h2>{_finding_cards(context['quality_findings'], 'No structured code-quality evidence was recorded for this analysis.')}</section>
<section class="card" id="dependency-configuration"><div class="section-kicker">Coverage statement</div><h2>Dependency, Secrets, and Configuration Analysis</h2><table class="table"><tr><th>Dependency inventory</th><td>Insufficient evidence: the current analysis record does not preserve a package inventory or vulnerability database result.</td></tr><tr><th>Secrets detection</th><td>Security findings are mapped when stored scanner evidence mentions credentials, passwords, tokens, or API keys. Absence of such findings is not proof that no secrets exist.</td></tr><tr><th>Configuration analysis</th><td>Insufficient evidence unless a stored finding explicitly references configuration behavior. Runtime and deployment configuration require separate validation.</td></tr></table></section>
<section class="card page-break" id="standards"><div class="section-kicker">Control guidance</div><h2>Standards and Compliance Mapping</h2><p class="mapping-disclaimer">Mappings indicate relevance between observed findings and framework themes. They are not a certification, legal opinion, or proof of control implementation.</p><div class="table-scroll"><table class="table"><thead><tr><th>Framework</th><th>Assessment</th><th>Mapped findings</th><th>Basis</th></tr></thead><tbody>{''.join(mapped)}</tbody></table></div></section>
<section class="card" id="educational-notes"><div class="section-kicker">Reviewer guidance</div><h2>Educational and Audit Notes</h2><p>Severity describes potential impact, while confidence describes the scanner's certainty. A high-confidence result can still be non-exploitable, and a low-confidence result can still identify a real weakness. Validate reachability, data flow, trust boundaries, and compensating controls before accepting or closing a finding.</p><p>Recommended audit wording: “Sentrix identified the following static-analysis observations based on the evidence retained at scan time. Management should validate applicability, document remediation or risk acceptance, and retain verification evidence.”</p></section>
"""


REPORT_INTELLIGENCE_CSS = """
.finding-card{border:1px solid var(--border);border-radius:14px;padding:20px;margin:16px 0;background:#fbfdff;break-inside:avoid}.finding-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.finding-head h3{margin:4px 0 10px}.finding-category{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--primary-dark)}.severity{display:inline-flex;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:800}.severity-critical,.severity-high{background:#fee2e2;color:#991b1b}.severity-medium{background:#fef3c7;color:#92400e}.severity-low{background:#dcfce7;color:#166534}.severity-info{background:#e0f2fe;color:#075985}.compact-table th{width:auto}.compact-table td{width:30%}.evidence{white-space:pre-wrap;word-break:break-word;background:#f1f5f9;border:1px solid var(--border);padding:13px;border-radius:9px;font:12px/1.55 Consolas,monospace}.finding-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.finding-grid h4,.finding-card h4{margin:14px 0 5px}.mapping-note,.mapping-disclaimer{color:var(--muted);font-size:13px}.risk-matrix{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}.risk-matrix div{border:1px solid var(--border);border-radius:12px;padding:14px;background:#f8fafc}.risk-matrix span{display:block;color:var(--muted);font-size:12px}.risk-matrix strong{font-size:24px}.mapping-status{display:inline-flex;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:800}.mapping-status.mapped{background:#dcfce7;color:#166534}.mapping-status.insufficient{background:#f1f5f9;color:#475569}.evidence-empty{padding:18px;border:1px dashed var(--border);border-radius:12px;color:var(--muted);background:#f8fafc}.table-scroll{overflow-x:auto}@media(max-width:820px){.finding-grid,.risk-matrix{grid-template-columns:1fr}.finding-head{flex-direction:column}.compact-table th,.compact-table td{display:block;width:100%}}
"""
