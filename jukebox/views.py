import jsonpickle
from django.http import HttpResponse
from django.shortcuts import render
from .controller import get_controller


def dashboard(request):
    return render(request, 'dashboard.html')


def state_api(request):
    controller = get_controller()
    state = controller.get_state()
    data = jsonpickle.encode(state, unpicklable=False)
    return HttpResponse(data, content_type="application/json")
