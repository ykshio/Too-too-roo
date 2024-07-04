# main/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from main.models import CustomUser

class EnsureCustomUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Try to access the CustomUser to ensure it exists
                request.user.customuser
            except CustomUser.DoesNotExist:
                # Create the CustomUser if it does not exist
                CustomUser.objects.create(user=request.user)
        response = self.get_response(request)
        return response
