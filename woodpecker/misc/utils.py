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


def import_from_path(str_path, str_class_name, dic_kwargs=None):
    class_inst = None
    py_mod = None

    if not dic_kwargs:
        dic_kwargs = {}

    mod_name, file_ext = os.path.splitext(os.path.split(str_path)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, str_path)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, str_path)

    if hasattr(py_mod, str_class_name):
        class_inst = getattr(py_mod, str_class_name)(**dic_kwargs)

    return class_inst


def get_abs_path(str_path, str_cwd=None):
    if not str_cwd:
        str_cwd = os.getcwd()

    if os.path.isabs(str_path):
        return str_path
    else:
        tpl_scenario_path = (str_cwd, str_path)
        return os.path.normpath(''.join(tpl_scenario_path))


def logify(str_message, str_submodule='MAIN'):
    return ''.join(('[', get_timestamp(), ']',
                    '\t', '[', str_submodule, ']',
                    '\t', str_message))


def unicode2ascii(mix_input):
    if isinstance(mix_input, basestring):
        return unicodedata.normalize('NFKD', mix_input).encode('ascii', 'ignore')
    else:
        return mix_input
