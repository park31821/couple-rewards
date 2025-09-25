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


class RewardListView(generics.ListAPIView):
    queryset = Reward.objects.filter(is_active=True)
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]
