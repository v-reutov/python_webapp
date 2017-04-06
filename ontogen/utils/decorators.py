from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def ontogen_login_required(function):
    """Wrap for login_required decorator with specified login_url"""
    @login_required(login_url='ontogen:login')
    def function_wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return function_wrapper


def ajax_only(function):
    """Decorator for views that checks if requests was send via ajax"""
    def function_wrapper(*args, **kwargs):
        request = args[0]
        if not request.is_ajax():
            raise Http404
        return function(*args, **kwargs)
    return function_wrapper


def ajax_login_only(function):
    @ontogen_login_required
    @ajax_only
    def function_wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return function_wrapper


def permission_check(permission, action):
    """Decorator for views that checks if the active user has corresponding
    permission, redirecting to the error-page if not."""
    def permission_wrapper(function):
        @ontogen_login_required
        def function_wrapper(*args, **kwargs):
            request = args[0]
            if not request.user.has_perm(permission):
                return render(request, 'ontogen/permission_error.html',
                              {'action': action})
            return function(*args, **kwargs)
        return function_wrapper
    return permission_wrapper
