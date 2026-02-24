"fuselage skin"

import numpy as np
from gpkit import Model, Var

from gpkitmodels import g


class FuselageSkin(Model):
    "fuselage skin model"

    W = Var("lbf", "fuselage skin weight")
    m = Var("kg", "fuselage skin mass")
    rho_kevlar = Var("g/cm**3", "kevlar density", value=1.3629)
    t = Var("in", "skin thickness")
    t_min = Var("in", "minimum skin thickness", value=0.03)
    I = Var("m**4", "wing skin moment of inertia")
    I_g = Var("kg*m**2", "mass moment of inertia")
    E = Var("GPa", "Young's Modulus of Kevlar", value=30)

    def setup(self, S, R, l):
        self.R = R
        self.l = l
        return [
            self.m >= S * self.rho_kevlar * self.t,
            self.W >= self.m * g,
            self.t >= self.t_min,
            self.I <= np.pi * R**3 * self.t,
            self.I_g >= self.m * (4 * R**2 + 4 * R * self.t + self.t**2),
        ]

    def loading(self, Wcent):
        return FuselageSkinL(self, Wcent)

    def landing(self, Wcent):
        return FuselageLanding(self, Wcent)


class FuselageSkinL(Model):
    "fuselage skin loading"

    M_h = Var("N*m", "horizontal axis center fuselage moment")
    N_max = Var("-", "max loading", value=5)
    sigma_kevlar = Var("MPa", "stress strength of Kevlar", value=190)
    q = Var("N/m", "distributed load")
    kappa = Var("-", "maximum tip deflection ratio", value=0.05)

    def setup(self, static, Wcent):
        return [
            self.M_h >= self.N_max * Wcent / 4 * static.l,
            self.sigma_kevlar >= self.M_h * static.R / static.I,
            self.q >= Wcent * self.N_max / static.l,
            self.kappa * static.l / 2
            >= self.q * (static.l / 2) ** 4 / (8 * static.E * static.I),
        ]


class FuselageLanding(Model):
    "fuselage loading case"

    F = Var("lbf", "maximum landing force")
    N_max = Var("-", "maximum landing load factor", value=5)
    a = Var("m/s**2", "landing vertical acceleration")
    omegadot = Var("1/s**2", "angular acceleration about rear fuselage")
    M_g = Var("N*m", "landing moment about center of mass")
    sigma_kevlar = Var("MPa", "stress strength of Kevlar", value=190)

    def setup(self, static, Wcent):
        return [
            self.F >= Wcent * self.N_max,
            self.a >= self.F / static.m,
            self.omegadot >= self.a / (static.l / 2),
            self.M_g >= static.I_g * self.omegadot,
            self.sigma_kevlar >= self.M_g * static.R / static.I,
        ]
