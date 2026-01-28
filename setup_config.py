"""
Advanced Configuration and Setup Script
========================================

This script helps configure the IKEA Health Check Monitor with advanced options.
Run it to customize monitoring parameters without manually editing config files.
"""

import os
import sys
import json
from pathlib import Path
from configparser import ConfigParser

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)

def get_input(prompt, default=None, input_type=str):
    """Get validated user input"""
    while True:
        if default:
            display_prompt = f"{prompt} [{default}]: "
        else:
            display_prompt = f"{prompt}: "
        
        user_input = input(display_prompt).strip()
        
        if not user_input and default:
            return default
        elif not user_input:
            print("  ⚠ Please enter a value")
            continue
        
        try:
            if input_type == int:
                return int(user_input)
            elif input_type == bool:
                return user_input.lower() in ['true', 'yes', 'y', '1']
            else:
                return user_input
        except ValueError:
            print(f"  ⚠ Please enter a valid {input_type.__name__}")

def configure_monitoring():
    """Configure monitoring parameters"""
    print_header("MONITORING CONFIGURATION")
    
    print("\nConfigure how often checks are performed:")
    print("  - Higher interval = less resource usage, slower alerts")
    print("  - Lower interval = more resource usage, faster alerts")
    
    check_interval = get_input(
        "Check interval in seconds (default 300)",
        default=300,
        input_type=int
    )
    
    quick_check_interval = get_input(
        "Quick check interval when server is down (default 60)",
        default=60,
        input_type=int
    )
    
    request_timeout = get_input(
        "Request timeout in seconds (default 10)",
        default=10,
        input_type=int
    )
    
    alert_threshold = get_input(
        "Consecutive failures before alert (default 2)",
        default=2,
        input_type=int
    )
    
    return {
        'check_interval': check_interval,
        'quick_check_interval': quick_check_interval,
        'request_timeout': request_timeout,
        'alert_threshold': alert_threshold
    }

def configure_email():
    """Configure email alerts"""
    print_header("EMAIL ALERTS CONFIGURATION")
    
    enable_email = get_input(
        "Enable email alerts? (yes/no)",
        default="no"
    ).lower() in ['yes', 'y', 'true']
    
    if not enable_email:
        return {'enabled': False}
    
    print("\nIMPORTANT: For Gmail users:")
    print("  1. Go to https://myaccount.google.com/apppasswords")
    print("  2. Select 'Mail' and 'Windows'")
    print("  3. Generate an app password")
    print("  4. Paste the 16-character password when prompted")
    
    smtp_server = get_input(
        "SMTP Server",
        default="smtp.gmail.com"
    )
    
    smtp_port = get_input(
        "SMTP Port",
        default=587,
        input_type=int
    )
    
    sender_email = get_input("Sender email address")
    sender_password = get_input("Sender password or app password")
    
    print("\nRecipient email addresses (comma-separated):")
    print("  Example: admin@ikea.com,ops@ikea.com,alerts@ikea.com")
    recipient_emails = get_input("Recipient email addresses")
    
    return {
        'enabled': True,
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'sender_email': sender_email,
        'sender_password': sender_password,
        'recipient_emails': recipient_emails
    }

def configure_logging():
    """Configure logging parameters"""
    print_header("LOGGING CONFIGURATION")
    
    log_directory = get_input(
        "Log directory",
        default="logs"
    )
    
    return {
        'log_directory': log_directory,
        'log_file': 'health_check.log',
        'alert_log_file': 'health_check_alerts.log',
        'report_file': 'health_check_report.json'
    }

def save_configuration(monitoring, email, logging):
    """Save configuration to config.ini"""
    config = ConfigParser()
    
    config['MONITORING'] = {
        'check_interval': str(monitoring['check_interval']),
        'quick_check_interval': str(monitoring['quick_check_interval']),
        'request_timeout': str(monitoring['request_timeout']),
        'alert_threshold': str(monitoring['alert_threshold'])
    }
    
    config['EMAIL_ALERTS'] = {
        'enabled': str(email['enabled']),
        'smtp_server': email.get('smtp_server', 'smtp.gmail.com'),
        'smtp_port': str(email.get('smtp_port', 587)),
        'sender_email': email.get('sender_email', 'your_email@gmail.com'),
        'sender_password': email.get('sender_password', 'your_app_password'),
        'recipient_emails': email.get('recipient_emails', 'admin@ikea.com')
    }
    
    config['LOGGING'] = logging
    
    config['HTTP_STATUS'] = {
        'healthy_status_codes': '200,201,202,204,301,302,304,307,308'
    }
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("\n✓ Configuration saved to config.ini")

def verify_setup():
    """Verify the installation is complete"""
    print_header("VERIFYING SETUP")
    
    checks = [
        ("Python packages", lambda: __import__('requests')),
        ("urls.txt", lambda: Path('urls.txt').exists()),
        ("config.ini", lambda: Path('config.ini').exists()),
        ("health_check_monitor.py", lambda: Path('health_check_monitor.py').exists()),
        ("report_generator.py", lambda: Path('report_generator.py').exists()),
    ]
    
    all_good = True
    for check_name, check_func in checks:
        try:
            check_func()
            print(f"  ✓ {check_name}")
        except Exception as e:
            print(f"  ✗ {check_name}: {str(e)}")
            all_good = False
    
    if all_good:
        print("\n✓ All checks passed! Your setup is ready.")
        return True
    else:
        print("\n⚠ Some checks failed. Please review the errors above.")
        return False

def show_next_steps():
    """Show next steps"""
    print_header("NEXT STEPS")
    
    print("""
1. START MONITORING:
   Option A: Run start_monitor.bat (Windows GUI)
   Option B: Run 'python health_check_monitor.py' (Terminal)

2. GENERATE REPORTS:
   python report_generator.py              (Console report)
   python report_generator.py html out.html (HTML dashboard)
   python report_generator.py csv out.csv  (CSV export)

3. SCHEDULE CONTINUOUS MONITORING:
   Use Windows Task Scheduler to run start_monitor.bat at startup

4. VIEW LOGS:
   - logs/health_check.log          (All activities)
   - logs/health_check_alerts.log   (Alerts only)
   - logs/health_check_report.json  (Status in JSON)

5. CUSTOMIZE:
   Edit config.ini to adjust monitoring parameters
   Edit urls.txt to add/remove URLs to monitor

Need help? Check README.md or QUICKSTART.md
    """)

def main():
    """Main setup wizard"""
    print_header("IKEA HEALTH CHECK MONITOR - CONFIGURATION WIZARD")
    
    print("""
This wizard will help you configure the IKEA Health Check Monitor.
It will ask you questions about monitoring preferences.

Press Ctrl+C anytime to cancel.
    """)
    
    try:
        # Configure each section
        monitoring = configure_monitoring()
        email = configure_email()
        logging = configure_logging()
        
        # Show summary
        print_header("CONFIGURATION SUMMARY")
        print("\nMonitoring Settings:")
        for key, value in monitoring.items():
            print(f"  - {key}: {value}")
        
        if email['enabled']:
            print("\nEmail Alerts:")
            print(f"  - Enabled: Yes")
            print(f"  - SMTP Server: {email['smtp_server']}:{email['smtp_port']}")
            print(f"  - From: {email['sender_email']}")
            print(f"  - To: {email['recipient_emails']}")
        else:
            print("\nEmail Alerts: Disabled")
        
        print("\nLogging:")
        for key, value in logging.items():
            print(f"  - {key}: {value}")
        
        # Confirm and save
        confirm = input("\nSave this configuration? (yes/no): ").strip().lower()
        if confirm in ['yes', 'y', 'true']:
            save_configuration(monitoring, email, logging)
            
            # Verify and show next steps
            if verify_setup():
                show_next_steps()
            else:
                print("\nPlease fix the issues above before running the monitor.")
        else:
            print("Configuration cancelled. No changes were made.")
    
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
