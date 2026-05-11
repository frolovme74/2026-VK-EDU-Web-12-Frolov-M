from django.shortcuts import render

def signup(request):
    return render(request, 'core/signup.html')

def login(request):
    return render(request, 'core/login.html')

def profile(request):
    return render(request, 'core/profile.html')

# Create your views here.
