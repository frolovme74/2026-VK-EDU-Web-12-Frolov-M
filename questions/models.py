from django.db import models
from django.utils.text import Truncator
from django.urls import reverse
from django.shortcuts import get_object_or_404
class Tag(models.Model):

    name = models.CharField(verbose_name="Название", max_length=30, unique=True)
    question_count = models.IntegerField(verbose_name="Количество вопросов с тегом", default=0)
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self):
        return self.name

class QuestionManager(models.Manager):

    # def get_queryset(self):
    #     return super().get_queryset().annotate(
    #         answers_count=Count('answers', distinct=True),
    #         rating=(
    #             Count('votes', filter=Q(votes__is_like=True), distinct=True) - 
    #             Count('votes', filter=Q(votes__is_like=False), distinct=True)
    #         )
    #     )
    
    def get_new_questions(self, tag_name=None):
        queryset = self.select_related('author', 'author__profile').prefetch_related('tags').order_by('-created_at')
        if tag_name:
            queryset = queryset.filter(tags__name=tag_name)
        return queryset
    
    def get_hot_questions(self, tag_name=None):
        queryset = self.select_related('author', 'author__profile').prefetch_related('tags').order_by('-rating')
        if tag_name:
            queryset = queryset.filter(tags__name=tag_name)
        return queryset
    
    def get_with_related(self, question_id):
        return get_object_or_404(
            self.select_related('author', 'author__profile').prefetch_related('tags'), 
            pk=question_id
        )
    
class Question(models.Model):
    content = models.TextField(verbose_name="Текст вопроса")
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)
    author = models.ForeignKey("auth.User", verbose_name="Автор вопроса", on_delete=models.CASCADE, related_name="questions")
    tags = models.ManyToManyField("questions.Tag", related_name="questions", verbose_name="Теги")
    # rating = models.IntegerField()
    rating = models.IntegerField(verbose_name="Рейтинг", default=0, db_index=True)
    answers_count = models.PositiveIntegerField(verbose_name="Количество ответов", default=0)
    objects = QuestionManager()

    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.id})
    
    def summary(self):
        return Truncator(self.content).chars(500)
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        # short_title = self.title[:20] + "..." if len(self.title) > 20 else self.title
        # return f"Вопрос {self.id}: {short_title}"
        return f"Вопрос {self.id}: {Truncator(self.title).chars(40)}"
    
class QuestionLike(models.Model):

    question = models.ForeignKey("questions.Question", verbose_name="Вопрос", on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey("auth.User", verbose_name="От пользователя", on_delete=models.CASCADE)
    # is_positive = models.BooleanField(verbose_name= "Лайк или дизлайк?")
    is_like = models.BooleanField(default=True, verbose_name="Тип оценки", choices=((True, 'Лайк'), (False, 'Дизлайк')))

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"
        unique_together = [
            ["question", "user"]
        ]
    def __str__(self):
        return f"Лайк пользователя {self.user_id} на {self.question_id}"
    
class AnswerManager(models.Manager):
    def get_for_question(self, question):
        return question.answers.select_related('author', 'author__profile').order_by('-rating')
    # def get_queryset(self):
    #     return super().get_queryset().annotate(
    #         rating=(
    #             Count('votes', filter=Q(votes__is_like=True)) - 
    #             Count('votes', filter=Q(votes__is_like=False))
    #         )
    #     )
class Answer(models.Model):

    content = models.TextField(verbose_name="Текст ответа")
    related_question = models.ForeignKey("questions.Question", verbose_name= "Соответсвтующий вопрос", on_delete=models.CASCADE, related_name="answers")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)
    author = models.ForeignKey("auth.User", verbose_name="Автор ответа", on_delete=models.CASCADE, related_name="answers")
    is_correct = models.BooleanField(verbose_name= "Правильно?")
    rating = models.IntegerField(verbose_name="Рейтинг", default=0, db_index=True)

    objects = AnswerManager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    # def __str__(self):
    #     return f"Ответ {self.id}"
    def __str__(self):
        # short_answer = self.content[:20] + "..." if len(self.content) > 20 else self.content
        # return f"Ответ {self.id}: {short_answer}"
        return f"Ответ {self.id}: {Truncator(self.content).chars(40)}"
    
class AnswerLike(models.Model):

    answer = models.ForeignKey("questions.Answer", verbose_name="Ответ", on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey("auth.User", verbose_name="От пользователя", on_delete=models.CASCADE)
    # is_positive = models.BooleanField(verbose_name= "Лайк или дизлайк?")
    is_like = models.BooleanField(default=True, verbose_name="Тип оценки", choices=((True, 'Лайк'), (False, 'Дизлайк')))
    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"
        unique_together = [
            ["answer", "user"]
        ]
    def __str__(self):
        return f"Лайк пользователя {self.user_id} на ответ {self.answer_id}"

