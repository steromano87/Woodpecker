import pytest

from woodpecker.data.settings import BaseSettings
from woodpecker.data.variablejar import VariableJar


@pytest.fixture
def variablejar():
    return VariableJar()


def test_set_variable(variablejar):
    variablejar.set('foo', 'bar')
    assert variablejar.get('foo') == 'bar'


def test_get_unset_variable_not_strict():
    settings = BaseSettings()
    settings.set('runtime', 'raise_error_if_variable_not_defined', False)
    variable_jar = VariableJar(settings=settings)
    assert variable_jar.get('foo') == 'foo'


def test_get_unset_variable_strict():
    settings = BaseSettings()
    settings.set('runtime', 'raise_error_if_variable_not_defined', True)
    variable_jar = VariableJar(settings=settings)
    with pytest.raises(KeyError):
        variable_jar.get('foo')


def test_get_reserved_variable(variablejar):
    with pytest.raises(KeyError):
        variablejar.get('last_updated_on')


def test_set_reserved_variable(variablejar):
    with pytest.raises(KeyError):
        variablejar.set('last_updated_on', 0)


def test_delete_variable():
    settings = BaseSettings()
    settings.set('runtime', 'raise_error_if_variable_not_defined', True)
    variable_jar = VariableJar(settings=settings)
    variable_jar.set('foo', 'bar')
    assert variable_jar.get('foo') == 'bar'
    variable_jar.delete('foo')
    with pytest.raises(KeyError):
        variable_jar.get('foo')


def test_reset_variablejar():
    settings = BaseSettings()
    settings.set('runtime', 'raise_error_if_variable_not_defined', True)
    variable_jar = VariableJar(settings=settings)
    variable_jar.set('foo', 'bar')
    assert variable_jar.get('foo') == 'bar'
    variable_jar.reset()
    with pytest.raises(KeyError):
        variable_jar.get('foo')


def test_set_get_pecker_id(variablejar):
    variablejar.set_pecker_id('abcde')
    assert variablejar.get_pecker_id() == 'abcde'


def test_set_get_current_transaction(variablejar):
    variablejar.set_current_transaction('Test Transaction')
    assert variablejar.get_current_transaction() == 'Test Transaction'
