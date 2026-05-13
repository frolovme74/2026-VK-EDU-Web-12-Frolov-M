
from django.urls import path
from core import views

urlpatterns = [
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile_self, name = 'profile_self'),
    path('profile/settings/', views.profile_settings, name='settings'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('logout/', views.logout, name = 'logout')
]
