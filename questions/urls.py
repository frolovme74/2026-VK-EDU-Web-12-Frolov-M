
from django.urls import path
from questions import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('ask/', views.ask, name="ask"),
    path('question/', views.question, name = 'question'),
    path('hot/', views.hot, name="hot"),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ajax/like-question/', views.like_question, name='like_question'),
    path('ajax/like-answer/', views.like_answer, name='like_answer'),
    path('ajax/mark-correct/', views.mark_correct_answer, name='mark_correct_answer'),
]
