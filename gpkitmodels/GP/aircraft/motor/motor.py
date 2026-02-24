"Electric motor model"

from gpkit import Model, Var

from gpkitmodels import g


class MotorPerf(Model):
    """Electric Motor Performance Model

    Note: The last two constraints may not be tight if there is a motor energy
          constraint that does not size the motor. TCS removed to prevent
          unnecessary warnings - for most normal usage they will be tight.
    """

    Pshaft = Var("kW", "motor output shaft power")
    Pelec = Var("kW", "motor input shaft power")
    etam = Var("-", "motor efficiency")
    Q = Var("N*m", "torque")
    omega = Var("rpm", "propeller rotation rate")
    i = Var("amp", "current")
    v = Var("V", "voltage")

    def setup(self, static, state):
        Kv = static.Kv
        R = static.R
        i0 = static.i0
        V_max = static.V_max

        return [
            self.Pshaft == self.Q * self.omega,
            self.Pelec == self.v * self.i,
            self.etam == self.Pshaft / self.Pelec,
            static.Qmax >= self.Q,
            self.v <= V_max,
            self.i >= self.Q * Kv + i0,
            self.v >= self.omega / Kv + self.i * R,
        ]


class Motor(Model):
    """Electric Motor Model"""

    Qstar = Var("kg/(N*m)", "motor specific torque", value=0.8)
    W = Var("lbf", "motor weight")
    Qmax = Var("N*m", "motor max. torque")
    V_max = Var("V", "motor max voltage", value=300)
    Kv_min = Var("rpm/V", "min motor voltage constant", value=1)
    Kv_max = Var("rpm/V", "max motor voltage constant", value=1000)
    Kv = Var("rpm/V", "motor voltage constant")
    i0 = Var("amp", "zero-load current", value=4.5)
    R = Var("ohms", "internal resistance", value=0.033)

    flight_model = MotorPerf

    def setup(self):
        return [
            self.W >= self.Qstar * self.Qmax * g,
            self.Kv >= self.Kv_min,
            self.Kv <= self.Kv_max,
        ]
