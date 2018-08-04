from __future__ import absolute_import, division, print_function
# import signal
# import sys
import os
import logging
import click
from bs4 import BeautifulSoup
import urllib3
import shutil

urllib3.disable_warnings()
logger = logging.getLogger(__name__)
_DEBUG = False


'''
def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        logger.warning('Caught signal %s, exiting.', str(signum))
        # gin_app.stop()
        sys.exit()
    else:
        logger.warning('Ignoring signal %s.', str(signum))
    return stack


def set_sig_handler(funcname, avoid=['SIG_DFL', 'SIGSTOP', 'SIGKILL']):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            logger.warning("Skipping {} {}".format(i, m))

'''


@click.command()
@click.argument('url')
@click.argument('path')
def main(url, path):
    if _DEBUG:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(name)10s | %(levelname)-7s | %(funcName)15s() | %(threadName)-10s | %(message)s', )
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(name)10s | %(levelname)-7s | %(funcName)15s() | %(threadName)-10s | %(message)s', )

    # logger.info("Loaded [" + MD.__name__ + "] from [" + MD.__file__ + "]")
#    set_sig_handler(sig_handler)
    parse_uri(url, path)


def parse_uri(url, path):
    logging.getLogger("urllib3").setLevel(logging.INFO)
    host = urllib3.get_host(url)
    logger.info(host)
    if host[0] == 'http':
        pool = urllib3.HTTPConnectionPool(host=host[1], port=host[2], maxsize=10)
    elif host[0] == 'https':
        pool = urllib3.HTTPSConnectionPool(host=host[1], port=host[2], maxsize=10)

    req = pool.request("GET", url, timeout=2.5)
    if req.status == 200:
        logging.info("Make directory %s" % path)
        try:
            os.mkdir(os.path.join(os.path.curdir, path))
        except Exception as e:
            logger.warning(str(e))
        parse_body(req.data, url, path)
    else:
        logger.error("Error while loading page: %s" % repr(req))


def parse_body(data, url, path):
    soup = BeautifulSoup(data, 'html.parser')
    for link in soup.find_all('a'):
        name = link.get('href')
        if name[-3:] in ('jpg', 'png', 'bmp', 'peg', 'gif'):
            logger.info('Image found: {}'.format(name))
            download(url + '/' + name, os.path.join(path, name))
        else:
            logger.info("Subpath found, continue parsing tree [%s]" % name)
            parse_uri(url + '/' + name, os.path.join(path, name))


def download(url, path='./target'):
    http = urllib3.PoolManager(num_pools=10)
    logger.info("Saving image to [%s]" % path)
    try:
        with http.request("GET", url, preload_content=False) as r, open(path, 'wb') as outfile:
            shutil.copyfileobj(r, outfile)
    except Exception as e:
        logger.error("Error: %s" % str(e))
