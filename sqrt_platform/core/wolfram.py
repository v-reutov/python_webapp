import wolframalpha
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

LAST_QUERY_TIME = timezone.now()
POD_WITH_ANSWER_INDEX = 3
COOLDOWN_SEC = 30


def get_sqrt(expression):
    client = wolframalpha.Client('LY7R7X-TLR279LWX6')
    response = client.query(expression)

    # deny frequently querying: wolframapi allows only 2000 request per month
    global LAST_QUERY_TIME
    sec_since_last_query = (timezone.now() - LAST_QUERY_TIME).total_seconds()

    if settings.DEBUG is False and sec_since_last_query < COOLDOWN_SEC:
        raise Exception(_('Next expression evaluate will be available in {} sec.')
                        .format(COOLDOWN_SEC - sec_since_last_query))

    LAST_QUERY_TIME = timezone.now()

    # titles of pods where sqrt can be located (depends on the input)
    possible_answer_locations = [
        'positive', 'result'
    ]
    if response['@success'] == 'true':
        for title in possible_answer_locations:
            result = search_pod(response, title)
            if result is not None:
                return result
        return expression
    else:
        raise Exception(_('Invalid expression. Try again in {} sec.')
                        .format(COOLDOWN_SEC))


def search_pod(response, title):
    """Try to find pod with corresponding title.
    Titles are compared with endswith"""
    low_title = title.lower()
    for pod in list(response.info):
            if str(pod['@title']).lower().endswith(low_title):
                return pod['subpod']['plaintext']
    return None
