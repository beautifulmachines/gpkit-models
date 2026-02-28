import pytest
from gpkit import Model

from gpkitmodels.GP.aircraft.fuselage.elliptical_fuselage import Fuselage
from gpkitmodels.GP.aircraft.wing.wing_test import FlightState


def test_ellp():
    "elliptical fuselage test"
    f = Fuselage()
    fs = FlightState()
    faero = f.flight_model(f, fs)
    f.substitutions[f.Vol] = 1.33

    m = Model(f.W * faero.Cd, [f, fs, faero])
    sol = m.solve(verbosity=0)
    assert sol.cost == pytest.approx(0.016480, rel=1e-2)


def test():
    "tests"
    test_ellp()


if __name__ == "__main__":
    test()
