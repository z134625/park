import warnings
import re

from .utils.data import Compare, VersionCompare
from .conf.setting import PythonVersion
from .conf.setting import ParkConcurrency

__version__ = "1.7.1"
__name__ = "park"

python_version = re.split(r'[|\s]', PythonVersion)
if ">=" not in Compare(VersionCompare(python_version[0]), VersionCompare("3.10.0")):
    warnings.warn("当前python版本低于要求版本(3.10.0)，可能会有未知错误", RuntimeWarning, stacklevel=2)


del warnings, re, Compare, VersionCompare, PythonVersion, ParkConcurrency, python_version
