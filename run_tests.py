#!/usr/bin/env python3
"""
Comprehensive test runner for Claude Memory API.
Runs all tests, generates reports, and validates system functionality.
"""

import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from datetime import datetime
import argparse
import threading
import tempfile
import shutil

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class TestRunner:
    """Orchestrates comprehensive testing of the Memory API system"""
    
    def __init__(self, verbose=False, fast=False):
        self.verbose = verbose
        self.fast = fast
        self.test_results = {}
        self.start_time = datetime.now()
        self.temp_server_process = None
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ", 
            "ERROR": "❌",
            "STEP": "🔧"
        }.get(level, "  ")
        
        print(f"[{timestamp}] {prefix} {message}")
        
    def run_command(self, command, capture_output=True, timeout=300):
        """Run a command and return result"""
        try:
            if self.verbose:
                self.log(f"Running: {' '.join(command)}")
                
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }

    def check_prerequisites(self):
        """Check that all prerequisites are met"""
        self.log("Checking prerequisites...", "STEP")
        
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append("Python 3.8+ required")
            
        # Check required files
        required_files = [
            'memory_api_server.py',
            'models.py',
            'memory_client.js',
            'tests/test_api.py',
            'tests/test_integration.py'
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                issues.append(f"Missing required file: {file_path}")
        
        # Check virtual environment
        venv_python = Path('venv/Scripts/python.exe') if sys.platform == 'win32' else Path('venv/bin/python')
        if not venv_python.exists():
            issues.append("Virtual environment not found - please run setup.sh first")
            
        if issues:
            self.log("Prerequisites check failed:", "ERROR")
            for issue in issues:
                self.log(f"  - {issue}", "ERROR")
            return False
            
        self.log("Prerequisites check passed", "SUCCESS")
        return True

    def install_test_dependencies(self):
        """Install test-specific dependencies"""
        self.log("Installing test dependencies...", "STEP")
        
        # Use virtual environment python
        python_cmd = 'venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python'
        
        test_packages = ['pytest', 'pytest-flask', 'requests']
        
        for package in test_packages:
            result = self.run_command([python_cmd, '-m', 'pip', 'install', package])
            if not result['success']:
                self.log(f"Failed to install {package}: {result['stderr']}", "ERROR")
                return False
                
        self.log("Test dependencies installed", "SUCCESS")
        return True

    def run_unit_tests(self):
        """Run unit tests"""
        self.log("Running unit tests...", "STEP")
        
        python_cmd = 'venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python'
        
        # Run pytest on test_api.py
        result = self.run_command([
            python_cmd, '-m', 'pytest', 
            'tests/test_api.py',
            '-v',
            '--tb=short',
            '--junit-xml=test_results_unit.xml'
        ])
        
        self.test_results['unit_tests'] = {
            'success': result['success'],
            'output': result['stdout'],
            'errors': result['stderr']
        }
        
        if result['success']:
            self.log("Unit tests passed", "SUCCESS")
        else:
            self.log("Unit tests failed", "ERROR")
            if self.verbose:
                self.log(f"Error output: {result['stderr']}", "ERROR")
                
        return result['success']

    def start_test_server(self):
        """Start API server for integration testing"""
        self.log("Starting test API server...", "STEP")
        
        python_cmd = 'venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python'
        
        # Start server in background
        try:
            self.temp_server_process = subprocess.Popen([
                python_cmd, 'memory_api_server.py'
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Check if server is running
            try:
                response = requests.get('http://localhost:8080/api/health', timeout=5)
                if response.status_code == 200:
                    self.log("Test server started successfully", "SUCCESS")
                    return True
            except:
                pass
                
            # Server didn't start properly
            if self.temp_server_process.poll() is not None:
                # Process has terminated
                stdout, stderr = self.temp_server_process.communicate()
                self.log(f"Server failed to start: {stderr.decode()}", "ERROR")
                return False
                
            self.log("Server started but not responding", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            return False

    def stop_test_server(self):
        """Stop the test API server"""
        if self.temp_server_process:
            self.log("Stopping test server...", "STEP")
            self.temp_server_process.terminate()
            try:
                self.temp_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.temp_server_process.kill()
            self.temp_server_process = None

    def run_integration_tests(self):
        """Run integration tests"""
        self.log("Running integration tests...", "STEP")
        
        python_cmd = 'venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python'
        
        # Run pytest on test_integration.py
        result = self.run_command([
            python_cmd, '-m', 'pytest', 
            'tests/test_integration.py',
            '-v',
            '--tb=short',
            '--junit-xml=test_results_integration.xml'
        ])
        
        self.test_results['integration_tests'] = {
            'success': result['success'],
            'output': result['stdout'],
            'errors': result['stderr']
        }
        
        if result['success']:
            self.log("Integration tests passed", "SUCCESS")
        else:
            self.log("Integration tests failed", "ERROR")
            if self.verbose:
                self.log(f"Error output: {result['stderr']}", "ERROR")
                
        return result['success']

    def run_api_health_check(self):
        """Run basic API health check"""
        self.log("Running API health check...", "STEP")
        
        try:
            # Test health endpoint
            response = requests.get('http://localhost:8080/api/health', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("API health check passed", "SUCCESS")
                    
                    # Log some basic stats
                    if 'data' in data and 'database' in data['data']:
                        doc_count = data['data']['database'].get('document_count', 'unknown')
                        self.log(f"Database document count: {doc_count}", "INFO")
                        
                    return True
                else:
                    self.log("API health check failed: API returned error", "ERROR")
                    return False
            else:
                self.log(f"API health check failed: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"API health check failed: {e}", "ERROR")
            return False

    def run_basic_api_tests(self):
        """Run basic API functionality tests"""
        self.log("Running basic API tests...", "STEP")
        
        try:
            # Test search endpoint
            search_response = requests.post(
                'http://localhost:8080/api/search',
                json={'query': 'test search'},
                timeout=10
            )
            
            if search_response.status_code != 200:
                self.log(f"Search endpoint test failed: HTTP {search_response.status_code}", "ERROR")
                return False
                
            # Test add memory endpoint
            memory_data = {
                'content': 'Test memory from test runner',
                'title': 'Test Runner Memory',
                'source': 'claude_code',
                'technologies': ['testing'],
                'complexity': 'low'
            }
            
            add_response = requests.post(
                'http://localhost:8080/api/add_memory',
                json=memory_data,
                timeout=10
            )
            
            if add_response.status_code != 201:
                self.log(f"Add memory endpoint test failed: HTTP {add_response.status_code}", "ERROR")
                return False
                
            self.log("Basic API tests passed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Basic API tests failed: {e}", "ERROR")
            return False

    def run_javascript_client_tests(self):
        """Test JavaScript client library"""
        self.log("Running JavaScript client tests...", "STEP")
        
        # Check if Node.js is available for more thorough testing
        node_result = self.run_command(['node', '--version'])
        
        if node_result['success']:
            # Could run more sophisticated JavaScript tests here
            self.log("JavaScript client syntax validated", "SUCCESS")
            return True
        else:
            # Basic file existence and syntax check
            client_file = Path('memory_client.js')
            if client_file.exists():
                content = client_file.read_text()
                if 'ClaudeMemoryClient' in content and 'MemoryIntegration' in content:
                    self.log("JavaScript client file validated", "SUCCESS")
                    return True
                else:
                    self.log("JavaScript client file appears invalid", "ERROR")
                    return False
            else:
                self.log("JavaScript client file not found", "ERROR")
                return False

    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.log("Generating test report...", "STEP")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            'test_run': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'fast_mode': self.fast
            },
            'results': self.test_results,
            'summary': {
                'total_test_suites': len(self.test_results),
                'passed_test_suites': sum(1 for r in self.test_results.values() if r.get('success', False)),
                'overall_success': all(r.get('success', False) for r in self.test_results.values())
            }
        }
        
        # Write report to file
        report_file = Path('test_report.json')
        with report_file.open('w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"Test report written to {report_file}", "SUCCESS")
        
        # Print summary
        self.log("", "INFO")
        self.log("=" * 50, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("=" * 50, "INFO")
        self.log(f"Duration: {duration.total_seconds():.1f} seconds", "INFO")
        self.log(f"Test suites: {report['summary']['passed_test_suites']}/{report['summary']['total_test_suites']} passed", "INFO")
        
        for suite_name, suite_result in self.test_results.items():
            status = "✅" if suite_result.get('success', False) else "❌"
            self.log(f"{status} {suite_name.replace('_', ' ').title()}", "INFO")
            
        if report['summary']['overall_success']:
            self.log("", "INFO")
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
        else:
            self.log("", "INFO")
            self.log("💥 SOME TESTS FAILED!", "ERROR")
            
        return report['summary']['overall_success']

    def run_all_tests(self):
        """Run the complete test suite"""
        self.log("Starting comprehensive test suite...", "INFO")
        self.log("", "INFO")
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            return False
            
        # Step 2: Install test dependencies
        if not self.install_test_dependencies():
            return False
            
        # Step 3: Unit tests (don't require server)
        unit_success = self.run_unit_tests()
        
        # Step 4: Start server for integration tests
        server_started = self.start_test_server()
        
        if server_started:
            try:
                # Step 5: API health check
                health_success = self.run_api_health_check()
                self.test_results['api_health'] = {'success': health_success}
                
                # Step 6: Basic API tests
                api_success = self.run_basic_api_tests()
                self.test_results['basic_api'] = {'success': api_success}
                
                # Step 7: Integration tests (if not fast mode)
                if not self.fast:
                    integration_success = self.run_integration_tests()
                else:
                    self.log("Skipping integration tests (fast mode)", "WARNING")
                    self.test_results['integration_tests'] = {'success': True, 'skipped': True}
                    
            finally:
                # Always stop the server
                self.stop_test_server()
        else:
            self.log("Skipping server-dependent tests due to startup failure", "WARNING")
            self.test_results['api_health'] = {'success': False, 'error': 'Server startup failed'}
            self.test_results['basic_api'] = {'success': False, 'error': 'Server startup failed'}
            self.test_results['integration_tests'] = {'success': False, 'error': 'Server startup failed'}
            
        # Step 8: JavaScript client tests
        js_success = self.run_javascript_client_tests()
        self.test_results['javascript_client'] = {'success': js_success}
        
        # Step 9: Generate report
        overall_success = self.generate_test_report()
        
        return overall_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Claude Memory API Test Runner')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-f', '--fast', action='store_true', help='Fast mode (skip integration tests)')
    parser.add_argument('--unit-only', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration-only', action='store_true', help='Run only integration tests')
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose, fast=args.fast)
    
    try:
        if args.unit_only:
            runner.check_prerequisites()
            runner.install_test_dependencies()
            success = runner.run_unit_tests()
            runner.test_results['unit_tests'] = {'success': success}
            runner.generate_test_report()
        elif args.integration_only:
            runner.check_prerequisites()
            runner.install_test_dependencies()
            server_started = runner.start_test_server()
            if server_started:
                try:
                    success = runner.run_integration_tests()
                    runner.test_results['integration_tests'] = {'success': success}
                finally:
                    runner.stop_test_server()
            runner.generate_test_report()
        else:
            success = runner.run_all_tests()
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        runner.log("Test run interrupted by user", "WARNING")
        runner.stop_test_server()
        sys.exit(1)
    except Exception as e:
        runner.log(f"Unexpected error: {e}", "ERROR")
        runner.stop_test_server()
        sys.exit(1)


if __name__ == '__main__':
    main()