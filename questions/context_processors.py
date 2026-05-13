from questions.models import Tag
from core.models import Profile
def popular_tags(request):
    tags = Tag.objects.order_by('-question_count')[:10]
    return {'popular_tags': tags}

def best_members(request):
    return {
        'best_members': Profile.objects.select_related('user').order_by('-questions_count')[:5]
    }