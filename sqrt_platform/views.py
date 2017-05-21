from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import activate
from django.utils.translation import ugettext as _

from .core import sqrt
# Create your views here.

LANGUAGES_CONTEXT = {'available_languages': ['ru', 'en']}


def ajax_only(function):
    """Decorator for views that checks if requests was send via ajax"""
    def function_wrapper(*args, **kwargs):
        request = args[0]
        if not request.is_ajax():
            raise Http404
        return function(*args, **kwargs)
    return function_wrapper


def index(request):
    return render(request, 'sqrt_platform/index.html', LANGUAGES_CONTEXT)


def index_locale(request, locale):
    activate(locale)
    request.session[translation.LANGUAGE_SESSION_KEY] = locale
    return render(request, 'sqrt_platform/redir_to_index.html')


@ajax_only
def get_sqrt(request):
    response = HttpResponse()
    response['result'] = None
    response['error'] = None
    response['debug'] = request.POST

    if request.POST.get('number') == "":
        response['error'] = _('Number is required')
    else:
        try:
            response['result'] = \
                sqrt.get_sqrt(request.POST.get('number', None),
                              request.POST.get('precision', None))
        except Exception as e:
            response['error'] = str(e)
    return response
