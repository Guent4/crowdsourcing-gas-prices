from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'backend_sync', views.backend_sync, name='backend_sync'),
    url(r'^upload_gas_price', views.upload_gas_price, name='upload_gas_price'),
    url(r'^company_mapping', views.company_mapping, name='company_mapping'),
    url(r'^map', views.map, name='map'),
    url(r'^', views.index, name='index'),
]
