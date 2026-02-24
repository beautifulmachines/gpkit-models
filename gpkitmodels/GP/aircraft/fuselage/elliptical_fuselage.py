"elliptical fuselage.py"

import numpy as np
from gpkit import Model, Var

from gpkitmodels import g
from gpkitmodels.GP.materials import cfrpfabric


class FuselageAero(Model):
    "Fuselage Aerodynamic Model"

    Cf = Var("-", "fuselage skin friction coefficient")
    Re = Var("-", "fuselage reynolds number")
    Cd = Var("-", "fuselage drag coefficient")
    mfac = Var("-", "fuselage drag margin", value=1.0)

    def setup(self, static, state):
        V = state.V
        rho = state.rho
        l = static.l
        mu = state.mu
        k = static.k

        constraints = [
            self.Re == V * rho * l / mu,
            self.Cf >= 0.455 / self.Re**0.3,
            self.Cd / self.mfac >= self.Cf * k,
        ]

        return constraints


class Fuselage(Model):
    "Fuselage Model"

    R = Var("ft", "fuselage radius")
    l = Var("ft", "fuselage length")
    S = Var("ft^2", "wetted fuselage area")
    W = Var("lbf", "fuselage weight")
    mfac = Var("-", "fuselage weight margin factor", value=2.0)
    f = Var("-", "fineness ratio of length to diameter")
    k = Var("-", "fuselage form factor")
    Vol = Var("ft^3", "fuselage volume")
    rhofuel = Var("lbf/gallon", "density of 100LL", value=6.01)
    rhocfrp = Var("g/cm^3", "density of CFRP", value=1.6)
    t = Var("in", "fuselage skin thickness")
    nply = Var("-", "number of plys", value=2)

    material = cfrpfabric
    flight_model = FuselageAero

    def setup(self):
        rhocfrp = self.material.rho
        tmin = self.material.tmin

        constraints = [
            self.f == self.l / self.R / 2,
            self.k >= 1 + 60 / self.f**3 + self.f / 400,
            3 * (self.S / np.pi) ** 1.6075
            >= 2 * (self.l * self.R * 2) ** 1.6075 + (2 * self.R) ** (2 * 1.6075),
            self.Vol <= 4 * np.pi / 3 * (self.l / 2) * self.R**2,
            self.W / self.mfac >= self.S * rhocfrp * self.t * g,
            self.t >= self.nply * tmin,
            self.material,
        ]

        return constraints
