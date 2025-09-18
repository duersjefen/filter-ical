#!/usr/bin/env python3
"""
Contract-First CI/CD Validation Script
Validates OpenAPI specification and ensures backend compliance

Usage:
    python scripts/validate-contracts.py
    
Exit codes:
    0: All validations passed
    1: Validation failed
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {msg} ==={Colors.END}")

class ContractValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.frontend_dir = project_root / "frontend"
        self.openapi_path = self.backend_dir / "openapi.yaml"
        
    def validate_all(self) -> bool:
        """Run all contract validations"""
        print_header("Contract-First CI/CD Validation")
        
        validations = [
            ("OpenAPI Specification", self.validate_openapi_spec),
            ("Backend Contract Compliance", self.validate_backend_contracts),
            ("Frontend Type Generation", self.validate_frontend_types),
            ("Contract Test Coverage", self.validate_contract_tests),
        ]
        
        failed_validations = []
        
        for name, validation_func in validations:
            print_header(name)
            try:
                if not validation_func():
                    failed_validations.append(name)
            except Exception as e:
                print_error(f"Validation failed with exception: {e}")
                failed_validations.append(name)
        
        # Summary
        print_header("Validation Summary")
        if failed_validations:
            print_error(f"Failed validations: {', '.join(failed_validations)}")
            return False
        else:
            print_success("All contract validations passed!")
            return True
    
    def validate_openapi_spec(self) -> bool:
        """Validate OpenAPI specification syntax and structure"""
        if not self.openapi_path.exists():
            print_error(f"OpenAPI specification not found: {self.openapi_path}")
            return False
        
        try:
            # Parse YAML syntax
            with open(self.openapi_path, 'r') as f:
                spec = yaml.safe_load(f)
            
            # Basic structure validation
            required_sections = ['openapi', 'info', 'paths', 'components']
            for section in required_sections:
                if section not in spec:
                    print_error(f"Missing required OpenAPI section: {section}")
                    return False
            
            # Validate paths exist
            if not spec['paths']:
                print_error("No API paths defined in OpenAPI spec")
                return False
            
            path_count = len(spec['paths'])
            print_success(f"OpenAPI specification is valid ({path_count} endpoints)")
            
            # Check for schemas
            schemas = spec.get('components', {}).get('schemas', {})
            schema_count = len(schemas)
            print_info(f"Found {schema_count} schema definitions")
            
            return True
            
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML syntax in OpenAPI spec: {e}")
            return False
        except Exception as e:
            print_error(f"Error validating OpenAPI spec: {e}")
            return False
    
    def validate_backend_contracts(self) -> bool:
        """Validate backend contract compliance tests"""
        try:
            # Run backend contract tests using virtual environment
            venv_python = self.backend_dir / "venv" / "bin" / "python"
            if not venv_python.exists():
                # Fallback to system python3
                python_cmd = "python3"
            else:
                python_cmd = str(venv_python)
            
            result = subprocess.run(
                [python_cmd, "-m", "pytest", "tests/test_contract_compliance.py", "-v"],
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print_success("Backend contract tests passed")
                
                # Parse output for test count
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'passed' in line and 'test' in line:
                        print_info(f"Test results: {line.strip()}")
                        break
                
                return True
            else:
                print_error("Backend contract tests failed")
                if result.stdout:
                    print_error(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print_error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print_error("Backend contract tests timed out")
            return False
        except Exception as e:
            print_error(f"Error running backend contract tests: {e}")
            return False
    
    def validate_frontend_types(self) -> bool:
        """Validate frontend TypeScript types can be generated"""
        try:
            # Check if types file exists and is up to date
            types_file = self.frontend_dir / "src" / "types" / "api.ts"
            
            if not types_file.exists():
                print_warning("Frontend API types file doesn't exist, generating...")
            
            # Generate types
            result = subprocess.run(
                ["npm", "run", "types:generate"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("Frontend TypeScript types generated successfully")
                
                # Check generated file
                if types_file.exists():
                    stat = types_file.stat()
                    lines = len(types_file.read_text().splitlines())
                    print_info(f"Generated {lines} lines of TypeScript types")
                
                return True
            else:
                print_error("Failed to generate frontend types")
                if result.stdout:
                    print_error(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print_error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print_error("Frontend type generation timed out")
            return False
        except Exception as e:
            print_error(f"Error generating frontend types: {e}")
            return False
    
    def validate_contract_tests(self) -> bool:
        """Validate contract test coverage"""
        try:
            # Count OpenAPI endpoints
            with open(self.openapi_path, 'r') as f:
                spec = yaml.safe_load(f)
            
            endpoint_count = len(spec['paths'])
            
            # Check for contract test file
            contract_test_file = self.backend_dir / "tests" / "test_contract_compliance.py"
            if not contract_test_file.exists():
                print_error("Contract compliance test file not found")
                return False
            
            # Count test methods
            test_content = contract_test_file.read_text()
            test_methods = test_content.count("def test_")
            
            print_info(f"OpenAPI endpoints: {endpoint_count}")
            print_info(f"Contract test methods: {test_methods}")
            
            # We should have reasonable test coverage
            if test_methods >= 3:  # At least basic endpoint tests
                print_success("Contract test coverage is adequate")
                return True
            else:
                print_warning("Contract test coverage could be improved")
                return True  # Don't fail for this
                
        except Exception as e:
            print_error(f"Error validating contract test coverage: {e}")
            return False

def main():
    """Main entry point"""
    # Find project root
    current_dir = Path(__file__).parent.parent
    if not (current_dir / "backend" / "openapi.yaml").exists():
        print_error("Cannot find project root with OpenAPI specification")
        sys.exit(1)
    
    validator = ContractValidator(current_dir)
    
    if validator.validate_all():
        print_success("\n🎉 All contract validations passed! Ready for deployment.")
        sys.exit(0)
    else:
        print_error("\n💥 Contract validation failed! Please fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()