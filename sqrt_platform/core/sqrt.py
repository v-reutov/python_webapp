from mpmath import *
from django.utils.translation import ugettext as _
import re

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


def parse_number(str_number):
    try:
        check_parentheses(str_number)
        return parse_number_impl(clean_number(str_number))
    except ValueError:
        # ValueError on all known types
        raise Exception(_('"{}" is not a real or complex number')
                        .format(str_number))


def parse_number_impl(str_number, no_complex=False):
    try:
        # Try parse a complex number
        complex_parts = \
            re.findall(
                r'^\s*(?:([+-]*\s*\w+(?:[.]\w*)?))?\s*([+-]*\s*\w*(?:[.]\w*)?\s*i)\s*$',
                str_number)
        if complex_parts != []:
            return mpc(parse_number_impl(complex_parts[0][0], True),
                       parse_number_impl(complex_parts[0][1].rstrip('i'), True))
        else:
            raise ValueError
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

    raise ValueError


def clean_number(str_number):
    # remove parentheses and whitespace
    str_number = re.sub(r'\(', '', str_number)
    str_number = re.sub(r'\)', '', str_number)
    str_number = re.sub(r'\s+', '', str_number)
    # -+ is -
    str_number = re.sub(r'[+]*-[+]*', '-', str_number)
    # -- is +
    str_number = re.sub(r'--', '+', str_number)
    # ++ is +
    str_number = re.sub(r'[+]+', '+', str_number)

    return str_number


def check_parentheses(string):
    count = 0
    for i in string:
        if i == "(":
            count += 1
        elif i == ")":
            count -= 1
        if count < 0:
            return False
    if count != 0:
        raise ValueError
