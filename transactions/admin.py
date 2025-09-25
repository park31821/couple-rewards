from django.contrib import admin
from .models import TokenTransaction, Reward


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "amount", "transaction_type", "created_at"]
    list_filter = ["transaction_type", "created_at"]
    search_fields = ["sender__username", "receiver__username", "message"]
    readonly_fields = ["created_at"]


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ["title", "token_cost", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "description"]
