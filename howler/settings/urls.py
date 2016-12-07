from django.conf.urls import url

from . import views

app_name = 'settings'
urlpatterns = [
    url(r'^synonym/$', views.SynonymIndex.as_view(), name='synonym'),
    url(r'^synonym/create$', views.SynonymCreate.as_view(), name='synonym_new'),
    url(r'^synonym/edit/(?P<pk>\d+)$$', views.SynonymUpdate.as_view(), name='synonym_edit'),
    url(r'^synonym/delete/(?P<pk>\d+)$$', views.synonym_delete, name='synonym_delete'),
    url(r'^synonym/import/$', views.synonym_import, name='synonym_import'),
]

