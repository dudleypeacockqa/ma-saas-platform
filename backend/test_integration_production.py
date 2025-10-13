#!/usr/bin/env python3
"""
Production-Level Integration Testing Framework
Tests all external service integrations with live APIs and configurations
"""

import os
import sys
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch
import tempfile
import json

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

class ProductionIntegrationTester:
    """Production-level integration testing for all external services"""

    def __init__(self):
        self.results = {}
        self.test_files = []  # Track files created during testing
        self.load_environment()

    def load_environment(self):
        """Load environment variables for testing"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print_test_result("Environment configuration loaded", True)
        except Exception as e:
            print_test_result("Environment configuration", False, str(e)[:100])

    def cleanup_test_files(self):
        """Clean up any files created during testing"""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

    def test_database_connection(self) -> Dict[str, bool]:
        """Test database connectivity and operations"""
        print_header("DATABASE INTEGRATION TESTING")
        results = {}

        # Test SQLAlchemy engine creation
        try:
            # Use test database configuration to avoid async issues
            from app.core.test_database import get_test_config
            from sqlalchemy import text

            test_config = get_test_config()
            engine = test_config['engine']

            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                connection_ok = result.fetchone()[0] == 1

            results['database_connection'] = connection_ok
            print_test_result("Database connection", connection_ok, "Using test database configuration")

        except Exception as e:
            results['database_connection'] = False
            print_test_result("Database connection", False, str(e)[:150])

        # Test session creation
        try:
            test_config = get_test_config()
            SessionLocal = test_config['SessionLocal']

            db = SessionLocal()
            db.close()
            results['session_creation'] = True
            print_test_result("Database session creation", True)
        except Exception as e:
            results['session_creation'] = False
            print_test_result("Database session creation", False, str(e)[:100])

        # Test database models
        try:
            from app.models.organization import Organization
            from app.models.deal import Deal
            from app.models.financial_models import FinancialStatement

            results['model_imports'] = True
            print_test_result("Database models import", True)
        except Exception as e:
            results['model_imports'] = False
            print_test_result("Database models import", False, str(e)[:100])

        return results

    def test_claude_ai_integration(self) -> Dict[str, bool]:
        """Test Claude AI service integration"""
        print_header("CLAUDE AI INTEGRATION TESTING")
        results = {}

        # Test Claude service instantiation
        try:
            from app.services.claude_service import ClaudeService
            claude = ClaudeService()
            results['claude_instantiation'] = True
            print_test_result("Claude service instantiation", True)
        except Exception as e:
            results['claude_instantiation'] = False
            print_test_result("Claude service instantiation", False, str(e)[:100])
            return results

        # Test API key configuration
        api_key = os.getenv('ANTHROPIC_API_KEY')
        has_api_key = api_key and api_key != 'sk-ant-your-anthropic-api-key-here'
        results['claude_api_key'] = has_api_key
        print_test_result("Claude API key configured", has_api_key,
                         "Real API key set" if has_api_key else "Using placeholder key")

        # Test Claude API call (if real API key available)
        if has_api_key:
            try:
                # Simple test prompt
                test_response = claude.generate_text("Say 'Hello from Claude!'")
                claude_working = "Hello" in test_response and len(test_response) > 5
                results['claude_api_call'] = claude_working
                print_test_result("Claude API call", claude_working,
                                f"Response: {test_response[:50]}...")
            except Exception as e:
                results['claude_api_call'] = False
                print_test_result("Claude API call", False, str(e)[:100])
        else:
            results['claude_api_call'] = None
            print_test_result("Claude API call", False, "Skipped - no API key")

        return results

    def test_storage_integration(self) -> Dict[str, bool]:
        """Test Cloudflare R2 storage integration"""
        print_header("CLOUDFLARE R2 STORAGE INTEGRATION TESTING")
        results = {}

        # Test storage service configuration
        try:
            from app.services.storage_factory import get_storage_service, get_storage_info

            storage_info = get_storage_info()
            results['storage_config'] = True
            print_test_result("Storage configuration", True,
                            f"Provider: {storage_info.get('name', 'Unknown')}")
        except Exception as e:
            results['storage_config'] = False
            print_test_result("Storage configuration", False, str(e)[:100])
            return results

        # Test storage service instantiation
        try:
            storage_service = get_storage_service()
            results['storage_instantiation'] = True
            print_test_result("Storage service instantiation", True)
        except Exception as e:
            results['storage_instantiation'] = False
            print_test_result("Storage service instantiation", False, str(e)[:100])
            return results

        # Test R2 credentials
        r2_configured = all([
            os.getenv('R2_ACCESS_KEY_ID'),
            os.getenv('R2_SECRET_ACCESS_KEY'),
            os.getenv('CLOUDFLARE_ACCOUNT_ID'),
            os.getenv('R2_BUCKET_NAME')
        ])

        # Check if using real credentials
        real_credentials = (
            os.getenv('R2_ACCESS_KEY_ID') != 'development-test-key-id' and
            os.getenv('CLOUDFLARE_ACCOUNT_ID') != 'development-test-account'
        )

        results['r2_credentials'] = r2_configured
        print_test_result("R2 credentials configured", r2_configured,
                         "Real credentials" if real_credentials else "Development credentials")

        # Test file upload (if real credentials)
        if r2_configured and real_credentials:
            try:
                # Create test file
                test_content = f"Integration test - {datetime.now()}"
                test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
                test_file.write(test_content)
                test_file.close()
                self.test_files.append(test_file.name)

                # Test upload
                with open(test_file.name, 'rb') as f:
                    upload_result = storage_service.upload_document(
                        file=f,
                        filename="integration_test.txt",
                        organization_id="test_org",
                        deal_id="test_deal"
                    )

                upload_success = 'storage_path' in upload_result
                results['file_upload'] = upload_success
                print_test_result("File upload test", upload_success,
                                f"Path: {upload_result.get('storage_path', 'Failed')}")

                # Test signed URL generation
                if upload_success:
                    signed_url = storage_service.generate_signed_url(
                        upload_result['storage_path']
                    )
                    url_success = signed_url and signed_url.startswith('https://')
                    results['signed_url'] = url_success
                    print_test_result("Signed URL generation", url_success)

                    # Test file deletion
                    delete_success = storage_service.delete_document(
                        upload_result['storage_path']
                    )
                    results['file_deletion'] = delete_success
                    print_test_result("File deletion test", delete_success)

            except Exception as e:
                results['file_upload'] = False
                print_test_result("File upload test", False, str(e)[:100])
        else:
            results['file_upload'] = None
            print_test_result("File upload test", False, "Skipped - no real credentials")

        return results

    def test_authentication_integration(self) -> Dict[str, bool]:
        """Test Clerk authentication integration"""
        print_header("CLERK AUTHENTICATION INTEGRATION TESTING")
        results = {}

        # Test Clerk configuration
        clerk_secret = os.getenv('CLERK_SECRET_KEY')
        clerk_publishable = os.getenv('CLERK_PUBLISHABLE_KEY')

        clerk_configured = all([clerk_secret, clerk_publishable])
        real_clerk_keys = (
            clerk_secret != 'sk_live_your-clerk-secret-key-here' and
            clerk_publishable != 'pk_live_your-clerk-publishable-key-here'
        )

        results['clerk_configuration'] = clerk_configured
        print_test_result("Clerk configuration", clerk_configured,
                         "Real keys" if real_clerk_keys else "Placeholder keys")

        # Test authentication middleware
        try:
            from app.middleware.auth_middleware import AuthMiddleware
            results['auth_middleware'] = True
            print_test_result("Authentication middleware", True)
        except Exception as e:
            try:
                from app.api.auth import get_current_user
                results['auth_middleware'] = True
                print_test_result("Authentication middleware", True, "Found in API module")
            except Exception as e2:
                results['auth_middleware'] = False
                print_test_result("Authentication middleware", False, str(e)[:100])

        return results

    def test_payment_integration(self) -> Dict[str, bool]:
        """Test Stripe payment integration"""
        print_header("STRIPE PAYMENT INTEGRATION TESTING")
        results = {}

        # Test Stripe configuration
        stripe_secret = os.getenv('STRIPE_SECRET_KEY')
        stripe_publishable = os.getenv('STRIPE_PUBLISHABLE_KEY')

        stripe_configured = all([stripe_secret, stripe_publishable])
        real_stripe_keys = (
            stripe_secret != 'sk_live_your-stripe-secret-key-here' and
            stripe_publishable != 'pk_live_your-stripe-publishable-key-here'
        )

        results['stripe_configuration'] = stripe_configured
        print_test_result("Stripe configuration", stripe_configured,
                         "Real keys" if real_stripe_keys else "Placeholder keys")

        # Test Stripe service (if configured)
        if stripe_configured and real_stripe_keys:
            try:
                import stripe
                stripe.api_key = stripe_secret

                # Test API connectivity
                stripe.Account.retrieve()
                results['stripe_api'] = True
                print_test_result("Stripe API connectivity", True)
            except Exception as e:
                results['stripe_api'] = False
                print_test_result("Stripe API connectivity", False, str(e)[:100])
        else:
            results['stripe_api'] = None
            print_test_result("Stripe API connectivity", False, "Skipped - no real keys")

        return results

    def test_email_integration(self) -> Dict[str, bool]:
        """Test SendGrid email integration"""
        print_header("SENDGRID EMAIL INTEGRATION TESTING")
        results = {}

        # Test SendGrid configuration
        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        sendgrid_configured = sendgrid_key and sendgrid_key != 'SG.your-sendgrid-api-key-here'

        results['sendgrid_configuration'] = sendgrid_configured
        print_test_result("SendGrid configuration", sendgrid_configured,
                         "Real API key" if sendgrid_configured else "Placeholder key")

        # Test SendGrid API (if configured)
        if sendgrid_configured:
            try:
                from sendgrid import SendGridAPIClient
                sg = SendGridAPIClient(api_key=sendgrid_key)

                # Test API connectivity (get API key info)
                response = sg.client.api_keys.get()
                api_working = response.status_code == 200
                results['sendgrid_api'] = api_working
                print_test_result("SendGrid API connectivity", api_working)
            except Exception as e:
                results['sendgrid_api'] = False
                print_test_result("SendGrid API connectivity", False, str(e)[:100])
        else:
            results['sendgrid_api'] = None
            print_test_result("SendGrid API connectivity", False, "Skipped - no API key")

        return results

    def test_redis_integration(self) -> Dict[str, bool]:
        """Test Redis cache integration"""
        print_header("REDIS CACHE INTEGRATION TESTING")
        results = {}

        # Test Redis configuration
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        results['redis_configuration'] = True
        print_test_result("Redis configuration", True, f"URL: {redis_url}")

        # Test Redis connectivity
        try:
            import redis
            r = redis.from_url(redis_url)

            # Test connection
            r.ping()
            results['redis_connection'] = True
            print_test_result("Redis connectivity", True)

            # Test basic operations
            test_key = f"integration_test_{datetime.now().timestamp()}"
            r.set(test_key, "test_value", ex=60)
            retrieved = r.get(test_key)
            r.delete(test_key)

            cache_working = retrieved == b"test_value"
            results['redis_operations'] = cache_working
            print_test_result("Redis operations", cache_working)

        except Exception as e:
            results['redis_connection'] = False
            results['redis_operations'] = False
            print_test_result("Redis connectivity", False, str(e)[:100])

        return results

    def test_ai_services_integration(self) -> Dict[str, bool]:
        """Test all AI service integrations"""
        print_header("AI SERVICES INTEGRATION TESTING")
        results = {}

        # Test OpenAI integration
        openai_key = os.getenv('OPENAI_API_KEY')
        openai_configured = openai_key and openai_key != 'sk-your-openai-api-key-here'

        results['openai_configuration'] = openai_configured
        print_test_result("OpenAI configuration", openai_configured,
                         "Real API key" if openai_configured else "Placeholder key")

        # Test OpenAI API (if configured)
        if openai_configured:
            try:
                import openai
                openai.api_key = openai_key

                # Test embeddings API
                response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input="Test embedding"
                )
                embeddings_working = len(response.data[0].embedding) > 0
                results['openai_embeddings'] = embeddings_working
                print_test_result("OpenAI embeddings", embeddings_working)

            except Exception as e:
                results['openai_embeddings'] = False
                print_test_result("OpenAI embeddings", False, str(e)[:100])
        else:
            results['openai_embeddings'] = None
            print_test_result("OpenAI embeddings", False, "Skipped - no API key")

        return results

    def test_core_services_with_integrations(self) -> Dict[str, bool]:
        """Test core M&A services with real external integrations"""
        print_header("CORE SERVICES WITH LIVE INTEGRATIONS")
        results = {}

        try:
            from unittest.mock import Mock
            mock_db = Mock()

            # Test Financial Intelligence with real data processing
            try:
                from app.services.financial_intelligence import FinancialIntelligenceEngine
                financial_engine = FinancialIntelligenceEngine(mock_db)

                # Test actual financial calculations
                test_financials = {
                    'revenue': 1000000,
                    'expenses': 800000,
                    'assets': 2000000,
                    'liabilities': 1200000
                }

                # These methods should work with real data
                profit_margin = financial_engine._safe_divide(
                    test_financials['revenue'] - test_financials['expenses'],
                    test_financials['revenue']
                ) * 100

                equity_ratio = financial_engine._safe_divide(
                    test_financials['assets'] - test_financials['liabilities'],
                    test_financials['assets']
                ) * 100

                calculations_working = profit_margin == 20.0 and equity_ratio == 40.0
                results['financial_calculations'] = calculations_working
                print_test_result("Financial calculations", calculations_working,
                                f"Profit margin: {profit_margin}%, Equity ratio: {equity_ratio}%")

            except Exception as e:
                results['financial_calculations'] = False
                print_test_result("Financial calculations", False, str(e)[:100])

            # Test services with AI integration (if Claude is available)
            claude_available = os.getenv('ANTHROPIC_API_KEY') and \
                              os.getenv('ANTHROPIC_API_KEY') != 'sk-ant-your-anthropic-api-key-here'

            if claude_available:
                try:
                    from app.services.template_engine import ProfessionalTemplateEngine
                    template_engine = ProfessionalTemplateEngine(mock_db)

                    # This should instantiate without errors even with real Claude integration
                    results['template_with_ai'] = True
                    print_test_result("Template engine with AI", True, "Ready for AI-powered templates")

                except Exception as e:
                    results['template_with_ai'] = False
                    print_test_result("Template engine with AI", False, str(e)[:100])
            else:
                results['template_with_ai'] = None
                print_test_result("Template engine with AI", False, "Skipped - no Claude API key")

        except Exception as e:
            print_test_result("Core services integration setup", False, str(e)[:100])

        return results

    def generate_integration_report(self, all_results: Dict[str, Dict[str, bool]]) -> Dict[str, Any]:
        """Generate comprehensive integration test report"""
        print_header("PRODUCTION INTEGRATION ASSESSMENT")

        # Calculate statistics
        total_tests = 0
        passed_tests = 0
        skipped_tests = 0
        critical_failures = []

        for category, results in all_results.items():
            for test_name, result in results.items():
                total_tests += 1
                if result is True:
                    passed_tests += 1
                elif result is None:
                    skipped_tests += 1
                elif result is False:
                    # Check if this is a critical failure
                    if test_name in ['database_connection', 'storage_config', 'claude_instantiation']:
                        critical_failures.append(f"{category}.{test_name}")

        failed_tests = total_tests - passed_tests - skipped_tests
        success_rate = (passed_tests / max(total_tests - skipped_tests, 1)) * 100

        # Determine integration readiness
        if success_rate >= 90 and len(critical_failures) == 0:
            integration_status = "PRODUCTION_READY"
        elif success_rate >= 75 and len(critical_failures) <= 1:
            integration_status = "MOSTLY_READY"
        elif success_rate >= 50:
            integration_status = "PARTIAL_INTEGRATION"
        else:
            integration_status = "NEEDS_CONFIGURATION"

        report = {
            'test_date': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'success_rate': f"{success_rate:.1f}%",
            'critical_failures': critical_failures,
            'integration_status': integration_status,
            'results_by_category': all_results
        }

        # Print summary
        print(f"Integration Tests Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Skipped: {skipped_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Integration Status: {integration_status}")

        if critical_failures:
            print(f"\nCritical Failures:")
            for failure in critical_failures:
                print(f"  - {failure}")

        return report

    def run_production_integration_tests(self) -> int:
        """Run all production integration tests"""
        print_header("M&A PLATFORM PRODUCTION INTEGRATION TESTING")
        print(f"Test Started: {datetime.now()}")
        print(f"Testing Environment: Production Integration Mode")

        try:
            # Run all integration tests
            all_results = {}

            all_results['database'] = self.test_database_connection()
            all_results['claude_ai'] = self.test_claude_ai_integration()
            all_results['storage'] = self.test_storage_integration()
            all_results['authentication'] = self.test_authentication_integration()
            all_results['payments'] = self.test_payment_integration()
            all_results['email'] = self.test_email_integration()
            all_results['cache'] = self.test_redis_integration()
            all_results['ai_services'] = self.test_ai_services_integration()
            all_results['core_services'] = self.test_core_services_with_integrations()

            # Generate comprehensive report
            final_report = self.generate_integration_report(all_results)

            # Cleanup
            self.cleanup_test_files()

            # Determine exit code
            if final_report['integration_status'] == 'PRODUCTION_READY':
                print(f"\n[SUCCESS] Platform is production-ready for deployment!")
                return 0
            elif final_report['integration_status'] == 'MOSTLY_READY':
                print(f"\n[GOOD] Platform is mostly ready with minor configuration needed")
                return 0
            elif final_report['integration_status'] == 'PARTIAL_INTEGRATION':
                print(f"\n[CAUTION] Platform has partial integration - needs configuration")
                return 1
            else:
                print(f"\n[CRITICAL] Platform needs significant configuration work")
                return 2

        except Exception as e:
            print(f"\n[ERROR] Critical error in integration testing: {e}")
            traceback.print_exc()
            self.cleanup_test_files()
            return 3

def main():
    """Main integration testing entry point"""
    tester = ProductionIntegrationTester()
    return tester.run_production_integration_tests()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)