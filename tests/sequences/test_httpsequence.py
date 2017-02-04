import pytest
import re

import requests

from six import StringIO

from woodpecker.sequences.httpsequence import HttpSequence


@pytest.fixture
def http_200_sequence():
    class Http200Sequence(HttpSequence):
        def steps(self):
            self.get('http://www.httpbin.org/status/200')

    return Http200Sequence


@pytest.fixture
def http_401_sequence():
    class Http401Sequence(HttpSequence):
        def steps(self):
            self.get('http://www.httpbin.org/status/401', is_resource=False)

    return Http401Sequence


@pytest.fixture
def http_200_async_pool_sequence():
    class Http200AsyncPoolSequence(HttpSequence):
        def steps(self):
            self.start_async_pool()
            self.async_get('http://www.httpbin.org/status/200')
            self.async_get('http://www.httpbin.org/status/201')
            self.async_get('http://www.httpbin.org/status/202')
            self.async_get('http://www.httpbin.org/status/203')
            self.end_async_pool()

    return Http200AsyncPoolSequence


@pytest.fixture
def variable_retrieving_sequence():
    class VariableRetrievingSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/html',
                response_hooks=[
                    self.var_from_regex(
                        'author',
                        "Herman (\w+)"
                    )
                ]
            )

    return VariableRetrievingSequence


@pytest.fixture
def variable_retrieving_error_sequence():
    class VariableRetrievingErrorSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/html',
                response_hooks=[
                    self.var_from_regex(
                        'author',
                        "Mayer (\w+)"
                    )
                ]
            )

    return VariableRetrievingErrorSequence


@pytest.fixture
def variable_usage_sequence():
    class VariableRetrievingSequence(HttpSequence):
        def steps(self):
            self.variables.set('author', 'Melville')
            self.get(
                'http://www.google.com/search',
                params={
                    'q': self.variables.get('author')
                }
            )

    return VariableRetrievingSequence


@pytest.fixture
def variable_usage_url_sequence():
    class VariableRetrievingUrlSequence(HttpSequence):
        def steps(self):
            self.variables.set('author', 'Melville')
            self.get(
                'http://www.google.com/search?q=${author}'
            )

    return VariableRetrievingUrlSequence


def test_http_200_transaction(http_200_sequence):
    output_stream = StringIO()
    sequence = http_200_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert '200 OK' in output_string


def test_http_401_transaction(http_401_sequence):
    output_stream = StringIO()
    sequence = http_401_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(requests.exceptions.HTTPError):
        sequence.run_steps()


def test_http_200_async_pool_transaction(http_200_async_pool_sequence):
    output_stream = StringIO()
    sequence = http_200_async_pool_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Starting async requests pool' in output_string
    assert 'Async requests pool ended' in output_string


def test_variable_retrieving_transaction(variable_retrieving_sequence):
    output_stream = StringIO()
    sequence = variable_retrieving_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Saved parameter "author": "Melville"' in output_string


def test_variable_retrieving_error_transaction(
        variable_retrieving_error_sequence):
    output_stream = StringIO()
    sequence = variable_retrieving_error_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(IOError):
        sequence.run_steps()


def test_variable_usage_transaction(variable_usage_sequence):
    output_stream = StringIO()
    sequence = variable_usage_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'http://www.google.com/search?q=Melville' in output_string


def test_variable_usage_url_transaction(variable_usage_url_sequence):
    output_stream = StringIO()
    sequence = variable_usage_url_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'http://www.google.com/search?q=Melville' in output_string
