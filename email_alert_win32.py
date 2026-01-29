import win32com.client as win32
from pathlib import Path
import os
from email_contacts import SENDER, RECIPIENTS, CC, BCC

def send_alert_email(sender, recipients, subject, body_html, attachments=None, cc=None, bcc=None):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipients if isinstance(recipients, str) else ';'.join(recipients)
    if cc:
        mail.CC = cc if isinstance(cc, str) else ';'.join(cc)
    if bcc:
        mail.BCC = bcc if isinstance(bcc, str) else ';'.join(bcc)
    mail.Subject = subject
    mail.HTMLBody = body_html
    if attachments:
        for file in attachments:
            if Path(file).exists():
                mail.Attachments.Add(str(file))
    mail.Send()

def build_alert_html(summary_dict, summary_fallback, timestamp, duration, failure_rate, healthy, down):
    if summary_dict:
        summary_table = """
            <table class="summary-table">
                <tr><th>Metric</th><th>Value</th></tr>
        """
        for k, v in summary_dict.items():
            summary_table += f'<tr><td>{k}</td><td>{v}</td></tr>'
        summary_table += "</table>"
        summary_html = f'<h3>Monitoring Summary</h3>{summary_table}'
    else:
        # Add line numbers to each log line
        log_lines = summary_fallback.splitlines()
        numbered_log = '\n'.join([f"{i+1:02d}. {line}" for i, line in enumerate(log_lines)])
        summary_html = f'<h3>Recent System Activity (Last 20 Health Check Events)</h3><pre style="background:#f8f8f8;padding:10px;border-radius:6px;">{numbered_log}</pre>'
    attachments_desc = '''
        <div style="margin:24px 0 10px 0;">
            <b>Attached Files:</b>
            <ul style="font-size:1em;line-height:1.6;">
                <li><b>health_check_report.xlsx</b>: Excel report with detailed status and history for each monitored URL.</li>
                <li><b>index.html</b>: Interactive HTML dashboard for a visual overview of server health and trends.</li>
                <li><b>health_check.log</b>: Raw log file containing all health check events, errors, and alerts for audit/troubleshooting.</li>
            </ul>
        </div>
    '''
    return f'''
    <html>
    <head>
        <style>
            body {{ font-family: Segoe UI, Arial, sans-serif; background: #f4f6fa; }}
            .header {{ background: #0051BA; color: #fff; padding: 18px; text-align: center; }}
            .summary {{ margin: 20px auto; width: 90%; }}
            .summary-table {{ width: 100%; border-collapse: collapse; }}
            .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            .summary-table th {{ background: #0051BA; color: #fff; }}
            .ok {{ color: #388e3c; font-weight: bold; }}
            .fail {{ color: #d32f2f; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>IKEA Health Check Alert</h2>
            <div>Report generated: {timestamp} | Duration: {duration} seconds</div>
        </div>
        <div class="summary">
            <table class="summary-table">
                <tr><th>Failure Rate</th><th>Currently Healthy</th><th>Currently Down</th></tr>
                <tr><td>{failure_rate}</td><td class="ok">{healthy}</td><td class="fail">{down}</td></tr>
            </table>
        </div>
        {attachments_desc}
        <div style="margin:20px auto;width:90%;">
            {summary_html}
        </div>
        <div style="text-align:center;color:#888;font-size:0.95em;margin-top:30px;">
            IKEA Health Check Monitoring Tool &copy; 2026
        </div>
    </body>
    </html>
    '''

def send_health_check_alert():
    # Configurable details
    sender = SENDER
    recipients = RECIPIENTS
    cc = CC
    bcc = BCC
    subject = 'IKEA Health Check Alert - Automated Report'
    # Paths
    logs_dir = Path(__file__).parent / 'logs'
    excel = logs_dir / 'health_check_report.xlsx'
    html = logs_dir / 'index.html'
    log = logs_dir / 'health_check.log'
    # Parse summary from log (look for MONITORING SUMMARY block)
    summary_dict = {}
    summary_fallback = ''
    if log.exists():
        with open(log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            summary_lines = []
            in_summary = False
            for line in lines[::-1]:
                if 'MONITORING SUMMARY' in line:
                    in_summary = True
                if in_summary:
                    summary_lines.append(line)
                if in_summary and line.strip().startswith('='):
                    break
            summary_lines = summary_lines[::-1]
            for l in summary_lines:
                if ':' in l and not l.strip().startswith('='):
                    k, v = l.split(':', 1)
                    summary_dict[k.strip()] = v.strip()
            # fallback: last 20 log lines
            summary_fallback = ''.join(lines[-20:])
    # Read meta from html report
    import re
    timestamp, duration, failure_rate, healthy, down = '', '', '', '', ''
    if html.exists():
        with open(html, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            m = re.search(r'Report generated: ([^<|&]+)', content)
            if m: timestamp = m.group(1).strip()
            m = re.search(r'Monitoring duration: (\d+) seconds', content)
            if m: duration = m.group(1)
            m = re.search(r'Failure Rate</div>\s*<div class=\'card-value\'>([^<]+)</div>', content)
            if m: failure_rate = m.group(1)
            m = re.search(r'Currently Healthy</div>\s*<div class=\'card-value healthy\'>(\d+)</div>', content)
            if m: healthy = m.group(1)
            m = re.search(r'Currently Down</div>\s*<div class=\'card-value down\'>(\d+)</div>', content)
            if m: down = m.group(1)
    body_html = build_alert_html(summary_dict, summary_fallback, timestamp, duration, failure_rate, healthy, down)
    send_alert_email(sender, recipients, subject, body_html, attachments=[excel, html, log], cc=cc, bcc=bcc)

if __name__ == '__main__':
    send_health_check_alert()
