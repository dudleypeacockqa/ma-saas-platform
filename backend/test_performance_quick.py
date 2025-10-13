#!/usr/bin/env python3
"""
Quick Performance Validation
Lightweight performance testing for resource-constrained environments
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Set up test environment
os.environ['TESTING'] = 'true'

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status}: {test_name}")
    if details:
        print(f"    {details}")

def measure_time(func, *args, **kwargs):
    """Simple time measurement"""
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    end = time.perf_counter()
    return {'result': result, 'success': success, 'time': end - start, 'error': error}

def main():
    """Quick performance validation"""
    print("M&A Platform Quick Performance Validation")
    print(f"Started: {datetime.now()}")

    total_tests = 0
    passed_tests = 0

    # Test 1: Service Import Performance
    def test_imports():
        from app.services.financial_intelligence import FinancialIntelligenceEngine
        from app.services.template_engine import ProfessionalTemplateEngine
        return True

    result = measure_time(test_imports)
    total_tests += 1
    if result['success'] and result['time'] < 2.0:
        passed_tests += 1
        print_test_result("Service imports", True, f"Time: {result['time']:.3f}s")
    else:
        print_test_result("Service imports", False, f"Time: {result['time']:.3f}s, Error: {result['error']}")

    # Test 2: Service Instantiation
    def test_instantiation():
        from app.services.financial_intelligence import FinancialIntelligenceEngine
        from unittest.mock import Mock
        mock_db = Mock()
        service = FinancialIntelligenceEngine(mock_db)
        return service

    result = measure_time(test_instantiation)
    total_tests += 1
    if result['success'] and result['time'] < 1.0:
        passed_tests += 1
        print_test_result("Service instantiation", True, f"Time: {result['time']:.3f}s")
    else:
        print_test_result("Service instantiation", False, f"Time: {result['time']:.3f}s, Error: {result['error']}")

    # Test 3: Basic Operations
    def test_operations():
        from app.services.financial_intelligence import FinancialIntelligenceEngine
        from unittest.mock import Mock
        mock_db = Mock()
        service = FinancialIntelligenceEngine(mock_db)

        # Perform calculations
        for i in range(10):
            service._safe_divide(100 + i, 10 + i)
            service._calculate_growth(120 + i, 100 + i)
        return True

    result = measure_time(test_operations)
    total_tests += 1
    if result['success'] and result['time'] < 1.0:
        passed_tests += 1
        print_test_result("Basic operations", True, f"Time: {result['time']:.3f}s")
    else:
        print_test_result("Basic operations", False, f"Time: {result['time']:.3f}s, Error: {result['error']}")

    # Test 4: Database Configuration
    def test_database():
        from app.core.test_database import get_test_config
        config = get_test_config()
        return config['engine']

    result = measure_time(test_database)
    total_tests += 1
    if result['success'] and result['time'] < 0.5:
        passed_tests += 1
        print_test_result("Database configuration", True, f"Time: {result['time']:.3f}s")
    else:
        print_test_result("Database configuration", False, f"Time: {result['time']:.3f}s, Error: {result['error']}")

    # Test 5: Storage Service
    def test_storage():
        from app.services.storage_factory import get_storage_service
        return get_storage_service()

    result = measure_time(test_storage)
    total_tests += 1
    if result['success'] and result['time'] < 1.0:
        passed_tests += 1
        print_test_result("Storage service", True, f"Time: {result['time']:.3f}s")
    else:
        print_test_result("Storage service", False, f"Time: {result['time']:.3f}s, Error: {result['error']}")

    # Results Summary
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nQuick Performance Summary:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print(f"[SUCCESS] Platform performance is acceptable for production")
        return 0
    else:
        print(f"[CAUTION] Platform performance needs optimization")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)