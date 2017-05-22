from mpmath import *
from django.utils.translation import ugettext as _

DEFAULT_PRECISION = 16


def get_sqrt(str_number, precision=None):
    if precision is not None and len(precision) > 0:
        work_precision = int(precision)
    else:
        work_precision = DEFAULT_PRECISION

    mp.dps = work_precision
    result = sqrt(parse_number(str_number))

    return format_output(result)


def format_output(output):
    return str(output).replace('j', 'i') .lstrip('(').rstrip(')')


def parse_number(str_number, no_complex=False):
    str_number = str_number.strip(' ')

    try:
        if '+' in str_number:
            complex_parts = str_number.split('+')
            if len(complex_parts) != 2:
                raise ValueError
            else:
                return mpc(parse_number(complex_parts[0], True),
                           parse_number(complex_parts[1].rstrip('i'), True))
        if str_number.endswith('i'):
            if len(str_number) == 1:
                str_number = '1' + str_number
            return mpc(0, parse_number(str_number.rstrip('i')))
    except ValueError:
        pass

    try:
        return int(str_number)
    except ValueError:
        pass

    try:
        return float(str_number)
    except ValueError:
        pass

    raise Exception(_('"{}" is not an real or complex number')
                    .format(str_number))
