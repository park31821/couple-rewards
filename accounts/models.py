from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    token_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    couple = models.ForeignKey(
        "Couple", on_delete=models.SET_NULL, null=True, blank=True
    )


class Couple(AbstractUser):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
