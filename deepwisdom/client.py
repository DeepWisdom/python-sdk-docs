import os

import yaml
from ._version import __version__

from .rest import DeepWisdomClientConfig, RESTClientObject
from deepwisdom.enums import API_DOMAIN

__all__ = ("Client", "get_client", "set_client")

_global_client = None


def Client(
    api_key=None,
    secret_key=None,
    appid=None,
    domain=None,
    admin_domain=API_DOMAIN.ADMIN
):
    """
    api请求客户端
    Args:
        admin_domain (str):
        api_key:
        secret_key:
        appid:
        domain:

    Returns:

    """
    global _global_client

    if api_key and appid and secret_key:
        dwconfig = DeepWisdomClientConfig(
            appid=appid,
            api_key=api_key,
            secret_key=secret_key,
            domain=domain,
            admin_domain=admin_domain
        )
    else:
        config_path = _get_default_config_file()
        if config_path is None:
            raise ValueError("Config No Found.")

        dwconfig = _config_from_file(config_path)

    if dwconfig.domain is None:
        dwconfig.domain = API_DOMAIN.API

    _global_client = RESTClientObject.from_config(dwconfig)

    return _global_client


def _get_client_version():
    return __version__


def get_client():
    return _global_client or Client()


class staticproperty(property):
    def __get__(self, instance, owner):
        return self.fget()


def set_client(client):
    """
    Set the global HTTP client for sdk.
    Returns previous client.
    """
    global _global_client
    previous = _global_client
    _global_client = client
    return previous


def _get_config_dir():
    return os.path.expanduser(os.path.join("~", ".config", "deepwisdom"))


def _get_default_config_file():
    first_choice_config_path = os.path.join(_get_config_dir(), "dwconfig.yaml")
    if _file_exists(first_choice_config_path):
        return first_choice_config_path
    else:
        return None


_file_exists = os.path.isfile


def _config_from_file(config_path):
    """
    Create and return a DeepWisdomClientConfig from a config path. The file must be
    a yaml formatted file

    Parameters
    ----------
    config_path : str
        Path to the configuration file

    Returns
    -------
    config : DeepWisdomClientConfig
    """
    with open(config_path, "rb") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return DeepWisdomClientConfig.from_data(data)

