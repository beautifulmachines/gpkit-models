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
    test = Actuator_Propulsor_Test()
    test.solve()


def ME_propulsor_test():
    test = BladeElement_Propulsor_Test()
    _ = test.localsolve(use_leqs=False)  # cvxopt gets singular with leqs


def propulsor_test():
    test = Propulsor_Test()
    _ = test.solve()


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
    test = Motor_P_Test()
    test.solve()


def test():
    motor_test()
    actuator_propulsor_test()
    propulsor_test()
    ME_propulsor_test()


if __name__ == "__main__":
    test()
