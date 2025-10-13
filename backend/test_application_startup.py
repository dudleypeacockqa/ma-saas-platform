#!/usr/bin/env python3
"""
Application Startup Validation
Tests that the application can start successfully and handle basic operations
"""

import os
import sys
import time
from datetime import datetime

# Set up test environment
os.environ['TESTING'] = 'true'

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status}: {test_name}")
    if details:
        print(f"    {details}")

def test_environment_loading():
    """Test environment configuration loading"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except Exception as e:
        return False, str(e)

def test_database_initialization():
    """Test database initialization"""
    try:
        from app.core.test_database import get_test_config
        config = get_test_config()
        return True, config['database_url']
    except Exception as e:
        return False, str(e)

def test_core_service_availability():
    """Test that all core services can be imported and instantiated"""
    services_status = {}

    # Test Financial Intelligence
    try:
        from app.services.financial_intelligence import FinancialIntelligenceEngine
        from unittest.mock import Mock
        mock_db = Mock()
        service = FinancialIntelligenceEngine(mock_db)
        services_status['financial_intelligence'] = True
    except Exception as e:
        services_status['financial_intelligence'] = str(e)

    # Test Template Engine
    try:
        from app.services.template_engine import ProfessionalTemplateEngine
        from unittest.mock import Mock
        mock_db = Mock()
        service = ProfessionalTemplateEngine(mock_db)
        services_status['template_engine'] = True
    except Exception as e:
        services_status['template_engine'] = str(e)

    # Test Storage Service
    try:
        from app.services.storage_factory import get_storage_service
        service = get_storage_service()
        services_status['storage_service'] = True
    except Exception as e:
        services_status['storage_service'] = str(e)

    return services_status

def test_external_service_availability():
    """Test external service connections"""
    external_status = {}

    # Test Claude Service
    try:
        from app.services.claude_service import ClaudeService
        service = ClaudeService()
        external_status['claude_service'] = True
    except Exception as e:
        external_status['claude_service'] = str(e)

    return external_status

def simulate_application_startup():
    """Simulate full application startup sequence"""
    startup_results = {
        'environment': False,
        'database': False,
        'services': False,
        'external': False,
        'total_time': 0
    }

    start_time = time.perf_counter()

    # Step 1: Environment loading
    env_result = test_environment_loading()
    startup_results['environment'] = env_result

    # Step 2: Database initialization
    db_result = test_database_initialization()
    startup_results['database'] = db_result[0] if isinstance(db_result, tuple) else db_result

    # Step 3: Core services
    services_result = test_core_service_availability()
    services_working = all(status is True for status in services_result.values())
    startup_results['services'] = services_working

    # Step 4: External services
    external_result = test_external_service_availability()
    external_working = all(status is True for status in external_result.values())
    startup_results['external'] = external_working

    end_time = time.perf_counter()
    startup_results['total_time'] = end_time - start_time

    return startup_results, services_result, external_result

def main():
    """Run application startup validation"""
    print("M&A Platform Application Startup Validation")
    print("=" * 50)
    print(f"Started: {datetime.now()}")

    # Run startup simulation
    startup_results, services_detail, external_detail = simulate_application_startup()

    # Report results
    print(f"\nStartup Validation Results:")
    print_test_result("Environment loading", startup_results['environment'])
    print_test_result("Database initialization", startup_results['database'])
    print_test_result("Core services loading", startup_results['services'])
    print_test_result("External services loading", startup_results['external'])

    print(f"\nDetailed Service Status:")
    for service, status in services_detail.items():
        service_ok = status is True
        details = "" if service_ok else f"Error: {status}"
        print_test_result(f"  {service}", service_ok, details)

    print(f"\nExternal Service Status:")
    for service, status in external_detail.items():
        service_ok = status is True
        details = "" if service_ok else f"Error: {status}"
        print_test_result(f"  {service}", service_ok, details)

    # Overall assessment
    total_startup_time = startup_results['total_time']
    core_components_working = startup_results['environment'] and startup_results['database'] and startup_results['services']

    print(f"\nStartup Performance:")
    print(f"  Total startup time: {total_startup_time:.3f} seconds")
    print(f"  Fast startup: {'Yes' if total_startup_time < 5.0 else 'No'}")

    print(f"\nOverall Assessment:")
    if core_components_working:
        if total_startup_time < 5.0:
            print("[SUCCESS] Application startup is fast and all core components are working")
            return 0
        else:
            print("[GOOD] Application startup works but could be optimized")
            return 0
    else:
        print("[CRITICAL] Application startup has critical issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)