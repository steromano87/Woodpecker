import os
import copy
import six

from woodpecker.io.generators.basegenerator import BaseGenerator


class HttpSequenceGenerator(BaseGenerator):
    def generate(self, filename, sequence_name='NewSequence', **kwargs):
        self._generate_headers()
        self._generate_class_definition(sequence_name)
        self._generate_calls(**kwargs)

        with open(os.path.abspath(filename), 'w') as fp:
            fp.write(self._fix_code())

    def _generate_headers(self):
        self.buffer.write(
            'from woodpecker.sequences.httpsequence import HttpSequence'
        )
        self.buffer.write('\n\n')

    def _generate_class_definition(self, sequence_name):
        self.buffer.write(
            'class {classname}(HttpSequence):\n'.format(
                classname=sequence_name
            )
        )

    def _generate_calls(self,
                        group_resources=True,
                        auto_assert=True,
                        new_sequence_threshold=7.0,
                        async_request_threshold=0.1):
        # Generate steps call
        self.buffer.write('    def steps(self):\n')

        previous_entry = None
        for entry in six.viewvalues(self._parsed_entries):
            self._generate_single_entry(entry,
                                        previous_entry,
                                        group_resources,
                                        auto_assert,
                                        new_sequence_threshold,
                                        async_request_threshold,
                                        False)
            self.buffer.write('\n')
            previous_entry = copy.deepcopy(entry)
            if not group_resources and len(entry.resources) > 0:
                self.buffer.write('        self.start_async_pool()\n\n')
                for resource in entry.resources:
                    self._generate_single_entry(resource,
                                                previous_entry,
                                                group_resources,
                                                auto_assert,
                                                new_sequence_threshold,
                                                async_request_threshold,
                                                True)
                self.buffer.write('        self.end_async_pool()\n\n')

    def _generate_single_entry(self,
                               entry,
                               previous_entry,
                               group_resources,
                               auto_assert,
                               new_sequence_threshold,
                               async_request_threshold,
                               _async):
        # Write the call according to the method
        if entry.method.upper() in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
            self.buffer.write(
                '        self.{async}{method}('.format(
                    async='async_' if _async else '',
                    method=entry.method.lower()
                )
            )
            # Write the URL
            self.buffer.write("'{url}'\n".format(url=entry.url))
            self.buffer.write(', ')
        else:
            self.buffer.write(
                '        self.http_request('
            )
            # Write the URL
            self.buffer.write("'{url}'\n".format(url=entry.url))
            self.buffer.write(", method='{method}', ".format(
                method=entry.method.upper()
            ))

        # Check if URL is resource
        if entry.mime_type() in (
            'text/css',
            'application/javascript',
            'image/png'
            'image/jpeg'
            'image/gif',
            'image/tiff'
        ):
            self.buffer.write('is_resource=True, ')

        # If auto assert is true, perform some checks on the entry response
        # text to perform a semi-intelligent assert
        # TODO: add automatic assert feature

        # If group resources is true, group them in the with_resources clause
        if group_resources and len(entry.resources) > 0:
            self.buffer.write('with_resources=(')
            for resource in entry.resources:
                if resource.method == 'GET':
                    self.buffer.write("'{url}'".format(url=resource.url))
                else:
                    self.buffer.write("('{url}', '{method}')")
                self.buffer.write(',')
            self.buffer.write(')')

        # Close the method call
        self.buffer.write(')\n\n')
