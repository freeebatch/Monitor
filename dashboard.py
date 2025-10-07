from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)
STATUS_FILE = "monitor.log"

TEMPLATE = """        <!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Website Monitor Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f8fafc; color:#111; padding:2rem; }
    .card { background:#fff; padding:1rem; border-radius:10px; box-shadow:0 4px 16px rgba(0,0,0,0.07); max-width:900px; margin-bottom:1rem; }
    pre { white-space:pre-wrap; word-wrap:break-word; }
    h1 { margin-top:0; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🌐 Website Monitor Status</h1>
    <p>Last updates (most recent first):</p>
    <pre>{{logs}}</pre>
  </div>
  <div class="card">
    <h2>Raw API</h2>
    <p>GET <code>/api/status</code> to fetch JSON lines.</p>
  </div>
</body>
</html>
"""

@app.route('/')
def home():
    if not os.path.exists(STATUS_FILE):
        return "<p>No logs yet. Monitoring just started.</p>"
    with open(STATUS_FILE, 'r') as f:
        lines = f.readlines()[-200:]
    # show most recent first
    lines = reversed(lines)
    return render_template_string(TEMPLATE, logs=''.join(lines))

@app.route('/api/status')
def api_status():
    if not os.path.exists(STATUS_FILE):
        return jsonify([])
    with open(STATUS_FILE, 'r') as f:
        lines = [l.strip() for l in f.readlines()[-1000:]]
    # return as list of strings
    return jsonify(lines)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
