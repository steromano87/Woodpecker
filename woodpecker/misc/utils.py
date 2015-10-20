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
