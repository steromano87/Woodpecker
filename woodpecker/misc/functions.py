import importlib
import itertools


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
