"tail boom model"

from gpkit import Model, Var, Variable, VectorVariable, units
from numpy import pi

from gpkitmodels import g
from gpkitmodels.GP.beam.beam import Beam

from .tube_spar import TubeSpar

# pylint: disable=invalid-name


class TailBoomAero(Model):
    "Tail Boom Aero Model"

    Cf = Var("-", "tail boom skin friction coefficient")
    Re = Var("-", "tail boom reynolds number")

    def setup(self, static, state):
        self.state = state

        l = self.l = static.l
        rho = self.rho = state.rho
        V = self.V = state.V
        mu = self.mu = state.mu

        return [
            self.Re == V * rho * l / mu,
            self.Cf >= 0.455 / self.Re**0.3,
        ]


class TailBoomState(Model):
    "Tail Boom Loading State"

    rhosl = Var("kg/m^3", "air density at sea level", value=1.225)
    Vne = Var("m/s", "never exceed vehicle speed", value=40)

    def setup(self):
        pass


class VerticalBoomTorsion(Model):
    "Tail Boom Torsion from Vertical Tail"

    T = Var("N*m", "vertical tail moment")
    taucfrp = Var("MPa", "torsional stress limit of carbon", value=210)

    def setup(self, tailboom, vtail, state):
        J = self.J = tailboom.J
        d0 = self.d0 = tailboom.d
        b = self.b = vtail.planform.b
        S = self.S = vtail.planform.S
        rhosl = self.rhosl = state.rhosl
        Vne = self.Vne = state.Vne
        CLmax = vtail.planform.CLmax

        return [
            self.T >= 0.5 * rhosl * Vne**2 * S * CLmax * b,
            self.taucfrp >= self.T * d0 / 2 / J,
        ]


class TailBoomBending(Model):
    "Tail Boom Bending"

    F = Var("N", "tail force")
    th = Var("-", "tail boom deflection angle")
    kappa = Var("-", "max tail boom deflection", value=0.1)
    Nsafety = Var("-", "safety load factor", value=1.0)

    def setup(self, tailboom, htail, state):
        N = self.N = tailboom.N
        self.state = state
        self.htail = htail
        self.tailboom = tailboom

        Beam.qbarFun = [1e-10] * N
        Beam.SbarFun = [1.0] * N
        beam = self.beam = Beam(N)

        Mr = VectorVariable(tailboom.N - 1, "Mr", "N*m", "section root moment")

        I = tailboom.I
        tailboom.I0 = I[0]
        l = tailboom.l
        S = htail.planform.S
        E = tailboom.material.E
        Sy = tailboom.Sy
        qne = state.qne
        CLmax = htail.planform.CLmax
        deta = tailboom.deta
        sigma = tailboom.material.sigma

        constraints = [
            beam.dx == deta,
            self.F >= qne * S,
            beam["\\bar{EI}"] <= E * I / self.F / l**2 / 2,
            Mr >= beam["\\bar{M}"][:-1] * self.F * l,
            sigma >= Mr / Sy,
            self.th == beam["\\theta"][-1],
            beam["\\bar{\\delta}"][-1] * CLmax * self.Nsafety <= self.kappa,
        ]

        self.tailboomJ = hasattr(tailboom, "J")
        if self.tailboomJ:
            constraints.append(tailboom.J >= 1e-10 * units("m^4"))

        return constraints, beam


class TailBoom(TubeSpar):
    "Tail Boom Model"

    l = Var("ft", "tail boom length")
    S = Var("ft^2", "tail boom surface area")
    b = Var("ft", "twice tail boom length")
    tau = Var("-", "thickness to width ratio", value=1.0)
    rhoA = Var("kg/m^2", "total aerial density", value=0.15)

    flight_model = TailBoomAero
    tailLoad = TailBoomBending
    secondaryWeight = None
    spar_model = TubeSpar  # override in subclasses to swap spar type

    def setup(self, N=5):
        self.N = N
        # deta and cave must exist before spar_model.setup() accesses surface.deta/cave
        self.deta = Variable("deta", 1.0 / (N - 1), "-", "normalized segment length")
        self.cave = VectorVariable(N - 1, "cave", "in", "average segment width")
        self.spar = type(self).spar_model.setup(self, N, self)

        if self.secondaryWeight:
            self.weight.right += self.rhoA * g * self.S

        d0 = self.d0 = self.d[0]

        return self.spar, [self.S == self.l * pi * d0, self.b == 2 * self.l]
