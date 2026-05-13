from django.shortcuts import render, redirect
from django.http import HttpResponse
from questions.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from questions.forms import AskForm, AnswerForm
from django.urls import reverse_lazy

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

@login_required(login_url=reverse_lazy('login'))
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            form.save_tags(question)
            return redirect(question.get_absolute_url())
    else:
        form = AskForm()
    
    return render(request, 'questions/ask.html', {'form': form})

def question(request, question_id):
    question_item = Question.objects.get_with_related(question_id)
    
    if request.method == 'POST':

        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.related_question = question_item
            answer.is_correct = False
            answer.save()
            return redirect(question_item.get_absolute_url())
    else:
        form = AnswerForm()

    answers = Answer.objects.get_for_question(question_item)
    page_obj = paginate(answers, request)

    return render(request, 'questions/question.html', {
        'question': question_item,
        'page_obj': page_obj,
        'form': form,
    })