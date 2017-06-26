import six

from copy import deepcopy

from woodpecker.io.generators.basegenerator import BaseGenerator
from woodpecker.io.generators.basegenerator import CommandGenerator


class HttpSequenceGenerator(BaseGenerator):
    def __init__(self, event_collection):
        super(HttpSequenceGenerator, self).__init__(event_collection)

        # Added async active flag to handle async pool
        self.async_pool_active = False

    def generate(self,
                 filename,
                 sequence_name='NewSequence',
                 folder='sequences'):
        self.base_sequence_name = sequence_name

        self._generate_headers()
        self._generate_class_definition(sequence_name)
        self._generate_calls()

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

    def _generate_calls(self):
        # Generate steps call
        self._generate_steps_method_definition()

        self._handle_event_list(self.events.all_events())

        # In the end, clean and store the current buffer
        self._clean_buffer()

    def _handle_event_list(self, event_list):
        for event in event_list:
            if event.type in ('http_request', 'http_load_page'):
                self._generate_load_page_entry(event)
            elif event.type == 'http_load_resource':
                self._generate_load_resource_entry(event)
            elif event.type == 'http_async_request':
                self._generate_async_request_entry(event)
            elif event.type == 'http_set_headers':
                self._generate_set_header_entry(event)
            elif event.type == 'http_set_cookie':
                self._generate_set_cookie_entry(event)
            elif event.type == 'think_time':
                self._generate_think_time_entry(event)
            elif event.type == 'sequence_break':
                self._clean_buffer()
                sequence_name = '{basename}_{index}'.format(
                    basename=self.base_sequence_name,
                    index=len(self.buffer_list)
                )
                self._generate_headers()
                self._generate_class_definition(sequence_name)

        if self.async_pool_active:
            async_pool = CommandGenerator('self.end_async_pool', indents=2)
            self.buffer.write(async_pool.generate_command())
            self.buffer.write('\n\n')
            self.async_pool_active = False

    def _generate_http_request_entry(self,
                                     event,
                                     is_resource=False,
                                     is_async=False):
        # Check for prepended events
        if event.has_prepended_events():
            self._handle_event_list(event.prepended_events.all_events())

        if event.data['method'].upper() \
                in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
            if is_async:
                load_page = CommandGenerator(
                    'self.async_{method}'.format(
                        method=event.data['method'].lower()),
                    indents=2
                )
            else:
                load_page = CommandGenerator(
                    'self.{method}'.format(
                        method=event.data['method'].lower()),
                    indents=2
                )
            load_page.add_argument(event.data['url'])
        else:
            if is_async:
                load_page = CommandGenerator(
                    'self.async_http_request',
                    indents=2
                )
            else:
                load_page = CommandGenerator(
                    'self.http_request',
                    indents=2
                )
            load_page.add_argument(event.data['url'])
            load_page.add_named_argument('method',
                                         event.data['method'].lower())

        # Add headers
        if len(event.data['headers']) > 0:
            load_page.add_named_argument('headers', event.data['headers'])

        # Add query string params
        if len(event.data['query_params']) > 0:
            load_page.add_named_argument('params', event.data['query_params'])

        # Add POST form data
        if len(event.data['form_data']) > 0:
            load_page.add_named_argument('data', event.data['form_data'])

        # Mark if resource or not
        load_page.add_named_argument('is_resource', is_resource)

        # Add command to buffer
        self.buffer.write(load_page.generate_command())

        # Check for appended events
        if event.has_appended_events():
            self._handle_event_list(event.appended_events.all_events())

    def _generate_load_page_entry(self, event):
        if self.async_pool_active:
            async_pool = CommandGenerator('self.end_async_pool', indents=2)
            self.buffer.write(async_pool.generate_command())
            self.buffer.write('\n\n')
            self.async_pool_active = False

        self._generate_http_request_entry(event,
                                          is_async=False,
                                          is_resource=False)

    def _generate_load_resource_entry(self, event):
        if not self.async_pool_active:
            async_pool = CommandGenerator('self.start_async_pool', indents=2)
            self.buffer.write(async_pool.generate_command())
            self.buffer.write('\n\n')
            self.async_pool_active = True

        self._generate_http_request_entry(event,
                                          is_async=True,
                                          is_resource=True)

    def _generate_async_request_entry(self, event):
        if not self.async_pool_active:
            async_pool = CommandGenerator('self.start_async_pool', indents=2)
            self.buffer.write(async_pool.generate_command())
            self.buffer.write('\n\n')
            self.async_pool_active = True

        self._generate_http_request_entry(event,
                                          is_async=True,
                                          is_resource=False)

    def _generate_set_header_entry(self, event):
        for header_name, header_value in six.iteritems(event.data):
            set_header = CommandGenerator('self.set_header', indents=2)
            set_header.add_argument(header_name)
            set_header.add_argument(header_value)
            self.buffer.write(set_header.generate_command())
            self.buffer.write('\n\n')

    def _generate_set_cookie_entry(self, event):
        set_cookie = CommandGenerator('self.set_cookie', indents=2)
        cookie_specs = deepcopy(event.data)
        set_cookie.add_argument(cookie_specs['name'])
        del cookie_specs['name']
        set_cookie.add_argument(cookie_specs['value'])
        del cookie_specs['value']

        for spec_name, spec_value in six.iteritems(cookie_specs):
            set_cookie.add_named_argument(spec_name, spec_value)

        self.buffer.write(set_cookie.generate_command())

    def _generate_think_time_entry(self, event):
        think_time = CommandGenerator('self.think_time')
        think_time.add_argument(event.data['think_time'])
        self.buffer.write(think_time.generate_command())
