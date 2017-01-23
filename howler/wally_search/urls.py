from django.conf.urls import url

from . import views

app_name = 'wally'
urlpatterns = [
    # ex: /wally/
    url(r'^$', views.searchmail, name='searchmail'),
    # ex: /wally/irc
    url(r'^irc/$', views.searchirc, name='searchirc'),
    # ex: /wally/
    url(r'^find/$', views.find, name='find'),
    # ex: /wally/updatesession/
    url(r'^updatesession$', views.update_session_values, name='updatesession'),
    # ex: /wally/detail/
    url(r'^irc/detail/$', views.detail_irc, name='detail_irc'),

]
