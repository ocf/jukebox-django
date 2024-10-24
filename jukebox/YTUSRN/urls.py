from django.urls import path

from . import views

app_name = "YTUSRN"

urlpatterns = [
    path("", views.index, name="index"),
    path("givemeYT", views.ytflp, name="ytflp"),
    path("THANKYOU!!", views.thankyou, name="thankyou"),
]