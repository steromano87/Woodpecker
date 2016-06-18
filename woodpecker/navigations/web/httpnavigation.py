import abc

from woodpecker.navigations.generic.basenavigation import BaseNavigation
from woodpecker.options.web.httpoptions import http_options


class HttpNavigation(BaseNavigation):
    __metaclass__ = abc.ABCMeta

    def _default_options(self):
        super(HttpNavigation, self)._default_options()
        self.options.update(http_options())
