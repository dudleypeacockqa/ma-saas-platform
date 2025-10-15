"""Tests for StripeService event pricing and checkout helpers."""

from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.services.stripe_service import StripeService

EXPECTED_KEYS = {
    'premium_masterclass',
    'executive_workshop',
    'vip_deal_summit',
}


def test_event_pricing_contains_expected_events():
    service = StripeService()
    pricing = service.get_event_pricing()
    assert set(pricing.keys()) == EXPECTED_KEYS


@pytest.mark.asyncio
async def test_create_event_checkout_session_monkeypatched(monkeypatch):
    service = StripeService()
    captured = {}

    settings.FRONTEND_URL = 'https://example.com'
    settings.ENVIRONMENT = 'test'

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id='sess_test', url='https://stripe.test/session')

    monkeypatch.setattr('app.services.stripe_service.stripe.checkout.Session.create', fake_create)

    result = await service.create_event_checkout_session('Premium Masterclass', 'customer@example.com')

    assert result['session_id'] == 'sess_test'
    assert result['url'] == 'https://stripe.test/session'
    assert captured['line_items'][0]['price_data']['unit_amount'] == service.event_pricing['premium_masterclass']['price']
    assert captured['metadata']['payment_type'] == 'one_time_event'


@pytest.mark.asyncio
async def test_create_event_checkout_session_rejects_unknown_event():
    service = StripeService()
    settings.FRONTEND_URL = 'https://example.com'
    settings.ENVIRONMENT = 'test'
    with pytest.raises(ValueError):
        await service.create_event_checkout_session('Unknown Event', 'customer@example.com')
