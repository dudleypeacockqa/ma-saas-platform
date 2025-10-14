#!/usr/bin/env python3
"""
BMAD v6 MCP Server Test Runner
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run the complete test suite."""
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🧪 Running BMAD v6 MCP Server Test Suite")
    print("=" * 50)
    
    # Test commands to run
    test_commands = [
        {
            "name": "Unit Tests",
            "command": ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "unit"],
            "description": "Running all unit tests"
        },
        {
            "name": "Integration Tests", 
            "command": ["python", "-m", "pytest", "tests/", "-v", "-m", "integration"],
            "description": "Running integration tests"
        },
        {
            "name": "Coverage Report",
            "command": ["python", "-m", "pytest", "tests/"],
            "description": "Generating coverage report"
        }
    ]
    
    results = {}
    
    for test_config in test_commands:
        print(f"\n📋 {test_config['description']}")
        print("-" * 30)
        
        try:
            result = subprocess.run(
                test_config["command"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {test_config['name']}: PASSED")
                results[test_config['name']] = "PASSED"
            else:
                print(f"❌ {test_config['name']}: FAILED")
                print(f"Error output: {result.stderr}")
                results[test_config['name']] = "FAILED"
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_config['name']}: TIMEOUT")
            results[test_config['name']] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {test_config['name']}: ERROR - {str(e)}")
            results[test_config['name']] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result == "PASSED")
    
    for test_name, result in results.items():
        status_emoji = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "TIMEOUT": "⏰",
            "ERROR": "💥"
        }.get(result, "❓")
        
        print(f"{status_emoji} {test_name}: {result}")
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print("🚨 Some tests failed. Please review and fix issues.")
        return 1

def run_specific_test(test_path):
    """Run a specific test file or test function."""
    print(f"🎯 Running specific test: {test_path}")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_path, "-v"],
            timeout=120
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
        return 1
    except Exception as e:
        print(f"💥 Error running test: {str(e)}")
        return 1

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific test
        test_path = sys.argv[1]
        return run_specific_test(test_path)
    else:
        # Run full test suite
        return run_tests()

if __name__ == "__main__":
    sys.exit(main())

