from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate(objects, request, per_page=5):
    page_number = request.GET.get('page')
    paginator = Paginator(objects, per_page)

    return paginator.get_page(page_number)

def index(request):
    tag = request.GET.get('tag')
    questions = Question.objects.get_new_questions(tag)
    page_obj = paginate(questions, request)
    
    return render(request, 'questions/index.html', {'page_obj': page_obj, 'selected_tag': tag})

def hot(request):
    tag = request.GET.get('tag')
    questions = Question.objects.get_hot_questions(tag)
    page_obj = paginate(questions, request)
    
    return render(request, 'questions/index.html', {'page_obj': page_obj, 'selected_tag': tag, 'is_hot': True})


def ask(request):
    return render(request, 'questions/ask.html')

def question(request, question_id):
    question_item = Question.objects.get_with_related(question_id)
    answers = Answer.objects.get_for_question(question_item)
    page_obj = paginate(answers, request)

    return render(request, 'questions/question.html', {
        'question': question_item,
        'page_obj': page_obj,
    })