from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("YTUSRN/", include("YTUSRN.urls")),
    path("admin/", admin.site.urls),
]
