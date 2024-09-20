from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Company
from .serializer import CompanySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.http import JsonResponse
from stripe_subscription.models import StripeSubscription
from users.models import UserAccount
   

class CompanyApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        user = UserAccount.objects.get(user_id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
        
        try:
            company = Company.objects.get(user_id = request.user.id)
            serializer = CompanySerializer(company, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response("Not found", status=status.HTTP_400_BAD_REQUEST)

    # 2. Create
    def post(self, request, *args, **kwargs):
        
        user = UserAccount.objects.get(user_id = request.user.id)
        subscription = StripeSubscription.objects.filter(user=user, active=True).first()

        if not subscription or not subscription.is_valid():
            return JsonResponse({'error': 'No valid subscription'}, status=403)
          
        
        data = {
            'name': request.data.get('name'), 
            'website': request.data.get('website'), 
            'phone': request.data.get('phone'), 
            'country': request.data.get('country'), 
            'user_id': request.user.id
        }
        serializer = CompanySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, company_id, *args, **kwargs):
        
        user = UserAccount.objects.get(user_id = request.user.id)
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
        serializer = CompanySerializer(instance = company_instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, company_id, *args, **kwargs):
        
        user = UserAccount.objects.get(user_id = request.user.id)
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