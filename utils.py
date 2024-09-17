# utils.py
# from stripe_subscription.models import StripeSubscription

# def has_active_subscription(user):
#     try:
#         subscription = StripeSubscription.objects.get(user=user)
#         return subscription.is_active()
#     except StripeSubscription.DoesNotExist:
#         return False
from django.utils import timezone
from chatbots.models import Chatbot
from stripe_subscription.models import UserProfile

def check_subscription_expiry(user):
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.subscription_plan and user_profile.subscription_expiry < timezone.now():
        # Disable all chatbots for this user if their subscription expired
        Chatbot.objects.filter(user=user).update(is_active=False)