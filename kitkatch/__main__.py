"""
Runs the python app template service
"""
import logging
import plac
import json
import os.path
import datetime
from os import path, mkdir
from kitkatch import utils, collect
from pygments import highlight, lexers, formatters

_LOGGER = logging.getLogger('kitkatch')


def run_report(form_urls, compressed_urls, now, loot_dir):
        form_formatted_json = json.dumps(form_urls, sort_keys=True, indent=4)
        compressed_formatted_json = json.dumps(form_urls, sort_keys=True, indent=4)
        form_colorful_json = highlight(form_formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
        compressed_colorful_json = highlight(compressed_formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
        data = {}
        data['forms'] = form_urls
        data['compressed'] = compressed_urls
        full_path = '%sreport-%s.json' % (loot_dir, str(now))
        with open(full_path, 'a') as fd:
            _LOGGER.info('* Writing out report')
            json.dump(data, fd, ensure_ascii=False, indent=4)
        print(form_colorful_json)
        print(compressed_colorful_json)


@plac.annotations(
    url=plac.Annotation('URL to navigate to', kind='option',  abbrev='url', type=str),
    log_level=plac.Annotation('Logging level [LOG_LEVEL]', 'option', 'l', str, ['debug', 'info', 'warn', 'warning', 'error']),  # noqa: E501
    log_format=plac.Annotation('Logging format [LOG_FORMAT]', 'option', 'f', str, ['json', 'text']),
    url_file=plac.Annotation('File with newline separated URLs', kind='option', type=str),
    loot_dir=plac.Annotation('Directory to add loot and logging', kind='option', type=str),
)
def main(url,
         url_file,
         loot_dir ='loot/',
         log_level='info',
         log_format='json'):

    args = utils.process_arguments(
        #ruledir=ruledir,
        url=url,
        url_file=url_file,
        loot_dir=loot_dir,
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

    form_urls = []
    compressed_urls = []
    now = datetime.datetime.now()
    if url_file:
        _LOGGER.info('Loading URLs from %s' % url_file)
        with open(url_file, 'r') as fd:
            urls = [x.replace('\n','') for x in fd.readlines()]
            _LOGGER.info('Loading %s URLs' % len(urls))
        for url in urls:
            data = collect.collect_info(url, loot_dir, now)
            compressed_urls = compressed_urls + data[0]
            form_urls = form_urls + data[1]
    else:
        compressed_urls, form_urls = collect.collect_info(url, loot_dir, now)
    run_report(form_urls, compressed_urls, now, loot_dir)

if __name__ == '__main__':
    msg = plac.call(main)
    if msg is not None:
        print(msg)
