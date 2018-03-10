from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def set_session(request):

    request.session["abc"] = "meoup"
    return HttpResponse("设置session")


def get_session(request):

    session = request.session.get('abc')
    return HttpResponse(session)
