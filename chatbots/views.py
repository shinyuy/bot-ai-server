from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chatbot
from chats.models import Chat
from data_store.models import DataStore
from .serializer import ChatbotSerializer, ChatbotDetailsSerializer
from rest_framework.views import APIView  
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from collections import namedtuple
from django.http import JsonResponse
from stripe_subscription.models import StripeSubscription, UserProfile
from users.models import UserAccount
from .static_files import generate_html_css, save_files, upload_to_backblaze, upload_logo
from rest_framework.parsers import MultiPartParser, FormParser
from os import getenv, path
from django.http import HttpResponse, Http404
import requests
from django.utils.decorators import decorator_from_middleware
from django.middleware.clickjacking import XFrameOptionsMiddleware
   
class ChatbotApiView(APIView):
    # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
        try:  
            chatbot = Chatbot.objects.filter(user_id = request.user.id)
            serializer = ChatbotSerializer(chatbot, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Chatbot.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)

    # 2. Create
    def post(self, request, *args, **kwargs):

        subscription = StripeSubscription.objects.filter(user=request.user.id, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
        user_profile = UserProfile.objects.get(user=request.user.id)
        subscription_plan = user_profile.subscription_plan
        max_chatbots = user_profile.max_chatbots
        
        # Get the total number of chatbots the user has already created
        user_chatbots_count = Chatbot.objects.filter(user_id=request.user.id).count()

        # Check if the user has reached their max chatbot limit
       
        if user_chatbots_count >= max_chatbots:
            return JsonResponse({  
            'error': 'You have reached the maximum number of chatbots allowed by your subscription plan.'
        }, status=400)
   
        # Check if the user wants to enable social media access but doesn't have that feature
        if request.data.get('enable_social_media') and not subscription_plan.has_social_media_access:
            return JsonResponse({
                'error': 'Your subscription plan does not allow chatbots with social media access.'
        }, status=400)

            
        files = generate_html_css(request.data.get('name'),request.data.get('logo_url'), request.data.get('primary_color'), request.data.get('welcomeMessage'), request.data.get('placeholderText'), request.data.get('hideBranding')) 
        
        
        paths = save_files(files['html_content'], files['css_content'], request.data.get('name'), request.user.external_id) 
         
        chatbot = upload_to_backblaze(paths['html_file_path'], paths['css_file_path'], getenv('BACKBLAZE_KEY_NAME'), getenv('BACKBLAZE_API_KEY_ID'), getenv('BACKBLAZE_API_KEY'))
        
        data = {    
            'name': request.data.get('name'),   
            'user_id': request.user.id, 
            'data_sources': request.data.get('data_source'), 
            'public' : request.data.get('chatbot_public'),   
            'hide_branding' : request.data.get('hideBranding'),   
            'chatbot_url' : chatbot["html_file_path"],
            'chatbot_css_url' : chatbot["css_file_path"],
            'link_to_logo' : request.data.get('logo_url')   
       
        }
        serializer = ChatbotSerializer(data=data)
        if serializer.is_valid():  
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, company_id, *args, **kwargs):

        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
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

        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
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
        
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
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
          
        user = UserAccount.objects.get(id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
      
        ChatbotDetails = namedtuple('ChatbotDetails', ('data_source'))
        try:  
            chatbotDetails = ChatbotDetails(
            data_source = DataStore.objects.filter(created_by = user.external_id, id=request.query_params.get('data_source_id')),
            )  
            serializer = ChatbotDetailsSerializer(chatbotDetails)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Chatbot.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)   
        
        
class LogoApiView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)  # Ensure this is set
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        uploaded_logo = upload_logo(file_obj)  
        
        return Response({
            'message': 'File uploaded successfully',
            'logo': uploaded_logo['secure_url'],  # Return URL to access the file if needed
            'public_id': uploaded_logo['public_id']  # Return URL to access the file if needed
        }, status=status.HTTP_201_CREATED)
        

def allow_iframe(view_func):
    middleware = decorator_from_middleware(XFrameOptionsMiddleware)
    return middleware(view_func)        
        
         
@allow_iframe         
def serve_static_file(request, file_name):
    # Backblaze public file URL
   
    html_file_name = "Test_4d06e3f2-7e84-4473-98a8-b58ffe0c4ded_chatbot.html"
    css_file_name = "Test_style.css"
    base_url = "https://f005.backblazeb2.com/file/contexx"
    html_file_url = f"{base_url}/{file_name}"

    # Fetch the file from Backblaze
    response = requests.get(html_file_url)
    print(html_file_url)
    print("111111111111111111111111111111111111111111111111111111111111111111111111111111")
    print(response.content)
    print("111111111111111111111111111111111111111111111111111111111111111111111111111111")
    if response.status_code == 200:
        return HttpResponse(response.content, content_type='text/html')
    else:
        raise Http404("File not found")             