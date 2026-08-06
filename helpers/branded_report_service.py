from pathlib import Path

from helpers.report_service import generate_html_report as _generate_html_report


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


def generate_html_report(project, analysis):
    """Generate the standard report, then apply the permanent Sentrix wing brand."""
    report_path = _generate_html_report(project, analysis)
    path = Path(report_path)
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

    path.write_text(html, encoding="utf-8")
    return report_path
