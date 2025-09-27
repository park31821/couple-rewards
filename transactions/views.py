from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Count, Sum, Q
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_statistics(request):
    user = request.user

    thirty_days_ago = timezone.now() - timedelta(days=30)

    set_stats = TokenTransaction.objects.filter(
        sender=user, created_at__gte=thirty_days_ago
    ).aggregate(total_sent=Sum("amount"), sent_count=Count("*"))

    received_stats = TokenTransaction.objects.filter(
        receiver=user, created_at__gte=thirty_days_ago
    ).aggregate(total_received=Sum("amount"), received_count=Count("*"))

    reward_stats = TokenTransaction.objects.filter(
        sender=user, transaction_type="reward", created_at__gte=thirty_days_ago
    ).aggregate(total_rewards=Sum("amount"), reward_count=Count("*"))

    return Response(
        {
            "user": user.username,
            "current_balance": user.token_balance,
            "period": "Last 30 days",
            "sent": {
                "total_amount": set_stats["total_sent"] or 0,
                "transaction_count": set_stats["sent_count"] or 0,
            },
            "received": {
                "total_amount": received_stats["total_received"] or 0,
                "transaction_count": received_stats["received_count"] or 0,
            },
            "rewards": {
                "total_amount": reward_stats["total_rewards"] or 0,
                "transaction_count": reward_stats["reward_count"] or 0,
            },
        },
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def couple_statistics(request):
    user = request.user

    if not user.couple:
        return Response(
            {"error": "You are not a couple."}, status=status.HTTP_400_BAD_REQUEST
        )

    couple_members = User.objects.filter(couple=user.couple)
    member_ids = [member.id for member in couple_members]

    thirty_days_ago = timezone.now() - timedelta(days=30)

    couple_transactions = TokenTransaction.objects.filter(
        sender__in=member_ids,
        receiver__in=member_ids,
        transaction_type="send",
        created_at__gte=thirty_days_ago,
    )

    total_stats = couple_transactions.aggregate(
        total_exchanges=Sum("amount"), exchange_count=Count("*")
    )

    member_stats = []
    for member in couple_members:
        member_data = {
            "username": member.username,
            "current_balance": member.token_balance,
            "sent_to_partner": couple_transactions.filter(sender=member).aggregate(
                total=Sum("amount"), count=Count("*")
            ),
            "received_from_partner": couple_transactions.filter(
                receiver=member
            ).aggregate(total=Sum("amount"), count=Count("*")),
        }

        member_stats.append(member_data)

    return Response(
        {
            "couple_name": user.couple.name,
            "couple_since": user.couple.created_at,
            "period": "Last 30 days",
            "total_exchanges": {
                "amount": total_stats["total_exchanges"] or 0,
                "count": total_stats["exchange_count"] or 0,
            },
            "members": member_stats,
        }
    )
