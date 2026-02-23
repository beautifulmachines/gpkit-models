"tube spar"

from gpkit import Model, Var, Variable, VectorVariable
from numpy import pi

from gpkitmodels import g
from gpkitmodels.GP.materials import CFRPFabric

# pylint: disable=invalid-name


class TubeSpar(Model):
    "Tail Boom Model"

    mfac = Var("-", "weight margin factor", value=1.0)
    k = Var("-", "taper index", value=0.8)
    W = Var("lbf", "spar weight")

    def minusk2(self, c):
        return 1 - c[self.k] / 2.0

    def setup(self, N, surface):
        self.material = CFRPFabric()
        deta = surface.deta
        tmin = self.material.tmin
        rho = self.material.rho
        l = surface.l

        # kfac uses a linked function — must be created inside setup
        kfac = self.kfac = Variable("kfac", self.minusk2, "-", "(1-k/2)")

        I = self.I = VectorVariable(N - 1, "I", "m^4", "moment of inertia")
        d = self.d = VectorVariable(N - 1, "d", "in", "diameter")
        t = self.t = VectorVariable(N - 1, "t", "in", "thickness")
        dm = self.dm = VectorVariable(N - 1, "dm", "kg", "segment mass")
        Sy = self.Sy = VectorVariable(N - 1, "Sy", "m^3", "section modulus")

        self.weight = self.W / self.mfac >= g * dm.sum()

        return [
            I <= pi * t * d**3 / 8.0,
            Sy <= 2 * I / d,
            dm >= pi * rho * d * deta * t * kfac * l,
            self.weight,
            t >= tmin,
            self.material,
        ]
