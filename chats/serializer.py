from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model=Chat  
        fields=('id', 'question','answer', 'created_at', 'created_by', 'data_source')