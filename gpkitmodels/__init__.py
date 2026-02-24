"""GPkit Models - Library of exponential cone compatible sizing models"""

__version__ = "0.1.4"

from gpkit import Variable

from .tools.modular import PerformanceModel, PhysicalComponent

g = Variable("g", 9.81, "m/s^2", "earth surface gravitational acceleration")

__all__ = (PerformanceModel, PhysicalComponent)
