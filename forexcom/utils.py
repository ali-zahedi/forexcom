import json
import logging
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

log = logging.getLogger()


def _url_encode(params):
    return urlencode(params).encode("utf-8")


def _iteritems(d):
    return iter(d.items())


def encode_params(params):
    """Encode the parameter for HTTP submissions, but
    only for non empty values..."""
    return _url_encode(dict([(k, v) for (k, v) in _iteritems(params) if v]))


def _parse_json(data):
    if data:
        return json.loads(data.decode("utf-8"))
    else:
        return {}


def send_request(
    method,
    base_url,
    path,
    params=None,
    json_format=False,
    headers=None,
    http_proxy=None,
    https_proxy=None,
    stream=False,
):
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

    req = Request(url)
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
        response = urlopen(**kwargs)
    except HTTPError as e:
        log.debug('The server couldn\'t fulfill the request. <%s>', e.code)
        if stream:
            return e
        res_body = e.read()
        return _parse_json(res_body) if json_format else res_body
    except URLError as e:
        log.debug("Request failed to reach a server <%s>", e.reason)
    else:
        if stream:
            return response
        res_body = response.read()
        return _parse_json(res_body) if json_format else res_body
    return {} if json_format else ''
