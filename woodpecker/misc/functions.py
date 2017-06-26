import importlib
import itertools
import urllib
import datetime
import re


def import_sequence(sequence_file, sequence_class):
    sequence_module = sequence_file.replace('.py', '')
    module = importlib.import_module(
        '.{module}'.format(module=sequence_module),
        'sequences'
    )
    class_object = getattr(module, sequence_class)
    return class_object()


def split_by_element(iterable, splitters):
    return [
        list(g)
        for k, g in itertools.groupby(iterable,
                                      lambda x:x in splitters) if not k
        ]


def decode_datetime(obj):
    if b'__datetime__' in obj:
        obj = obj.isoformat()
    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        obj = obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()
    return obj


def get_eol(test_string):
    line_endings = ('\r\n', '\r', '\n')
    for ending in line_endings:
        if ending in test_string:
            return ending


def cc2underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
