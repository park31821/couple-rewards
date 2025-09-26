from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import User, Couple
from .serializers import UserSerializer, CoupleSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_couple(request):
    user = request.user
    couple_name = request.data.get("couple_name")
    partner_username = request.data.get("partner_username")

    if user.couple:
        return Response(
            {"error": "You are already a couple."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        partner = User.objects.get(username=partner_username)

        if partner.couple:
            return Response(
                {"error": "This user is already a couple."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            couple = Couple.objects.create(name=couple_name)

            user.couple = couple
            partner.couple = couple
            user.save()
            partner.save()

        return Response(
            {
                "message": "Couple created.",
                "couple_name": couple.name,
                "members": [user.username, partner.username],
            },
            status=status.HTTP_201_CREATED,
        )

    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_couple(request):
    user = request.user

    if not user.couple:
        return Response({"error": "You are not a couple."}, status=status.HTTP_200_OK)

    couple_members = User.objects.filter(couple=user.couple)

    return Response(
        {
            "couple_name": user.couple.name,
            "create_at": user.couple.created_at,
            "members": [member.username for member in couple_members],
            "is_active": user.couple.is_active,
        },
        status=status.HTTP_200_OK,
    )
