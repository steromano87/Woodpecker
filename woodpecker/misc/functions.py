import importlib


def import_sequence(sequence_file, sequence_class):
    sequence_module = sequence_file.replace('.py', '')
    module = importlib.import_module(
        '.{module}'.format(module=sequence_module),
        'sequences'
    )
    return getattr(module, sequence_class)
