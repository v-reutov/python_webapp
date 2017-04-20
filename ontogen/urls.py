from django.utils import timezone
from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import login
from django.views.decorators.http import last_modified

from . import views

app_name = 'ontogen'
last_modified_date = timezone.now()

urlpatterns = [
    url(r'^jsi18n/$',
        last_modified(lambda req, **kw: last_modified_date)
        (JavaScriptCatalog.as_view()), name='javascript-catalog'),
    url(r'^$',
        views.index, name='index'),
    url(r'^result/$',
        views.generate_ont, name='generate'),
    url(r'^history/$',
        views.usage_history, name='usage_history'),
    url(r'^tree/$',
        views.get_tree_data, name='get_tree'),
    url(r'^pattern/(?P<pk>[0-9]+)/$',
        views.PatternDetailView.as_view(), name='pattern_view'),
    url(r'^pattern/add/$',
        views.PatternCreateView, name='pattern_add'),
    url(r'^pattern/(?P<pattern_id>[0-9]+)/edit/$',
        views.PatternUpdateView, name='pattern_update'),
    url(r'^pattern/(?P<pk>[0-9]+)/delete/$',
        views.PatternDeleteView.as_view(), name='pattern_delete'),
    url(r'^instruction/(?P<pk>[0-9]+)/$',
        views.InstructionDetailView.as_view(), name='instruction_view'),
    url(r'^instruction/add/$',
        views.InstructionCreateView.as_view(
            # Translators: This string represents view's header
            extra_context={'header': _('Add new instruction')}),
        name='instruction_add'),
    url(r'^instruction/(?P<pk>[0-9]+)/edit/$',
        views.InstructionUpdateView.as_view(
            # Translators: This string represents view's header
            extra_context={'header': _('Edit instruction')}),
        name='instruction_update'),
    url(r'^instruction/(?P<pk>[0-9]+)/delete/$',
        views.InstructionDeleteView.as_view(), name='instruction_delete'),
    url(r'^login/$', login,
        {'template_name': 'ontogen/login.html'}, name='login'),
    url(r'^ok/', views.ok_response, name='ok')
]
