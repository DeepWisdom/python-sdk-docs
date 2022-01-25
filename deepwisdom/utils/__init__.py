# -*- encoding: utf-8 -*-

"""This module is not considered part of the public interface. As of 2.3, anything here
may change or be removed without warning."""
from collections import defaultdict
from datetime import date, datetime
import re

from dateutil import parser, tz
import pytz
import six

class rawdict(dict):
    """
    Dictionaries returned from models will have their keys snakeCased.
    Wrapping them in rawdict will pass them through to the API verbatim.
    """

    pass

ALL_CAPITAL = re.compile(r"(.)([A-Z][a-z]+)")
CASE_SWITCH = re.compile(r"([a-z0-9])([A-Z])")
UNDERSCORES = re.compile(r"([a-z]?)(_+)([a-z])")

def underscorize(value):
    partial_result = ALL_CAPITAL.sub(r"\1_\2", value)
    return CASE_SWITCH.sub(r"\1_\2", partial_result).lower()


def underscoreToCamel(match):
    prefix, underscores, postfix = match.groups()
    if len(underscores) > 1:
        # underscoreToCamel('sample_pct__gte') -> 'samplePct__gte'
        return match.group()
    return prefix + postfix.upper()


def camelize(value):
    return UNDERSCORES.sub(underscoreToCamel, value)


def from_api(data, do_recursive=True, keep_attrs=None, keep_null_keys=False):
    if type(data) not in (dict, list):
        return data
    if isinstance(data, list):
        return _from_api_list(data, do_recursive=do_recursive, keep_null_keys=keep_null_keys)
    return _from_api_dict(
        data, do_recursive=do_recursive, keep_attrs=keep_attrs, keep_null_keys=keep_null_keys
    )


def _from_api_dict(data, do_recursive=True, keep_attrs=None, keep_null_keys=False):
    keep_attrs = keep_attrs or []
    # prepare attributes in format 'top.middle.bottom' for processing
    parsed_attrs = []
    for attr in keep_attrs:
        if isinstance(attr, six.string_types):
            parsed_attrs.append(attr.split("."))
        else:
            parsed_attrs.append(attr)
    # take index 0 since recursion goes from top to bottom
    current_level = [attr.pop(0) for attr in parsed_attrs if len(attr)]
    # filter out empty attrs to pass through recursive call
    next_level_attrs = [attr for attr in parsed_attrs if attr]

    app_data = {}
    for k, v in six.iteritems(data):
        k_under = underscorize(k)
        if v is None and k_under not in current_level and not keep_null_keys:
            continue
        if do_recursive:
            data_val = from_api(
                v,
                do_recursive=do_recursive,
                keep_attrs=next_level_attrs,
                keep_null_keys=keep_null_keys,
            )
        else:
            data_val = v
        app_data[k_under] = data_val
    return app_data


def _from_api_list(data, do_recursive=True, keep_null_keys=False):
    return [
        from_api(datum, do_recursive=do_recursive, keep_null_keys=keep_null_keys) for datum in data
    ]


def remove_empty_keys(metadata, keep_attrs=None):
    keep_attrs = keep_attrs or []
    return {k: v for k, v in metadata.items() if v is not None or k in keep_attrs}


def parse_time(time_str):
    try:
        return parser.parse(time_str, tzinfos={"UTC": tz.tzutc()})
    except Exception:
        return time_str


def datetime_to_string(datetime_obj, ensure_rfc_3339=False):
    """ Converts to isoformat
    """
    if not isinstance(datetime_obj, datetime):
        msg = "expected to be passed a datetime.datetime, was passed {}".format(type(datetime_obj))
        raise ValueError(msg)
    if ensure_rfc_3339 and not datetime_obj.tzinfo:
        datetime_obj = datetime_obj.replace(tzinfo=pytz.utc)
    return datetime_obj.isoformat()


def to_api(data, keep_attrs=None):
    """
    :param data: dictionary {'max_digits': 1}
    :return: {'maxDigits': 1}
    """
    if not data:
        return {}
    assert isinstance(data, dict), "Wrong type"
    return _to_api_item(data, keep_attrs)


def _to_api_item(item, keep_attrs=None):
    if isinstance(item, rawdict):
        return item
    elif isinstance(item, dict):
        dense_item = remove_empty_keys(item, keep_attrs)
        return {
            camelize(k): _to_api_item(v, keep_attrs=keep_attrs)
            for k, v in six.iteritems(dense_item)
        }
    elif isinstance(item, list):
        return [_to_api_item(subitem, keep_attrs=keep_attrs) for subitem in item]
    elif isinstance(item, datetime):
        return datetime_to_string(item)
    elif isinstance(item, date):
        return item.isoformat()
    else:
        return item


def get_id_from_response(response):
    location_string = response.headers["Location"]
    return get_id_from_location(location_string)


def get_id_from_location(location_string):
    return location_string.split("/")[-2]


def get_duplicate_features(features):
    duplicate_features = set()
    seen_features = set()
    for feature in features:
        if feature in seen_features:
            duplicate_features.add(feature)
        else:
            seen_features.add(feature)
    return list(duplicate_features)


