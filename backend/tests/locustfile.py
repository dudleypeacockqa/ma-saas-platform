"""Load testing configuration for 1000+ concurrent users using Locust"""

from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import StatsEntry
import random
import json
import time
from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class MASystemUser(HttpUser):
    """
    Simulates real user behavior on the M&A SaaS platform.
    Represents different user personas with varying usage patterns.
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = "http://localhost:8000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.organization_id = None
        self.user_type = random.choice(["solo", "growth", "enterprise"])
        self.deal_ids = []

    def on_start(self):
        """Called when a user starts - performs login"""
        self.login()
        self.load_initial_data()

    def on_stop(self):
        """Called when a user stops"""
        self.logout()

    def login(self):
        """Authenticate user and obtain token"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": f"test_{self.user_type}_{random.randint(1, 1000)}@example.com",
                "password": "test_password_123",
                "organization_id": f"org_{self.user_type}_{random.randint(1, 100)}"
            },
            catch_response=True
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.organization_id = data.get("organization_id")
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")

    def logout(self):
        """Logout user"""
        if self.token:
            self.client.post(
                "/api/v1/auth/logout",
                headers=self.auth_headers(),
                catch_response=True
            )

    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def load_initial_data(self):
        """Load initial data for the user session"""
        # Load user's deals
        with self.client.get(
            "/api/v1/deals/list",
            params={"limit": 10},
            headers=self.auth_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.deal_ids = [deal["id"] for deal in data.get("items", [])]
                response.success()

    # ==================== TASKS ====================

    @task(30)
    def view_dashboard(self):
        """View main dashboard - most common operation"""
        with self.client.get(
            "/api/v1/dashboard/overview",
            headers=self.auth_headers(),
            name="/dashboard",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard failed: {response.status_code}")

        # Load dashboard widgets in parallel
        self.client.get(
            "/api/v1/dashboard/stats",
            headers=self.auth_headers(),
            name="/dashboard/stats"
        )
        self.client.get(
            "/api/v1/dashboard/recent-activity",
            headers=self.auth_headers(),
            name="/dashboard/activity"
        )

    @task(20)
    def search_deals(self):
        """Search for M&A deals"""
        search_queries = [
            "technology acquisition",
            "SaaS merger",
            "healthcare buyout",
            "fintech investment",
            "enterprise software"
        ]

        query = random.choice(search_queries)

        with self.client.get(
            "/api/v1/deals/search",
            params={
                "query": query,
                "limit": 20,
                "filters": json.dumps({
                    "min_value": random.randint(1, 10) * 1000000,
                    "max_value": random.randint(10, 100) * 1000000,
                    "industries": [random.choice(["tech", "healthcare", "finance"])]
                })
            },
            headers=self.auth_headers(),
            name="/deals/search",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Store some deal IDs for later use
                new_deals = [deal["id"] for deal in data.get("items", [])]
                self.deal_ids.extend(new_deals[:5])
                response.success()
            else:
                response.failure(f"Search failed: {response.status_code}")

    @task(15)
    def view_deal_details(self):
        """View detailed information about a specific deal"""
        if not self.deal_ids:
            self.search_deals()
            return

        deal_id = random.choice(self.deal_ids)

        with self.client.get(
            f"/api/v1/deals/{deal_id}",
            headers=self.auth_headers(),
            name="/deals/[id]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()

                # Load related data
                self.client.get(
                    f"/api/v1/deals/{deal_id}/documents",
                    headers=self.auth_headers(),
                    name="/deals/[id]/documents"
                )
                self.client.get(
                    f"/api/v1/deals/{deal_id}/timeline",
                    headers=self.auth_headers(),
                    name="/deals/[id]/timeline"
                )
            else:
                response.failure(f"Deal details failed: {response.status_code}")

    @task(10)
    def ai_analysis(self):
        """Request AI-powered deal analysis"""
        if not self.deal_ids:
            return

        deal_id = random.choice(self.deal_ids)

        analysis_types = ["valuation", "risks", "synergies", "market_analysis"]

        with self.client.post(
            "/api/v1/ai/analyze",
            json={
                "deal_id": deal_id,
                "analysis_type": random.choice(analysis_types),
                "context": {
                    "industry": random.choice(["technology", "healthcare", "finance"]),
                    "revenue": random.randint(1, 100) * 1000000,
                    "employees": random.randint(10, 1000)
                }
            },
            headers=self.auth_headers(),
            name="/ai/analyze",
            catch_response=True,
            timeout=5
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 202:  # Async processing
                response.success()
                # Poll for results
                self.poll_ai_results(response.json().get("task_id"))
            else:
                response.failure(f"AI analysis failed: {response.status_code}")

    def poll_ai_results(self, task_id: str):
        """Poll for async AI analysis results"""
        if not task_id:
            return

        for _ in range(5):  # Try 5 times
            time.sleep(1)
            with self.client.get(
                f"/api/v1/ai/tasks/{task_id}",
                headers=self.auth_headers(),
                name="/ai/tasks/[id]",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "completed":
                        response.success()
                        break

    @task(8)
    def upload_document(self):
        """Upload a document for a deal"""
        if not self.deal_ids:
            return

        deal_id = random.choice(self.deal_ids)

        # Simulate document upload
        with self.client.post(
            f"/api/v1/deals/{deal_id}/documents",
            files={"file": ("test.pdf", b"test document content", "application/pdf")},
            data={
                "document_type": random.choice(["financial", "legal", "technical"]),
                "confidentiality": random.choice(["public", "confidential", "highly_confidential"])
            },
            headers=self.auth_headers(),
            name="/deals/[id]/documents/upload",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Upload failed: {response.status_code}")

    @task(5)
    def generate_report(self):
        """Generate a comprehensive deal report"""
        if not self.deal_ids:
            return

        deal_id = random.choice(self.deal_ids)

        with self.client.post(
            f"/api/v1/reports/generate",
            json={
                "deal_id": deal_id,
                "report_type": random.choice(["executive_summary", "due_diligence", "valuation"]),
                "format": random.choice(["pdf", "docx", "html"])
            },
            headers=self.auth_headers(),
            name="/reports/generate",
            catch_response=True,
            timeout=10
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Report generation failed: {response.status_code}")

    @task(3)
    def ecosystem_intelligence(self):
        """Access ecosystem intelligence features"""
        with self.client.post(
            "/api/v1/intelligence/market-insights",
            json={
                "sectors": [random.choice(["tech", "healthcare", "finance"])],
                "regions": [random.choice(["US", "EU", "APAC"])],
                "timeframe": random.choice(["1M", "3M", "6M", "1Y"])
            },
            headers=self.auth_headers(),
            name="/intelligence/insights",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Intelligence failed: {response.status_code}")

    @task(2)
    def check_notifications(self):
        """Check for new notifications"""
        with self.client.get(
            "/api/v1/notifications",
            params={"unread_only": True},
            headers=self.auth_headers(),
            name="/notifications",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Notifications failed: {response.status_code}")


class EnterpriseUser(MASystemUser):
    """
    Enterprise user with heavy usage patterns.
    Represents high-value customers with complex workflows.
    """

    wait_time = between(0.5, 2)  # More aggressive usage

    @task(40)
    def bulk_operations(self):
        """Perform bulk deal operations"""
        with self.client.post(
            "/api/v1/deals/bulk",
            json={
                "operation": "export",
                "deal_ids": self.deal_ids[:20] if len(self.deal_ids) >= 20 else self.deal_ids,
                "format": "excel"
            },
            headers=self.auth_headers(),
            name="/deals/bulk",
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Bulk operation failed: {response.status_code}")

    @task(30)
    def advanced_analytics(self):
        """Access advanced analytics features"""
        with self.client.post(
            "/api/v1/analytics/portfolio",
            json={
                "metrics": ["irr", "moic", "tvpi", "dpi"],
                "grouping": random.choice(["sector", "vintage", "geography"]),
                "time_period": "all"
            },
            headers=self.auth_headers(),
            name="/analytics/portfolio",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Analytics failed: {response.status_code}")


class APIIntegrationUser(HttpUser):
    """
    Simulates external API integration traffic.
    Represents partners and third-party integrations.
    """

    wait_time = between(2, 5)
    host = "http://localhost:8000"

    def on_start(self):
        """Get API key for authentication"""
        self.api_key = f"api_key_{random.randint(1, 100)}"

    @task(50)
    def api_data_sync(self):
        """Sync data via API"""
        with self.client.post(
            "/api/v1/integration/sync",
            json={
                "sync_type": random.choice(["deals", "contacts", "documents"]),
                "since": "2024-01-01T00:00:00Z",
                "limit": 100
            },
            headers={"X-API-Key": self.api_key},
            name="/api/sync",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API sync failed: {response.status_code}")

    @task(30)
    def webhook_delivery(self):
        """Simulate webhook event delivery"""
        events = ["deal.created", "deal.updated", "document.uploaded", "analysis.completed"]

        with self.client.post(
            "/api/v1/webhooks/test",
            json={
                "event": random.choice(events),
                "data": {
                    "id": f"test_{random.randint(1, 1000)}",
                    "timestamp": time.time()
                }
            },
            headers={"X-API-Key": self.api_key},
            name="/webhooks",
            catch_response=True
        ) as response:
            if response.status_code in [200, 204]:
                response.success()
            else:
                response.failure(f"Webhook failed: {response.status_code}")

    @task(20)
    def api_health_check(self):
        """Check API health status"""
        with self.client.get(
            "/api/v1/health",
            name="/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


# Custom event handlers for detailed reporting
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, **kwargs):
    """Log detailed request metrics"""
    if response_time > 1000:  # Log slow requests over 1 second
        logger.warning(
            "Slow request detected",
            request_type=request_type,
            name=name,
            response_time=response_time,
            status_code=response.status_code if response else None
        )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate performance report at test end"""
    stats = environment.stats

    print("\n" + "="*60)
    print("LOAD TEST PERFORMANCE REPORT")
    print("="*60)

    print(f"\nTest Duration: {stats.total.total_time}s")
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Failed Requests: {stats.total.num_failures}")
    print(f"Failure Rate: {stats.total.fail_ratio:.2%}")

    print(f"\nResponse Times:")
    print(f"  Median: {stats.total.median_response_time}ms")
    print(f"  Average: {stats.total.avg_response_time:.2f}ms")
    print(f"  Min: {stats.total.min_response_time}ms")
    print(f"  Max: {stats.total.max_response_time}ms")
    print(f"  P95: {stats.total.get_response_time_percentile(0.95)}ms")
    print(f"  P99: {stats.total.get_response_time_percentile(0.99)}ms")

    print(f"\nRequests per Second:")
    print(f"  Current: {stats.total.current_rps:.2f}")
    print(f"  Average: {stats.total.total_rps:.2f}")

    print("\nTop 5 Slowest Endpoints:")
    entries = sorted(
        [e for e in stats.entries.values() if e.num_requests > 0],
        key=lambda e: e.avg_response_time,
        reverse=True
    )[:5]

    for entry in entries:
        print(f"  {entry.name}: {entry.avg_response_time:.2f}ms (P95: {entry.get_response_time_percentile(0.95)}ms)")

    print("\n" + "="*60)


# Configuration for different test scenarios
class LoadTestScenarios:
    """Pre-configured load test scenarios"""

    @staticmethod
    def normal_load():
        """Normal daily load - 100-200 concurrent users"""
        return {
            "users": 150,
            "spawn_rate": 5,
            "run_time": "5m",
            "user_classes": [MASystemUser]
        }

    @staticmethod
    def peak_load():
        """Peak load during business hours - 500-750 concurrent users"""
        return {
            "users": 600,
            "spawn_rate": 20,
            "run_time": "10m",
            "user_classes": [MASystemUser, EnterpriseUser]
        }

    @staticmethod
    def stress_test():
        """Stress test - 1000+ concurrent users"""
        return {
            "users": 1200,
            "spawn_rate": 50,
            "run_time": "15m",
            "user_classes": [MASystemUser, EnterpriseUser, APIIntegrationUser]
        }

    @staticmethod
    def spike_test():
        """Sudden spike in traffic"""
        return {
            "users": 1000,
            "spawn_rate": 100,  # Rapid user increase
            "run_time": "5m",
            "user_classes": [MASystemUser]
        }

    @staticmethod
    def endurance_test():
        """Long-running test for memory leaks and degradation"""
        return {
            "users": 300,
            "spawn_rate": 10,
            "run_time": "1h",
            "user_classes": [MASystemUser, EnterpriseUser]
        }


# Command to run tests:
# Normal load: locust -f locustfile.py --users 150 --spawn-rate 5 --run-time 5m
# Peak load: locust -f locustfile.py --users 600 --spawn-rate 20 --run-time 10m
# Stress test: locust -f locustfile.py --users 1200 --spawn-rate 50 --run-time 15m
# Web UI: locust -f locustfile.py --host http://localhost:8000 --web-host 0.0.0.0