from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import DataStore
from .serializer import DataStoreSerializer
from chats.serializer import ChatSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import AllowAny
import json
from .vector import vectorize, vector2text, get_chat_completion, get_embeddings
from pgvector.django import L2Distance
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter 
from pgvector.django import CosineDistance
from chats.models import Chat
from stripe_subscription.models import StripeSubscription
from django.http import JsonResponse
from chatbots.models import Chatbot
from users.models import UserAccount
  
class DataStoreApiView(APIView):
    # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
        try:
            data_store = DataStore.objects.get(company_id = request.data['company_id'])
            serializer = DataStoreSerializer(data_store)
            return Response(serializer.data, status=status.HTTP_200_OK)  
        except DataStore.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)

    # 2. Create
    def post(self, request, *args, **kwargs):
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
          
        
        text_splitter = RecursiveCharacterTextSplitter (   
            chunk_size=1000,
            chunk_overlap=50
        )

        chunks = text_splitter.split_text(request.data.get('pdf_text'))
        
        try:
            for index, chunk in enumerate(chunks): 
                # vectors = vectorize(chunk, request.data.get('name'))
                vectors = get_embeddings(chunk)
                
                data = {
                    'name': request.data.get('name'),   
                    # 'company_id': request.data.get('id'),   
                    # 'company_website': request.data.get('company_website'),   
                    'created_by': user.external_id,
                    'content': chunk,
                    'embedding': vectors,
                    'tokens': index,     
                    }
                serializer = DataStoreSerializer(data=data)
                print("00000000000000000000000000000000000000000000000000000000000000000000000000000000")
                if serializer.is_valid():
                    print("valid")
                    serializer.save()
                if not serializer.is_valid():
                    print(serializer.errors)    
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except DataStore.DoesNotExist:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, data_store_id, *args, **kwargs):
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
       
        data_store_instance = self.get_object(data_store_id, request.user.id)
        if not data_store_instance:
            return Response(
                {"res": "Object with data_store id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'name': request.data.get('name'), 
            # 'user': request.user.id
        }
        serializer = DataStoreSerializer(instance = data_store_instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, data_store_id, *args, **kwargs):
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
       
        data_store_instance = self.get_object(data_store_id, request.user.id)
        if not data_store_instance:
            return Response(
                {"res": "Object with data_store id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data_store_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
   
class QuestionApiView(APIView):
    # add permission to check if user is authenticated     
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        
        question = request.data.get('question')
        
        external_id = request.data.get('external_id')
        # query = vectorize(question, 'question')
        query = get_embeddings(question)
        print(query)
        result = ''
        data_source = ''
        created_by = 0   
        print("000000000000000000000000000000000000000000000000000000000000000000000000")

        try:
            answers = DataStore.objects.filter(created_by=external_id)
            answers_with_distance = answers.annotate(
                distance=CosineDistance("embedding", query)
                ).order_by("distance")[:3]
            # answers = DataStore.objects.order_by(L2Distance('embedding', query))[:3]
            for answer in answers_with_distance:  
                if answer.created_by == external_id:
                    answer_text =  answer.content
                    result = result + " " + answer_text
                    print(answer)
                    data_source = answer.name  
                    created_by = answer.created_by_id
                    
            res = get_chat_completion(question, result)            
            # answers = answers.get(company_id=company_id)
            # serializer = DataStoreSerializer(result, many=True)
            print("uuoddddddddddddddddddddddddddddddddddddddddddddddddah")
            data = {  
                    'question': question,  
                    'answer': res, 
                    'data_source': data_source,
                    'created_by': created_by,
                    }
            
            serializer = ChatSerializer(data=data)
            if serializer.is_valid():
                print("valid")
                serializer.save()
            if not serializer.is_valid():
                print(serializer.errors) 
            return Response(res, status=status.HTTP_200_OK)  
        except DataStore.DoesNotExist:
            return Response("Sorry, I don't have a response to your query", status=status.HTTP_400_BAD_REQUEST)
        

class FileApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    
    # Upload file
    def post(self, request, *args, **kwargs):  
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
        
        data = {
            'filename': request.data.get('filename'), 
        }
        
        print("ooooooooooooooooooooooooooooooooooooo")
        
        
        # print(json.loads(request.data.get('filename')))
        # print(json.loads(request.data.get('file')))
        # print(json.loads(request.data.get('formData')))
      
        
        return  Response(
            {"res": "File uploaded"},
            status=status.HTTP_200_OK
        )
    
    # 5. Delete
    def delete(self, request, data_store_id, *args, **kwargs):
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
       
        data_store_instance = self.get_object(data_store_id, request.user.id)
        if not data_store_instance:
            return Response(
                {"res": "Object with data_store id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data_store_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
        
        
class DataStoreAllApiView(APIView):
    # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
    
        # data_store = DataStore.objects.filter(company_id = request.data['company_id'])
        # serializer = DataStoreSerializer(data_store)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    
        try:
            data_store = DataStore.objects.distinct('name')
            serializer = DataStoreSerializer(data_store, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)  
        except DataStore.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)