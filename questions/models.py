from django.db import models

class Tag(models.Model):

    name = models.CharField(verbose_name="Название", max_length=30, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self):
        return self.name

class Question(models.Model):
    content = models.TextField(verbose_name="Текст вопроса")
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    author = models.ForeignKey("auth.User", verbose_name="Автор вопроса", on_delete=models.CASCADE, related_name="questions")
    tags = models.ManyToManyField("questions.Tag", related_name="questions", verbose_name="Теги")
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        short_title = self.title[:20] + "..." if len(self.title) > 20 else self.title
        return f"Вопрос {self.id}: {short_title}"
    
class QuestionLike(models.Model):

    question = models.ForeignKey("questions.Question", verbose_name="Вопрос", on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE)
    is_positive = models.BooleanField(verbose_name= "Лайк или дизлайк?")

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"
        unique_together = [
            ["question", "user"]
        ]
    def __str__(self):
        return f"Лайк пользователя {self.user_id} на {self.question_id}"

class Answer(models.Model):

    content = models.TextField(verbose_name="Текст ответа")
    related_question = models.ForeignKey("questions.Question", verbose_name= "Соответсвтующий вопрос", on_delete=models.CASCADE, related_name="answers")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    author = models.ForeignKey("auth.User", verbose_name="Автор ответа", on_delete=models.CASCADE, related_name="answers")
    is_correct = models.BooleanField(verbose_name= "Правильно?")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    # def __str__(self):
    #     return f"Ответ {self.id}"
    def __str__(self):
        short_answer = self.content[:20] + "..." if len(self.content) > 20 else self.content
        return f"Ответ {self.id}: {short_answer}"
    
class AnswerLike(models.Model):

    answer = models.ForeignKey("questions.Answer", verbose_name="Ответ", on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE)
    is_positive = models.BooleanField(verbose_name= "Лайк или дизлайк?")

    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"
        unique_together = [
            ["answer", "user"]
        ]
    def __str__(self):
        return f"Лайк пользователя {self.user_id} на ответ {self.answer_id}"

