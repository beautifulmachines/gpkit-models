"wing interior"

from gpkit import Model, Var

from gpkitmodels import g
from gpkitmodels.GP.materials import FoamHD


class WingCore(Model):
    "Wing Core Model"

    W = Var("lbf", "wing core weight")
    Abar = Var("-", "normalized cross section area", value=0.0753449)

    def setup(self, surface):
        self.surface = surface
        self.material = FoamHD()

        cave = self.cave = surface.cave
        b = self.b = surface.b
        deta = surface.deta  # surface panel widths
        rho = self.material.rho

        return [
            self.W >= 2 * (g * rho * self.Abar * cave**2 * b / 2 * deta).sum(),
            self.material,
        ]
