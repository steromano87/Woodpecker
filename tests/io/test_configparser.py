import pytest
import os

from woodpecker.io.configparser import ConfigParser


def test_init_config_file(tmpdir):
    config_file = str(tmpdir.mkdir('temp').join('woodpecker.yml'))
    parser = ConfigParser(config_file)
    parser.init()
    assert os.path.isfile(config_file)


def test_init_failing_if_not_forced(tmpdir):
    config_file = tmpdir.mkdir('temp').join('woodpecker.yml')
    config_file_path = str(config_file)
    config_file.write('foo')
    parser = ConfigParser(config_file_path)
    with pytest.raises(IOError):
        parser.init(forced=False)


def test_init_not_failing_if_forced(tmpdir):
    config_file = tmpdir.mkdir('temp').join('woodpecker.yml')
    config_file_path = str(config_file)
    config_file.write('foo')
    parser = ConfigParser(config_file_path)
    parser.init(forced=True)
    file_content = config_file.read()
    assert 'scenarios' in file_content
    assert 'settings' in file_content
