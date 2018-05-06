from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^map', views.map, name='map'),
    url(r'^company_mapping$', views.company_mapping, name='company_mapping'),
    url(r'^edge_update$', views.edge_update, name='edge_update'),
    url(r'^historical$', views.historical, name='historical'),
    url(r'^', views.index, name='index'),
]