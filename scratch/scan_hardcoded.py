import re
from pathlib import Path

app_code = Path('src/dashboard/app.py').read_text(encoding='utf-8')
lines = app_code.splitlines()

print("=== Titles, Section Headers, Subtitles, Annotations in app.py ===")
for idx, line in enumerate(lines, 1):
    l = line.strip()
    if any(k in l for k in ['_title', 'title=', 'title =', 'create_section_header', 'annotation_text', 'html.H4', 'html.H5', 'html.H6', 'y_title', 'x_title', 'text=']):
        if not l.startswith('#') and not l.startswith('//'):
            print(f"{idx:4d}: {l}")
