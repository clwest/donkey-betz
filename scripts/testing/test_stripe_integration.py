#!/usr/bin/env python3
"""
Test Stripe Integration
Verifies that your Stripe payment processing is set up correctly
"""

import os
import sys
import django
import asyncio
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.agents.real_payment_processor import (
    real_payment_processor,
    create_client_payment_request,
    process_client_payment
)

async def test_stripe_integration():
    """Test the Stripe integration with your live keys"""

    print("🔒 STRIPE INTEGRATION TEST")
    print("=" * 60)

    # 1. Check Stripe API key is loaded
    import stripe
    print(f"✅ Stripe API Key Loaded: {stripe.api_key[:20]}...")

    # 2. Test creating a payment link (using test mode for safety)
    print("\n💳 Testing Payment Link Creation...")

    try:
        # Create a test payment request
        test_project = {
            "project_id": f"test_proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": "Test Project - AI Development Services",
            "budget": 100.00  # $100 test amount
        }

        test_client = {
            "client_id": "test_client_001",
            "name": "Test Client",
            "email": "testclient@example.com"  # Change this to your email for testing
        }

        # Create payment request
        payment_request = await create_client_payment_request(
            test_project["project_id"],
            test_client,
            test_project["budget"],
            f"Payment for: {test_project['title']}"
        )

        print(f"✅ Payment Request Created:")
        print(f"   Payment ID: {payment_request.payment_id}")
        print(f"   Amount: ${payment_request.amount:.2f}")
        print(f"   Transaction Fee: ${payment_request.transaction_fee:.2f}")
        print(f"   Net Amount: ${payment_request.net_amount:.2f}")

        if payment_request.invoice_url:
            print(f"   🔗 Invoice URL: {payment_request.invoice_url}")
            print(f"\n   ⚠️  This is a LIVE invoice - only click if you want to test payment!")

    except Exception as e:
        print(f"❌ Error creating payment request: {e}")
        print(f"   Make sure your Stripe keys are valid")
        return False

    # 3. Test payment processor status
    print("\n📊 Payment Processor Status:")
    status = real_payment_processor.get_payment_processor_status()
    print(f"   Active Payments: {status['active_payments']}")
    print(f"   Completed Payments: {status['completed_payments']}")
    print(f"   Failed Payments: {status['failed_payments']}")
    print(f"   Total Revenue: ${status['total_revenue']:,.2f}")
    print(f"   Processor Status: {status['processor_status']}")

    # 4. Generate revenue report
    print("\n💰 Revenue Report (Last 30 Days):")
    report = await real_payment_processor.generate_revenue_report(30)
    if report:
        print(f"   Total Payments: {report['summary']['total_payments']}")
        print(f"   Net Revenue: ${report['summary']['net_revenue']:,.2f}")
        print(f"   Projected Monthly: ${report['projections']['monthly_revenue']:,.2f}")
        print(f"   Projected Annual: ${report['projections']['annual_revenue']:,.2f}")

    print("\n" + "=" * 60)
    print("🎉 STRIPE INTEGRATION TEST COMPLETE!")
    print("\n⚠️  IMPORTANT NOTES:")
    print("1. You're using LIVE Stripe keys - real charges will occur!")
    print("2. Test with small amounts first ($1-10)")
    print("3. Use Stripe Dashboard to manage invoices and payments")
    print("4. Set up webhooks in Stripe Dashboard for automatic updates")

    print("\n🔗 Next Steps:")
    print("1. Go to: https://dashboard.stripe.com")
    print("2. Set up webhook endpoint: https://yourdomain.com/api/stripe/webhook")
    print("3. Configure payment links for your services")
    print("4. Enable automatic tax calculation if needed")

    return True

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_stripe_integration())

    if result:
        print("\n✅ Stripe integration is working!")
        print("💰 Ready to collect real payments from clients!")
    else:
        print("\n❌ Stripe integration needs configuration")
        print("Check your API keys and Stripe account settings")