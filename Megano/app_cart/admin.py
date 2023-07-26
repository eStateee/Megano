from django.contrib import admin
from .models import UserCart


@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "good", "amount",)
    list_display_links = ("pk",)
