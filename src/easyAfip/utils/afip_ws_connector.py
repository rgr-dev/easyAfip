import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context
import logging

logger = logging.getLogger(__name__)

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers(":HIGH:!DH:!aNULL")
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

    def build_response(self, req, resp):
        response = super(SSLAdapter, self).build_response(req, resp)
        return response

class AfipWSConnector:

    HEADERS = {
        "Content-Type": "text/xml;charset=UTF-8",
        "User-Agent": "easy-afip/1.0 (+https://example.com/contact)"
    }

    def __init__(self, ws_url: str):
        self.ws_url = ws_url

    def execute_request(self, data: str, headers:dict ={}):
        headers = {**self.HEADERS, **headers}
        session = requests.Session()
        session.mount('https://', SSLAdapter())
        response = session.post(self.ws_url, data=data, headers=headers, verify=False)
        # response = requests.post(self.ws_url, headers=headers, data=data, verify=False)
        if response.status_code != 200:
            logger.warning('AFIP communication error. Error Detail: %s', response.text)
            raise Exception(f"AFIP service communication error. ErrorCode={response.status_code}")
        return response.text

    def add_header(self, key: str, value: str):
        self.HEADERS[key] = value