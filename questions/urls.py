
from django.urls import path
from questions import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('signup', views.signup, name = "signup"),
    path('login', views.login, name='login'),
    path('profile', views.profile, name='profile'),
    path('ask', views.ask, name="ask"),
    path('question', views.question, name = 'question')
]
