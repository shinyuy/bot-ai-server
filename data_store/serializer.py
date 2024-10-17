from rest_framework import serializers
from .models import DataStore

class DataStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model=DataStore
        fields=('id', 'name', 'created_by', 'tokens','embedding', 'content')