from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from jukebox.jukebox.backend.runner import Controller

controller = Controller()  

@api_view(['GET'])
def queue_status(request):
    current_song = controller.song_queue.queue[0].name if not controller.song_queue.empty() else None
    return Response({"current_song": current_song})

@api_view(['POST'])
def play_song(request):
    song_name = request.data.get('song_name')
    controller.play(song_name)
    return Response({"status": "playing", "song": song_name})

@api_view(['POST'])
def pause_song(request):
    controller.pause()
    return Response({"status": "paused"})

@api_view(['POST'])
def next_song(request):
    controller.next()
    return Response({"status": "next"})
