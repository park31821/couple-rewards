from rest_framework import serializers
from .models import User, Couple


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "token_balance"]


class CoupleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Couple
        fields = ["id", "name", "create_at", "is_active"]
