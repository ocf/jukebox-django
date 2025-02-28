from django.urls import path

from . import views

app_name = "YTUSRN"

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
]