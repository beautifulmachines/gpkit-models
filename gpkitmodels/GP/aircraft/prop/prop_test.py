"propeller tests"

import pytest
from gpkit import Model, units

from gpkitmodels.GP.aircraft.prop.propeller import Propeller
from gpkitmodels.GP.aircraft.wing.wing_test import FlightState
from gpkitmodels.SP.aircraft.prop.propeller import BladeElementProp


def simpleprop_test():
    "test simple propeller model"
    fs = FlightState()
    p = Propeller()
    pp = p.flight_model(p, fs)
    m = Model(
        1 / pp.eta + p.W / (100.0 * units("lbf")) + pp.Q / (100.0 * units("N*m")),
        [fs, p, pp],
    )
    m.substitutions.update({"rho": 1.225, "V": 50, "T": 100, "omega": 1000})
    sol = m.solve(verbosity=0)
    assert sol.cost == pytest.approx(3.7509, rel=1e-3)


def ME_eta_test():

    fs = FlightState()
    p = Propeller()
    pp = BladeElementProp(p, fs)
    pp.substitutions[pp.T] = 100
    pp.cost = (
        1.0 / pp.eta + pp.Q / (1000.0 * units("N*m")) + p.T_m / (1000 * units("N"))
    )
    sol = pp.localsolve(verbosity=0, iteration_limit=400)
    assert sol.cost == pytest.approx(1.6613, rel=1e-3)


def test():
    "tests"
    simpleprop_test()
    ME_eta_test()


if __name__ == "__main__":
    test()
