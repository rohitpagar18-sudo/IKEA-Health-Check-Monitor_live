"""
Health Check Monitor - Testing and Diagnostics Script
======================================================

This script helps test and diagnose the health check monitor.
It can verify connectivity, test individual URLs, and simulate scenarios.
"""

import requests
import time
import sys
from datetime import datetime
from pathlib import Path

class HealthCheckTester:
    """Test and diagnose the health check system"""
    
    def __init__(self):
        self.urls = self._load_urls()
        self.results = []
    
    def _load_urls(self):
        """Load URLs from file"""
        try:
            with open('urls.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("ERROR: urls.txt not found!")
            return []
    
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * 100)
        print(title.center(100))
        print("=" * 100)
    
    def test_connectivity(self):
        """Test basic connectivity to each URL"""
        self.print_header("CONNECTIVITY TEST")
        
        print(f"\nTesting {len(self.urls)} URLs...\n")
        print(f"{'#':<3} {'URL':<50} {'Status':<20} {'Response Time':<15}")
        print("-" * 100)
        
        healthy_count = 0
        failed_count = 0
        
        for i, url in enumerate(self.urls, 1):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, allow_redirects=True)
                response_time = time.time() - start_time
                
                status = response.status_code
                is_healthy = status in [200, 201, 202, 204, 301, 302, 304, 307, 308]
                
                status_text = f"✓ OK ({status})" if is_healthy else f"✗ ERROR ({status})"
                if is_healthy:
                    healthy_count += 1
                else:
                    failed_count += 1
                
                print(f"{i:<3} {url:<50} {status_text:<20} {response_time:.3f}s")
                
                self.results.append({
                    'url': url,
                    'status': status,
                    'healthy': is_healthy,
                    'response_time': response_time
                })
            
            except requests.exceptions.Timeout:
                print(f"{i:<3} {url:<50} {'✗ TIMEOUT':<20}")
                failed_count += 1
                self.results.append({
                    'url': url,
                    'status': 0,
                    'healthy': False,
                    'response_time': 10.0
                })
            
            except requests.exceptions.ConnectionError:
                print(f"{i:<3} {url:<50} {'✗ CONNECTION ERROR':<20}")
                failed_count += 1
                self.results.append({
                    'url': url,
                    'status': 0,
                    'healthy': False,
                    'response_time': 0
                })
            
            except Exception as e:
                print(f"{i:<3} {url:<50} {'✗ ERROR':<20} {str(e)[:15]}")
                failed_count += 1
                self.results.append({
                    'url': url,
                    'status': 0,
                    'healthy': False,
                    'response_time': 0
                })
        
        print("-" * 100)
        print(f"\nSummary: {healthy_count} healthy, {failed_count} failed out of {len(self.urls)} URLs")
        
        return healthy_count, failed_count
    
    def test_response_times(self):
        """Analyze response times"""
        self.print_header("RESPONSE TIME ANALYSIS")
        
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        
        if not response_times:
            print("No response times recorded.")
            return
        
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\nResponse Time Statistics:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Fastest: {min_time:.3f}s")
        print(f"  Slowest: {max_time:.3f}s")
        
        # Find slowest URLs
        print(f"\nTop 5 Slowest URLs:")
        slow_urls = sorted(self.results, key=lambda x: x['response_time'], reverse=True)[:5]
        for i, result in enumerate(slow_urls, 1):
            print(f"  {i}. {result['url']}: {result['response_time']:.3f}s")
    
    def test_dependencies(self):
        """Test if all dependencies are installed"""
        self.print_header("DEPENDENCY CHECK")
        
        dependencies = {
            'requests': 'HTTP requests library',
            'urllib3': 'HTTP client for requests',
            'json': 'JSON processing (built-in)',
            'csv': 'CSV processing (built-in)',
            'logging': 'Logging (built-in)',
            'pathlib': 'Path utilities (built-in)',
            'configparser': 'Config file handling (built-in)',
        }
        
        all_good = True
        for module_name, description in dependencies.items():
            try:
                __import__(module_name)
                print(f"✓ {module_name:<15} - {description}")
            except ImportError:
                print(f"✗ {module_name:<15} - {description} [MISSING]")
                all_good = False
        
        if not all_good:
            print("\n⚠ Missing dependencies detected!")
            print("Run: pip install -r requirements.txt")
        
        return all_good
    
    def test_file_structure(self):
        """Test if all required files exist"""
        self.print_header("FILE STRUCTURE CHECK")
        
        required_files = {
            'health_check_monitor.py': 'Main monitoring script',
            'report_generator.py': 'Report generation tool',
            'setup_config.py': 'Configuration wizard',
            'urls.txt': 'List of URLs to monitor',
            'config.ini': 'Configuration file',
            'requirements.txt': 'Python dependencies',
            'README.md': 'Documentation',
            'QUICKSTART.md': 'Quick start guide',
            'start_monitor.bat': 'Windows startup script',
        }
        
        all_exist = True
        for filename, description in required_files.items():
            exists = Path(filename).exists()
            status = "✓" if exists else "✗"
            print(f"{status} {filename:<30} - {description}")
            if not exists:
                all_exist = False
        
        # Check logs directory
        logs_dir = Path('logs')
        if logs_dir.exists():
            print(f"✓ logs/                        - Logs directory (exists)")
        
        return all_exist
    
    def test_configuration(self):
        """Test if configuration is valid"""
        self.print_header("CONFIGURATION CHECK")
        
        if not Path('config.ini').exists():
            print("⚠ config.ini not found. Use setup_config.py to create it.")
            return False
        
        try:
            from configparser import ConfigParser
            config = ConfigParser()
            config.read('config.ini')
            
            print("✓ config.ini is valid\n")
            
            print("Configuration values:")
            for section in config.sections():
                print(f"\n[{section}]")
                for key, value in config.items(section):
                    if 'password' in key.lower():
                        display_value = '*' * len(value)
                    else:
                        display_value = value
                    print(f"  {key}: {display_value}")
            
            return True
        except Exception as e:
            print(f"✗ Error reading config.ini: {str(e)}")
            return False
    
    def diagnose_url(self, url):
        """Detailed diagnosis of a specific URL"""
        self.print_header(f"DETAILED DIAGNOSIS: {url}")
        
        print(f"\nTesting {url}...\n")
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10, allow_redirects=True)
            response_time = time.time() - start_time
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.3f}s")
            print(f"Content Length: {len(response.content)} bytes")
            print(f"URL: {response.url}")
            print(f"\nHeaders:")
            for key, value in response.headers.items():
                if key.lower() not in ['set-cookie', 'authorization']:
                    print(f"  {key}: {value}")
            
            # Check for redirects
            if response.history:
                print(f"\nRedirects ({len(response.history)}):")
                for i, redirect in enumerate(response.history, 1):
                    print(f"  {i}. {redirect.status_code} -> {redirect.url}")
            
            print(f"\n✓ URL is accessible")
            return True
        
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("IKEA HEALTH CHECK MONITOR - DIAGNOSTIC TESTS")
        
        print("\nRunning comprehensive diagnostics...\n")
        
        # Run tests
        print("\n1. Checking file structure...")
        files_ok = self.test_file_structure()
        
        print("\n2. Checking dependencies...")
        deps_ok = self.test_dependencies()
        
        print("\n3. Checking configuration...")
        config_ok = self.test_configuration()
        
        if len(self.urls) > 0:
            print("\n4. Testing URL connectivity...")
            healthy, failed = self.test_connectivity()
            
            print("\n5. Analyzing response times...")
            self.test_response_times()
        
        # Summary
        self.print_header("DIAGNOSTIC SUMMARY")
        print(f"\nAll systems operational: {'Yes ✓' if all([files_ok, deps_ok, config_ok]) else 'No ✗'}")
        
        if not files_ok:
            print("  ⚠ Some files are missing. Please check the file structure.")
        if not deps_ok:
            print("  ⚠ Some dependencies are missing. Run: pip install -r requirements.txt")
        if not config_ok:
            print("  ⚠ Configuration has issues. Run: python setup_config.py")
        
        print("\nReady to start monitoring: " + ("Yes ✓" if all([files_ok, deps_ok, config_ok]) else "No ✗"))

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        tester = HealthCheckTester()
        
        if command == "all":
            tester.run_all_tests()
        elif command == "connectivity":
            tester.test_connectivity()
            tester.test_response_times()
        elif command == "dependencies":
            tester.test_dependencies()
        elif command == "files":
            tester.test_file_structure()
        elif command == "config":
            tester.test_configuration()
        elif command == "url" and len(sys.argv) > 2:
            tester.diagnose_url(sys.argv[2])
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python test_monitor.py all              - Run all tests")
            print("  python test_monitor.py connectivity     - Test URL connectivity")
            print("  python test_monitor.py dependencies     - Check Python packages")
            print("  python test_monitor.py files            - Verify file structure")
            print("  python test_monitor.py config           - Check configuration")
            print("  python test_monitor.py url <url>        - Diagnose specific URL")
    else:
        tester = HealthCheckTester()
        tester.run_all_tests()

if __name__ == "__main__":
    main()
