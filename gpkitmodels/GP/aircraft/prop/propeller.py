"propeller model"

from gpkit import Model, Var, VectorVariable
from numpy import asarray, pi


class ActuatorProp(Model):
    "Propeller Model"

    T = Var("lbf", "thrust")
    Tc = Var("-", "coefficient of thrust")
    etaadd = Var("-", "swirl and nonuniformity losses", value=0.7)
    etav = Var("-", "viscous losses", value=0.85)
    etai = Var("-", "inviscid losses")
    eta = Var("-", "overall efficiency")
    z1 = Var("-", "efficiency helper 1")
    z2 = Var("-", "efficiency helper 2")
    lam = Var("-", "advance ratio")
    CT = Var("-", "thrust coefficient")
    CP = Var("-", "power coefficient")
    Q = Var("N*m", "torque")
    omega = Var("rpm", "propeller rotation rate")
    omega_max = Var("rpm", "max rotation rate", value=10000)
    P_shaft = Var("kW", "shaft power")
    M_tip = Var("-", "Tip mach number", value=0.5)
    a = Var("m/s", "Speed of sound at altitude", value=295)

    def helper(self, c):
        return 2.0 - 1.0 / asarray(c[self.etaadd])

    def setup(self, static, state):
        V = state.V
        rho = state.rho
        R = static.R
        eta, Tc, omega, lam = self.eta, self.Tc, self.omega, self.lam

        constraints = [
            eta <= self.etav * self.etai,
            Tc >= self.T / (0.5 * rho * V**2 * pi * R**2),
            self.z2 >= Tc + 1,
            self.etai * (self.z1 + self.z2**0.5 / self.etaadd) <= 2,
            lam >= V / (omega * R),
            self.CT >= Tc * lam**2,
            self.CP <= self.Q * omega / (0.5 * rho * (omega * R) ** 3 * pi * R**2),
            eta >= self.CT * lam / self.CP,
            omega <= self.omega_max,
            self.P_shaft == self.Q * omega,
            (self.M_tip * self.a) ** 2 >= (omega * R) ** 2 + V**2,
            static.T_m >= self.T,
        ]
        return constraints, {self.z1: self.helper}


class Propeller(Model):
    "Propeller Model"

    R = Var("ft", "prop radius")
    W = Var("lbf", "prop weight")
    K = Var("1/ft^2", "prop weight scaling factor", value=4e-4)
    T_m = Var("lbf", "prop max static thrust")

    flight_model = ActuatorProp

    def setup(self, N=5):
        self.N = N
        self.c = VectorVariable(N, "c", "ft", "prop chord")
        return [self.W >= self.K * self.T_m * self.R**2]
