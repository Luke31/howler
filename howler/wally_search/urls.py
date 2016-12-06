from django.conf.urls import url

from . import views

app_name = 'wally'
urlpatterns = [
    # ex: /wally/
    url(r'^$', views.search, name='search'),
    # ex: /wally/
    url(r'^find/$', views.find, name='find'),
    # ex: /wally/wally/
    #url(r^/results/$', views.results, name='results'),
    # ex: /wally/5/
    url(r'^(?P<email_id>[0-9]+)/$', views.detail, name='detail'),

    url(r'^synonyms/$', views.IndexView.as_view(), name='synonyms'),

]