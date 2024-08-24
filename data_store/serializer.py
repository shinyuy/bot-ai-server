from rest_framework import serializers
from .models import DataStore

class DataStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model=DataStore
        fields=('name', 'company_id', 'created_by', 'company_website', 'tokens','embedding', 'content')