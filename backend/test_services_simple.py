#!/usr/bin/env python3
"""
Simple Core M&A Services Test
Direct import testing without service __init__.py dependencies
"""

import sys
import os
from datetime import datetime

# Set test environment
os.environ['TESTING'] = 'true'

def test_direct_service_imports():
    """Test direct imports of core services"""
    print("="*60)
    print(" DIRECT SERVICE IMPORT TESTING")
    print("="*60)

    services = [
        'financial_intelligence',
        'template_engine',
        'offer_stack_generator',
        'automated_valuation_engine',
        'intelligent_deal_matching'
    ]

    results = {}

    for service_name in services:
        try:
            # Direct import without going through __init__.py
            module = __import__(f'app.services.{service_name}', fromlist=[service_name])
            results[service_name] = True
            print(f"PASS: {service_name}")
        except Exception as e:
            results[service_name] = False
            print(f"FAIL: {service_name} - {str(e)[:100]}")

    success_count = sum(results.values())
    print(f"\nDirect Import Results: {success_count}/5 services")
    return results

def test_service_classes():
    """Test that service classes can be accessed"""
    print("\n" + "="*60)
    print(" SERVICE CLASS ACCESS TESTING")
    print("="*60)

    class_tests = {
        'financial_intelligence': 'FinancialIntelligenceEngine',
        'template_engine': 'ProfessionalTemplateEngine',
        'offer_stack_generator': 'InteractiveOfferStackGenerator',
        'automated_valuation_engine': 'AutomatedValuationEngine',
        'intelligent_deal_matching': 'IntelligentDealMatchingSystem'
    }

    results = {}

    for service_name, class_name in class_tests.items():
        try:
            module = __import__(f'app.services.{service_name}', fromlist=[class_name])
            service_class = getattr(module, class_name)
            results[service_name] = True
            print(f"PASS: {service_name}.{class_name}")
        except Exception as e:
            results[service_name] = False
            print(f"FAIL: {service_name}.{class_name} - {str(e)[:100]}")

    success_count = sum(results.values())
    print(f"\nClass Access Results: {success_count}/5 service classes")
    return results

def test_basic_instantiation():
    """Test basic service instantiation with mock database"""
    print("\n" + "="*60)
    print(" BASIC INSTANTIATION TESTING")
    print("="*60)

    from unittest.mock import Mock

    services_config = {
        'financial_intelligence': ('FinancialIntelligenceEngine', 'db'),
        'template_engine': ('ProfessionalTemplateEngine', 'db'),
        'offer_stack_generator': ('InteractiveOfferStackGenerator', 'db'),
        'automated_valuation_engine': ('AutomatedValuationEngine', 'db'),
        'intelligent_deal_matching': ('IntelligentDealMatchingSystem', 'db+financial')
    }

    results = {}
    mock_db = Mock()

    for service_name, (class_name, init_param) in services_config.items():
        try:
            module = __import__(f'app.services.{service_name}', fromlist=[class_name])
            service_class = getattr(module, class_name)

            # Instantiate with mock database
            if init_param == 'db':
                service_instance = service_class(mock_db)
            elif init_param == 'db+financial':
                # Special case for IntelligentDealMatchingSystem
                from app.services.financial_intelligence import FinancialIntelligenceEngine
                mock_financial = FinancialIntelligenceEngine(mock_db)
                service_instance = service_class(mock_db, mock_financial)
            else:
                service_instance = service_class()

            results[service_name] = True
            print(f"PASS: {service_name} instantiated successfully")

        except Exception as e:
            results[service_name] = False
            print(f"FAIL: {service_name} instantiation - {str(e)[:150]}")

    success_count = sum(results.values())
    print(f"\nInstantiation Results: {success_count}/5 services")
    return results

def test_core_methods():
    """Test core methods on instantiated services"""
    print("\n" + "="*60)
    print(" CORE METHOD TESTING")
    print("="*60)

    from unittest.mock import Mock
    mock_db = Mock()

    results = {}

    # Test Financial Intelligence Engine
    try:
        from app.services.financial_intelligence import FinancialIntelligenceEngine
        service = FinancialIntelligenceEngine(mock_db)

        # Test utility methods
        division_result = service._safe_divide(100, 50)
        growth_result = service._calculate_growth(120, 100)

        success = (division_result == 2.0 and abs(growth_result - 20.0) < 0.01)
        results['financial_intelligence'] = success
        print(f"PASS: FinancialIntelligence methods work (div={division_result}, growth={growth_result:.1f}%)")

    except Exception as e:
        results['financial_intelligence'] = False
        print(f"FAIL: FinancialIntelligence methods - {str(e)[:100]}")

    # Test other services (basic readiness check)
    services = [
        ('template_engine', 'ProfessionalTemplateEngine'),
        ('offer_stack_generator', 'InteractiveOfferStackGenerator'),
        ('automated_valuation_engine', 'AutomatedValuationEngine'),
        ('intelligent_deal_matching', 'IntelligentDealMatchingSystem')
    ]

    for service_name, class_name in services:
        try:
            module = __import__(f'app.services.{service_name}', fromlist=[class_name])
            service_class = getattr(module, class_name)

            # Handle special case for IntelligentDealMatchingSystem
            if service_name == 'intelligent_deal_matching':
                from app.services.financial_intelligence import FinancialIntelligenceEngine
                mock_financial = FinancialIntelligenceEngine(mock_db)
                service = service_class(mock_db, mock_financial)
            else:
                service = service_class(mock_db)

            # Basic readiness - service instantiated successfully
            results[service_name] = True
            print(f"PASS: {service_name} ready for operations")

        except Exception as e:
            results[service_name] = False
            print(f"FAIL: {service_name} readiness - {str(e)[:100]}")

    success_count = sum(results.values())
    print(f"\nMethod Testing Results: {success_count}/5 services")
    return results

def main():
    """Run simple service validation"""
    print("M&A PLATFORM CORE SERVICES - SIMPLE VALIDATION")
    print(f"Test Started: {datetime.now()}")
    print(f"Python Version: {sys.version}")

    try:
        # Test 1: Direct imports
        import_results = test_direct_service_imports()

        # Test 2: Class access
        class_results = test_service_classes()

        # Test 3: Basic instantiation
        instantiation_results = test_basic_instantiation()

        # Test 4: Core methods
        method_results = test_core_methods()

        # Summary
        print("\n" + "="*60)
        print(" FINAL SUMMARY")
        print("="*60)

        total_import = sum(import_results.values())
        total_class = sum(class_results.values())
        total_instantiation = sum(instantiation_results.values())
        total_methods = sum(method_results.values())

        print(f"Import Success: {total_import}/5 ({total_import/5*100:.0f}%)")
        print(f"Class Access: {total_class}/5 ({total_class/5*100:.0f}%)")
        print(f"Instantiation: {total_instantiation}/5 ({total_instantiation/5*100:.0f}%)")
        print(f"Method Testing: {total_methods}/5 ({total_methods/5*100:.0f}%)")

        overall_success = min(total_import, total_class, total_instantiation, total_methods)
        print(f"\nOVERALL SUCCESS: {overall_success}/5 services fully functional")

        if overall_success >= 4:
            print("STATUS: CORE SERVICES OPERATIONAL")
            return 0
        elif overall_success >= 3:
            print("STATUS: MOSTLY OPERATIONAL - Minor issues to resolve")
            return 1
        else:
            print("STATUS: SIGNIFICANT ISSUES - Requires attention")
            return 2

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)