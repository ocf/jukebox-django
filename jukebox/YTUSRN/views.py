from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from .models import UserField


def index(request):
    current_users = get_object_or_404(UserField)
    try:
        username_input = request.POST["username"]
        print(username_input)
    except KeyError:
        return render(
            request,
            "jukebox/index.html",
        )
    else:
        return HttpResponseRedirect(reverse("YTUSRN:ytflp"))



def ytflp(request):
    return render(request, "jukebox/ytflp.html")


def thankyou(request):
    return render(request, "jukebox/thankyou.html")
