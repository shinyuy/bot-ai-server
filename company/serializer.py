from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields=('id', 'name','website', 'country', 'number_of_chatbots', 'number_of_queries', 'number_of_users', 'phone', 'user_id')