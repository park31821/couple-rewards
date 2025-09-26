from rest_framework import serializers
from .models import TokenTransaction, Reward


class TokenTransactionSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(
        source="sender.username",
        read_only=True,
    )
    receiver_username = serializers.CharField(
        source="receiver.username",
        read_only=True,
    )

    class Meta:
        model = TokenTransaction
        fields = [
            "id",
            "sender",
            "receiver",
            "sender_username",
            "receiver_username",
            "amount",
            "transaction_type",
            "message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ["id", "title", "description", "token_cost", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
