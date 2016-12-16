from django.conf.urls import url

from . import views

app_name = 'doc'
urlpatterns = [
    url(r'^home/$', views.home, name='home'),
    url(r'^env/$', views.env, name='env'),
    url(r'^done/$', views.done, name='done'),
    url(r'^initsetup/$', views.initsetup, name='initsetup'),
    url(r'^importscript/$', views.importscript, name='importscript'),
]
