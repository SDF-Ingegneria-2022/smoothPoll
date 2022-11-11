from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def dummy(request): 
    return render(request, 'polls/vote.html', {})
