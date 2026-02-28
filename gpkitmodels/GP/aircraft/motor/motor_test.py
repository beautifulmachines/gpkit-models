import pytest
from gpkit import Model, units

from gpkitmodels.GP.aircraft.motor.motor import Motor, MotorPerf
from gpkitmodels.GP.aircraft.prop.propeller import ActuatorProp, Propeller
from gpkitmodels.GP.aircraft.wing.wing_test import FlightState
from gpkitmodels.SP.aircraft.prop.propeller import BladeElementProp


class Propulsor_Test(Model):
    """Propulsor Test Model"""

    def setup(self):
        fs = FlightState()
        motor = Motor()
        prop = Propeller()
        mp = MotorPerf(motor, fs)
        pp = prop.flight_model(prop, fs)
        pp.substitutions[pp.T] = 100
        self.cost = (
            1.0 / mp.etam + (prop.W + motor.W) / (1000 * units("lbf")) + 1.0 / pp.eta
        )
        return fs, motor, prop, mp, pp, [pp.Q == mp.Q, pp.omega == mp.omega]


class Actuator_Propulsor_Test(Model):
    """Propulsor Test Model w/ Actuator Disk Propeller"""

    def setup(self):
        fs = FlightState()
        motor = Motor()
        prop = Propeller()
        mp = MotorPerf(motor, fs)
        pp = ActuatorProp(prop, fs)
        pp.substitutions[pp.T] = 100
        self.cost = mp.Pelec / (1000 * units("W")) + (prop.W + motor.W) / (
            1000 * units("lbf")
        )
        return fs, motor, prop, mp, pp, [pp.Q == mp.Q, pp.omega == mp.omega]


class BladeElement_Propulsor_Test(Model):
    """Propulsor Test Model w/ Blade Element Propeller"""

    def setup(self):
        fs = FlightState()
        motor = Motor()
        prop = Propeller()
        mp = MotorPerf(motor, fs)
        pp = BladeElementProp(prop, fs)
        pp.substitutions[pp.T] = 100
        self.cost = mp.Pelec / (1000 * units("W")) + (prop.W + motor.W) / (
            1000 * units("lbf")
        )
        return fs, motor, prop, mp, pp, [pp.Q == mp.Q, pp.omega == mp.omega]


def actuator_propulsor_test():
    m = Actuator_Propulsor_Test()
    sol = m.solve(verbosity=0)
    assert sol.cost == pytest.approx(28.532, rel=1e-2)


def ME_propulsor_test():
    m = BladeElement_Propulsor_Test()
    sol = m.localsolve(verbosity=0, use_leqs=False)  # cvxopt gets singular with leqs
    assert sol.cost == pytest.approx(25.134, rel=1e-2)


def propulsor_test():
    m = Propulsor_Test()
    sol = m.solve(verbosity=0)
    assert sol.cost == pytest.approx(2.5481, rel=1e-2)


class Motor_P_Test(Model):
    def setup(self):
        fs = FlightState()
        m = Motor()
        mp = MotorPerf(m, fs)
        self.mp = mp
        mp.substitutions[m.Qmax] = 100
        mp.substitutions[mp.Q] = 10
        self.cost = 1.0 / mp.etam + m.W / (100.0 * units("lbf"))
        return self.mp, fs, m


class speed_280_motor(Model):
    def setup(self):
        fs = FlightState()
        m = Motor()
        mp = MotorPerf(m, fs)
        self.mp = mp
        mp.substitutions[m.Qmax] = 100
        mp.substitutions[mp.R] = 0.7
        mp.substitutions[mp.i0] = 0.16
        mp.substitutions[mp.Kv] = 3800
        mp.substitutions[mp.v] = 6
        self.cost = 1.0 / mp.etam
        return self.mp, fs


class hacker_q150_45_motor(Model):
    def setup(self):
        fs = FlightState()
        m = Motor()
        mp = MotorPerf(m, fs)
        self.mp = mp
        mp.substitutions[m.Qmax] = 10000
        mp.substitutions[mp.R] = 0.033
        mp.substitutions[mp.i0] = 4.5
        mp.substitutions[mp.Kv] = 29
        self.cost = 1.0 / mp.etam
        return self.mp, fs


def motor_test():
    m = Motor_P_Test()
    sol = m.solve(verbosity=0)
    assert sol.cost == pytest.approx(2.8103, rel=1e-2)


def test():
    motor_test()
    actuator_propulsor_test()
    propulsor_test()
    ME_propulsor_test()


if __name__ == "__main__":
    test()
