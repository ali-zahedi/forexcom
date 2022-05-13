import json
import logging
import ssl
import urllib
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen as _urlopen

import certifi

log = logging.getLogger()


def _url_encode(params):
    return urlencode(params).encode("utf-8")


def _iteritems(d):
    return iter(d.items())


def encode_params(params):
    """Encode the parameter for HTTP submissions, but
    only for non empty values..."""
    return _url_encode(
        dict([(k, v) for (k, v) in _iteritems(params) if v])
    )


def send_request(method, base_url, path, params=None, json_format=False, headers=None, http_proxy=None, https_proxy=None):
    """Open a network connection and performs HTTP with provided params."""
    if method not in ["GET", "POST"]:
        raise ValueError(f"Unknown method <{method}>")

    url = f'{base_url.strip("/")}/{path.lstrip("/")}'
    if headers is None:
        headers = {}
    if params:
        if json_format and method != "GET":
            params = json.dumps(params).encode("utf-8")
            headers['Content-Type'] = 'application/json'
        else:
            params = encode_params(params)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    context = ssl.create_default_context(cafile=certifi.where())
    if method == "GET" and params:
        url += "?" + params.decode("utf-8")

    req = urllib.request.Request(url)
    if http_proxy:
        req.set_proxy(http_proxy, 'http')
    if https_proxy:
        req.set_proxy(https_proxy, 'https')

    for k, v in headers.items():
        req.add_header(k, v)

    kwargs = {
        'url': req,
        'context': context,
    }

    if method == "POST":
        kwargs['data'] = params

    log.debug("Making a request to <%s> with params <%s>", url, kwargs.get('data', params))
    try:
        response = urllib.request.urlopen(**kwargs)
    except HTTPError as e:
        log.debug('The server couldn\'t fulfill the request. <%s>', e.code)
        res_body = e.read()
        return json.loads(res_body.decode("utf-8")) if json_format else res_body
    except URLError as e:
        log.debug("Request failed to reach a server <%s>", e.reason)
    else:
        res_body = response.read()
        return json.loads(res_body.decode("utf-8")) if json_format else res_body
    return {} if json_format else ''




