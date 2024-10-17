from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import speech_to_text, text_to_speech
from data_store.vector import vectorize, vector2text, get_chat_completion, get_embeddings
from data_store.models import DataStore
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from pgvector.django import CosineDistance
from rest_framework import status




class CallsApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        audio_content = request.data.get('audio')  # Expect audio file input
        user_text = speech_to_text(audio_content)
        # chatbot_response = chatbot_interact(user_text)  # Your chatbot function
        
        user_text_embeddings = get_embeddings(user_text)
        website = request.data.get('website')
        try:
            answers = DataStore.objects.filter(company_website=website)
            answers_with_distance = answers.annotate(
                distance=CosineDistance("embedding", user_text_embeddings)
                ).order_by("distance")[:3]
            # answers = DataStore.objects.order_by(L2Distance('embedding', query))[:3]
            for answer in answers_with_distance:  
                if answer.company_website == website:
                    answer_text =  answer.content
                    result = result + " " + answer_text
                    print(answer)
                    
            chatbot_response = get_chat_completion(user_text, result) 
            audio_response = text_to_speech(chatbot_response)
            return Response({'audio_response': audio_response})
        except DataStore.DoesNotExist:
            return Response("Sorry, I don't have a response to your query", status=status.HTTP_400_BAD_REQUEST)
            
        
    