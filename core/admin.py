from django.contrib import admin
from core.models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    search_fields = ["user__username"]
    list_select_related = ["user"]