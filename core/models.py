from django.db import models
from django.templatetags.static import static
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.db.models import F
from questions.models import Question, Answer
from django.urls import reverse
import uuid
import os

class ProfileManager(models.Manager):
    def get_top_askers(self):
        return self.select_related('user').order_by('-questions_count')[:5]
    
def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    return os.path.join('users/avatars/', unique_name)

class Profile(models.Model):
    objects = ProfileManager()
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, verbose_name="Аватар")
    questions_count = models.PositiveIntegerField(default=0, verbose_name="Вопросов задано")
    answers_count = models.PositiveIntegerField(default=0, verbose_name="Ответов дано")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль пользователя: {self.user.username}"
    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return static('img/default-avatar.jpg')
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'user_id': self.user_id})
    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)

                if old_profile.avatar and old_profile.avatar != self.avatar:
                    if os.path.isfile(old_profile.avatar.path):
                        os.remove(old_profile.avatar.path)
            except Profile.DoesNotExist:
                pass
        super().save(*args, **kwargs)
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Question)
def update_user_questions_count(sender, instance, created, **kwargs):
    if created:
        Profile.objects.filter(user=instance.author).update(questions_count=F('questions_count') + 1)

@receiver(post_delete, sender=Question)
def decrement_user_questions_count(sender, instance, **kwargs):
    Profile.objects.filter(user=instance.author).update(questions_count=F('questions_count') - 1)

@receiver(post_save, sender=Answer)
def update_user_answers_count(sender, instance, created, **kwargs):
    if created:
        Profile.objects.filter(user=instance.author).update(answers_count=F('answers_count') + 1)

@receiver(post_delete, sender=Answer)
def decrement_user_answers_count(sender, instance, **kwargs):
    Profile.objects.filter(user=instance.author).update(answers_count=F('answers_count') - 1)