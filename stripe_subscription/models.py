# models.py
from django.db import models
from django.conf import settings
from users.models import UserAccount
from django.utils import timezone

class StripeSubscription(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    plan = models.CharField(max_length=50)  # e.g. 'monthly', 'yearly', etc.
    created_at = models.DateTimeField(auto_now_add=True)
    max_chatbots = models.IntegerField(default=1)
    has_social_media_access = models.BooleanField(default=False)  # Social media access like WhatsApp, Messenger
    max_queries_per_month = models.IntegerField(default=1000)  # Max queries allowed per chatbot per month


    
    def is_valid(self):
        return self.active and self.end_date > timezone.now()
    
    # def save(self, *args, **kwargs):
    #     # Automatically disable subscription when expired
    #     if self.end_date <= timezone.now():
    #         self.active = False
    #     super(StripeSubscription, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name    

class UserProfile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(StripeSubscription, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.subscription_plan.name}'    