from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from .models import TokenTransaction, Reward
from .serializers import TokenTransactionSerializer, RewardSerializer
from accounts.models import User


class TokenTransactionListView(generics.ListAPIView):
    serializer_class = TokenTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return TokenTransaction.objects.filter(
                Q(sender=user) | Q(receiver=user)
            ).order_by("-created_at")
        return TokenTransaction.objects.none()


class RewardListView(generics.ListAPIView):
    queryset = Reward.objects.filter(is_active=True)
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_tokens(request):
    sender = request.user
    receiver_username = request.data.get("receiver_username")
    amount = request.data.get("amount")
    message = request.data.get("message", "")

    try:
        receiver = User.objects.get(username=receiver_username)
        amount = Decimal(str(amount))

        if sender.token_balance < amount:
            return Response(
                {"error": "Not enough token"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            sender.token_balance -= amount
            receiver.token_balance += amount
            sender.save()
            receiver.save()

            TokenTransaction.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
                transaction_type="send",
                message=message,
            )

        return Response({"message": "Token sent"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase_reward(request):
    user = request.user
    reward_id = request.data.get("reward_id")

    try:
        reward = Reward.objects.get(id=reward_id, is_active=True)

        if user.token_balance < reward.token_cost:
            return Response(
                {"error": "Not enough tokens"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user.token_balance -= reward.token_cost
            user.save()

            TokenTransaction.objects.create(
                sender=user,
                receiver=user,
                amount=reward.token_cost,
                transaction_type="reward",
                message=f"Purchased reward: {reward.title}",
            )

        return Response(
            {
                "message": "Completed reward purchase",
                "reward": reward.title,
                "remaining_balance": user.token_balance,
            },
            status=status.HTTP_200_OK,
        )

    except Reward.DoesNotExist:
        return Response(
            {"error": "Could not find reward"}, status=status.HTTP_404_BAD_REQUEST
        )
