import urllib.parse
import requests

from django.conf import settings


class SimplyFireError(Exception):
    pass


class SimplyFireClient:
    @classmethod
    def __url(cls, api_call):
        api_url = urllib.parse.urljoin(
            settings.SIMPLYFIRE_ADDRESS,
            'v{0}/api/{1}/'.format(settings.SIMPLYFIRE_API_VERSION, settings.SIMPLYFIRE_PROJECT_ID))

        return urllib.parse.urljoin(api_url, api_call)

    @classmethod
    def __headers(cls):
        return {
            'Authorization': settings.SIMPLYFIRE_TOKEN
        }

    @classmethod
    def __enhance_params(cls, params):
        params = params or {}
        params['auth_token'] = settings.SIMPLYFIRE_TOKEN
        return params

    # TODO: make get & post private

    @classmethod
    def get(cls, request, params=None):
        try:
            return requests.get(cls.__url(request), params=cls.__enhance_params(params))
        except (requests.ConnectionError, requests.ConnectTimeout):
            raise SimplyFireError

    @classmethod
    def post(cls, request, data, params=None):
        try:
            return requests.post(cls.__url(request), json=data, params=cls.__enhance_params(params))
        except (requests.ConnectionError, requests.ConnectTimeout):
            raise SimplyFireError

    @classmethod
    def post_files(cls, request, files, params=None):
        try:
            return requests.post(cls.__url(request), files=files, params=cls.__enhance_params(params))
        except (requests.ConnectionError, requests.ConnectTimeout):
            raise SimplyFireError

    @classmethod
    def __check_response(cls, response):
        if not response.ok:
            raise SimplyFireError

    @classmethod
    def create_directory(cls, name, path):
        """Creates directory with specified name under path. Returns full path of created directory"""
        response = SimplyFireClient.post('files/createDirectory', {'name': name}, {'path': path})

        cls.__check_response(response)

        return urllib.parse.urljoin(path + '/', name + '/')

    @classmethod
    def upload_file(cls, file, path):
        """Uploads a file to specified path. Returns id of uploaded file"""
        response = cls.post_files('files/upload', {'File': file}, {'path': path})

        cls.__check_response(response)

        return response.json()['response']['id']

    @classmethod
    def get_file(cls, file_id):
        """Gets a file by gived id"""
        api_call = 'files/{}/download'.format(file_id)
        return SimplyFireClient.get(api_call)
