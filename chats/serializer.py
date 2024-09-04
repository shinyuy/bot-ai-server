from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model=Chat  
        fields=('id', 'question','answer', 'company_id', 'company_website', 'created_at', 'created_by', 'data_source')