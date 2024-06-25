from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def top(request):
    return render(request,'toot/top.html')
