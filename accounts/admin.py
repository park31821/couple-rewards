from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Couple


@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    list_display = ["username", "email", "token_balance", "couple", "is_active"]
    list_filter = ["is_active", "couple"]

    fieldsets = UserAdmin.fieldsets + (
        ("Couple Information", {"fields": ("token_balance", "couple")}),
    )


@admin.register(Couple)
class CoupleAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name"]
