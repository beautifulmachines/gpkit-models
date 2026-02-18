"""
Spacecraft propulsion models

This module provides models for analyzing rocket propulsion systems, including:
- Rocket stages
- Propulsive burns
- Performance analysis
"""

from gpkit import Variable, units
from gpkit.tools import te_exp_minus1

from .. import PerformanceModel


class Burn(PerformanceModel):
    """Generic rocket equation

    Constrains prop mass, cutoff mass, deltav, and ISP.

    Args:
        stage: A PhysicalComponent with ISP
        deltav: Variable for the required delta-V
    """

    def setup(self, stage, deltav):
        """See class docstring for parameter documentation."""
        g = 9.81 * units("m/s^2")

        m_prop = Variable("m_prop", "kg", "propellant mass")
        m_co = Variable("m_co", "kg", "mass at cutoff")

        constraints = [m_prop / m_co >= te_exp_minus1(deltav / g / stage["ISP"], 3)]

        return constraints
