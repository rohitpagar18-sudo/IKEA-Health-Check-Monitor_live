"""
Flask dashboard for live IKEA Health Check monitoring
"""
from flask import Flask, render_template_string, send_file
import json
import os
from pathlib import Path
import pandas as pd

app = Flask(__name__)

LOG_DIR = Path("logs")
REPORT_FILE = LOG_DIR / "health_check_report.json"
EXCEL_FILE = LOG_DIR / "health_check_report.xlsx"

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>IKEA Health Check Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        h1 { color: #0051BA; }
        table { border-collapse: collapse; width: 100%; background: #fff; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background: #0051BA; color: #fff; }
        tr:nth-child(even) { background: #f2f2f2; }
        .up { color: green; font-weight: bold; }
        .down { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>IKEA Health Check Dashboard</h1>
    <p>Last updated: {{ report['timestamp'] }}</p>
    <table>
        <tr>
            <th>URL</th>
            <th>Status</th>
            <th>Last Status Code</th>
            <th>Response Time</th>
            <th>Consecutive Failures</th>
            <th>Last Check</th>
        </tr>
        {% for url, info in report['url_status_summary'].items() %}
        <tr>
            <td>{{ url }}</td>
            <td class="{{ 'up' if info['current_status']=='UP' else 'down' }}">{{ info['current_status'] }}</td>
            <td>{{ info['last_status_code'] }}</td>
            <td>{{ info['last_response_time'] }}</td>
            <td>{{ info['consecutive_failures'] }}</td>
            <td>{{ info['last_check'] }}</td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <a href="/download_excel">Download Excel Report</a>
</body>
</html>
'''

@app.route("/")
def dashboard():
    if not REPORT_FILE.exists():
        return "No report available. Run the health check monitor first."
    with open(REPORT_FILE) as f:
        report = json.load(f)
    return render_template_string(TEMPLATE, report=report)

@app.route("/download_excel")
def download_excel():
    if not REPORT_FILE.exists():
        return "No report available."
    with open(REPORT_FILE) as f:
        report = json.load(f)
    df = pd.DataFrame.from_dict(report['url_status_summary'], orient='index')
    df.to_excel(EXCEL_FILE)
    return send_file(EXCEL_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
