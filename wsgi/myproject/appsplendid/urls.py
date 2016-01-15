from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.pack_list, name='pack_list'),
    url(r'^/new/$', views.pack_new, name='pack_new')
]
