#!/usr/bin/env python3
"""
Performance Testing and Validation Framework
Tests platform performance, load handling, and optimization for production deployment
"""

import os
import sys
import asyncio
import time
import concurrent.futures
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch
import statistics
import json
import gc
import psutil
import traceback

# Set up test environment
os.environ['TESTING'] = 'true'

def print_header(title: str, level: int = 1):
    """Print formatted test section header"""
    if level == 1:
        print(f"\n{'='*80}")
        print(f" {title}")
        print(f"{'='*80}")
    else:
        print(f"\n{'-'*60}")
        print(f" {title}")
        print(f"{'-'*60}")

def print_test_result(test_name: str, success: bool, details: str = "", indent: int = 0):
    """Print formatted test result"""
    status = "[PASS]" if success else "[FAIL]"
    prefix = "  " * indent
    print(f"{prefix}{status}: {test_name}")
    if details:
        print(f"{prefix}    {details}")

class PerformanceTester:
    """Performance testing and optimization validation framework"""

    def __init__(self):
        self.results = {}
        self.performance_metrics = {}
        self.baseline_metrics = {}

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'disk_io_read_mb': psutil.disk_io_counters().read_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0,
                'disk_io_write_mb': psutil.disk_io_counters().write_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0
            }
        except Exception:
            return {'cpu_percent': 0, 'memory_percent': 0, 'memory_available_mb': 0, 'disk_io_read_mb': 0, 'disk_io_write_mb': 0}

    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time and resource usage"""
        gc.collect()  # Clean up before measurement

        start_metrics = self.get_system_metrics()
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.perf_counter()
        end_metrics = self.get_system_metrics()

        execution_time = end_time - start_time

        return {
            'result': result,
            'success': success,
            'error': error,
            'execution_time': execution_time,
            'start_metrics': start_metrics,
            'end_metrics': end_metrics,
            'cpu_usage_delta': end_metrics['cpu_percent'] - start_metrics['cpu_percent'],
            'memory_usage_delta': end_metrics['memory_percent'] - start_metrics['memory_percent']
        }

    def test_service_instantiation_performance(self) -> Dict[str, bool]:
        """Test performance of service instantiation"""
        print_header("SERVICE INSTANTIATION PERFORMANCE")
        results = {}

        # Test Financial Intelligence Service
        def create_financial_service():
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            mock_db = Mock()
            return FinancialIntelligenceEngine(mock_db)

        metrics = self.measure_execution_time(create_financial_service)
        results['financial_service_instantiation'] = metrics['success'] and metrics['execution_time'] < 1.0
        print_test_result("Financial Intelligence instantiation", results['financial_service_instantiation'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        # Test Template Engine Service
        def create_template_service():
            from app.services.template_engine import ProfessionalTemplateEngine
            mock_db = Mock()
            return ProfessionalTemplateEngine(mock_db)

        metrics = self.measure_execution_time(create_template_service)
        results['template_service_instantiation'] = metrics['success'] and metrics['execution_time'] < 1.0
        print_test_result("Template Engine instantiation", results['template_service_instantiation'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        # Test Offer Stack Generator
        def create_offer_service():
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            from app.services.offer_stack_generator import InteractiveOfferStackGenerator
            mock_db = Mock()
            financial_engine = FinancialIntelligenceEngine(mock_db)
            return InteractiveOfferStackGenerator(financial_engine)

        metrics = self.measure_execution_time(create_offer_service)
        results['offer_service_instantiation'] = metrics['success'] and metrics['execution_time'] < 2.0
        print_test_result("Offer Stack Generator instantiation", results['offer_service_instantiation'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        # Test Automated Valuation Engine
        def create_valuation_service():
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            from app.services.automated_valuation_engine import AutomatedValuationEngine
            mock_db = Mock()
            financial_engine = FinancialIntelligenceEngine(mock_db)
            return AutomatedValuationEngine(financial_engine)

        metrics = self.measure_execution_time(create_valuation_service)
        results['valuation_service_instantiation'] = metrics['success'] and metrics['execution_time'] < 2.0
        print_test_result("Valuation Engine instantiation", results['valuation_service_instantiation'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        # Test Deal Matching System
        def create_matching_service():
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            from app.services.intelligent_deal_matching import IntelligentDealMatchingSystem
            mock_db = Mock()
            financial_engine = FinancialIntelligenceEngine(mock_db)
            return IntelligentDealMatchingSystem(mock_db, financial_engine)

        metrics = self.measure_execution_time(create_matching_service)
        results['matching_service_instantiation'] = metrics['success'] and metrics['execution_time'] < 2.0
        print_test_result("Deal Matching System instantiation", results['matching_service_instantiation'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        return results

    def test_concurrent_service_operations(self) -> Dict[str, bool]:
        """Test concurrent service operations under load"""
        print_header("CONCURRENT SERVICE OPERATIONS")
        results = {}

        # Test concurrent financial calculations
        def financial_calculation():
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            mock_db = Mock()
            service = FinancialIntelligenceEngine(mock_db)

            # Perform multiple calculations
            results = []
            for i in range(100):
                div_result = service._safe_divide(1000 + i, 10 + i)
                growth_result = service._calculate_growth(120 + i, 100 + i)
                results.append((div_result, growth_result))
            return results

        # Test with multiple concurrent workers
        concurrent_times = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.perf_counter()
            futures = [executor.submit(financial_calculation) for _ in range(5)]
            concurrent.futures.wait(futures)
            end_time = time.perf_counter()
            concurrent_time = end_time - start_time
            concurrent_times.append(concurrent_time)

        # Test sequential execution for comparison
        start_time = time.perf_counter()
        for _ in range(5):
            financial_calculation()
        end_time = time.perf_counter()
        sequential_time = end_time - start_time

        speedup_ratio = sequential_time / concurrent_time if concurrent_time > 0 else 0
        concurrency_effective = speedup_ratio > 1.5  # Expect at least 50% improvement

        results['concurrent_financial_calculations'] = concurrency_effective
        print_test_result("Concurrent financial calculations", concurrency_effective,
                         f"Sequential: {sequential_time:.3f}s, Concurrent: {concurrent_time:.3f}s, Speedup: {speedup_ratio:.2f}x")

        return results

    def test_memory_usage_patterns(self) -> Dict[str, bool]:
        """Test memory usage and potential memory leaks"""
        print_header("MEMORY USAGE ANALYSIS")
        results = {}

        # Test service instantiation memory usage
        def memory_stress_test():
            services = []
            for i in range(100):
                from app.services.financial_intelligence import FinancialIntelligenceEngine
                mock_db = Mock()
                service = FinancialIntelligenceEngine(mock_db)
                services.append(service)

                # Perform operations
                service._safe_divide(1000, 10)
                service._calculate_growth(120, 100)

            return services

        # Measure memory before and after
        gc.collect()
        start_memory = psutil.virtual_memory().percent

        metrics = self.measure_execution_time(memory_stress_test)

        gc.collect()
        end_memory = psutil.virtual_memory().percent

        memory_increase = end_memory - start_memory
        memory_efficient = memory_increase < 5.0  # Less than 5% memory increase

        results['memory_efficiency'] = memory_efficient and metrics['success']
        print_test_result("Memory efficiency", results['memory_efficiency'],
                         f"Memory increase: {memory_increase:.2f}%, Execution: {metrics['execution_time']:.3f}s")

        # Test garbage collection effectiveness
        del metrics
        gc.collect()
        gc_memory = psutil.virtual_memory().percent
        gc_effective = (end_memory - gc_memory) > 0.1  # Some memory should be freed

        results['garbage_collection'] = gc_effective
        print_test_result("Garbage collection effectiveness", gc_effective,
                         f"Memory freed: {end_memory - gc_memory:.2f}%")

        return results

    def test_database_operations_performance(self) -> Dict[str, bool]:
        """Test database operations performance"""
        print_header("DATABASE OPERATIONS PERFORMANCE")
        results = {}

        # Test database connection performance
        def create_db_connection():
            from app.core.test_database import get_test_config
            config = get_test_config()
            return config['engine']

        metrics = self.measure_execution_time(create_db_connection)
        results['db_connection_speed'] = metrics['success'] and metrics['execution_time'] < 0.5
        print_test_result("Database connection speed", results['db_connection_speed'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        # Test session operations
        def session_operations():
            from app.core.test_database import get_test_config
            from sqlalchemy import text

            config = get_test_config()
            SessionLocal = config['SessionLocal']

            operations = []
            for i in range(50):
                db = SessionLocal()
                try:
                    # Simulate typical operations
                    result = db.execute(text("SELECT 1"))
                    operations.append(result.fetchone()[0])
                finally:
                    db.close()
            return operations

        metrics = self.measure_execution_time(session_operations)
        results['session_operations_speed'] = metrics['success'] and metrics['execution_time'] < 2.0
        print_test_result("Database session operations", results['session_operations_speed'],
                         f"Time: {metrics['execution_time']:.3f}s, Operations: 50, Success: {metrics['success']}")

        return results

    def test_import_performance(self) -> Dict[str, bool]:
        """Test module import performance"""
        print_header("MODULE IMPORT PERFORMANCE")
        results = {}

        # Test core service imports
        import_times = {}

        modules_to_test = [
            'app.services.financial_intelligence',
            'app.services.template_engine',
            'app.services.offer_stack_generator',
            'app.services.automated_valuation_engine',
            'app.services.intelligent_deal_matching'
        ]

        total_import_time = 0
        all_imports_successful = True

        for module_name in modules_to_test:
            def import_module():
                return __import__(module_name, fromlist=[module_name.split('.')[-1]])

            metrics = self.measure_execution_time(import_module)
            import_times[module_name] = metrics['execution_time']
            total_import_time += metrics['execution_time']

            if not metrics['success']:
                all_imports_successful = False

            fast_import = metrics['execution_time'] < 1.0
            print_test_result(f"Import {module_name.split('.')[-1]}", fast_import,
                             f"Time: {metrics['execution_time']:.3f}s")

        # Overall import performance
        fast_total_imports = total_import_time < 3.0  # All imports under 3 seconds
        results['import_performance'] = fast_total_imports and all_imports_successful
        print_test_result("Overall import performance", results['import_performance'],
                         f"Total time: {total_import_time:.3f}s")

        return results

    def test_storage_service_performance(self) -> Dict[str, bool]:
        """Test storage service performance"""
        print_header("STORAGE SERVICE PERFORMANCE")
        results = {}

        # Test storage service instantiation
        def create_storage_service():
            from app.services.storage_factory import get_storage_service
            return get_storage_service()

        metrics = self.measure_execution_time(create_storage_service)
        results['storage_instantiation'] = metrics['success'] and metrics['execution_time'] < 1.0
        print_test_result("Storage service instantiation", results['storage_instantiation'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        # Test storage info retrieval
        def get_storage_info():
            from app.services.storage_factory import get_storage_info
            return get_storage_info()

        metrics = self.measure_execution_time(get_storage_info)
        results['storage_info_speed'] = metrics['success'] and metrics['execution_time'] < 0.5
        print_test_result("Storage info retrieval", results['storage_info_speed'],
                         f"Time: {metrics['execution_time']:.3f}s, Success: {metrics['success']}")

        return results

    def test_application_startup_performance(self) -> Dict[str, bool]:
        """Test application startup performance simulation"""
        print_header("APPLICATION STARTUP PERFORMANCE")
        results = {}

        # Simulate full application initialization
        def simulate_app_startup():
            startup_times = {}

            # 1. Environment loading
            start_time = time.perf_counter()
            from dotenv import load_dotenv
            load_dotenv()
            startup_times['env_loading'] = time.perf_counter() - start_time

            # 2. Database initialization
            start_time = time.perf_counter()
            from app.core.test_database import get_test_config
            db_config = get_test_config()
            startup_times['db_init'] = time.perf_counter() - start_time

            # 3. Service imports
            start_time = time.perf_counter()
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            from app.services.template_engine import ProfessionalTemplateEngine
            startup_times['service_imports'] = time.perf_counter() - start_time

            # 4. Storage service
            start_time = time.perf_counter()
            from app.services.storage_factory import get_storage_service
            storage = get_storage_service()
            startup_times['storage_init'] = time.perf_counter() - start_time

            return startup_times

        metrics = self.measure_execution_time(simulate_app_startup)
        startup_times = metrics['result'] if metrics['success'] else {}

        total_startup_time = sum(startup_times.values()) if startup_times else metrics['execution_time']
        fast_startup = total_startup_time < 5.0  # Under 5 seconds total

        results['application_startup'] = metrics['success'] and fast_startup
        print_test_result("Application startup simulation", results['application_startup'],
                         f"Total time: {total_startup_time:.3f}s, Success: {metrics['success']}")

        if startup_times:
            for component, time_taken in startup_times.items():
                print_test_result(f"  {component}", time_taken < 2.0,
                                f"Time: {time_taken:.3f}s", indent=1)

        return results

    def test_error_handling_performance(self) -> Dict[str, bool]:
        """Test error handling performance under stress"""
        print_header("ERROR HANDLING PERFORMANCE")
        results = {}

        # Test error handling in financial calculations
        def error_stress_test():
            from app.services.financial_intelligence import FinancialIntelligenceEngine
            mock_db = Mock()
            service = FinancialIntelligenceEngine(mock_db)

            error_count = 0
            success_count = 0

            for i in range(1000):
                try:
                    # Mix of valid and invalid operations
                    if i % 10 == 0:
                        # Division by zero test
                        result = service._safe_divide(100, 0)
                        if result == 0.0:  # Should handle gracefully
                            success_count += 1
                    else:
                        # Normal operation
                        result = service._safe_divide(100, i % 50 + 1)
                        if result > 0:
                            success_count += 1
                except Exception:
                    error_count += 1

            return success_count, error_count

        metrics = self.measure_execution_time(error_stress_test)

        if metrics['success'] and metrics['result']:
            success_count, error_count = metrics['result']
            error_rate = error_count / (success_count + error_count) if (success_count + error_count) > 0 else 1.0
            good_error_handling = error_rate < 0.01 and metrics['execution_time'] < 2.0  # Less than 1% errors
        else:
            good_error_handling = False
            error_rate = 1.0

        results['error_handling_performance'] = good_error_handling
        print_test_result("Error handling under stress", good_error_handling,
                         f"Error rate: {error_rate*100:.2f}%, Time: {metrics['execution_time']:.3f}s")

        return results

    def generate_performance_report(self, all_results: Dict[str, Dict[str, bool]]) -> Dict[str, Any]:
        """Generate comprehensive performance assessment report"""
        print_header("PERFORMANCE ASSESSMENT SUMMARY")

        # Calculate statistics
        total_tests = 0
        passed_tests = 0
        critical_performance_areas = [
            'application_startup', 'import_performance', 'memory_efficiency',
            'concurrent_financial_calculations', 'db_connection_speed'
        ]
        performance_issues = []

        for category, results in all_results.items():
            for test_name, result in results.items():
                total_tests += 1
                if result is True:
                    passed_tests += 1
                elif result is False and test_name in critical_performance_areas:
                    performance_issues.append(f"{category}.{test_name}")

        success_rate = (passed_tests / max(total_tests, 1)) * 100

        # Determine performance status
        if success_rate >= 90 and len(performance_issues) == 0:
            performance_status = "PRODUCTION_OPTIMIZED"
        elif success_rate >= 80 and len(performance_issues) <= 1:
            performance_status = "PRODUCTION_READY"
        elif success_rate >= 70:
            performance_status = "NEEDS_OPTIMIZATION"
        else:
            performance_status = "PERFORMANCE_ISSUES"

        report = {
            'test_date': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': f"{success_rate:.1f}%",
            'performance_issues': performance_issues,
            'performance_status': performance_status,
            'results_by_category': all_results
        }

        # Print summary
        print(f"Performance Tests Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Performance Status: {performance_status}")

        if performance_issues:
            print(f"\nPerformance Issues:")
            for issue in performance_issues:
                print(f"  - {issue}")

        return report

    def run_performance_validation(self) -> int:
        """Run comprehensive performance validation"""
        print_header("M&A PLATFORM PERFORMANCE VALIDATION")
        print(f"Test Started: {datetime.now()}")
        print(f"Testing Environment: Performance Optimization Mode")

        try:
            # Collect baseline system metrics
            self.baseline_metrics = self.get_system_metrics()
            print(f"Baseline System Metrics:")
            print(f"  CPU: {self.baseline_metrics['cpu_percent']:.1f}%")
            print(f"  Memory: {self.baseline_metrics['memory_percent']:.1f}%")
            print(f"  Available Memory: {self.baseline_metrics['memory_available_mb']:.1f} MB")

            # Run all performance tests
            all_results = {}

            all_results['instantiation'] = self.test_service_instantiation_performance()
            all_results['concurrency'] = self.test_concurrent_service_operations()
            all_results['memory'] = self.test_memory_usage_patterns()
            all_results['database'] = self.test_database_operations_performance()
            all_results['imports'] = self.test_import_performance()
            all_results['storage'] = self.test_storage_service_performance()
            all_results['startup'] = self.test_application_startup_performance()
            all_results['error_handling'] = self.test_error_handling_performance()

            # Generate comprehensive report
            final_report = self.generate_performance_report(all_results)

            # Final system metrics
            final_metrics = self.get_system_metrics()
            print(f"\nFinal System Metrics:")
            print(f"  CPU: {final_metrics['cpu_percent']:.1f}%")
            print(f"  Memory: {final_metrics['memory_percent']:.1f}%")
            print(f"  Memory Delta: {final_metrics['memory_percent'] - self.baseline_metrics['memory_percent']:+.1f}%")

            # Determine exit code
            if final_report['performance_status'] == 'PRODUCTION_OPTIMIZED':
                print(f"\n[SUCCESS] Platform is production-optimized for high performance!")
                return 0
            elif final_report['performance_status'] == 'PRODUCTION_READY':
                print(f"\n[GOOD] Platform performance is production-ready")
                return 0
            elif final_report['performance_status'] == 'NEEDS_OPTIMIZATION':
                print(f"\n[CAUTION] Platform needs performance optimization")
                return 1
            else:
                print(f"\n[CRITICAL] Platform has significant performance issues")
                return 2

        except Exception as e:
            print(f"\n[ERROR] Critical error in performance testing: {e}")
            traceback.print_exc()
            return 3

def main():
    """Main performance testing entry point"""
    tester = PerformanceTester()
    return tester.run_performance_validation()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)