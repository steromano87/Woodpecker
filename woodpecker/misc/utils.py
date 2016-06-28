import string
import time
import datetime
import random
import socket
import os
import imp
import unicodedata


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


def get_ip_address():
    return socket.gethostbyname(socket.gethostname())


def create_class_from(str_class_name, str_module_name, str_module_path,
                      *args, **kwargs):
    arr_module_subpaths = [x[0] for x in os.walk(str_module_path)]
    obj_file, str_filename, str_description = \
        imp.find_module(str_module_name,
                        arr_module_subpaths)
    obj_package = imp.load_module(str_module_name, obj_file,
                                  str_filename, str_description)
    return getattr(obj_package, str_class_name)(*args, **kwargs)


def get_abs_path(str_path, str_cwd=None):
    if not str_cwd:
        str_cwd = os.getcwd()

    if os.path.isabs(str_path):
        return str_path
    else:
        tpl_scenario_path = (str_cwd, str_path)
        return os.path.normpath(''.join(tpl_scenario_path))


def unicode2ascii(mix_input):
    if isinstance(mix_input, basestring):
        return unicodedata.normalize('NFKD', mix_input).encode('ascii',
                                                               'ignore')
    else:
        return mix_input
