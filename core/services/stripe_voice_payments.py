"""
Stripe Voice Marketplace Payment Service - Session 450

Handles one-time payments for voice marketplace purchases.
Uses Stripe Checkout for secure payment processing.

Revenue Split: 70% to voice owner, 30% platform fee
"""

import os
import logging
from decimal import Decimal
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Stripe
try:
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_CONFIGURED = bool(stripe.api_key and stripe.api_key.startswith('sk_'))
except ImportError:
    stripe = None
    STRIPE_CONFIGURED = False
    logger.warning("Stripe package not installed")

# Stripe configuration
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')


class StripeVoicePaymentService:
    """
    Manages Stripe payments for voice marketplace purchases.

    Flow:
    1. User selects voice and specifies text length
    2. create_checkout_session() creates Stripe Checkout session
    3. User completes payment on Stripe hosted page
    4. Webhook receives checkout.session.completed
    5. handle_checkout_completed() creates VoiceTransaction
    6. Audio is generated and delivered
    """

    def __init__(self):
        self.stripe_configured = STRIPE_CONFIGURED
        if not self.stripe_configured:
            logger.warning("Stripe not configured - payments will be simulated")

    def create_checkout_session(
        self,
        voice_id: str,
        buyer,
        text_length: int,
        duration_estimate: int = None,
        content_type: str = 'other',
        success_url: str = None,
        cancel_url: str = None,
        metadata: Dict = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe Checkout session for voice purchase.

        Args:
            voice_id: UUID of the VoiceProfile
            buyer: User purchasing the voice
            text_length: Number of characters to generate
            duration_estimate: Estimated audio duration in seconds
            content_type: What the audio will be used for
            success_url: Redirect URL after successful payment
            cancel_url: Redirect URL if user cancels
            metadata: Additional data to store with the session

        Returns:
            Dict with session_id, url, and price info
        """
        try:
            from core.models_voice_marketplace import VoiceProfile

            # Get voice
            voice = VoiceProfile.objects.get(id=voice_id, is_active=True, is_public=True)

            # Calculate price
            if duration_estimate is None:
                # Estimate duration: ~150 chars/minute for TTS
                duration_estimate = max(10, int(text_length / 150 * 60))

            gross_price = voice.calculate_cost(
                text_length=text_length,
                duration_seconds=duration_estimate
            )

            # Minimum price of $0.10
            gross_price = max(gross_price, Decimal('0.10'))

            # Convert to cents for Stripe
            price_cents = int(gross_price * 100)

            # Build URLs
            base_url = os.getenv('SITE_URL', 'http://localhost:8000')
            if not success_url:
                success_url = f"{base_url}/voice-checkout/success/?session_id={{CHECKOUT_SESSION_ID}}"
            if not cancel_url:
                cancel_url = f"{base_url}/voice-checkout/cancel/"

            # Session metadata
            session_metadata = {
                'voice_id': str(voice_id),
                'buyer_id': str(buyer.id),
                'text_length': str(text_length),
                'duration_estimate': str(duration_estimate),
                'content_type': content_type,
                'voice_name': voice.name,
                'voice_owner_id': str(voice.owner.id),
            }
            if metadata:
                session_metadata.update(metadata)

            if not self.stripe_configured:
                # Return simulated session for testing
                logger.info(f"Stripe not configured - simulating checkout for {voice.name}")
                return {
                    'session_id': f'sim_sess_{voice_id}_{buyer.id}',
                    'url': f"{base_url}/voice-checkout/simulate/?voice_id={voice_id}&price={gross_price}",
                    'voice_name': voice.name,
                    'price': float(gross_price),
                    'price_display': f"${gross_price:.2f}",
                    'text_length': text_length,
                    'duration_estimate': duration_estimate,
                    'simulated': True,
                }

            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Voice: {voice.name}",
                            'description': f"TTS generation ({text_length} characters, ~{duration_estimate}s audio)",
                            'metadata': {
                                'voice_id': str(voice_id),
                                'voice_owner': voice.owner.username,
                            }
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=session_metadata,
                customer_email=buyer.email if buyer.email else None,
            )

            logger.info(f"Created checkout session {session.id} for voice {voice.name}, ${gross_price}")

            return {
                'session_id': session.id,
                'url': session.url,
                'voice_name': voice.name,
                'price': float(gross_price),
                'price_display': f"${gross_price:.2f}",
                'text_length': text_length,
                'duration_estimate': duration_estimate,
                'simulated': False,
            }

        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return None

    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle incoming Stripe webhook events.

        Args:
            payload: Raw request body
            signature: Stripe-Signature header

        Returns:
            Dict with success status and message
        """
        try:
            if not self.stripe_configured:
                return {'success': False, 'error': 'Stripe not configured'}

            # Verify webhook signature
            if STRIPE_WEBHOOK_SECRET:
                event = stripe.Webhook.construct_event(
                    payload, signature, STRIPE_WEBHOOK_SECRET
                )
            else:
                # For testing without webhook secret
                import json
                event = stripe.Event.construct_from(
                    json.loads(payload), stripe.api_key
                )

            event_type = event['type']
            logger.info(f"Received Stripe webhook: {event_type}")

            # Handle different event types
            if event_type == 'checkout.session.completed':
                session = event['data']['object']
                return self._handle_checkout_completed(session)

            elif event_type == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                logger.info(f"Payment succeeded: {payment_intent['id']}")
                return {'success': True, 'message': 'Payment recorded'}

            elif event_type == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                logger.warning(f"Payment failed: {payment_intent['id']}")
                return {'success': True, 'message': 'Payment failure recorded'}

            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {'success': True, 'message': f'Event {event_type} acknowledged'}

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return {'success': False, 'error': 'Invalid signature'}
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_checkout_completed(self, session: Dict) -> Dict[str, Any]:
        """
        Handle successful checkout completion.

        Creates VoiceTransaction and triggers audio generation.
        """
        try:
            from django.contrib.auth import get_user_model
            from core.models_voice_marketplace import VoiceProfile, VoiceTransaction

            User = get_user_model()

            metadata = session.get('metadata', {})
            voice_id = metadata.get('voice_id')
            buyer_id = metadata.get('buyer_id')
            text_length = int(metadata.get('text_length', 0))
            duration_estimate = int(metadata.get('duration_estimate', 0))
            content_type = metadata.get('content_type', 'other')

            if not voice_id or not buyer_id:
                logger.error("Missing voice_id or buyer_id in checkout metadata")
                return {'success': False, 'error': 'Missing metadata'}

            # Get voice and buyer
            voice = VoiceProfile.objects.get(id=voice_id)
            buyer = User.objects.get(id=buyer_id)

            # Calculate actual amounts
            amount_total = session.get('amount_total', 0)  # In cents
            gross_price = Decimal(amount_total) / Decimal('100')
            platform_fee = (gross_price * Decimal('0.30')).quantize(Decimal('0.01'))
            owner_payout = gross_price - platform_fee

            # Create transaction
            transaction = VoiceTransaction.objects.create(
                voice=voice,
                buyer=buyer,
                text_length=text_length,
                audio_duration_seconds=duration_estimate,
                generated_text='',  # Will be populated when user provides text
                gross_price=gross_price,
                platform_fee=platform_fee,
                owner_payout=owner_payout,
                content_type=content_type,
                stripe_payment_intent_id=session.get('payment_intent', ''),
                payout_status='pending',
            )

            # Update voice statistics
            voice.update_statistics(text_length, duration_estimate, gross_price)

            logger.info(
                f"Created VoiceTransaction {transaction.id}: "
                f"{buyer.username} purchased {voice.name} for ${gross_price}"
            )

            # TODO: Trigger notification to voice owner
            # TODO: Queue audio generation if text was provided

            return {
                'success': True,
                'message': 'Transaction created',
                'transaction_id': str(transaction.id),
                'voice_name': voice.name,
                'amount': float(gross_price),
            }

        except Exception as e:
            logger.error(f"Error handling checkout completed: {e}")
            return {'success': False, 'error': str(e)}

    def get_checkout_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a checkout session.

        Args:
            session_id: Stripe Checkout Session ID

        Returns:
            Dict with session status and details
        """
        try:
            if not self.stripe_configured:
                return {
                    'status': 'simulated',
                    'payment_status': 'paid',
                    'simulated': True,
                }

            session = stripe.checkout.Session.retrieve(session_id)

            return {
                'status': session.status,  # 'open', 'complete', 'expired'
                'payment_status': session.payment_status,  # 'unpaid', 'paid'
                'customer_email': session.customer_email,
                'amount_total': session.amount_total,
                'currency': session.currency,
                'metadata': session.metadata,
            }

        except Exception as e:
            logger.error(f"Error getting checkout status: {e}")
            return None

    def get_voice_price_estimate(
        self,
        voice_id: str,
        text_length: int,
        duration_estimate: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get price estimate for a voice purchase without creating a session.

        Useful for showing prices in the UI before checkout.
        """
        try:
            from core.models_voice_marketplace import VoiceProfile

            voice = VoiceProfile.objects.get(id=voice_id, is_active=True)

            if duration_estimate is None:
                duration_estimate = max(10, int(text_length / 150 * 60))

            gross_price = voice.calculate_cost(
                text_length=text_length,
                duration_seconds=duration_estimate
            )
            gross_price = max(gross_price, Decimal('0.10'))

            platform_fee = (gross_price * Decimal('0.30')).quantize(Decimal('0.01'))
            owner_payout = gross_price - platform_fee

            return {
                'voice_id': str(voice_id),
                'voice_name': voice.name,
                'pricing_model': voice.pricing_model,
                'base_price': float(voice.price),
                'text_length': text_length,
                'duration_estimate': duration_estimate,
                'gross_price': float(gross_price),
                'platform_fee': float(platform_fee),
                'owner_payout': float(owner_payout),
                'price_display': f"${gross_price:.2f}",
            }

        except Exception as e:
            logger.error(f"Error getting price estimate: {e}")
            return None

    def simulate_purchase(
        self,
        voice_id: str,
        buyer,
        text_length: int,
        text: str = '',
        content_type: str = 'other'
    ) -> Optional[Dict[str, Any]]:
        """
        Simulate a voice purchase for testing (when Stripe is not configured).

        Creates a VoiceTransaction without actual payment.
        """
        try:
            from core.models_voice_marketplace import VoiceProfile, VoiceTransaction

            voice = VoiceProfile.objects.get(id=voice_id, is_active=True)

            # Estimate duration
            duration_estimate = max(10, int(text_length / 150 * 60))

            # Calculate price
            gross_price = voice.calculate_cost(
                text_length=text_length,
                duration_seconds=duration_estimate
            )
            gross_price = max(gross_price, Decimal('0.10'))
            platform_fee = (gross_price * Decimal('0.30')).quantize(Decimal('0.01'))
            owner_payout = gross_price - platform_fee

            # Create transaction
            transaction = VoiceTransaction.objects.create(
                voice=voice,
                buyer=buyer,
                text_length=text_length,
                audio_duration_seconds=duration_estimate,
                generated_text=text[:1000] if text else '',
                gross_price=gross_price,
                platform_fee=platform_fee,
                owner_payout=owner_payout,
                content_type=content_type,
                stripe_payment_intent_id='sim_' + str(voice_id)[:8],
                payout_status='pending',
            )

            # Update voice statistics
            voice.update_statistics(text_length, duration_estimate, gross_price)

            logger.info(f"Simulated purchase: {buyer.username} bought {voice.name} for ${gross_price}")

            return {
                'success': True,
                'transaction_id': str(transaction.id),
                'voice_name': voice.name,
                'price': float(gross_price),
                'simulated': True,
            }

        except Exception as e:
            logger.error(f"Error simulating purchase: {e}")
            return None


# Global instance
_stripe_voice_service = None


def get_stripe_voice_service() -> StripeVoicePaymentService:
    """Get the singleton StripeVoicePaymentService instance."""
    global _stripe_voice_service
    if _stripe_voice_service is None:
        _stripe_voice_service = StripeVoicePaymentService()
    return _stripe_voice_service


# Convenience functions
def create_voice_checkout(
    voice_id: str,
    buyer,
    text_length: int,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """Create a checkout session for a voice purchase."""
    return get_stripe_voice_service().create_checkout_session(
        voice_id, buyer, text_length, **kwargs
    )


def get_voice_price(voice_id: str, text_length: int) -> Optional[Dict[str, Any]]:
    """Get price estimate for a voice purchase."""
    return get_stripe_voice_service().get_voice_price_estimate(voice_id, text_length)
