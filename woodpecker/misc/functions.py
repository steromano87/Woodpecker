import importlib
import itertools
import urllib


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


def split_query_string(query_string):
    output = {}
    # Split query string by '&'
    query_parameters = query_string.split('&')
    for query_parameter in query_parameters:
        post_couple = query_parameter.split('=')
        output[urllib.unquote_plus(post_couple[0])] = \
            urllib.unquote_plus(post_couple[1])

    return output
