from django.shortcuts import render

# Create your views here.


def addBook(request):
    return render(request, 'addbook.html')

def dashboard(request):
    return render(request, 'dashboard.html')