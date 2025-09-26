from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/transactions/",
        views.TokenTransactionListView.as_view(),
        name="transaction-list",
    ),
    path("api/send-tokens/", views.send_tokens, name="send-tokens"),
    path("api/rewards/", views.RewardListView.as_view(), name="reward-list"),
    path("api/purchase-reward/", views.purchase_reward, name="purchase-reward"),
]
