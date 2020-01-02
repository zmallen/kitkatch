import requests
import fake_useragent
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, urljoin

_LOGGER = logging.getLogger('kitkatch.collect')

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
    return '%s://%s%s/' % (scheme, netloc, path)

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
"""
def url_candidates(url):
    urls = []
    urls.append(url)
    parsed = urlparse(url)
    path = parsed.path
    if path == '':
        return urls

    scheme = parsed.scheme
    netloc = parsed.netloc

    split_path = path.split('/')
    for i in range(len(split_path)):
        new_path = '/'.join(split_path[0:i+1])
        url_candidate = build_url_from_parse(scheme, netloc, new_path)
        urls.append(url_candidate)
    return urls

def scrape_and_log(url):
    r = requests.get(
            url,
            headers=build_headers()
        )
    return r

def download_zip(url):
    response = requests.get(url, stream=True)
    with open(url.split('/')[-1], 'wb') as fd:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                fd.write(chunk)

def collect_info(url):
    candidates = url_candidates(url)
    _LOGGER.info('Processing the following candidate URLs -> %s' % candidates)
    candidates_from_open_index = []
    for url in candidates:
        resp = scrape_and_log(url)
        if not resp.ok:
            _LOGGER.error('Error scraping %s, status code %s' % (candidate, str(r.status_code)))
            continue
        open_index_urls = collect_indexed_links(resp.text, url)
        if len(open_index_urls) > 0:
            _LOGGER.info('Found open index! Processing for kits..')
            for idx_url in open_index_urls:
                if idx_url.endswith('zip'):
                    _LOGGER.info('Found ZIP file, possible kit. Downloading..')


    import ipdb; ipdb.set_trace()
