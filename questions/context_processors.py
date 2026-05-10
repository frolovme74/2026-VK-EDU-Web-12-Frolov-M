from questions.models import Tag

def popular_tags(request):
    tags = Tag.objects.order_by('-question_count')[:10]
    return {'popular_tags': tags}