from rest_framework import serializers
from .models import Chatbot
from data_store.serializer import DataStoreSerializer
from company.serializer import CompanySerializer

class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model=Chatbot
        fields=('id', 'name','website', 'phone_number', 'industry', 'company_id', 'data_sources', 'number_of_queries', 'number_of_users', 'user_id')

class ChatbotDetailsSerializer(serializers.Serializer):
    data_source = DataStoreSerializer(many=True)
    company = CompanySerializer(many=True)