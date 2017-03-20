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


def parse_set_cookie_header(cookie_string):
    cookie_dict = {}
    cookie_pairs = cookie_string.split('; ')
    for cookie_entry in cookie_pairs:
        cookie_couple = cookie_entry.split('=')
        if cookie_couple[0].lower() \
            not in ('expires', 'max-age', 'domain', 'path',
                    'secure', 'httponly', 'samesite'):
            cookie_dict['name'] = urllib.unquote_plus(cookie_couple[0])
            cookie_dict['value'] = urllib.unquote_plus(cookie_couple[1])
        elif cookie_couple[0].lower() in ('secure', 'httponly'):
            cookie_dict[cookie_couple[0].lower()] = True
        else:
            cookie_dict[cookie_couple[0].lower()] = \
                urllib.unquote_plus(cookie_couple[1])
    return cookie_dict


def get_eol(test_string):
    line_endings = ('\r\n', '\r', '\n')
    for ending in line_endings:
        if ending in test_string:
            return ending
