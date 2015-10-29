import string
import time
import datetime
import random

__author__ = 'Stefano.Romano'


def random_id(int_length):
    return ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits) for _ in range(
        int_length))


def get_timestamp(bool_is_string=True):
    if bool_is_string:
        return datetime.datetime.fromtimestamp(time.time()).strftime(
            '%Y-%m-%d %H:%M:%S.%f')
    else:
        return datetime.datetime.fromtimestamp(time.time())


def print_sample():
    print('Hello world')


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
