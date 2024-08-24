from django.db import models
from users.models import UserAccount
# Create your models here.

# Create your models here.
class Company(models.Model):
    # id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, unique=True)
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE) #.PositiveIntegerField(primary_key=True)
    
    # def save(self, **kwargs):
    #     company = self.model(**kwargs)

    #     company.save(using=self._db)
    