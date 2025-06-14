from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("hey welcome to home page <a href='/books'> ExploreBooks</a>")