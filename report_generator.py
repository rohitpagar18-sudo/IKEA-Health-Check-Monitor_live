"""
IKEA Health Check Report Generator
===================================

Generates and displays health check reports in various formats.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

class ReportGenerator:
    """Generate health check reports"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.report_file = self.log_dir / "health_check_report.json"
        self.alert_log_file = self.log_dir / "health_check_alerts.log"
    
    def generate_html_report(self, output_file: str = None) -> str:
        """Generate an HTML report"""
        
        if not self.report_file.exists():
            return "No report data available yet."
        
        with open(self.report_file, 'r') as f:
            data = json.load(f)
        
        # Generate HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IKEA Server Health Check Report</title>
            <meta http-equiv=\"refresh\" content=\"30\">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .header {
                    background-color: #0051BA;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .summary {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }
                .card {
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .card h3 {
                    margin: 0 0 10px 0;
                    color: #0051BA;
                }
                .card .value {
                    font-size: 24px;
                    font-weight: bold;
                }
                .status-up {
                    color: #28a745;
                }
                .status-down {
                    color: #dc3545;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    margin-top: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                table thead {
                    background-color: #0051BA;
                    color: white;
                }
                table th, table td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                table tbody tr:hover {
                    background-color: #f9f9f9;
                }
                .footer {
                    margin-top: 30px;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-radius: 5px;
                    color: #666;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IKEA Server Health Check Report</h1>
                <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
            
            <div class="summary">
                <div class="card">
                    <h3>Total URLs Monitored</h3>
                    <div class="value">""" + str(data.get('monitored_urls', 0)) + """</div>
                </div>
                <div class="card">
                    <h3>Currently Healthy</h3>
                    <div class="value status-up">""" + str(sum(1 for v in data.get('url_status_summary', {}).values() if v['current_status'] == 'UP')) + """</div>
                </div>
                <div class="card">
                    <h3>Currently Down</h3>
                    <div class="value status-down">""" + str(sum(1 for v in data.get('url_status_summary', {}).values() if v['current_status'] == 'DOWN')) + """</div>
                </div>
                <div class="card">
                    <h3>Overall Failure Rate</h3>
                    <div class="value">""" + str(data.get('failure_rate', 'N/A')) + """</div>
                </div>
            </div>
            
            <h2>Detailed URL Status</h2>
            <table>
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Last Status Code</th>
                        <th>Response Time</th>
                        <th>Consecutive Failures</th>
                        <th>Last Check</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for url, status_info in data.get('url_status_summary', {}).items():
            status_class = 'status-up' if status_info['current_status'] == 'UP' else 'status-down'
            html_content += f"""
                    <tr>
                        <td>{url}</td>
                        <td><span class="{status_class}">{status_info['current_status']}</span></td>
                        <td>{status_info.get('last_status_code', 'N/A')}</td>
                        <td>{status_info.get('last_response_time', 'N/A')}</td>
                        <td>{status_info.get('consecutive_failures', 0)}</td>
                        <td>{status_info.get('last_check', 'N/A')}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
            
            <div class="footer">
                <p>This report was automatically generated by the IKEA Health Check Monitor.</p>
                <p>For more information, check the logs directory.</p>
            </div>
        </body>
        </html>
        """
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(html_content)
        
        return html_content
    
    def generate_csv_report(self, output_file: str = "health_check_report.csv") -> None:
        """Generate a CSV report"""
        
        if not self.report_file.exists():
            print("No report data available yet.")
            return
        
        with open(self.report_file, 'r') as f:
            data = json.load(f)
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['URL', 'Status', 'Last Status Code', 'Response Time', 
                         'Consecutive Failures', 'Last Check Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for url, status_info in data.get('url_status_summary', {}).items():
                writer.writerow({
                    'URL': url,
                    'Status': status_info['current_status'],
                    'Last Status Code': status_info.get('last_status_code', 'N/A'),
                    'Response Time': status_info.get('last_response_time', 'N/A'),
                    'Consecutive Failures': status_info.get('consecutive_failures', 0),
                    'Last Check Time': status_info.get('last_check', 'N/A')
                })
        
        print(f"CSV report generated: {output_file}")
    
    def print_console_report(self) -> None:
        """Print a text report to console"""
        
        if not self.report_file.exists():
            print("No report data available yet.")
            return
        
        with open(self.report_file, 'r') as f:
            data = json.load(f)
        
        print("\n" + "=" * 100)
        print("IKEA SERVER HEALTH CHECK REPORT")
        print("=" * 100)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Monitoring Duration: {data.get('monitoring_duration_seconds', 0):.0f} seconds")
        print(f"Total Checks Performed: {data.get('total_checks', 0)}")
        print(f"Total Failures: {data.get('total_failures', 0)}")
        print(f"Overall Failure Rate: {data.get('failure_rate', 'N/A')}")
        print(f"URLs Monitored: {data.get('monitored_urls', 0)}")
        print("=" * 100)
        print("\nDETAILED STATUS:\n")
        
        print(f"{'URL':<50} {'Status':<10} {'Code':<6} {'Response':<10} {'Failures':<10}")
        print("-" * 100)
        
        for url, status_info in data.get('url_status_summary', {}).items():
            status = status_info['current_status']
            status_icon = "✓" if status == "UP" else "✗"
            print(f"{url:<50} {status_icon} {status:<8} {str(status_info.get('last_status_code', 'N/A')):<6} "
                  f"{str(status_info.get('last_response_time', 'N/A')):<10} {status_info.get('consecutive_failures', 0):<10}")
        
        print("=" * 100 + "\n")


if __name__ == "__main__":
    import sys
    
    generator = ReportGenerator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "html":
            output_file = sys.argv[2] if len(sys.argv) > 2 else "health_check_report.html"
            generator.generate_html_report(output_file)
            print(f"HTML report generated: {output_file}")
        elif command == "csv":
            output_file = sys.argv[2] if len(sys.argv) > 2 else "health_check_report.csv"
            generator.generate_csv_report(output_file)
        else:
            print(f"Unknown command: {command}")
    else:
        generator.print_console_report()
