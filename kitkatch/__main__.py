"""
Runs the python app template service
"""
import logging
import plac
import os.path
from os import path, mkdir
from kitkatch import utils, collect

_LOGGER = logging.getLogger('kitkatch')


@plac.annotations(
    #ruledir=plac.Annotation('Directory to load rules'),
    url=plac.Annotation('URL to navigate to', kind='option',  abbrev='url', type=str),
    log_level=plac.Annotation('Logging level [LOG_LEVEL]', 'option', 'l', str, ['debug', 'info', 'warn', 'warning', 'error']),  # noqa: E501
    log_format=plac.Annotation('Logging format [LOG_FORMAT]', 'option', 'f', str, ['json', 'text']),
    url_file=plac.Annotation('File with newline separated URLs', kind='option', type=str),
    loot_dir=plac.Annotation('Directory to add loot and logging', kind='option', type=str),
)

def main(url,
         #ruledir='./rules',
         url_file,
         loot_dir ='loot/',
         log_level='info',
         log_format='json'):

    args = utils.process_arguments(
        #ruledir=ruledir,
        url=url,
        url_file=url_file,
        loot_dir='./loot',
        log_level=log_level,
        log_format=log_format,
    )

    if not path.exists(loot_dir):
        _LOGGER.info('Loot Directory %s does not exist, creating' % loot_dir)
        mkdir(loot_dir)


    utils.set_logger(args['log_level'], args['log_format'])
    utils.log_arguments(**args)
    collect.set_logger(args['log_level'], args['log_format'])

    is_debug = False
    if args['log_level'] == 'debug':
        is_debug = True

    if url_file:
        _LOGGER.info('Loading URLs from %s' % url_file)
        with open(url_file, 'r') as fd:
            urls = [x.replace('\n','') for x in fd.readlines()]
            _LOGGER.info('Loading %s URLs' % len(urls))
        for url in urls:
            collect.collect_info(url, loot_dir)
    else:
        collect.collect_info(url, loot_dir)

if __name__ == '__main__':
    msg = plac.call(main)
    if msg is not None:
        print(msg)
