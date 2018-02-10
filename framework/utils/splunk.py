__author__ = 'pavan.tummalapalli'

import json
import logging.config

from .http_utils import HttpClient, HttpError

logger = logging.getLogger(__name__)


class SplunkClient:
    def __init__(self, **kwargs):
        """

        """
        if kwargs.get('host') is None:
            raise Exception('host should not be none')
        self.host = kwargs.get('host')

        if kwargs.get('username') is None:
            raise Exception('username should not be none')
        if kwargs.get('password')is None:
            raise Exception('password should not be none')
        self.auth = (kwargs.get('username'), kwargs.get('password'))

        if kwargs.get('source') is None:
            raise Exception('source should not be none')
        if kwargs.get('sourcetype') is None:
            raise Exception('sourcetype should not be none')
        if kwargs.get('index') is None:
            raise Exception('index should not be none')
        self.params = dict()
        self.params['source'] = kwargs.get('source')
        self.params['sourcetype'] = kwargs.get('sourcetype')
        self.params['index'] = kwargs.get('index')

        if kwargs.get('timeout') is None:
            raise Exception('timeout should not be none')
        self.timeout = kwargs.get('timeout')

        if kwargs.get('retries') is not None:
            self.retries = kwargs.get('retries')

        self.http_client = HttpClient(max_retries=self.retries, timeout=self.timeout)

        self.workers = kwargs.get('workers')

    def sendToSplunk(self, data=None):
        """
        send data to splunk.

        .. function:: sendToSplunk(host='http://localhost:8089/services/receivers/simple', response=None, **kwargs)

        sample data send to splunk is str format of JSON
        ::

            {
                "messageId": "e9de01c97136472190da3557527b1d2b",
                "status": "success"
            }

        :param response: raw event to send
        :type response: dict

        :Keyword Arguments:
            * *auth* (``tuple``) --
              username(``str``) , password(``str``)
            * *params* (``dict``) --
              index(``str``), source(``str``), and sourcetype(``str``)

        :raises HttpError

        """

        extra = dict()
        if self.host.startswith('https'):
            extra['verify'] = False

        try:
            response = self.http_client.post(url=self.host, data=json.dumps(data), auth=self.auth, params=self.params, **extra)
        except HttpError as e:
            logger.error(e, exc_info=True)
        return response


if __name__ == '__main__':

    kwargs = dict()
    kwargs['host'] = 'http://localhost:8089/services/receivers/simple'
    kwargs['username'] = 'admin'
    kwargs['password'] = 'password'
    kwargs['index'] = 'order'
    kwargs['source'] = 'test_splunk'
    kwargs['sourcetype'] = '_json'
    kwargs['timeout'] = 5
    kwargs['retries'] = 2

    # to search the nested json we use the following  - index="order" | spath path=a.aa.aaa=true
    msg = {
                "messageId": "e9de01c97136472190da3557527b1d2b",
                "status": "success",
                "a":{
                "aa": {
                    "aaa": "true"
                },
                "bb":{
                        "bbb":"false"
                }
        }
    }

    http = SplunkClient(**kwargs)
    res = http.sendToSplunk(msg)
    print(res.text)

