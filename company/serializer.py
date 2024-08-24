from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields=('id', 'name','website', 'country', 'phone', 'user_id')