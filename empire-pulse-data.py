#!/usr/bin/env python3
"""Empire Pulse — Data Gatherer
Collects Empire-wide status: crons, VFL, cabinet, agents, system health.
Outputs JSON that feeds into the Empire Pulse HTML template.
"""
import json, sqlite3, os, subprocess, platform
from datetime import datetime

BASE = os.path.expanduser('~')
DATA = {}

# 1. System Health
DATA['generated_at'] = datetime.now().strftime('%A, %B %d, %Y at %I:%M %p ET')
DATA['generated_iso'] = datetime.now().isoformat()
DATA['hostname'] = platform.node()
try:
    with open('/proc/uptime') as f:
        uptime_secs = float(f.read().split()[0])
        days = int(uptime_secs // 86400)
        hours = int((uptime_secs % 86400) // 3600)
        DATA['uptime'] = f'{days}d {hours}h'
except: DATA['uptime'] = 'N/A'

try:
    s = os.statvfs('/')
    free_gb = (s.f_frsize * s.f_bavail) / (1024**3)
    DATA['disk_free_gb'] = round(free_gb, 1)
except: DATA['disk_free_gb'] = 'N/A'

# 2. Cron Jobs (via hermes cron list)
try:
    result = subprocess.run(
        ['hermes', 'cron', 'list', '--json'],
        capture_output=True, text=True, timeout=10,
        env={**os.environ}
    )
    crons = json.loads(result.stdout) if result.stdout else {}
    jobs = []
    if isinstance(crons, dict) and 'jobs' in crons:
        for j in crons['jobs']:
            jobs.append({
                'name': j.get('name', '?'),
                'schedule': j.get('schedule', '?'),
                'status': j.get('last_status', '?'),
                'enabled': j.get('enabled', False),
                'channel': str(j.get('deliver', '?')).split(':')[-1][:20] if j.get('deliver') else '?',
                'next_run': j.get('next_run_at', '?')[:16] if j.get('next_run_at') else '?',
                'last_run': j.get('last_run_at', '?')[:16] if j.get('last_run_at') else '?',
            })
    DATA['cron_jobs'] = jobs
except:
    DATA['cron_jobs'] = []

# 3. VFL Ledger
ledger_path = os.path.join(BASE, '.hermes/cron/state/vfl_ledger.json')
if os.path.exists(ledger_path):
    try:
        with open(ledger_path) as f:
            d = json.load(f)
        preds = d.get('predictions', [])
        pending = [p for p in preds if not p.get('settled')]
        settled = [p for p in preds if p.get('settled')]
        won = [p for p in preds if p.get('outcome') == 'WON']
        lost = [p for p in preds if p.get('outcome') == 'LOST']
        DATA['vfl'] = {
            'total': len(preds),
            'pending': len(pending),
            'settled': len(settled),
            'won': len(won),
            'lost': len(lost),
            'latest_md': preds[-1].get('match_day') if preds else 'N/A',
            'latest_season': preds[-1].get('season_name') if preds else 'N/A',
        }
        # Recent predictions
        recent = preds[-8:] if len(preds) >= 8 else preds
        DATA['vfl']['recent_predictions'] = [{
            'md': p.get('match_day'),
            'home': p.get('home', '?')[:12],
            'away': p.get('away', '?')[:12],
            'pred': p.get('prediction', '?'),
            'conf': p.get('confidence', 0),
            'settled': p.get('settled', False),
            'outcome': p.get('outcome', '-'),
        } for p in recent]
    except:
        DATA['vfl'] = {'error': 'parse_failed'}
else:
    DATA['vfl'] = {'error': 'no_ledger'}

# 4. Sovereign DB
db_path = os.path.join(BASE, 'Documents/Projects/vfl-data/databases/sovereign.db')
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT status, COUNT(*) FROM master_ledger GROUP BY status')
        DATA['sovereign'] = {r[0]: r[1] for r in c.fetchall()}
        conn.close()
    except:
        DATA['sovereign'] = {}

# 5. Accuracy
acc_path = os.path.join(BASE, 'Documents/Projects/vfl-data/models/accuracy_tracker.json')
if os.path.exists(acc_path):
    try:
        with open(acc_path) as f:
            acc = json.load(f)
        DATA['accuracy'] = acc
    except:
        DATA['accuracy'] = {}

# 6. Cabinet roster
cabinet_path = os.path.join(BASE, 'Documents/Projects/trillions-empire/cabinet/ministers.md')
ministers = []
if os.path.exists(cabinet_path):
    with open(cabinet_path) as f:
        for line in f:
            if '|' in line and '---' not in line and line.strip().startswith('|'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3 and not parts[0].startswith('Minister'):
                    ministers.append({
                        'name': parts[0],
                        'ministry': parts[1],
                        'sex': parts[2] if len(parts) > 2 else '?'
                    })
DATA['cabinet'] = ministers[:12]

# 7. Pulse archives
tech_path = os.path.join(BASE, 'tech-pulse-server/tech-pulse')
video_path = os.path.join(BASE, 'tech-pulse-server/ai-video-pulse')
tech_count = len([f for f in os.listdir(tech_path) if f.endswith('.html')]) if os.path.exists(tech_path) else 0
video_count = len([f for f in os.listdir(video_path) if f.endswith('.html')]) if os.path.exists(video_path) else 0
DATA['pulse_archives'] = {'tech': tech_count, 'video': video_count, 'total': tech_count + video_count}

# 8. Agent channels
DATA['channels'] = {
    'oracle': {'id': '1502437593122603088', 'purpose': 'Predictions'},
    'verity': {'id': '1502437595366559826', 'purpose': 'Settlements'},
    'nova': {'id': '1502437597018980352', 'purpose': 'Surveillance'},
    'apollo': {'id': '1502437599602806825', 'purpose': 'Research'},
    'sage': {'id': '1502437601909411971', 'purpose': 'Intel Briefings'},
    'clara': {'id': '1502437604430184590', 'purpose': 'Analysis'},
}

# 9. Recent session activity (last 5 cron outputs)
output_dir = os.path.join(BASE, '.hermes/cron/output')
recent_activity = []
if os.path.exists(output_dir):
    files = sorted([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))], 
                   key=lambda f: os.path.getmtime(os.path.join(output_dir, f)), reverse=True)[:5]
    for f in files:
        fp = os.path.join(output_dir, f)
        size = os.path.getsize(fp)
        mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%I:%M %p')
        recent_activity.append({'file': f, 'size': f'{size/1024:.1f}K', 'time': mtime})
DATA['recent_activity'] = recent_activity

# Output as JSON
print(json.dumps(DATA, indent=2))
