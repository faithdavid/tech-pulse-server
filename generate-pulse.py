import json
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--type', default='tech')
parser.add_argument('--file', default='pulse-data.json')
args = parser.parse_args()

with open(args.file) as f:
    data = json.load(f)

html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Tech Pulse</title></head>
<body>
<h1>Tech Pulse — {datetime.utcnow().strftime('%Y-%m-%d')}</h1>
<pre>{json.dumps(data, indent=2)}</pre>
</body></html>'''

with open('latest-tech-pulse.html', 'w') as out:
    out.write(html)
print("HTML generated: latest-tech-pulse.html")
