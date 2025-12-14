"""
Stripe Subscription Service - Session 438

Handles recurring subscriptions with Discord role integration.
Manages subscription tiers: Free, Pro ($9.99/mo), Premium ($29.99/mo)
"""

import os
import logging
import stripe
from typing import Optional, Dict, Any
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Stripe Price IDs - Create these in Stripe Dashboard
# These should be set in .env for production
STRIPE_PRICE_IDS = {
    'pro': os.getenv('STRIPE_PRICE_PRO', 'price_pro_monthly'),  # $9.99/mo
    'premium': os.getenv('STRIPE_PRICE_PREMIUM', 'price_premium_monthly'),  # $29.99/mo
}

# Discord Role IDs - Set these after creating roles in Discord
DISCORD_ROLE_IDS = {
    'pro': os.getenv('DISCORD_ROLE_PRO_ID'),
    'premium': os.getenv('DISCORD_ROLE_PREMIUM_ID'),
}


class StripeSubscriptionService:
    """Manages Stripe subscriptions with Discord integration."""

    def __init__(self):
        self.stripe_configured = bool(stripe.api_key and stripe.api_key.startswith('sk_'))

    async def create_or_get_customer(self, user) -> Optional[str]:
        """Create or retrieve a Stripe customer for the user."""
        try:
            from core.models import EnhancedUserProfile

            profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

            # Return existing customer if we have one
            if profile.stripe_customer_id:
                return profile.stripe_customer_id

            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                metadata={
                    'user_id': str(user.id),
                    'username': user.username,
                }
            )

            # Save customer ID
            profile.stripe_customer_id = customer.id
            profile.save(update_fields=['stripe_customer_id'])

            logger.info(f"Created Stripe customer {customer.id} for user {user.username}")
            return customer.id

        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return None

    async def create_checkout_session(
        self,
        user,
        tier: str,
        success_url: str,
        cancel_url: str
    ) -> Optional[Dict[str, Any]]:
        """Create a Stripe Checkout session for subscription."""
        try:
            if tier not in STRIPE_PRICE_IDS:
                raise ValueError(f"Invalid tier: {tier}. Must be 'pro' or 'premium'")

            customer_id = await self.create_or_get_customer(user)
            if not customer_id:
                raise ValueError("Could not create Stripe customer")

            price_id = STRIPE_PRICE_IDS[tier]

            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user.id),
                    'tier': tier,
                },
                subscription_data={
                    'metadata': {
                        'user_id': str(user.id),
                        'tier': tier,
                    }
                }
            )

            logger.info(f"Created checkout session {session.id} for user {user.username}, tier {tier}")

            return {
                'session_id': session.id,
                'url': session.url,
                'tier': tier,
            }

        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return None

    async def handle_subscription_created(self, subscription: stripe.Subscription) -> bool:
        """Handle new subscription from webhook."""
        try:
            from django.contrib.auth import get_user_model
            from core.models import EnhancedUserProfile

            User = get_user_model()

            # Get user from metadata
            user_id = subscription.metadata.get('user_id')
            tier = subscription.metadata.get('tier', 'pro')

            if not user_id:
                logger.error("No user_id in subscription metadata")
                return False

            user = User.objects.get(id=user_id)
            profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

            # Update profile
            profile.subscription_tier = tier
            profile.stripe_subscription_id = subscription.id
            profile.subscription_status = 'active'
            profile.subscription_started_at = timezone.now()
            profile.subscription_ends_at = None
            profile.discord_role_synced = False  # Will be synced separately
            profile.save()

            logger.info(f"Activated {tier} subscription for user {user.username}")

            # Trigger Discord role sync
            await self._sync_discord_role(user, tier)

            return True

        except Exception as e:
            logger.error(f"Error handling subscription created: {e}")
            return False

    async def handle_subscription_updated(self, subscription: stripe.Subscription) -> bool:
        """Handle subscription update from webhook."""
        try:
            from django.contrib.auth import get_user_model
            from core.models import EnhancedUserProfile

            User = get_user_model()

            user_id = subscription.metadata.get('user_id')
            if not user_id:
                # Try to find by subscription ID
                profile = EnhancedUserProfile.objects.filter(
                    stripe_subscription_id=subscription.id
                ).first()
                if not profile:
                    logger.error("Could not find user for subscription")
                    return False
                user = profile.user
            else:
                user = User.objects.get(id=user_id)
                profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

            # Map Stripe status to our status
            status_map = {
                'active': 'active',
                'past_due': 'past_due',
                'canceled': 'canceled',
                'incomplete': 'incomplete',
                'trialing': 'trialing',
            }

            new_status = status_map.get(subscription.status, 'active')
            tier = subscription.metadata.get('tier', profile.subscription_tier)

            profile.subscription_status = new_status
            profile.subscription_tier = tier

            # Handle cancellation
            if subscription.cancel_at_period_end:
                profile.subscription_ends_at = datetime.fromtimestamp(
                    subscription.current_period_end,
                    tz=timezone.utc
                )
            else:
                profile.subscription_ends_at = None

            profile.save()

            logger.info(f"Updated subscription for {user.username}: {tier} ({new_status})")

            # Sync Discord role
            await self._sync_discord_role(user, tier if new_status == 'active' else 'free')

            return True

        except Exception as e:
            logger.error(f"Error handling subscription updated: {e}")
            return False

    async def handle_subscription_deleted(self, subscription: stripe.Subscription) -> bool:
        """Handle subscription cancellation from webhook."""
        try:
            from core.models import EnhancedUserProfile

            profile = EnhancedUserProfile.objects.filter(
                stripe_subscription_id=subscription.id
            ).first()

            if not profile:
                logger.warning(f"No profile found for subscription {subscription.id}")
                return False

            # Downgrade to free tier
            profile.subscription_tier = 'free'
            profile.subscription_status = 'canceled'
            profile.stripe_subscription_id = None
            profile.subscription_ends_at = timezone.now()
            profile.save()

            logger.info(f"Canceled subscription for {profile.user.username}")

            # Remove Discord role
            await self._sync_discord_role(profile.user, 'free')

            return True

        except Exception as e:
            logger.error(f"Error handling subscription deleted: {e}")
            return False

    async def cancel_subscription(self, user, at_period_end: bool = True) -> bool:
        """Cancel a user's subscription."""
        try:
            from core.models import EnhancedUserProfile

            profile = EnhancedUserProfile.objects.filter(user=user).first()
            if not profile or not profile.stripe_subscription_id:
                logger.warning(f"No active subscription for user {user.username}")
                return False

            if at_period_end:
                # Cancel at end of billing period
                stripe.Subscription.modify(
                    profile.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Scheduled subscription cancellation for {user.username}")
            else:
                # Cancel immediately
                stripe.Subscription.delete(profile.stripe_subscription_id)
                logger.info(f"Immediately canceled subscription for {user.username}")

            return True

        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            return False

    async def get_billing_portal_url(self, user, return_url: str) -> Optional[str]:
        """Get Stripe Customer Portal URL for managing subscription."""
        try:
            from core.models import EnhancedUserProfile

            profile = EnhancedUserProfile.objects.filter(user=user).first()
            if not profile or not profile.stripe_customer_id:
                return None

            session = stripe.billing_portal.Session.create(
                customer=profile.stripe_customer_id,
                return_url=return_url,
            )

            return session.url

        except Exception as e:
            logger.error(f"Error creating billing portal session: {e}")
            return None

    async def _sync_discord_role(self, user, tier: str) -> bool:
        """Sync Discord role based on subscription tier."""
        try:
            from core.models import DiscordLinkCode, EnhancedUserProfile

            # Get user's Discord ID
            discord_link = DiscordLinkCode.objects.filter(
                user=user,
                is_used=True
            ).first()

            if not discord_link or not discord_link.discord_user_id:
                logger.info(f"User {user.username} has no linked Discord account")
                return False

            discord_user_id = discord_link.discord_user_id

            # Get the Discord bot to manage roles
            # This will be called from the Discord bot's event loop
            from core.services.discord_bot import get_bot_instance

            bot = get_bot_instance()
            if not bot:
                logger.warning("Discord bot not available for role sync")
                return False

            # Queue role sync for the bot
            # The bot will process this asynchronously
            await self._queue_role_sync(discord_user_id, tier)

            # Mark as synced
            profile = EnhancedUserProfile.objects.filter(user=user).first()
            if profile:
                profile.discord_role_synced = True
                profile.save(update_fields=['discord_role_synced'])

            return True

        except Exception as e:
            logger.error(f"Error syncing Discord role: {e}")
            return False

    async def _queue_role_sync(self, discord_user_id: str, tier: str):
        """Queue a Discord role sync operation."""
        from django.core.cache import cache

        # Store in cache for the Discord bot to pick up
        sync_key = f"discord_role_sync:{discord_user_id}"
        cache.set(sync_key, {
            'discord_user_id': discord_user_id,
            'tier': tier,
            'timestamp': timezone.now().isoformat(),
        }, timeout=3600)  # 1 hour expiry

        logger.info(f"Queued Discord role sync for user {discord_user_id} -> {tier}")

    def get_subscription_info(self, user) -> Dict[str, Any]:
        """Get subscription information for a user."""
        try:
            from core.models import EnhancedUserProfile

            profile = EnhancedUserProfile.objects.filter(user=user).first()
            if not profile:
                return {
                    'tier': 'free',
                    'status': 'active',
                    'limits': self._get_tier_limits('free'),
                }

            return {
                'tier': profile.subscription_tier,
                'status': profile.subscription_status,
                'started_at': profile.subscription_started_at,
                'ends_at': profile.subscription_ends_at,
                'stripe_customer_id': profile.stripe_customer_id,
                'limits': profile.get_tier_limits(),
                'usage': {
                    'daily_tasks': profile.daily_task_count,
                    'daily_limit': profile.get_tier_limits()['daily_tasks'],
                },
            }

        except Exception as e:
            logger.error(f"Error getting subscription info: {e}")
            return {'tier': 'free', 'status': 'active', 'limits': self._get_tier_limits('free')}

    def _get_tier_limits(self, tier: str) -> Dict[str, Any]:
        """Get limits for a subscription tier."""
        tier_configs = {
            'free': {
                'daily_tasks': 5,
                'priority_alerts': False,
                'dm_notifications': False,
                'advisor_access': False,
                'custom_workflows': False,
                'discord_role': None,
                'price': 0,
            },
            'pro': {
                'daily_tasks': 50,
                'priority_alerts': True,
                'dm_notifications': True,
                'advisor_access': False,
                'custom_workflows': False,
                'discord_role': 'Pro Member',
                'price': 9.99,
            },
            'premium': {
                'daily_tasks': -1,
                'priority_alerts': True,
                'dm_notifications': True,
                'advisor_access': True,
                'custom_workflows': True,
                'discord_role': 'Premium Member',
                'price': 29.99,
            },
        }
        return tier_configs.get(tier, tier_configs['free'])


# Global instance
stripe_subscription_service = StripeSubscriptionService()


# Convenience functions
async def create_checkout(user, tier: str, success_url: str, cancel_url: str):
    """Create a checkout session for a subscription."""
    return await stripe_subscription_service.create_checkout_session(
        user, tier, success_url, cancel_url
    )


async def cancel_subscription(user, at_period_end: bool = True):
    """Cancel a user's subscription."""
    return await stripe_subscription_service.cancel_subscription(user, at_period_end)


def get_subscription_info(user):
    """Get subscription information for a user."""
    return stripe_subscription_service.get_subscription_info(user)
