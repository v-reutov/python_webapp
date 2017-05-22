from mpmath import *
from django.utils.translation import ugettext as _

DEFAULT_PRECISION = 16


def get_sqrt(str_number, precision=None):
    #  
    # ░░░░░░░░░▄░░░░░░░░░░░░░░▄
    # ░░░░░░░░▌▒█░░░░░░░░░░░▄▀▒▌
    # ░░░░░░░░▌▒▒█░░░░░░░░▄▀▒▒▒▐
    # ░░░░░░░▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐
    # ░░░░░▄▄▀▒░▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐
    # ░░░▄▀▒▒▒░░░▒▒▒░░░▒▒▒▀██▀▒▌
    # ░░▐▒▒▒▄▄▒▒▒▒░░░▒▒▒▒▒▒▒▀▄▒▒
    # ░░▌░░▌█▀▒▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒
    # ░▐░░░▒▒▒▒▒▒▒▒▌██▀▒▒░░░▒▒▒▀▌
    # ░▌░▒▄██▄▒▒▒▒▒▒▒▒▒░░░░░░▒▒▒▌
    # ░▌ ▐▄█▄█▌▄░▀▒▒░░░░░░░░░░▒▒▐
    # ▐▒▒▐▀▐▀▒░▄▄▒▄▒▒▒▒▒▒░▒░▒░▒▒▒▌
    # ▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒▒▒░▒░▒░▒▐
    # ░▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒░▒░▒░▒░▒▒▌
    # ░▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▒▄▒▒
    # ░░▀▄▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▄▒▒▒▒
    # ░░░░▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀
    # ░░░░░░▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀
    # ░░░░░░░░░▒▒▒▒▒▒▒▒▒▒
    # such function very sqrt wow
    if precision is not None and len(precision) > 0:
        work_precision = int(precision)
    else:
        work_precision = DEFAULT_PRECISION

    # mp.dps defines precision in numbers of decimal places
    mp.dps = work_precision
    result = sqrt(parse_number(str_number))

    return format_output(result)


def format_output(output):
    # Replacing j with i for complex numbers and removing brackets
    # Causing by using mpmath library
    return str(output).replace('j', 'i') .lstrip('(').rstrip(')')


def parse_number(str_number, no_complex=False):
    str_number = str_number.strip(' ')

    try:
        # Try parse a complex number
        if '+' in str_number:
            complex_parts = str_number.split('+')
            if len(complex_parts) != 2:
                # There can be only one '+' in complex number representaion
                raise ValueError
            else:
                # Parse real and imaginary part via recursive call
                # 'no_complex': complex number is present by real numbers only
                return mpc(parse_number(complex_parts[0], True),
                           parse_number(complex_parts[1].rstrip('i'), True))

        # Only imaginary part given
        if str_number.endswith('i'):
            # Handle i separatly
            if len(str_number) == 1:
                return mpc(0, 1)
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

    # ValueError on all known types
    raise Exception(_('"{}" is not a real or complex number')
                    .format(str_number))
