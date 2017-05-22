from django.utils import timezone
from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog
# from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import login
from django.views.decorators.http import last_modified

from . import views

# app_name is used to refence urls in template tags
app_name = 'sqrt_platform'

# patterns describe how app dispathes http-requests
# details: https://docs.djangoproject.com/en/1.11/topics/http/urls/
urlpatterns = [
    # js-catalog can be used to access translation fucntions on client-side
    url(r'^jsi18n/$',
        JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^$',
        views.index, name='index'),
    url(r'^lang/(?P<locale>.+)/$',
        views.index_locale, name='index_locale'),
    url(r'^calc/$',
        views.get_sqrt, name='get_sqrt'),
    url(r'^calc_ex/$',
        views.get_sqrt_ex, name='get_sqrt_ex'),
]
