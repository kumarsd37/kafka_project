__author__ = 'pavan.tummalapalli'


import json
import logging
try:  # Python 2.7+
    from logger import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

from requests.exceptions import ConnectionError
from requests import Session

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class HttpError(Exception):
    """General error raised for all problems in operation of the Http client."""

    def __init__(self, status_code=None, text=None, url=None, request=None, response=None, **kwargs):
        self.status_code = status_code
        self.text = text
        self.url = url
        self.request = request
        self.response = response
        self.headers = kwargs.get('headers', None)

    def __str__(self):
        """Return a string representation of the error."""
        t = "HttpError HTTP %s" % self.status_code
        if self.url:
            t += " url: %s" % self.url

        details = ""
        if self.request is not None and hasattr(self.request, 'headers'):
            details += "\n\trequest headers = %s" % self.request.headers

        if self.request is not None and hasattr(self.request, 'text'):
            details += "\n\trequest text = %s" % self.request.text

        if self.response is not None and hasattr(self.response, 'headers'):
            details += "\n\tresponse headers = %s" % self.response.headers

        if self.response is not None and hasattr(self.response, 'text'):
            details += "\n\tresponse text = %s" % self.response.text

        if self.text:
            t += "\n\ttext: %s" % self.text
            t += "\n\t" + details

        return t


def raise_on_error(r, verb='???', **kwargs):
    request = kwargs.get('request', None)
    # headers = kwargs.get('headers', None)

    if r is None:
        raise HttpError(None, **kwargs)

    if r.status_code >= 400:
        error = ''
        try:
            response = json.loads(r.text)
            error = r.text
        except ValueError:
            error = 'null'
        raise HttpError(
            r.status_code, error, r.url, request=request, response=r, **kwargs)

    if r.status_code not in [200, 201, 202, 204]:
        raise HttpError(r.status_code, request=request, response=r, **kwargs)

    if isinstance(r, Exception):
        raise HttpError(r.__str__())


class HttpClient(Session):
    """This class is supposed to retry requests that do return temporary errors.

    At this moment it supports: 502, 503, 504
    """

    def __init__(self, max_retries=1, timeout=None):
        self.max_retries = max_retries
        self.timeout = timeout
        super().__init__()

    def __recoverable(self, response, url, request, counter=1):
        msg = response
        if isinstance(response, ConnectionError):
            logger.warning("Got ConnectionError [%s] errno:%s on %s %s\n%s\%s" % (
                response, response.errno, request, url, vars(response), response.__dict__))
        if hasattr(response, 'status_code'):
            if response.status_code in [502, 503, 504, 401]:
                msg = "%s %s" % (response.status_code, response.reason)
            elif not (response.status_code == 200 and
                      len(response.content) == 0):
                return False
            else:
                msg = "please check with specific source"

        logger.warning("Got recoverable error from %s %s, will retry [%s/%s] . Err: %s" % (
            request, url, counter, self.max_retries, msg))

        return True

    def __verb(self, verb, url, retry_data=None, **kwargs):

        # if we pass a dictionary as the 'data' we assume we want to send json
        # data
        data = kwargs.get('data', {})
        if isinstance(data, dict):
            data = json.dumps(data)

        retry_number = 0
        while retry_number <= self.max_retries:
            response = None
            exception = None
            try:
                method = getattr(super(HttpClient, self), verb.lower())
                response = method(url, timeout=self.timeout, **kwargs)
                if response.status_code == 200:
                    return response
            except Exception as e:
                logger.warning(
                    "%s while doing %s %s [%s]" % (e, verb.upper(), url, kwargs))
                exception = e
            retry_number += 1

            if retry_number <= self.max_retries:
                response_or_exception = response if response is not None else exception
                if self.__recoverable(response_or_exception, url, verb.upper(), retry_number):
                    if retry_data:
                        # if data is a stream, we cannot just read again from it,
                        # retry_data() will give us a new stream with the data
                        kwargs['data'] = retry_data()
                    continue
                else:
                    break

        raise_on_error(response, verb=verb, **kwargs)
        return response

    def get(self, url, **kwargs):
        return self.__verb('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.__verb('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.__verb('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.__verb('DELETE', url, **kwargs)

    def head(self, url, **kwargs):
        return self.__verb('HEAD', url, **kwargs)

    def patch(self, url, **kwargs):
        return self.__verb('PATCH', url, **kwargs)

    def options(self, url, **kwargs):
        return self.__verb('OPTIONS', url, **kwargs)

