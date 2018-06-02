import urllib.parse
import requests

from django.conf import settings


class SimplyFireClient:
    @classmethod
    def url(cls, api_call):
        api_url = urllib.parse.urljoin(
            settings.SIMPLYFIRE_ADDRESS,
            'v{0}/api/{1}/'.format(settings.SIMPLYFIRE_API_VERSION, settings.SIMPLYFIRE_PROJECT_ID))

        return urllib.parse.urljoin(api_url, api_call)

    @classmethod
    def headers(cls):
        return {
            'Authorization': settings.SIMPLYFIRE_TOKEN
        }

    @classmethod
    def enhance_params(cls, params):
        params = params or {}
        params['auth_token'] = settings.SIMPLYFIRE_TOKEN
        return params

    @classmethod
    def get(cls, request, params=None):
        # return requests.get(cls.url(request), headers=cls.headers())
        return requests.get(cls.url(request), params=cls.enhance_params(params))

    @classmethod
    def post(cls, request, data, params=None):
        # return requests.post(cls.url(request), data, headers=cls.headers())
        return requests.post(cls.url(request), json=data, params=cls.enhance_params(params))

    @classmethod
    def post_files(cls, request, files, params=None):
        # return requests.post(cls.url(request), data, headers=cls.headers())
        return requests.post(cls.url(request), files=files, params=cls.enhance_params(params))
