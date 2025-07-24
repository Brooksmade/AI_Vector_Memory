#!/usr/bin/env python3
"""
System validation script for Claude Memory API.
Performs comprehensive validation of all components and functionality.
"""

import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class SystemValidator:
    """Validates the complete Claude Memory API system"""
    
    def __init__(self):
        self.results = {}
        self.api_base_url = "http://localhost:8080"
        self.test_server_process = None
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "[INFO] ",
            "SUCCESS": "[OK]   ",
            "WARNING": "[WARN] ",
            "ERROR": "[ERR]  ",
            "TEST": "[TEST] "
        }
        icon = icons.get(level, "       ")
        try:
            print(f"[{timestamp}] {icon} {message}")
        except UnicodeEncodeError:
            # Fallback for systems with encoding issues
            print(f"[{timestamp}] {icon} {message}".encode('ascii', 'ignore').decode('ascii'))

    def validate_file_structure(self):
        """Validate that all required files exist"""
        self.log("Validating file structure...", "TEST")
        
        required_files = {
            'memory_api_server.py': 'Main Flask API server',
            'models.py': 'Data models and validation',
            'memory_client.js': 'JavaScript client library',
            'config.json': 'Configuration file',
            'requirements_api.txt': 'API dependencies',
            'start_memory_api.bat': 'Windows startup script',
            'Start-MemoryAPI.ps1': 'PowerShell startup script',
            'run_tests.py': 'Test runner',
            'tests/test_api.py': 'API unit tests',
            'tests/test_integration.py': 'Integration tests'
        }
        
        missing_files = []
        for file_path, description in required_files.items():
            if not Path(file_path).exists():
                missing_files.append(f"{file_path} ({description})")
                
        if missing_files:
            self.log(f"Missing files: {', '.join(missing_files)}", "ERROR")
            self.results['file_structure'] = False
            return False
        else:
            self.log("All required files present", "SUCCESS")
            self.results['file_structure'] = True
            return True

    def validate_dependencies(self):
        """Validate that all dependencies are available"""
        self.log("Validating dependencies...", "TEST")
        
        # Check virtual environment
        venv_python = 'venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python'
        if not Path(venv_python).exists():
            self.log("Virtual environment not found", "ERROR")
            self.results['dependencies'] = False
            return False
            
        # Check key Python packages
        try:
            result = subprocess.run([
                venv_python, '-c', 
                'import flask, flask_cors, flask_limiter, chromadb, pydantic; print("All imports successful")'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log("Python dependencies validated", "SUCCESS")
                self.results['dependencies'] = True
                return True
            else:
                self.log(f"Dependency check failed: {result.stderr}", "ERROR")
                self.results['dependencies'] = False
                return False
                
        except Exception as e:
            self.log(f"Error checking dependencies: {e}", "ERROR")
            self.results['dependencies'] = False
            return False

    def validate_configuration(self):
        """Validate configuration file"""
        self.log("Validating configuration...", "TEST")
        
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                
            # Check required sections
            required_sections = ['api', 'database', 'search', 'logging']
            missing_sections = [s for s in required_sections if s not in config]
            
            if missing_sections:
                self.log(f"Missing config sections: {missing_sections}", "ERROR")
                self.results['configuration'] = False
                return False
                
            # Validate API config
            api_config = config.get('api', {})
            if not all(key in api_config for key in ['host', 'port']):
                self.log("Invalid API configuration", "ERROR")
                self.results['configuration'] = False
                return False
                
            self.log("Configuration validated", "SUCCESS")
            self.results['configuration'] = True
            return True
            
        except Exception as e:
            self.log(f"Configuration validation failed: {e}", "ERROR")
            self.results['configuration'] = False
            return False

    def start_api_server(self):
        """Start the API server for testing"""
        self.log("Starting API server...", "TEST")
        
        venv_python = 'venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python'
        
        try:
            self.test_server_process = subprocess.Popen([
                venv_python, 'memory_api_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(3)
            
            # Check if server is responding
            try:
                response = requests.get(f'{self.api_base_url}/api/health', timeout=5)
                if response.status_code == 200:
                    self.log("API server started successfully", "SUCCESS")
                    return True
            except:
                pass
                
            # Server failed to start
            if self.test_server_process.poll() is not None:
                stdout, stderr = self.test_server_process.communicate()
                self.log(f"Server startup failed: {stderr.decode()}", "ERROR")
            else:
                self.log("Server started but not responding", "ERROR")
                
            return False
            
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            return False

    def stop_api_server(self):
        """Stop the API server"""
        if self.test_server_process:
            self.log("Stopping API server...", "TEST")
            self.test_server_process.terminate()
            try:
                self.test_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.test_server_process.kill()
            self.test_server_process = None

    def validate_api_endpoints(self):
        """Validate all API endpoints"""
        self.log("Validating API endpoints...", "TEST")
        
        endpoint_tests = [
            ('GET', '/api/health', None, 200),
            ('GET', '/api/memories', None, 200),
            ('POST', '/api/search', {'query': 'test'}, 200),
            ('POST', '/api/add_memory', {
                'content': 'Test memory for validation',
                'title': 'Validation Test',
                'source': 'claude_code'
            }, 201)
        ]
        
        passed = 0
        total = len(endpoint_tests)
        
        for method, endpoint, data, expected_status in endpoint_tests:
            try:
                url = f"{self.api_base_url}{endpoint}"
                
                if method == 'GET':
                    response = requests.get(url, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, json=data, timeout=10)
                elif method == 'DELETE':
                    response = requests.delete(url, timeout=10)
                else:
                    continue
                    
                if response.status_code == expected_status:
                    self.log(f"PASS {method} {endpoint}: {response.status_code}", "SUCCESS")
                    passed += 1
                else:
                    self.log(f"FAIL {method} {endpoint}: {response.status_code} (expected {expected_status})", "ERROR")
                    
            except Exception as e:
                self.log(f"FAIL {method} {endpoint}: {e}", "ERROR")
                
        success = passed == total
        self.log(f"API endpoints: {passed}/{total} passed", "SUCCESS" if success else "ERROR")
        self.results['api_endpoints'] = success
        return success

    def validate_memory_workflow(self):
        """Validate complete memory workflow"""
        self.log("Validating memory workflow...", "TEST")
        
        try:
            # Step 1: Add a memory
            memory_data = {
                'content': 'System validation test memory with unique content for testing workflow',
                'title': 'System Validation Test',
                'source': 'claude_code',
                'technologies': ['validation', 'testing', 'workflow'],
                'complexity': 'low'
            }
            
            add_response = requests.post(
                f'{self.api_base_url}/api/add_memory',
                json=memory_data,
                timeout=10
            )
            
            if add_response.status_code != 201:
                self.log(f"Failed to add memory: {add_response.status_code}", "ERROR")
                self.results['memory_workflow'] = False
                return False
                
            memory_id = add_response.json()['data']['id']
            self.log(f"Memory added with ID: {memory_id}", "INFO")
            
            # Step 2: Search for the memory
            search_response = requests.post(
                f'{self.api_base_url}/api/search',
                json={'query': 'system validation test'},
                timeout=10
            )
            
            if search_response.status_code != 200:
                self.log(f"Search failed: {search_response.status_code}", "ERROR")
                self.results['memory_workflow'] = False
                return False
                
            search_results = search_response.json()['data']['results']
            found = any(r['id'] == memory_id for r in search_results)
            
            if found:
                self.log("Memory found in search results", "SUCCESS")
            else:
                self.log("Memory not found in search results", "WARNING")
                
            # Step 3: List memories (should include our memory)
            list_response = requests.get(f'{self.api_base_url}/api/memories?limit=50', timeout=10)
            
            if list_response.status_code != 200:
                self.log(f"List memories failed: {list_response.status_code}", "ERROR")
                self.results['memory_workflow'] = False
                return False
                
            memories = list_response.json()['data']['memories']
            found_in_list = any(m['id'] == memory_id for m in memories)
            
            if found_in_list:
                self.log("Memory found in memory list", "SUCCESS")
            else:
                self.log("Memory not found in memory list", "WARNING")
                
            # Step 4: Delete the memory
            delete_response = requests.delete(f'{self.api_base_url}/api/memory/{memory_id}', timeout=10)
            
            if delete_response.status_code == 200:
                self.log("Memory deleted successfully", "SUCCESS")
            else:
                self.log(f"Memory deletion failed: {delete_response.status_code}", "WARNING")
                
            self.log("Memory workflow validated", "SUCCESS")
            self.results['memory_workflow'] = True
            return True
            
        except Exception as e:
            self.log(f"Memory workflow validation failed: {e}", "ERROR")
            self.results['memory_workflow'] = False
            return False

    def validate_javascript_client(self):
        """Validate JavaScript client library"""
        self.log("Validating JavaScript client...", "TEST")
        
        try:
            client_file = Path('memory_client.js')
            if not client_file.exists():
                self.log("JavaScript client file not found", "ERROR")
                self.results['javascript_client'] = False
                return False
                
            content = client_file.read_text()
            
            # Check for required classes and methods
            required_elements = [
                'class ClaudeMemoryClient',
                'class MemoryIntegration',
                'async search(',
                'async addMemory(',
                'async getHealth(',
                'async listMemories(',
                'async deleteMemory('
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
                    
            if missing_elements:
                self.log(f"Missing JS elements: {missing_elements}", "ERROR")
                self.results['javascript_client'] = False
                return False
            else:
                self.log("JavaScript client validated", "SUCCESS")
                self.results['javascript_client'] = True
                return True
                
        except Exception as e:
            self.log(f"JavaScript validation failed: {e}", "ERROR")
            self.results['javascript_client'] = False
            return False

    def validate_performance(self):
        """Validate system performance"""
        self.log("Validating performance...", "TEST")
        
        try:
            # Test response times
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                response = requests.get(f'{self.api_base_url}/api/health', timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time) * 1000
                    response_times.append(response_time)
                    
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                self.log(f"Average response time: {avg_response_time:.2f}ms", "INFO")
                self.log(f"Max response time: {max_response_time:.2f}ms", "INFO")
                
                if avg_response_time < 200:  # Under 200ms average
                    self.log("Performance validation passed", "SUCCESS")
                    self.results['performance'] = True
                    return True
                else:
                    self.log("Performance validation failed: slow response times", "WARNING")
                    self.results['performance'] = False
                    return False
            else:
                self.log("No valid response times recorded", "ERROR")
                self.results['performance'] = False
                return False
                
        except Exception as e:
            self.log(f"Performance validation failed: {e}", "ERROR")
            self.results['performance'] = False
            return False

    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        self.log("Generating validation report...", "TEST")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        
        report = {
            'validation_run': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'results': self.results,
            'overall_success': all(self.results.values())
        }
        
        # Write report to file
        report_file = Path('validation_report.json')
        with report_file.open('w') as f:
            json.dump(report, f, indent=2)
            
        # Print summary
        self.log("", "INFO")
        self.log("=" * 60, "INFO")
        self.log("SYSTEM VALIDATION SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        for test_name, result in self.results.items():
            status = "PASS" if result else "FAIL"
            level = "SUCCESS" if result else "ERROR"
            self.log(f"{status} - {test_name.replace('_', ' ').title()}", level)
            
        self.log("", "INFO")
        self.log(f"Overall Result: {passed_tests}/{total_tests} tests passed ({report['validation_run']['success_rate']:.1f}%)", "INFO")
        
        if report['overall_success']:
            self.log("SYSTEM VALIDATION SUCCESSFUL!", "SUCCESS")
            self.log("Claude Memory API is ready for use!", "SUCCESS")
        else:
            self.log("SYSTEM VALIDATION FAILED!", "ERROR")
            self.log("Please address the failed tests before using the system.", "ERROR")
            
        self.log(f"Detailed report saved to: {report_file}", "INFO")
        
        return report['overall_success']

    def run_full_validation(self):
        """Run complete system validation"""
        self.log("Starting Claude Memory API System Validation", "INFO")
        self.log("", "INFO")
        
        validation_steps = [
            ('file_structure', self.validate_file_structure),
            ('dependencies', self.validate_dependencies),
            ('configuration', self.validate_configuration)
        ]
        
        # Run initial validations
        for step_name, step_func in validation_steps:
            if not step_func():
                self.log(f"Validation failed at: {step_name}", "ERROR")
                self.generate_validation_report()
                return False
                
        # Start server for API validations
        if self.start_api_server():
            try:
                api_validation_steps = [
                    ('api_endpoints', self.validate_api_endpoints),
                    ('memory_workflow', self.validate_memory_workflow),
                    ('performance', self.validate_performance)
                ]
                
                for step_name, step_func in api_validation_steps:
                    step_func()  # Continue even if some fail
                    
            finally:
                self.stop_api_server()
        else:
            self.log("Skipping API validations due to server startup failure", "WARNING")
            self.results.update({
                'api_endpoints': False,
                'memory_workflow': False, 
                'performance': False
            })
            
        # JavaScript client validation (doesn't require server)
        self.validate_javascript_client()
        
        # Generate final report
        return self.generate_validation_report()


def main():
    """Main entry point"""
    validator = SystemValidator()
    
    try:
        success = validator.run_full_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        validator.log("Validation interrupted by user", "WARNING")
        validator.stop_api_server()
        sys.exit(1)
    except Exception as e:
        validator.log(f"Unexpected error: {e}", "ERROR")
        validator.stop_api_server()
        sys.exit(1)


if __name__ == '__main__':
    main()