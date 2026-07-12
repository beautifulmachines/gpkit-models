"""GPkit Models - Library of exponential cone compatible sizing models"""

from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("gpkit-models")
except _PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

from gpkit import Variable

from .tools.modular import PerformanceModel, PhysicalComponent

g = Variable("g", 9.81, "m/s^2", "earth surface gravitational acceleration")

__all__ = ("PerformanceModel", "PhysicalComponent")
