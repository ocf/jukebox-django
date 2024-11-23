from django.urls import path
from .views import queue_status, play_song, pause_song, next_song

urlpatterns = [
    path('queue-status/', queue_status, name='queue_status'),
    path('play/', play_song, name='play_song'),
    path('pause/', pause_song, name='pause_song'),
    path('next/', next_song, name='next_song'),
]