import datetime


class BaseResource(object):
    def __init__(self, name=None):
        # Resource unique name
        self.name = name or None

        # Inner resource timings instance
        self.timings = BaseResourceTimings()

        # Resource's linked resources
        self.resources = list()

    def __repr__(self):
        return '{classname} - {name}'.format(
            classname=self.__class__.__name__,
            name=self.name,
        )


class BaseResourceTimings(object):
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.duration = 0.0
        self.elapsed = {
            'from_start': 0.0,
            'from_start_of_previous': 0.0,
            'from_end_of_previous': 0.0
        }
