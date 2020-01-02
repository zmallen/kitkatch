"""
Runs the python app template service
"""
import logging
import plac
from kitkatch import utils, collect

_LOGGER = logging.getLogger('kitkatch')


@plac.annotations(
    #ruledir=plac.Annotation('Directory to load rules'),
    url=plac.Annotation('URL to navigate to', kind='option',  abbrev='url', type=str),
    log_level=plac.Annotation('Logging level [LOG_LEVEL]', 'option', 'l', str, ['debug', 'info', 'warn', 'warning', 'error']),  # noqa: E501
    log_format=plac.Annotation('Logging format [LOG_FORMAT]', 'option', 'f', str, ['json', 'text']),
)

def main(url,
         #ruledir='./rules',
         log_level='info',
         log_format='json'):

    args = utils.process_arguments(
        #ruledir=ruledir,
        url=url,
        log_level=log_level,
        log_format=log_format,
    )

    utils.set_logger(args['log_level'], args['log_format'])
    utils.log_arguments(**args)
    collect.set_logger(args['log_level'], args['log_format'])

    is_debug = False
    if args['log_level'] == 'debug':
        is_debug = True

    collect.collect_info(url)

if __name__ == '__main__':
    msg = plac.call(main)
    if msg is not None:
        print(msg)
