from django.contrib import admin
from questions.models import Tag, Question, QuestionLike, Answer, AnswerLike

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    filter_horizontal = ["tags"]
    raw_id_fields = ["author"]
    list_display = ["__str__", "author"]
    search_fields = ["content", "title", "author__username"]
    list_select_related = ["author"]
    list_filter = ["tags"]

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    raw_id_fields = ["question", "user"]
    list_display = ["question", "user", "is_positive"]
    list_filter = ["is_positive"]
    search_fields = ["question__title", "user__username"]
    list_select_related = ["user", "question"]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    raw_id_fields = ["author","related_question"]
    list_display = ["__str__","related_question", "author"]
    search_fields = ["content", "author__username"]
    list_select_related = ["author", "related_question"]

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    raw_id_fields = ["answer", "user"]
    list_display = ["answer", "user", "is_positive"]
    list_filter = ["is_positive"]
    search_fields = ["answer", "user__username"]
    list_select_related = ["user", "answer"]
