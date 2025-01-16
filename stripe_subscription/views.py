# views.py
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StripeSubscription, UserProfile
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
import json
from rest_framework import permissions
from os import getenv
from users.models import UserAccount
import datetime
from django.utils import timezone

stripe.api_key = getenv("STRIPE_SECRET_KEY")
# This is your Stripe CLI webhook secret for testing your endpoint locally.

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, getenv("STRIPE_WEBHOOK_SECRET") #endpoint_secret 
        )
    except ValueError as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event)
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event)
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event)

    return JsonResponse({'status': 'success'})

def handle_subscription_created(event):
    data = event['data']['object']
    
    customer_id = data['customer']
    customer = stripe.Customer.retrieve(customer_id)
    customer_email = customer['email']
    
    subscription_id = data['id']
    current_period_end_unix = data['current_period_end']  # Unix timestamp
    current_period_start_unix = data['current_period_start']  # Unix timestamp
    current_period_end = datetime.datetime.fromtimestamp(current_period_end_unix, tz=timezone.utc)
    current_period_start = datetime.datetime.fromtimestamp(current_period_start_unix, tz=timezone.utc)
        
    user = UserAccount.objects.get(email=customer_email)
    
    sub = get_subscription_plan(data)
    try:
        StripeSubscription.objects.create(
        user=user, stripe_customer_id=customer_id, end_date=current_period_end, created_at=current_period_start,
        stripe_subscription_id=subscription_id, plan=sub["plan"], max_chatbots=sub["max_chatbots"], active=True)
        UserProfile.objects.create(
        user=user, subscription_plan_name=sub["plan"], max_chatbots=sub["max_chatbots"])
    except StripeSubscription.DoesNotExist:
        print('Not found')    

def handle_subscription_updated(event):
    print("3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333")
    data = event['data']['object']
    customer_id = data['customer']
    active = data['status'] == 'active'
    try:
        subscription = StripeSubscription.objects.get(stripe_customer_id=customer_id)
        subscription.active = active
        subscription.save()
    except StripeSubscription.DoesNotExist:
        subscription = None  

def handle_subscription_deleted(event):
    data = event['data']['object']
    customer_id = data['customer']

    try:
        subscription = StripeSubscription.objects.get(stripe_customer_id=customer_id)
        subscription.active = False
        subscription.save()
    except StripeSubscription.DoesNotExist:
        subscription = None     
    
    


class StripeApiView(APIView):
    # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs): 
        try:
            # Get the selected price from the frontend request
            
            # Create the Stripe Checkout session with the selected price
            user = request.user
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=user.email,
                # customer=user.id,
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': request.data.get('name'),
                            },
                            'unit_amount': request.data.get('price'),  # Use the selected price
                            'recurring': {
                                'interval': request.data.get('interval'), #Or 'year' for yearly plans
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=f'{getenv("FRONTEND_URL")}/success',
                cancel_url=f'{getenv("FRONTEND_URL")}/cancel',
            )
            # Return the session ID to the frontend
            return JsonResponse({'sessionId': checkout_session.id, 'checkout_session': checkout_session, 'status': 200 })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)    



def get_subscription_plan(subscription):
    latest_invoice_id = subscription.get('latest_invoice')
    
    if latest_invoice_id:
        # Retrieve the invoice using Stripe's API
        invoice = stripe.Invoice.retrieve(latest_invoice_id)
        
        # Get the amount paid from the invoice (in the smallest currency unit, e.g., cents)
        amount_paid = invoice['amount_paid']
        
        # Convert amount_paid to the main currency unit if needed
        amount_paid_converted = amount_paid / 100  # Assuming currency with two decimal places
        
    
    if amount_paid_converted == 9:
        return {
            "plan": "Basic",
            "max_chatbots": 3
        }
    elif amount_paid_converted == 29:
        return {
            "plan": "Standard",
            "max_chatbots": 10
        }
    elif amount_paid_converted == 59:
        return {
            "plan": "Premium",
            "max_chatbots": 20
        }
    else:
        return {
            "plan": "Unknown",
            "max_chatbots": 0
        }

