from django.shortcuts import render
from django.conf import settings as djsettings


def home(request):
    return render(request, 'doc/home.html')


def env(request):
    return render(request, 'doc/env.html')


def done(request):
    return render(request, 'doc/done.html')


def importscript(request):
    return render(request, 'doc/importscript.html')


def irc(request):
    return render(request, 'doc/irc.html')
