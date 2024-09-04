from django.db import models
from company.models import Company
from data_store.models import DataStore
from users.models import UserAccount

# Create your models here.
class Chat(models.Model):
    # id = models.PositiveIntegerField(primary_key=True)
    question = models.CharField(max_length=500)
    answer = models.TextField("answer", null=False, blank=False)
    data_source = models.CharField(DataStore, max_length=100)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE) #.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    company_website = models.CharField(Company, max_length=100)

   