import copy
import six

from woodpecker.io.generators.basegenerator import BaseGenerator


class HttpSequenceGenerator(BaseGenerator):
    def generate(self,
                 filename,
                 sequence_name='NewSequence',
                 folder='sequences',
                 **kwargs):
        self.base_sequence_name = sequence_name

        self._generate_headers()
        self._generate_class_definition(sequence_name)
        self._generate_calls(**kwargs)

        self._dump_buffers(filename, folder=folder)

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

    def _generate_steps_method_definition(self):
        self.buffer.write('    def steps(self):\n')

    def _generate_calls(self,
                        group_resources=True,
                        auto_assert=True,
                        think_time_threshold=2.0,
                        new_sequence_threshold=5.0,
                        async_request_threshold=0.1):
        # Generate steps call
        self._generate_steps_method_definition()

        previous_entry = None
        for entry in six.viewvalues(self._parsed_entries):
            self._generate_single_entry(entry,
                                        previous_entry,
                                        group_resources,
                                        auto_assert,
                                        think_time_threshold,
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
                                                think_time_threshold,
                                                new_sequence_threshold,
                                                async_request_threshold,
                                                True)
                self.buffer.write('        self.end_async_pool()\n\n')

        # In the end, clean and store the current buffer
        self._clean_buffer()

    def _generate_single_entry(self,
                               entry,
                               previous_entry,
                               group_resources,
                               auto_assert,
                               think_time_threshold,
                               new_sequence_threshold,
                               async_request_threshold,
                               _async):
        # Determine if the previous call has an elapsed higher than
        # the new sequence threshold. In such case, start a new sequence
        if entry.timings.elapsed[
                'from_end_of_previous'] / 1000 > new_sequence_threshold:
            self._clean_buffer()
            sequence_name = '{basename}_{index}'.format(
                basename=self.base_sequence_name,
                index=len(self.buffer_list)
            )
            self._generate_headers()
            self._generate_class_definition(sequence_name)
            self._generate_steps_method_definition()

        # If the elapsed is greater than the think time threshold,
        # set the think time
        elif entry.timings.elapsed[
                'from_end_of_previous'] / 1000 > think_time_threshold:
            self.buffer.write('\n\n')
            self.buffer.write('        self.think_time({amount})'.format(
                amount=entry.timings.elapsed['from_end_of_previous'] * 1000
            ))
            self.buffer.write('\n\n')

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
