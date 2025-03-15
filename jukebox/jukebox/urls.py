from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404
from django.shortcuts import redirect
from django.views.generic import RedirectView

urlpatterns = [
    path("YTUSRN/", include("YTUSRN.urls")),
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/YTUSRN/")),
]
