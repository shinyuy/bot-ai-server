from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Chat
from .serializer import ChatSerializer
from stripe_subscription.models import StripeSubscription
from django.http import JsonResponse
   

class ChatApiView(APIView):
     # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]
  
    def get(self, request, *args, **kwargs):
        user = request.user
        subscription = StripeSubscription.objects.filter(user=request.user.id, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
        # data_store = DataStore.objects.filter(company_id = request.data['company_id'])
        # serializer = DataStoreSerializer(data_store)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    
        try:
            chats = Chat.objects.filter(created_by=request.user.id)
            serializer = ChatSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)  
        except Chat.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)
