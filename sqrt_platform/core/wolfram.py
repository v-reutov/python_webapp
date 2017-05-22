import wolframalpha
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

LAST_QUERY_TIME = timezone.now()
POD_WITH_ANSWER_INDEX = 3
COOLDOWN_SEC = 30


def get_sqrt(expression):
    client = wolframalpha.Client('LY7R7X-TLR279LWX6')
    res = client.query(expression)

    global LAST_QUERY_TIME

    sec_since_last_query = (timezone.now() - LAST_QUERY_TIME).total_seconds()
    if settings.DEBUG is False and sec_since_last_query < COOLDOWN_SEC:
        raise Exception(_('Next expression evaluate will be avaiable in {} sec.')
                        .format(COOLDOWN_SEC - sec_since_last_query))

    LAST_QUERY_TIME = timezone.now()
    if res['@success'] == 'true':
        for pod in list(res.info):
            if str(pod['@title']).endswith('positive'):
                return pod['subpod']['plaintext']
    raise Exception(_('Invalid expression. Try again in {} sec.')
                    .format(COOLDOWN_SEC))
