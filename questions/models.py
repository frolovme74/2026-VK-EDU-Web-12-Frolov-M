from django.db import models
from django.utils.text import Truncator
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Case, When, IntegerField
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed, pre_delete
from django.db.models import F

class Tag(models.Model):

    name = models.SlugField(verbose_name="Название", max_length=30, unique=True)
    question_count = models.IntegerField(verbose_name="Количество вопросов с тегом", default=0)
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self):
        return self.name

class RatingMixin(models.Model):
    rating = models.IntegerField(verbose_name="Рейтинг", default=0, db_index=True)

    class Meta:
        abstract = True

    def update_rating(self):
        score = self.votes.aggregate(
            total=Sum(
                Case(
                    When(is_like=True, then=1),
                    When(is_like=False, then=-1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )['total'] or 0
        self.rating = score
        self.save(update_fields=['rating'])

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
    
class Question(RatingMixin):
    content = models.TextField(verbose_name="Текст вопроса", max_length=50000)
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)
    author = models.ForeignKey("auth.User", verbose_name="Автор вопроса", on_delete=models.CASCADE, related_name="questions")
    tags = models.ManyToManyField("questions.Tag", related_name="questions", verbose_name="Теги")
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
class Answer(RatingMixin):

    content = models.TextField(verbose_name="Текст ответа", max_length=30000)
    related_question = models.ForeignKey("questions.Question", verbose_name= "Соответсвтующий вопрос", on_delete=models.CASCADE, related_name="answers")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)
    author = models.ForeignKey("auth.User", verbose_name="Автор ответа", on_delete=models.CASCADE, related_name="answers")
    is_correct = models.BooleanField(verbose_name= "Правильно?")

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

@receiver([post_save, post_delete], sender=QuestionLike)
@receiver([post_save, post_delete], sender=AnswerLike)
def auto_update_rating(sender, instance, **kwargs):
    target = getattr(instance, 'question', None) or getattr(instance, 'answer', None)
    if target:
        target.update_rating()

@receiver(post_save, sender=Answer)
def increment_answers_count(sender, instance, created, **kwargs):
    if created:
        Question.objects.filter(pk=instance.related_question_id).update(
            answers_count=F('answers_count') + 1
        )

@receiver(post_delete, sender=Answer)
def decrement_answers_count(sender, instance, **kwargs):
    Question.objects.filter(pk=instance.related_question_id).update(
        answers_count=F('answers_count') - 1
    )

@receiver(m2m_changed, sender=Question.tags.through)
def update_tag_question_count(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        Tag.objects.filter(pk__in=pk_set).update(question_count=F('question_count') + 1)
        
    elif action == "post_remove":
        Tag.objects.filter(pk__in=pk_set).update(question_count=F('question_count') - 1)

@receiver(pre_delete, sender=Question)
def update_tag_count_on_delete(sender, instance, **kwargs):
    tag_ids = instance.tags.values_list('id', flat=True)
    if tag_ids:
        Tag.objects.filter(pk__in=tag_ids).update(question_count=F('question_count') - 1)