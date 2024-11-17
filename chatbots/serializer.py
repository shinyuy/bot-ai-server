from rest_framework import serializers
from .models import Chatbot
from data_store.serializer import DataStoreSerializer

class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model=Chatbot
        fields=('id', 'name', 'link_to_logo', 'public', 'hide_branding', 'chatbot_url', 'data_sources', 'number_of_queries', 'number_of_users', 'user_id')

class ChatbotDetailsSerializer(serializers.Serializer):
    data_source = DataStoreSerializer(many=True)