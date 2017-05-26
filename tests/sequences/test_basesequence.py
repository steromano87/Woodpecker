import pytest
import re

from six import StringIO

from woodpecker.sequences.basesequence import BaseSequence


@pytest.fixture
def stopwatch_sequence():
    class stopwatchSequence(BaseSequence):
        def steps(self):
            self.start_stopwatch('stopwatch_test')
            self.end_stopwatch('stopwatch_test')

    return stopwatchSequence


@pytest.fixture
def bad_stopwatch_sequence():
    class BadstopwatchSequence(BaseSequence):
        def steps(self):
            self.end_stopwatch('stopwatch_test')

    return BadstopwatchSequence


@pytest.fixture
def fixed_think_time_sequence():
    class FixedThinkTimeSequence(BaseSequence):
        def steps(self):
            self.think_time(1, kind='fixed')

    return FixedThinkTimeSequence


@pytest.fixture
def random_gaussian_think_time_sequence():
    class RandomGaussianThinkTimeSequence(BaseSequence):
        def steps(self):
            self.think_time(1, kind='gaussian')

    return RandomGaussianThinkTimeSequence


def test_stopwatches(stopwatch_sequence):
    output_stream = StringIO()
    sequence = stopwatch_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Stopwatch "stopwatch_test" started' in output_string
    assert 'Stopwatch "stopwatch_test" ended' in output_string


def test_bad_stopwatches(bad_stopwatch_sequence):
    output_stream = StringIO()
    sequence = bad_stopwatch_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    with pytest.raises(KeyError):
        sequence.run_steps()


def test_fixed_think_time(fixed_think_time_sequence):
    output_stream = StringIO()
    sequence = fixed_think_time_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert 'Think time: 1 s (fixed)' in output_string


def test_gaussian_random_think_time(random_gaussian_think_time_sequence):
    output_stream = StringIO()
    sequence = random_gaussian_think_time_sequence(
        debug=True,
        inline_log_sinks=(output_stream,)
    )
    sequence.run_steps()
    output_stream.seek(0)
    output_string = output_stream.getvalue()
    assert re.search(r"Think time: \d+\.\d{,3} s \(gaussian\)", output_string) \
        is not None
    think_time = float(re.findall(
        r"Think time: (\d+\.\d{,3}) s \(gaussian\)", output_string
    )[0])
    assert think_time >= 0
