from django.conf.urls import url
from django.contrib.auth.views import login
from django.utils.translation import ugettext as _

from . import views

app_name = 'ontogen'
urlpatterns = [
    url(r'^$',
        views.index, name='index'),
    url(r'^result/$',
        views.generate_ont, name='generate'),
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
    url(r'^ok/', views.ok_response, name='ok'),
]
