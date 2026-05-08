from django.db import models

class Profile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name='profile')
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль пользователя: {self.user.username}"
    

