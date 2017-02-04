import pytest
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


@pytest.fixture
def http_assert_text_found_ok_sequence():
    class HttpAssertTextFoundOkSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/html',
                response_hooks=[
                    self.assert_body_has_text('Herman Melville')
                ]
            )

    return HttpAssertTextFoundOkSequence


@pytest.fixture
def http_assert_text_found_ko_sequence():
    class HttpAssertTextFoundKoSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/html',
                response_hooks=[
                    self.assert_body_has_text('Norman Foster')
                ]
            )

    return HttpAssertTextFoundKoSequence


@pytest.fixture
def http_assert_text_regex_ok_sequence():
    class HttpAssertTextRegexOkSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/html',
                response_hooks=[
                    self.assert_body_has_regex(r"\w+'s leg")
                ]
            )

    return HttpAssertTextRegexOkSequence


@pytest.fixture
def http_assert_text_regex_ko_sequence():
    class HttpAssertTextRegexKoSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/html',
                response_hooks=[
                    self.assert_body_has_regex(r"\w+'s shoulder")
                ]
            )

    return HttpAssertTextRegexKoSequence


@pytest.fixture
def http_assert_status_ok_sequence():
    class HttpAssertStatusOkSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/status/200',
                is_resource=True,
                response_hooks=[
                    self.assert_http_status(200)
                ]
            )

    return HttpAssertStatusOkSequence


@pytest.fixture
def http_assert_status_ko_sequence():
    class HttpAssertStatusKoSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/status/404',
                is_resource=True,
                response_hooks=[
                    self.assert_http_status(200)
                ]
            )

    return HttpAssertStatusKoSequence


@pytest.fixture
def http_assert_headers_ok_sequence():
    class HttpAssertHeadersOkSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/response-headers',
                params={
                    'X-Woodpecker-Context': 'UnitTest'
                },
                is_resource=True,
                response_hooks=[
                    self.assert_header_value(
                        'X-Woodpecker-Context', 'UnitTest'
                    )
                ]
            )

    return HttpAssertHeadersOkSequence


@pytest.fixture
def http_assert_headers_ko_sequence():
    class HttpAssertHeadersKoSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/response-headers',
                params={
                    'X-Woodpecker-Context': 'foo'
                },
                is_resource=True,
                response_hooks=[
                    self.assert_header_value(
                        'X-Woodpecker-Context', 'UnitTest'
                    )
                ]
            )

    return HttpAssertHeadersKoSequence


@pytest.fixture
def http_assert_elapsed_ok_sequence():
    class HttpAssertElapsedOkSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/delay/1',
                is_resource=True,
                response_hooks=[
                    self.assert_elapsed_within(3000)
                ]
            )

    return HttpAssertElapsedOkSequence


@pytest.fixture
def http_assert_elapsed_ko_sequence():
    class HttpAssertElapsedKoSequence(HttpSequence):
        def steps(self):
            self.get(
                'http://www.httpbin.org/delay/1',
                is_resource=True,
                response_hooks=[
                    self.assert_elapsed_within(500)
                ]
            )

    return HttpAssertElapsedKoSequence


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


# Assertions
def test_http_assert_text_found_ok(http_assert_text_found_ok_sequence):
    output_stream = StringIO()
    sequence = http_assert_text_found_ok_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Text "Herman Melville" correctly found in response body' \
           in output_string


def test_http_assert_text_found_ko(http_assert_text_found_ko_sequence):
    output_stream = StringIO()
    sequence = http_assert_text_found_ko_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(AssertionError):
        sequence.run_steps()


def test_http_assert_text_regex_ok(http_assert_text_regex_ok_sequence):
    output_stream = StringIO()
    sequence = http_assert_text_regex_ok_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Regex "\w+\'s leg" matched successfully in response body' \
           in output_string


def test_http_assert_text_regex_ko(http_assert_text_regex_ko_sequence):
    output_stream = StringIO()
    sequence = http_assert_text_regex_ko_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(AssertionError):
        sequence.run_steps()


def test_http_assert_status_ok(http_assert_status_ok_sequence):
    output_stream = StringIO()
    sequence = http_assert_status_ok_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'HTTP Status matched the expected code 200' \
           in output_string


def test_http_assert_status_ko(http_assert_status_ko_sequence):
    output_stream = StringIO()
    sequence = http_assert_status_ko_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(AssertionError):
        sequence.run_steps()


def test_http_assert_headers_ok(http_assert_headers_ok_sequence):
    output_stream = StringIO()
    sequence = http_assert_headers_ok_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Header "X-Woodpecker-Context" ' \
           'matched the expected value "UnitTest"' \
           in output_string


def test_http_assert_headers_ko(http_assert_headers_ko_sequence):
    output_stream = StringIO()
    sequence = http_assert_headers_ko_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(AssertionError):
        sequence.run_steps()


def test_http_assert_elapsed_ok(http_assert_elapsed_ok_sequence):
    output_stream = StringIO()
    sequence = http_assert_elapsed_ok_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Request completed within 3000 ms' \
           in output_string


def test_http_assert_elapsed_ko(http_assert_elapsed_ko_sequence):
    output_stream = StringIO()
    sequence = http_assert_elapsed_ko_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(AssertionError):
        sequence.run_steps()
