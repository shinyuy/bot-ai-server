from django.db import models
from users.models import UserAccount
from company.models import Company
from data_store.models import DataStore
# Create your models here.

# Create your models here.
class Chatbot(models.Model):
    # id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100, null=True)
    number_of_queries = models.PositiveIntegerField(default=0)
    number_of_users = models.PositiveIntegerField(default=0)
    website = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100, unique=True)
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE) 
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE) 
    data_sources = models.ForeignKey(DataStore, on_delete=models.CASCADE) 
    public = models.BooleanField(default=True) 
    is_social_media_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.name
    
    def queries_this_month(self):
        # Get the current month and year
        current_month = now().month
        current_year = now().year

        # Count the number of queries for the chatbot in the current month
        return ChatbotQuery.objects.filter(
            chatbot=self,
            created_at__year=current_year,
            created_at__month=current_month
        ).count()
    
    
class ChatbotQuery(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    query_text = models.TextField()
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query for {self.chatbot.name} at {self.created_at}"