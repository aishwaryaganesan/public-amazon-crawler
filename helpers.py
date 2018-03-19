import os
import random
from datetime import datetime
from urlparse import urlparse
import eventlet
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from eventlet.green import urllib2
import settings

requests = eventlet.import_patched('requests.__init__')
time = eventlet.import_patched('time')
num_requests = 0

def make_request(url, return_soup=True):
    # global request building and response handling
    url = format_url(url)
    if "picassoRedirect" in url:
        return None  # skip the redirect URLs
    global num_requests
    if num_requests >= settings.max_requests:
        raise Exception("Reached the max number of requests: {}".format(settings.max_requests))
    proxies = get_proxy()
    try:
        r = urllib2.urlopen(url)
        #r = requests.get(url, headers=settings.headers, proxies=proxies, timeout=10000000)
    except Exception as e:
        log("WARNING: Request for {} failed, trying again.".format(url))
        if return_soup:
            return None, None
        return None
    num_requests += 1

    if return_soup:
        return BeautifulSoup(r.read(), "html5lib"), r.read()
    return r.read()


def format_url(url):
    # make sure URLs aren't relative, and strip unnecssary query args
    u = urlparse(url)

    scheme = u.scheme or "http"
    host = u.netloc or settings.host
    path = u.path

    if not u.query:
        query = ""
    else:
        query = "?"
        for piece in u.query.split("&"):
            k, v = piece.split("=")
            if k in settings.allowed_params:
                query += "{k}={v}&".format(**locals())
        query = query[:-1]

    return "{scheme}://{host}{path}{query}".format(**locals())


def log(msg):
    # global logging function
    if settings.log_stdout:
        try:
            print "{}: {}".format(datetime.now(), msg)
        except UnicodeEncodeError:
            pass  # squash logging errors in case of non-ascii text


def get_proxy():
    # choose a proxy server to use for this request, if we need one
    if not settings.proxies or len(settings.proxies) == 0:
        return None

    proxy_ip = random.choice(settings.proxies)
    proxy_url = "socks5://{user}:{passwd}@{ip}:{port}/".format(
        user=settings.proxy_user,
        passwd=settings.proxy_pass,
        ip=proxy_ip,
        port=settings.proxy_port,

    )
    return {
        "http": proxy_url,
        "https": proxy_url
    }


if __name__ == '__main__':
    # test proxy server IP masking
    r = make_request('https://api.ipify.org?format=json', return_soup=False)
    print r.text