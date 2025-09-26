from django.urls import path
from . import views

urlpatterns = [
    path("api/create-couple/", views.create_couple, name="create-couple"),
    path("api/my-couple/", views.my_couple, name="my-couple"),
]
