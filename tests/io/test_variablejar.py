import pytest

from woodpecker.io.variablejar import VariableJar


@pytest.fixture
def variablejar():
    return VariableJar()


def test_set_variable(variablejar):
    variablejar.set('foo', 'bar')
    assert variablejar.get('foo') == 'bar'


def test_get_unset_variable_not_strict():
    variable_jar = VariableJar()
    assert variable_jar.get('foo') == 'foo'


def test_get_unset_variable_strict():
    variable_jar = VariableJar(raise_variable_error=True)
    with pytest.raises(KeyError):
        variable_jar.get('foo')


def test_get_reserved_variable(variablejar):
    with pytest.raises(KeyError):
        variablejar.get('last_updated_on')


def test_set_reserved_variable(variablejar):
    with pytest.raises(KeyError):
        variablejar.set('last_updated_on', 0)


def test_delete_variable():
    variable_jar = VariableJar(raise_variable_error=True)
    variable_jar.set('foo', 'bar')
    assert variable_jar.get('foo') == 'bar'
    variable_jar.delete('foo')
    with pytest.raises(KeyError):
        variable_jar.get('foo')


def test_reset_variablejar():
    variable_jar = VariableJar(raise_variable_error=True)
    variable_jar.set('foo', 'bar')
    assert variable_jar.get('foo') == 'bar'
    variable_jar.reset()
    with pytest.raises(KeyError):
        variable_jar.get('foo')


def test_set_get_pecker_id(variablejar):
    variablejar.set_pecker_id('abcde')
    assert variablejar.get_pecker_id() == 'abcde'


def test_set_get_current_sequence(variablejar):
    variablejar.set_current_sequence('Test Transaction')
    assert variablejar.get_current_sequence() == 'Test Transaction'
