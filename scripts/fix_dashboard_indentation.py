from pathlib import Path

path = Path("analyzer/routes/main.py")
source = path.read_text(encoding="utf-8")

bad_block = '''
        recent_activities.append({

            "project": analysis.filename,

            "score": analysis.overall_score,

            "status": analysis.status,

            "date": analysis.created_at.strftime("%d %b %Y")

        })
'''

if bad_block not in source:
    raise SystemExit("Expected malformed dashboard block was not found")

source = source.replace(bad_block, "", 1)
path.write_text(source, encoding="utf-8")
