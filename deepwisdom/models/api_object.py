import six
import trafaret as t

from deepwisdom.client import get_client, staticproperty
from deepwisdom.utils import from_api

class APIObject(object):
    # _client = staticproperty(get_client)
    _converter = t.Dict({}).allow_extra("*")

    @classmethod
    def _fields(cls):
        return {k.to_name or k.name for k in cls._converter.keys}

    @classmethod
    def from_data(cls, data):
        checked = cls._converter.check(data)
        safe_data = cls._filter_data(checked)
        return cls(**safe_data)

    @classmethod
    def _filter_data(cls, data):
        fields = cls._fields()
        return {key: value for key, value in six.iteritems(data) if key in fields}

    @classmethod
    def _safe_data(cls, data, do_recursive=False):
        return cls._filter_data(cls._converter.check(from_api(data, do_recursive=do_recursive)))

    @classmethod
    def _server_data(cls, url, data):
        return cls._client._get(url, data)["data"]

    @classmethod
    def _upload(cls, url, data, files):
        return cls._client._upload(url, data, files)

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        """
        """
        case_converted = from_api(data, keep_attrs=keep_attrs)
        return cls.from_data(case_converted)





