from django.urls import path, include
<<<<<<< HEAD
=======
from django.conf import settings
from django.conf.urls.static import static
>>>>>>> 7d29019 (Switch to uv, fix flake)

urlpatterns = [
    path('', include('jukebox.urls')),
]
<<<<<<< HEAD
=======

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve from STATICFILES_DIRS if needed
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
>>>>>>> 7d29019 (Switch to uv, fix flake)
