from django.db import models
from django.conf import settings


class TokenTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("send", "Send"),
        ("receive", "Receive"),
        ("reward", "Reward Purchase"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_transactions",
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_transactions",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount} tokens"


class Reward(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    token_cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.token_cost} tokens)"
