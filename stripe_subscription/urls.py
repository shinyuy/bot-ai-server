from django.urls import path
from .views import stripe_webhook, StripeApiView


urlpatterns = [
    path('stripe/webhook', stripe_webhook, name='stripe_webhook'),
    path('stripe/create-checkout-session', StripeApiView.as_view()),
]
   