"""Set up Stripe products and prices for subscription tiers"""

import stripe
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parents[1]))

from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_products_and_prices():
    """Create Stripe products and prices for subscription tiers"""

    # Define subscription tiers
    tiers = [
        {
            "name": "Solo",
            "id": "solo",
            "description": "Perfect for individual M&A professionals and small teams",
            "monthly_price": 27900,  # $279.00 in cents
            "annual_price": 301000,  # $3010.00 in cents
        },
        {
            "name": "Growth",
            "id": "growth",
            "description": "Ideal for growing firms and active deal makers",
            "monthly_price": 79800,  # $798.00 in cents
            "annual_price": 861800,  # $8618.00 in cents
        },
        {
            "name": "Enterprise",
            "id": "enterprise",
            "description": "Complete solution for large organizations and funds",
            "monthly_price": 159800,  # $1598.00 in cents
            "annual_price": 1725800,  # $17258.00 in cents
        }
    ]

    created_products = []

    for tier in tiers:
        try:
            # Check if product exists
            existing_products = stripe.Product.list(limit=100)
            product = None

            for p in existing_products.data:
                if p.metadata.get("tier_id") == tier["id"]:
                    product = p
                    print(f"✓ Product already exists: {tier['name']}")
                    break

            # Create product if doesn't exist
            if not product:
                product = stripe.Product.create(
                    name=f"M&A Platform - {tier['name']}",
                    description=tier["description"],
                    metadata={
                        "tier_id": tier["id"],
                        "tier_name": tier["name"]
                    }
                )
                print(f"✓ Created product: {tier['name']}")

            # Create monthly price
            try:
                monthly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier["monthly_price"],
                    currency="usd",
                    recurring={"interval": "month"},
                    nickname=f"{tier['name']} Monthly",
                    metadata={
                        "tier_id": tier["id"],
                        "billing_cycle": "monthly"
                    }
                )
                print(f"  - Created monthly price: ${tier['monthly_price'] / 100}")
            except stripe.error.InvalidRequestError as e:
                if "already exists" not in str(e):
                    raise
                print(f"  - Monthly price already exists")

            # Create annual price
            try:
                annual_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier["annual_price"],
                    currency="usd",
                    recurring={"interval": "year"},
                    nickname=f"{tier['name']} Annual",
                    metadata={
                        "tier_id": tier["id"],
                        "billing_cycle": "annual"
                    }
                )
                print(f"  - Created annual price: ${tier['annual_price'] / 100}")
            except stripe.error.InvalidRequestError as e:
                if "already exists" not in str(e):
                    raise
                print(f"  - Annual price already exists")

            created_products.append({
                "tier": tier["id"],
                "product_id": product.id,
                "monthly_price_id": monthly_price.id if 'monthly_price' in locals() else None,
                "annual_price_id": annual_price.id if 'annual_price' in locals() else None
            })

        except Exception as e:
            print(f"✗ Error creating product {tier['name']}: {e}")
            continue

    # Create webhook endpoint if doesn't exist
    try:
        endpoints = stripe.WebhookEndpoint.list(limit=10)
        webhook_url = f"{os.getenv('API_URL', 'https://api.ma-platform.com')}/api/v1/webhooks/stripe"

        webhook_exists = any(e.url == webhook_url for e in endpoints.data)

        if not webhook_exists:
            endpoint = stripe.WebhookEndpoint.create(
                url=webhook_url,
                enabled_events=[
                    "customer.subscription.created",
                    "customer.subscription.updated",
                    "customer.subscription.deleted",
                    "invoice.payment_succeeded",
                    "invoice.payment_failed",
                    "customer.subscription.trial_will_end",
                    "payment_method.attached",
                    "payment_method.detached"
                ],
                description="M&A Platform Production Webhook"
            )
            print(f"\n✓ Created webhook endpoint: {webhook_url}")
            print(f"  Webhook secret: {endpoint.secret}")
            print(f"  ⚠️  Add this secret to your environment variables as STRIPE_WEBHOOK_SECRET")
        else:
            print(f"\n✓ Webhook endpoint already exists: {webhook_url}")

    except Exception as e:
        print(f"✗ Error creating webhook: {e}")

    # Print summary
    print("\n" + "="*50)
    print("STRIPE SETUP COMPLETE")
    print("="*50)
    print("\nCreated/verified the following:")
    for product in created_products:
        print(f"\n{product['tier'].upper()} Tier:")
        print(f"  Product ID: {product['product_id']}")
        print(f"  Monthly Price ID: {product['monthly_price_id']}")
        print(f"  Annual Price ID: {product['annual_price_id']}")

    print("\n⚠️  IMPORTANT: Update your .env file with the price IDs above")
    print("    These will be used to create subscriptions")

    return created_products


if __name__ == "__main__":
    if not settings.STRIPE_SECRET_KEY:
        print("ERROR: STRIPE_SECRET_KEY not found in environment")
        sys.exit(1)

    print("Setting up Stripe products and prices...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Stripe Mode: {'Live' if 'live' in settings.STRIPE_SECRET_KEY else 'Test'}")
    print("="*50)

    create_products_and_prices()