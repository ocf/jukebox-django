from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404
from django.shortcuts import redirect

def custom_404(request, exception):
    return redirect('/YTUSRN')

handler404 = custom_404

urlpatterns = [
    path("YTUSRN/", include("YTUSRN.urls")),
    path("admin/", admin.site.urls),
]
