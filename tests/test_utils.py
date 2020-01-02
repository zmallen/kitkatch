import os

import pytest

from apptemplate.utils import process_arguments


@pytest.fixture
def clear_env():
    """ Clears any env vars that might have been set """
    env_vars = [
        'NUM_WORKERS',
        'KEYFILE_PATH',
        'CERTFILE_PATH',
        'NOT_ENABLED',
        'LOG_LEVEL',
        'LOG_FORMAT',
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
        'num_workers': 12,
        'ssl_keyfile': 'keyfile.pem',
        'ssl_certfile': 'certfile.pem',
        'not_enabled': True,
        'log_level': 'warning',
        'log_format': 'text',
    }


@pytest.fixture
def env_arguments01():
    return {
        'NUM_WORKERS': '12',
        'KEYFILE_PATH': 'keyfile.pem',
        'CERTFILE_PATH': 'certfile.pem',
        'NOT_ENABLED': 'True',
        'LOG_LEVEL': 'warning',
        'LOG_FORMAT': 'text',
    }


@pytest.fixture
def cli_arguments02():
    return {
        'num_workers': 29,
        'ssl_keyfile': None,
        'ssl_certfile': None,
        'not_enabled': False,
        'log_level': 'debug',
        'log_format': 'json',
    }


@pytest.fixture
def env_arguments02():
    return {
        'NUM_WORKERS': '29',
        'KEYFILE_PATH': None,
        'CERTFILE_PATH': None,
        'NOT_ENABLED': None,
        'LOG_LEVEL': 'debug',
        'LOG_FORMAT': 'json',
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