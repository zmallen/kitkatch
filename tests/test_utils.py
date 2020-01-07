import os
import pytest

from kitkatch.utils import process_arguments


@pytest.fixture
def clear_env():
    """ Clears any env vars that might have been set """
    env_vars = [
        'URL',
        'LOG_LEVEL',
        'LOG_FORMAT',
        'URL_FILE',
        'LOOT_DIR'
    ]

    existing_env_vars = {}
    for e in env_vars:
        if e in os.environ:
            existing_env_vars[e] = os.environ[e]
            del os.environ[e]
            os.unsetenv(e)

    yield

    for e in env_vars:
        if e in existing_env_vars:
            os.environ[e] = existing_env_vars[e]
            continue
        if e in os.environ:
            del os.environ[e]
            os.unsetenv(e)


@pytest.fixture
def cli_arguments01():
    return {
        'url': 'https://google.com/abcdefg',
        'log_level': 'warning',
        'log_format': 'text',
        'url_file': 'foobar',
        'loot_dir': 'loot/'
    }


@pytest.fixture
def env_arguments01():
    return {
        'URL': 'https://google.com/abcdefg',
        'LOG_LEVEL': 'warning',
        'LOG_FORMAT': 'text',
        'URL_FILE': 'foobar',
        'LOOT_DIR': 'loot/'
    }


@pytest.fixture
def cli_arguments02():
    return {
        'url': 'https://google.com/abcdefg',
        'log_level': 'warning',
        'log_format': 'text',
        'url_file': 'foobar',
        'loot_dir': 'loot/'
    }


@pytest.fixture
def env_arguments02():
    return {
        'URL': 'https://google.com/abcdefg',
        'LOG_LEVEL': 'warning',
        'LOG_FORMAT': 'text',
        'URL_FILE': 'foobar',
        'LOOT_DIR': 'loot/'
    }


@pytest.mark.usefixtures("clear_env")
class TestProcessArgs():
    def _cli_args(self, expected):
        args = process_arguments(**expected)
        assert args == expected

    def _env_args(self, cli, env):
        for env_var, val in env.items():
            if val is None:
                continue
            os.environ[env_var] = val

        args = process_arguments(**{k: None for k in cli.keys()})
        assert args == cli

    def test_cli01(self, cli_arguments01):
        self._cli_args(cli_arguments01)

    def test_cli02(self, cli_arguments02):
        self._cli_args(cli_arguments02)

    def test_env01(self, cli_arguments01, env_arguments01):
        self._env_args(cli_arguments01, env_arguments01)

    def test_env02(self, cli_arguments02, env_arguments02):
        self._env_args(cli_arguments02, env_arguments02)
