import json
import time

import requests
from urllib import parse

from urllib.parse import urljoin, urlparse

from .enums import (
    DEFAULT_TIMEOUT,
    DEFAULT_DOMAIN,
    DEFAULT_ADMIN_DOMAIN,
    API_URL,
)

import trafaret as t
from ._compat import Int, String

from . import __version__, errors


class RESTClientObject(requests.Session):
    """

    """

    @classmethod
    def from_config(cls, config):
        return cls(
            appid=config.appid,
            api_key=config.api_key,
            secret_key=config.secret_key,
            domain=config.domain,
            admin_domain=config.admin_domain
        )

    def __init__(
            self,
            appid=None,
            api_key=None,
            secret_key=None,
            domain=None,
            admin_domain=None

    ):
        super(RESTClientObject, self).__init__()

        self._auth_obj = {}
        self.appid = appid
        self.api_key = api_key
        self.secret_key = secret_key
        self.connect_timeout = DEFAULT_TIMEOUT.CONNECT
        self.socket_timeout = DEFAULT_TIMEOUT.SOCKET
        self.upload_timeout = 60.0 * 20
        self.domain = domain
        self.admin_domain = admin_domain

    def _auth(self, refresh=False):
        """
        OAuth2.0校验
        Args:
            refresh:

        Returns:
            obj: auth信息

        """
        # 未过期
        if not refresh:
            tm = self._auth_obj.get('time', 0) + int(self._auth_obj.get('expires_in', 0)) - 30
            if tm > int(time.time()):
                return self._auth_obj

        obj = self.post(self.domain + "/" + API_URL.AUTH, json={
            "grant_type": "client_credentials",
            "api_key": self.api_key,
            "secret_key": self.secret_key,
            "appid": self.appid
        }, timeout=(
            self.connect_timeout,
            self.socket_timeout,
        )).json()

        obj['time'] = int(time.time())
        self._auth_obj = obj

        return obj

    def _get_auth_headers(self, headers=None, auth_obj=None):
        """
        更新接口的请求头
        Args:
            headers: 请求头
            auth_obj: auth信息

        Returns:
            headers: 更新后的请求头
        """

        headers = headers or {}

        headers['authorization'] = auth_obj["data"]['access_token']
        headers['UserId'] = str(auth_obj["data"]['user_id'])
        return headers

    def _request(self, method, url, data=None, join_domain=False, headers=None):
        """
        请求api封装
        Args:
            method: 方法
            url: url
            data:
            join_domain: 是否加域名
            headers: 请求头

        Returns:
            response.json()
        """

        # 获取access_token
        auth_obj = self._auth()
        headers = self._get_auth_headers(headers, auth_obj)
        headers["Content-Type"] = 'application/x-www-form-urlencoded'

        # 增加domain
        if not url.startswith("http") or join_domain:
            url = self._join_endpoint(url)

        # tj后端需要的参数
        data["bcode"] = "autotable"
        data["token"] = "Hy+b55u4C9KE8GSKEJ5xhw=="
        payload = parse.urlencode(data)

        if method == "GET":
            response = super(RESTClientObject, self).request(method, url, params=data,
                                                             headers=headers,
                                                             timeout=(self.connect_timeout, self.socket_timeout))
        else:
            response = super(RESTClientObject, self).request(method, url, data=payload,
                                                         headers=headers,
                                                         timeout=(self.connect_timeout, self.socket_timeout))
        if not response:
            handle_http_error(response)

        return response.json()

    def _post(self, url, data=None, join_domain=False, headers=None):
        return self._request("POST", url, data, join_domain, headers)

    def _get(self, url, data=None, join_domain=False, headers=None):
        return self._request("GET", url, data, join_domain, headers)

    def _patch(self, url, data=None, join_domain=False, headers=None):
        return self._request("PATCH", url, data, join_domain, headers)

    def _delete(self, url, data=None, join_domain=False, headers=None):
        return self._request("DELETE", url, data, join_domain, headers)

    def _upload(self, url, data, files, join_domain=False, headers=None):
        """
        文件上传
        Args:
            url:
            data:
            files:
            join_domain:
            headers:

        Returns:

        """

        # 获取access_token
        auth_obj = self._auth()
        headers = self._get_auth_headers(headers, auth_obj)

        # 增加domain
        if not url.startswith("http") or join_domain:
            url = self._join_endpoint(url)

        # tj后端需要的参数
        data["bcode"] = "autotable"
        data["token"] = "Hy+b55u4C9KE8GSKEJ5xhw=="

        response = super(RESTClientObject, self).request("POST", url, data=data,
                                                         headers=headers, files=files,
                                                         timeout=(self.connect_timeout, self.upload_timeout))
        if not response:
            handle_http_error(response)

        return response.json()

    def _join_endpoint(self, url):
        if url.startswith("/"):
            raise ValueError("Cannot add absolute path {0} to endpoint".format(url))
        # Ensure endpoint always ends in a single slash
        endpoint = self.domain.rstrip("/") + "/"
        # normalized url join
        return urljoin(endpoint, url)

    def raw_request(self, method: str, url, data=None, json=None, join_domain=False, headers=None):

        response = super(RESTClientObject, self).request(method, url, data=data, json=json,
                                                         headers=headers,
                                                         timeout=(self.connect_timeout, self.socket_timeout))
        if not response:
            handle_http_error(response)

        return response.json()


def _http_message(response):
    # print(response)
    # return
    if response.status_code == 401:
        message = (
            "The server is saying you are not properly "
            "authenticated. Please make sure your API "
            "token is valid."
        )
    else:
        message = response.content
    return message


def handle_http_error(response, **kwargs):
    message = _http_message(response)
    if 400 <= response.status_code < 500:
        exception_type = errors.ClientError
        # One-off approach to raising special exception for now. We'll do something more
        # systematic when we have more of these:
        try:
            parsed_json = response.json()  # May raise error if response isn't JSON
        except (ValueError, AttributeError):
            parsed_json = {}
        template = "{} client error: {}"
        exc_message = template.format(response.status_code, message)
        raise exception_type(exc_message, response.status_code, json=parsed_json)
    else:
        template = "{} server error: {}"
        exc_message = template.format(response.status_code, message)
        raise errors.ServerError(exc_message, response.status_code)


class DeepWisdomClientConfig(object):
    """
    
    """

    _converter = t.Dict(
        {
            t.Key("appid"): Int,
            t.Key("api_key"): String,
            t.Key("secret_key"): String,
            t.Key("domain"): String,
            t.Key("admin_domain", optional=True): String
        }
    ).allow_extra("*")
    _fields = {k.to_name or k.name for k in _converter.keys}

    def __init__(
            self,
            appid=None,
            api_key=None,
            secret_key=None,
            domain=None,
            admin_domain=None
    ):
        self._authObj = None
        self.appid = appid
        self.api_key = api_key
        self.secret_key = secret_key
        self.domain = domain
        self.admin_domain = admin_domain

    @classmethod
    def from_data(cls, data):
        checked = {k: v for k, v in cls._converter.check(data).items() if k in cls._fields}
        return cls(**checked)
