import datetime


class BaseResource(object):
    def __init__(self, name=None):
        # Resource unique name
        self.name = name or None

        self.timings = BaseResourceTimings()

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
