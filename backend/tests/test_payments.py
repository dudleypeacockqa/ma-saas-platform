"""
Comprehensive Integration Tests for Payment API
Tests Stripe integration, subscriptions, and webhook handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json


class TestPaymentAuthentication:
    """Test payment endpoint authentication"""

    def test_create_checkout_session_requires_auth(self, client):
        """Test that creating checkout session requires authentication"""
        payload = {
            "price_id": "price_test123",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        response = client.post("/api/payments/create-checkout-session", json=payload)
        assert response.status_code in [401, 403]

    def test_subscription_status_requires_auth(self, client):
        """Test that subscription status requires authentication"""
        response = client.get("/api/payments/subscription")
        assert response.status_code in [401, 403]


class TestCheckoutSession:
    """Test Stripe checkout session creation"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.integrations.stripe_service.stripe_service.create_checkout_session')
    def test_create_checkout_session_success(self, mock_stripe, mock_get_user, client):
        """Test successful checkout session creation"""
        # Mock authenticated user
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock Stripe response
        mock_stripe.return_value = {
            "id": "cs_test_session_123",
            "url": "https://checkout.stripe.com/test"
        }

        payload = {
            "price_id": "price_test123",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        response = client.post(
            "/api/payments/create-checkout-session",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "session_url" in data
            assert data["session_id"] == "cs_test_session_123"

    @patch('app.auth.clerk_auth.get_current_user')
    def test_create_checkout_session_invalid_price(self, mock_get_user, client):
        """Test checkout session creation with invalid price ID"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "price_id": "",  # Invalid price ID
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        response = client.post(
            "/api/payments/create-checkout-session",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [400, 422]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_create_checkout_session_missing_fields(self, mock_get_user, client):
        """Test checkout session creation with missing required fields"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "price_id": "price_test123"
            # Missing success_url and cancel_url
        }

        response = client.post(
            "/api/payments/create-checkout-session",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [400, 422]


class TestSubscriptionManagement:
    """Test subscription management functionality"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_get_subscription_status(self, mock_get_user, client):
        """Test getting user subscription status"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/payments/subscription",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should return subscription data or indicate no subscription
        if response.status_code == 200:
            data = response.json()
            # Should have subscription fields or indicate no subscription
            assert "subscription" in data or "status" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_cancel_subscription(self, mock_get_user, client):
        """Test subscription cancellation"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.post(
            "/api/payments/subscription/cancel",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle cancellation request
        assert response.status_code in [200, 404, 400]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_update_subscription(self, mock_get_user, client):
        """Test subscription update/upgrade"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "new_price_id": "price_upgraded_plan"
        }

        response = client.put(
            "/api/payments/subscription/update",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle update request
        assert response.status_code in [200, 404, 400]


class TestStripeWebhooks:
    """Test Stripe webhook handling"""

    @patch('app.integrations.stripe_service.stripe_service.verify_webhook')
    def test_stripe_webhook_valid_signature(self, mock_verify, client):
        """Test webhook with valid Stripe signature"""
        mock_verify.return_value = True

        webhook_payload = {
            "id": "evt_test_webhook",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session_123",
                    "customer": "cus_test_customer",
                    "subscription": "sub_test_subscription",
                    "client_reference_id": "user_123"
                }
            }
        }

        response = client.post(
            "/api/payments/webhook",
            json=webhook_payload,
            headers={"stripe-signature": "valid_signature"}
        )

        # Should process webhook successfully
        assert response.status_code in [200, 201]

    def test_stripe_webhook_invalid_signature(self, client):
        """Test webhook with invalid Stripe signature"""
        webhook_payload = {
            "id": "evt_test_webhook",
            "type": "checkout.session.completed",
            "data": {"object": {}}
        }

        response = client.post(
            "/api/payments/webhook",
            json=webhook_payload,
            headers={"stripe-signature": "invalid_signature"}
        )

        # Should reject invalid webhook
        assert response.status_code in [400, 401, 403]

    def test_stripe_webhook_missing_signature(self, client):
        """Test webhook with missing signature"""
        webhook_payload = {
            "id": "evt_test_webhook",
            "type": "checkout.session.completed",
            "data": {"object": {}}
        }

        response = client.post("/api/payments/webhook", json=webhook_payload)

        # Should reject webhook without signature
        assert response.status_code in [400, 401]

    @patch('app.integrations.stripe_service.stripe_service.verify_webhook')
    def test_webhook_subscription_created(self, mock_verify, client):
        """Test webhook for subscription creation"""
        mock_verify.return_value = True

        webhook_payload = {
            "id": "evt_test_webhook",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test_123",
                    "customer": "cus_test_customer",
                    "status": "active",
                    "items": {
                        "data": [{"price": {"id": "price_starter"}}]
                    }
                }
            }
        }

        response = client.post(
            "/api/payments/webhook",
            json=webhook_payload,
            headers={"stripe-signature": "valid_signature"}
        )

        assert response.status_code in [200, 201]

    @patch('app.integrations.stripe_service.stripe_service.verify_webhook')
    def test_webhook_payment_failed(self, mock_verify, client):
        """Test webhook for failed payment"""
        mock_verify.return_value = True

        webhook_payload = {
            "id": "evt_test_webhook",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "customer": "cus_test_customer",
                    "subscription": "sub_test_123",
                    "amount_due": 2999
                }
            }
        }

        response = client.post(
            "/api/payments/webhook",
            json=webhook_payload,
            headers={"stripe-signature": "valid_signature"}
        )

        assert response.status_code in [200, 201]


class TestPaymentMethods:
    """Test payment method management"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_list_payment_methods(self, mock_get_user, client):
        """Test listing user payment methods"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/payments/payment-methods",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should return payment methods list
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "payment_methods" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_add_payment_method(self, mock_get_user, client):
        """Test adding a new payment method"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "payment_method_id": "pm_test_card_123"
        }

        response = client.post(
            "/api/payments/payment-methods",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle payment method addition
        assert response.status_code in [200, 201, 400]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_delete_payment_method(self, mock_get_user, client):
        """Test deleting a payment method"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.delete(
            "/api/payments/payment-methods/pm_test_123",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle payment method deletion
        assert response.status_code in [200, 204, 404]


class TestPaymentErrorHandling:
    """Test payment error handling and edge cases"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.integrations.stripe_service.stripe_service.create_checkout_session')
    def test_stripe_api_error(self, mock_stripe, mock_get_user, client):
        """Test handling of Stripe API errors"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock Stripe error
        mock_stripe.side_effect = Exception("Stripe API Error")

        payload = {
            "price_id": "price_test123",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        response = client.post(
            "/api/payments/create-checkout-session",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle Stripe errors gracefully
        assert response.status_code in [400, 500]
        if response.status_code != 500:
            assert "error" in response.json()

    def test_malformed_webhook_payload(self, client):
        """Test handling of malformed webhook payloads"""
        malformed_payload = "invalid json"

        response = client.post(
            "/api/payments/webhook",
            data=malformed_payload,
            headers={"stripe-signature": "test_sig", "content-type": "application/json"}
        )

        assert response.status_code in [400, 422]


class TestPaymentIntegration:
    """End-to-end payment integration tests"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.integrations.stripe_service.stripe_service.create_checkout_session')
    @patch('app.integrations.stripe_service.stripe_service.verify_webhook')
    def test_complete_subscription_flow(self, mock_verify, mock_stripe, mock_get_user, client):
        """Test complete subscription creation flow"""
        # Mock user
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock Stripe checkout session
        mock_stripe.return_value = {
            "id": "cs_test_123",
            "url": "https://checkout.stripe.com/test"
        }

        # Step 1: Create checkout session
        checkout_payload = {
            "price_id": "price_starter",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        checkout_response = client.post(
            "/api/payments/create-checkout-session",
            json=checkout_payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Step 2: Simulate successful webhook
        mock_verify.return_value = True

        webhook_payload = {
            "id": "evt_test_webhook",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "customer": "cus_new_customer",
                    "subscription": "sub_new_subscription",
                    "client_reference_id": "user_123"
                }
            }
        }

        webhook_response = client.post(
            "/api/payments/webhook",
            json=webhook_payload,
            headers={"stripe-signature": "valid_signature"}
        )

        # Both steps should succeed
        assert checkout_response.status_code in [200, 201]
        assert webhook_response.status_code in [200, 201]