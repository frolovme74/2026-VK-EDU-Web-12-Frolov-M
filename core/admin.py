from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from core.models import Profile



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    search_fields = ["user__username"]
    list_select_related = ["user"]

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    class ProfileInline(admin.StackedInline):
        model = Profile
        can_delete = False
        verbose_name_plural = 'Профиль'
    inlines = (ProfileInline, )