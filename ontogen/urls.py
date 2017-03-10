from django.conf.urls import url
from . import views

app_name = 'ontogen'
urlpatterns = [
    url(r'^generate/$', views.generate_ont, name='generate'),
    url(r'^$', views.index, name='index'),
]
