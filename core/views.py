from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from core.forms import SignupForm, LoginForm, UserSettingsForm, ProfileSettingsForm
from django.contrib import auth
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages

def signup(request):

    if request.user.is_authenticated:
        return redirect('profile_self')
    
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    
    return render(request, 'core/signup.html', {'form': form})

def login(request):

    if request.user.is_authenticated:
        return redirect('profile_self')
    
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user_cache)

            if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                next_url = reverse('index')
                
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form, 'next': next_url})

@login_required(login_url=reverse_lazy('login'))
def profile_self(request):
    user_id = request.user.id
    return redirect('profile', user_id = user_id)

@login_required(login_url=reverse_lazy('login'))
def profile_settings(request):
    if request.method == 'POST':
        user_form = UserSettingsForm(request.POST, instance=request.user)
        profile_form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Данные успешно обновлены!")
            return redirect('settings')
        else:
            print("Ошибки user_form:", user_form.errors)
            print("Ошибки profile_form:", profile_form.errors)
            print("Файлы в запросе:", request.FILES) # <-- ЭТО САМОЕ ВАЖНОЕ
    else:
        user_form = UserSettingsForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=request.user.profile)

    return render(request, 'core/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def logout(request):
    next_page = request.GET.get('next', 'index')
    auth.logout(request)
    if not url_has_allowed_host_and_scheme(url=next_page, allowed_hosts={request.get_host()}):
        next_page = reverse('index')
    return redirect(next_page)

def profile(request, user_id):
    target_user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)
    
    return render(request, 'core/user_profile.html', {
        'target_user': target_user,
    })
