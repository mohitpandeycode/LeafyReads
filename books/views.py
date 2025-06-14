from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("Explore the books made for you and read online <a href='/'> Home</a>")