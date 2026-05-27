from django.shortcuts import render, redirect
from django.http import HttpResponse
from questions.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from questions.forms import AskForm, AnswerForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Question, QuestionLike

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

@require_POST
def like_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходимо авторизоваться'}, status=401)
    
    question_id = request.POST.get('question_id')
    action = request.POST.get('action')
    
    if action not in ['like', 'dislike']:
        return JsonResponse({'error': 'Невалидные параметры'}, status=400)
        
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Вопрос не найден'}, status=404)

    new_rating = QuestionLike.objects.toggle_vote(request.user, question, action)
        
    return JsonResponse({'rating': new_rating})


@require_POST
def like_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходимо авторизоваться'}, status=401)
        
    answer_id = request.POST.get('answer_id')
    action = request.POST.get('action')
    
    if action not in ['like', 'dislike']:
        return JsonResponse({'error': 'Невалидные параметры'}, status=400)
        
    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Ответ не найден'}, status=404)
        
    # И здесь:
    new_rating = AnswerLike.objects.toggle_vote(request.user, answer, action)
        
    return JsonResponse({'rating': new_rating})


@require_POST
def mark_correct_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходимо авторизоваться'}, status=401)
        
    answer_id = request.POST.get('answer_id')
    
    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Ответ не найден'}, status=404)
        
    # Вызываем метод самой модели ответа
    is_correct = answer.toggle_correct(request.user)
    
    if is_correct is None:
        return JsonResponse({'error': 'Вы не являетесь автором этого вопроса'}, status=403)
        
    return JsonResponse({'is_correct': is_correct})