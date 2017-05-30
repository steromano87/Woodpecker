import six

from collections import OrderedDict

from woodpecker.io.correlators.basecorrelator import BaseCorrelator


class HtmlCorrelator(BaseCorrelator):
    def __init__(self, parsed_entries):
        super(HtmlCorrelator, self).__init__(parsed_entries)

        # List of referers
        self.referers = set()

        # Call hierarchy
        self._correlated = OrderedDict()

    def correlate(self):
        self._get_referers()
        self._calculate_call_hierarchy()
        return self._correlated

    def _get_referers(self):
        # Start reading the loaded entries and getting the Referers
        for entry in self._parsed_entries.get('entries', []):
            # If the call has a referer, add the referer to list
            for header_name, header_value \
                    in six.viewitems(entry.request.headers):
                if header_name.lower() in ('referer', 'referrer'):
                    self.referers.add(header_value)

    def _calculate_call_hierarchy(self):
        # Cycle through referers and entries and get the top calls
        for entry in self._parsed_entries.get('entries', []):
            if entry.url in self.referers:
                self._correlated[entry.url] = entry
            else:
                is_referred = False
                for header_name, header_value \
                        in six.viewitems(entry.request.headers):
                    if header_name.lower() in ('referer', 'referrer') \
                            and header_value in six.viewkeys(
                                self._correlated):
                        self._correlated[header_value].resources.append(
                            entry
                        )
                        is_referred = True
                        break

                if not is_referred:
                    self._correlated[entry.url] = entry
