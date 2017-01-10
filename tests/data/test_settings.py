import pytest

from woodpecker.data.settings import Settings, BaseSettings


@pytest.fixture
def settings():
    return BaseSettings()


@pytest.fixture
def derived_settings():
    class DerivedSettings(Settings):
        def __init__(self, peckerfile='Peckerfile'):
            self._validation_mask = {
                'foo': {
                    'type': 'dict',
                    'schema': {
                        'bar': {
                            'type': 'boolean'
                        },
                        'baz': {
                            'type': 'float'
                        }
                    }
                }
            }
            self._default_data = {
                'foo': {
                    'bar': True,
                    'baz': 3.4
                }
            }
            super(DerivedSettings, self).__init__(peckerfile)
    return DerivedSettings()


@pytest.fixture
def fake_settings():
    class FakeSettings(Settings):
        def __init__(self, peckerfile='Peckerfile'):
            self._validation_mask = {
                'foo': {
                    'type': 'dict',
                    'schema': {
                        'bar': {
                            'type': 'boolean'
                        },
                        'baz': {
                            'type': 'float'
                        }
                    }
                }
            }
            self._default_data = {
                'foo': {
                    'bar': True,
                    'baz': 'wunderbar'
                }
            }
            super(FakeSettings, self).__init__(peckerfile)
    return FakeSettings()


def test_inheritance(settings):
    assert isinstance(settings, Settings)


def test_default_value_loading(settings):
    output = settings.dump()
    assert isinstance(output, dict)


def test_value_modification(settings):
    old_value = settings.get('network', 'controller_port')
    new_value = 10101
    settings.set('network', 'controller_port', new_value)
    assert new_value == settings.get('network', 'controller_port')
    assert old_value != settings.get('network', 'controller_port')


def test_set_multiple_values_at_a_time(settings):
    settings.set({
        'timing': {
            'skip_think_time': True
        },
        'logging': {
            'max_entries_before_flush': 200
        }
    })
    assert settings.get('timing', 'skip_think_time') is True
    assert settings.get('logging', 'max_entries_before_flush') == 200


def test_value_retrieval_with_nonexistent_section(settings):
    with pytest.raises(KeyError):
        settings.get('foo', 'skip_think_time')


def test_value_retrieval_with_nonexistent_entry(settings):
    with pytest.raises(KeyError):
        settings.get('timing', 'baz')


def test_set_invalid_value(settings):
    with pytest.raises(ValueError):
        settings.set('timing', 'skip_think_time', 'bar')


def test_set_value_in_invalid_section(settings):
    with pytest.raises(ValueError):
        settings.set('foo', 'skip_think_time', True)


def test_set_value_in_invalid_key(settings):
    with pytest.raises(ValueError):
        settings.set('timing', 'bar', True)


def test_extension_with_valid_settings(settings, derived_settings):
    settings.extend(derived_settings)
    settings.set('foo', 'bar', False)
    settings.set('foo', 'baz', -0.5)
    assert settings.get('foo', 'bar') is False
    assert settings.get('foo', 'baz') == -0.5


def test_extension_with_valid_settings_and_massive_modification(settings, derived_settings):
    settings.extend(derived_settings)
    settings.set({
        'foo': {
            'bar': False,
            'baz': 15
        }
    })


def test_extension_with_invalid_settings(settings):
    with pytest.raises(TypeError):
        settings.extend({'foo': 'bar'})


def test_extension_with_non_consistent_settings(settings, fake_settings):
    with pytest.raises(ValueError):
        settings.extend(fake_settings)
