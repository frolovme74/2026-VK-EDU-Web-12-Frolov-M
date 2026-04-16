from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

QUESTIONS = [
    {
    'id': i,
    'title': f'question title {i}',
    'text': f'Text {i}',
    'tags': ['python', 'backend'] if i % 2 == 0 else ['cpp', 'ngnix']
    }
    for i in range(30)
]

ANSWERS = [
    {
    'likes': i,
    'text': f'Text {i}',
    }
    for i in range(20, 0, -1)
]

def paginate(objects, request, per_page=5):

    page_number = request.GET.get('page')
    paginator = Paginator(objects, per_page)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj

def index(request):
    selected_tag = request.GET.get('tag')

    if selected_tag:
        filtered_questions = [
            q for q in QUESTIONS 
            if selected_tag in q['tags']
        ]

    else:
        filtered_questions = QUESTIONS

    page_obj = paginate(filtered_questions, request, 4)

    return render(request, 'questions/index.html', context={'questions': page_obj.object_list, 'page_obj': page_obj, 'selected_tag': selected_tag})

def hot(request):

    reversed_questions = QUESTIONS[::-1]
    selected_tag = request.GET.get('tag')

    if selected_tag:
        filtered_questions = [
            q for q in reversed_questions 
            if selected_tag in q['tags']
        ]

    else:
        filtered_questions = reversed_questions
    
    page_obj = paginate(filtered_questions, request, 4)
    return render(request, 'questions/hot.html', context={'questions': page_obj.object_list, 'page_obj': page_obj, 'selected_tag': selected_tag})

def signup(request):
    return render(request, 'questions/signup.html')

def login(request):
    return render(request, 'questions/login.html')

def profile(request):
    return render(request, 'questions/profile.html')

def ask(request):
    return render(request, 'questions/ask.html')

def question(request):
    raw_id = request.GET.get('quest')
    
    try:
        selected_id = int(raw_id)
        item = next((q for q in QUESTIONS if q['id'] == selected_id), None)
    except (ValueError, TypeError):
        item = None

    if not item:
        return index(request)

    page_obj = paginate(ANSWERS, request, 4)
    return render(request, 'questions/question.html', context={'selected_question': item, 'page_obj': page_obj, 'answers': page_obj.object_list})