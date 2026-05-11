from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def signup(request):
    return render(request, 'core/signup.html')

def login(request):
    return render(request, 'core/login.html')

def profile(request):
    return render(request, 'core/profile.html')


def profile_view(request, user_id):
    target_user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)
    
    return render(request, 'core/user_profile.html', {
        'target_user': target_user,
    })
