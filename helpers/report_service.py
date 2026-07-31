import os



def generate_html_report(project, analysis):
    """
    Generate an HTML report for an analysis.
    """

    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"analysis_{analysis.id}.html"

    report_path = os.path.join(reports_dir, filename)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>CodeSentinel AI Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin:40px;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

th, td {{
    border:1px solid #ddd;
    padding:10px;
}}

th {{
    background:#f5f5f5;
}}

h1,h2 {{
    color:#0d6efd;
}}

</style>

</head>

<body>

<h1>CodeSentinel AI Report</h1>

<h2>Project Information</h2>

<table>

<tr>
<th>Project</th>
<td>{project.project_name}</td>
</tr>

<tr>
<th>Original File</th>
<td>{project.original_filename}</td>
</tr>

<tr>
<th>Language</th>
<td>{analysis.language}</td>
</tr>

<tr>
<th>Date</th>
<td>{analysis.created_at}</td>
</tr>

</table>

<br>

<h2>Analysis Results</h2>

<table>

<tr>
<th>Overall Score</th>
<td>{analysis.overall_score}%</td>
</tr>

<tr>
<th>Pylint Score</th>
<td>{analysis.pylint_score}</td>
</tr>

<tr>
<th>Security Issues</th>
<td>{analysis.security_count}</td>
</tr>

<tr>
<th>Complexity</th>
<td>{analysis.complexity}</td>
</tr>

<tr>
<th>Files</th>
<td>{analysis.total_files}</td>
</tr>

<tr>
<th>Lines</th>
<td>{analysis.total_lines}</td>
</tr>

<tr>
<th>Duration</th>
<td>{analysis.analysis_duration}</td>
</tr>

</table>

<br>

<h2>AI Summary</h2>

<p>{analysis.ai_summary}</p>

<h2>Recommendations</h2>

<p>{analysis.recommendations}</p>

</body>

</html>
"""

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(html)

    return report_path
