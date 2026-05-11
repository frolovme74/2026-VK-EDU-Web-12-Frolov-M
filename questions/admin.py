from django.contrib import admin
from questions.models import Tag, Question, QuestionLike, Answer, AnswerLike

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "question_count"]
    search_fields = ['name']
    readonly_fields = ['question_count']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    filter_horizontal = ["tags"]
    raw_id_fields = ["author"]
    list_display = ["__str__", "author"]
    search_fields = ["content", "title", "author__username"]
    list_select_related = ["author"]
    list_filter = ["tags"]
    readonly_fields = ['created_at', 'rating', 'answers_count']
    class AnswerInline(admin.TabularInline):
        model = Answer
        verbose_name_plural = 'Ответы'
        extra = 0
        raw_id_fields = ["author"]
    inlines = (AnswerInline, )


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    raw_id_fields = ["question", "user"]
    list_display = ["question", "user", "is_like"]
    list_filter = ["is_like"]
    search_fields = ["question__title", "user__username"]
    list_select_related = ["user", "question"]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    raw_id_fields = ["author","related_question"]
    list_display = ["__str__","related_question", "author"]
    search_fields = ["content", "author__username"]
    list_select_related = ["author", "related_question"]
    readonly_fields = ['created_at', 'rating']

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    raw_id_fields = ["answer", "user"]
    list_display = ["answer", "user", "is_like"]
    list_filter = ["is_like"]
    search_fields = ["answer__content", "user__username"]
    list_select_related = ["user", "answer"]
