from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chatbot
from chats.models import Chat
from company.models import Company
from data_store.models import DataStore
from .serializer import ChatbotSerializer, ChatbotDetailsSerializer
from rest_framework.views import APIView  
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from collections import namedtuple
   
class ChatbotApiView(APIView):
    # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
          
        # company = Company.objects.get(user_id = request.user.id)
        # serializer = CompanySerializer(company)
        # return Response(serializer.data, status=status.HTTP_200_OK)
      
        try:  
            chatbot = Chatbot.objects.filter(user_id = request.user.id)
            serializer = ChatbotSerializer(chatbot, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Chatbot.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)

    # 2. Create
    def post(self, request, *args, **kwargs):
        print(request.data)    
        company = Company.objects.get(id = request.data.get('company'))   
       
        data = {
            'name': request.data.get('name'), 
            'company_id': request.data.get('company'), 
            'website': company.website, 
            'phone_number': company.phone,   
            'country': company.country, 
            'user_id': request.user.id,
            'industry': company.industry,
            'data_sources': request.data.get('data_source')
        }
        serializer = ChatbotSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, company_id, *args, **kwargs):
       
        company_instance = self.get_object(company_id, request.user.id)
        if not company_instance:
            return Response(
                {"res": "Object with company id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'name': request.data.get('name'), 
            'website': request.data.get('website'), 
            'phone': request.data.get('phone'), 
            'country': request.data.get('country'),
            # 'user': request.user.id
        }
        serializer = ChatbotSerializer(instance = company_instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, company_id, *args, **kwargs):
       
        company_instance = self.get_object(company_id, request.user.id)
        if not company_instance:
            return Response(
                {"res": "Object with company id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        company_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
        
class StatsApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
       
        try:
            chatbot = Chatbot.objects.filter(user_id = request.user.id).count()
            chats = Chat.objects.filter(created_by=request.user.id).count()
            data_sources = DataStore.objects.filter(created_by=request.user.id).distinct('name').count()
            # serializer = ChatbotSerializer(chatbot, many=True)
            return Response({"chatbots": chatbot, "chats": chats, "data_sources" : data_sources}, status=status.HTTP_200_OK)
        except Chatbot.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)
        
class ChatbotDetailsApiView(APIView):
    # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
          
        # company = Company.objects.get(user_id = request.user.id)
        # serializer = CompanySerializer(company)
        # return Response(serializer.data, status=status.HTTP_200_OK)
      
        ChatbotDetails = namedtuple('ChatbotDetails', ('data_source', 'company'))
        try:  
            chatbotDetails = ChatbotDetails(
            data_source = DataStore.objects.filter(created_by = request.user.id, id=request.query_params.get('data_source_id')),
            company = Company.objects.filter(user_id = request.user.id, id=request.query_params.get('company_id'))
            )  
            serializer = ChatbotDetailsSerializer(chatbotDetails)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Chatbot.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)        