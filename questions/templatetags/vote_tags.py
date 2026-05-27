from django import template
from questions.models import QuestionLike, AnswerLike

register = template.Library()

@register.simple_tag
def get_user_vote(user, item, item_type):
    if not user.is_authenticated:
        return ""
        
    if item_type == 'question':
        vote = QuestionLike.objects.filter(question=item, user=user).first()
    else:
        vote = AnswerLike.objects.filter(answer=item, user=user).first()
        
    if vote:
        return "like" if vote.is_like else "dislike"
    return ""