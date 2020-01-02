"""
Contains various utility functions.
"""
import logging
from os import getenv

_LOGGER = logging.getLogger('kitkatch.utils')


def process_arguments(**kwargs):
    args = {}

#    args['ruledir'] = getenv('RULEDIR', kwargs['ruledir'])
    args['log_level'] = getenv('LOG_LEVEL', kwargs['log_level'])
    args['log_format'] = getenv('LOG_FORMAT', kwargs['log_format'])
    args['url'] = getenv('URL', kwargs['url'])

    return args


def log_arguments(**kwargs):
    for k, v in kwargs.items():
        _LOGGER.info('argument %s => %s', k, v)


def set_logger(level, output_fmt):
    fmt = '{' + \
          '"file":"%(pathname)s",' + \
          '"name":"%(name)s",' + \
          '"level":"%(levelname)s",' + \
          '"created":%(created)f,' + \
          '"line_number":%(lineno)d,' + \
          '"message":"%(message)s",' + \
          '"function":"%(funcName)s"' + \
          '}'

    if output_fmt == 'text':
        fmt = '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'

    _LOGGER.setLevel(getattr(logging, level.upper(), logging.INFO))
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt))
    _LOGGER.addHandler(ch)
