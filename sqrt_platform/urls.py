from django.utils import timezone
from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog
# from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import login
from django.views.decorators.http import last_modified

from . import views

app_name = 'sqrt_platform'
last_modified_date = timezone.now()

urlpatterns = [
    url(r'^jsi18n/$',
        JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^$',
        views.index, name='index'),
    url(r'^(?P<locale>.{2})/$',
        views.index_locale, name='index_locale'),
    url(r'^calc/$',
        views.get_sqrt, name='get_sqrt'),
    url(r'^calc_ex/$',
        views.get_sqrt_ex, name='get_sqrt_ex'),
]
