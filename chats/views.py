from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Chat
from .serializer import ChatSerializer

class ChatApiView(APIView):
     # add permission to check if user is authenticated  
    permission_classes = [permissions.IsAuthenticated]
  
    def get(self, request, *args, **kwargs):
    
        # data_store = DataStore.objects.filter(company_id = request.data['company_id'])
        # serializer = DataStoreSerializer(data_store)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    
        try:
            chats = Chat.objects.filter(created_by=request.user.id)
            serializer = ChatSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)  
        except Chat.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)
