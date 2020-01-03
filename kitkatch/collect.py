import requests
import fake_useragent
from bs4 import BeautifulSoup
import logging
import os
import datetime
import hashlib
import ssdeep
import json
from urllib.parse import urlparse, urljoin
from os.path import splitext

_LOGGER = logging.getLogger('kitkatch.collect')

def compressed_file_list():
    return [
        'zip',
        'rar',
        '7z',
        'tar',
        'gz'
    ]

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

def random_useragent():
    ua = fake_useragent.UserAgent()
    return str(ua.chrome)

def build_headers():
    return {
        'User-Agent': random_useragent()
    }

def build_url_from_parse(scheme, netloc, path):
    url = urljoin('%s://%s' % (scheme, netloc), path)
    if url[-1] != '/' and not splitext(path)[1].startswith('.'):
        url += '/'
    return url

"""
Given a URL, checks for an open directory listing
Common for phishing kits
Shoutout to Duo for this indexed link collector logic
"""
def collect_indexed_links(response, url):
    links = []
    soup = BeautifulSoup(response, 'html.parser')
    if 'Index of' not in response:
        return links
    for a in soup.find_all('a'):
        if 'Parent Directory' in a.text:
            continue
        href = a['href']
        if href and href[0] == '?':
            continue
        links.append(urljoin(url, href))
    return links

"""
Split URI in the path and return a list of URLs to traverse
example: www.google.com/a/b/c/foobar
return: www.google.com/a/, www.google.com/a/b/..
Doesnt need to return query as thats the original URL
create nested dirs to make it easy to traverse each
"""
def url_candidates(url):
    urls = []
    parsed = urlparse(url)
    path = parsed.path
    if path == '':
        return urls

    scheme = parsed.scheme
    netloc = parsed.netloc

    _LOGGER.info('Making directory structure for domain %s, structure -> %s' % (netloc, path))
    os.makedirs(netloc + path, exist_ok=True)

    split_path = path.split('/')
    for i in range(len(split_path)):
        new_path = '/'.join(split_path[0:i+1])
        url_candidate = build_url_from_parse(scheme, netloc, new_path)
        urls.append(url_candidate)
    return list(set(urls))

def scrape(url):
    r = requests.get(
            url,
            headers=build_headers()
        )
    return r

def get_forms(body):
    soup = BeautifulSoup(body, 'html.parser')
    return soup.find_all('form')

def log_data(url, resp, now):
    page_data = resp.text
    page_data_binary = page_data.encode()
    sha2 = hashlib.sha256(page_data_binary).hexdigest()
    parsed = urlparse(url)
    full_path = parsed.netloc + parsed.path + sha2
    with open(full_path, 'a') as fd:
        _LOGGER.info('Writing out HTTP text body for %s' % url)
        fd.write(page_data)
    payload = {
        'status_code': resp.status_code,
        'url': url,
        'time': str(now),
        'sha2': sha2,
        'md5': hashlib.md5(page_data.encode()).hexdigest(),
        'ssdeep': ssdeep.hash(page_data),
        'has_forms': len(get_forms()) > 0
    }
    with open('%s.json' % full_path, 'a') as fd:
        _LOGGER.info('Writing out metadata for %s' % url)
        json.dump(payload, fd, ensure_ascii=False, indent=4)
    return payload

def download_zip(url):
    response = requests.get(url, stream=True)
    parsed = urlparse(url)
    full_path = parsed.netloc + parsed.path
    with open(full_path, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                fd.write(chunk)

def compressed_file_in_url(url):
    for compressed_file in compressed_file_list():
        if url.endswith(compressed_file):
            return True
    return False

"""
Parses and scrapes a URI for open dirs and downloads any .zip files there
Will not recursively find open dirs that have more open dirs
"""
def collect_info(url):
    now = datetime.datetime.now()
    potential_compressed_kit_urls = []
    potential_form_urls = []
    _LOGGER.info('Starting to fingerprint URL -> %s' % url)
    candidates = url_candidates(url)
    _LOGGER.info('Processing the following candidate URLs -> %s' % candidates)
    candidates_from_open_index = []
    for url in candidates:
        resp = scrape(url)
        if not resp.ok:
            _LOGGER.error('Error scraping %s, status code %s' % (candidate, str(r.status_code)))
            continue
        log_data(url, resp, now)
        open_index_urls = collect_indexed_links(resp.text, url)
        if len(open_index_urls) > 0:
            _LOGGER.info('Found open index! Processing for kits..')
            for idx_url in open_index_urls:
                if compressed_file_in_url(idx_url):
                    _LOGGER.info('Found compressed file, at %s, possible kit. Downloading..' % idx_url)
                    download_zip(idx_url)
                    potential_compressed_kit_urls.append(idx_url)
