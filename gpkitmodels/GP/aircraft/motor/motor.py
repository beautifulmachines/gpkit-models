"Electric motor model"

from gpkit import Model, parse_variables

from gpkitmodels import g


class MotorPerf(Model):
    """Electric Motor Performance Model

    Note: The last two constraints may not be tight if there is a motor energy
          constraint that does not size the motor. TCS removed to prevent
          unnecessary warnings - for most normal useage they will be tight.

    Variables
    ---------
    Pshaft                  [kW]            motor output shaft power
    Pelec                   [kW]            motor input shaft power
    etam                    [-]             motor efficiency
    Q                       [N*m]           torque
    omega                   [rpm]           propeller rotation rate
    i                       [amp]           current
    v                       [V]             woltage
    """

    @parse_variables(__doc__, globals())
    def setup(self, static, state):
        Kv = static.Kv
        R = static.R
        i0 = static.i0
        V_max = static.V_max

        return [
            Pshaft == Q * omega,
            Pelec == v * i,
            etam == Pshaft / Pelec,
            static.Qmax >= Q,
            v <= V_max,
            i >= Q * Kv + i0,
            v >= omega / Kv + i * R,
        ]


class Motor(Model):
    """Electric Motor Model

    Variables
    ---------
    Qstar       .8          [kg/(N*m)]      motor specific torque
    W                       [lbf]           motor weight
    Qmax                    [N*m]           motor max. torque
    V_max       300         [V]             motor max voltage
    Kv_min     1            [rpm/V]         min motor voltage constant
    Kv_max     1000         [rpm/V]         max motor voltage constant
    Kv                      [rpm/V]         motor voltage constant
    i0         4.5          [amp]           zero-load current
    R          .033         [ohms]          internal resistance
    """

    flight_model = MotorPerf

    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = [W >= Qstar * Qmax * g, Kv >= Kv_min, Kv <= Kv_max]

        return constraints
