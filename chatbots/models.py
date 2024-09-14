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
    
    # def save(self, **kwargs):
    #     company = self.model(**kwargs)

    #     company.save(using=self._db)
    