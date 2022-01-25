"""
This module contains compatibility fixes to allow usage of both 1.x and 2.x Trafaret versions
"""
try:
    from trafaret import ToInt as Int
except ImportError:
    from trafaret import Int  # noqa


try:
    from trafaret import AnyString as String
except ImportError:
    from trafaret import String  # noqa

try:
    from trafaret import Any as Any
except ImportError:
    from trafaret import Any
