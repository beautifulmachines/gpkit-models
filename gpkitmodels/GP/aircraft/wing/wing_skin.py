"wing skin"

from gpkit import Model, Var

from gpkitmodels import g
from gpkitmodels.GP.materials import CFRPFabric


class WingSkin(Model):
    "Wing Skin model"

    W = Var("lbf", "wing skin weight")
    t = Var("in", "wing skin thickness")
    Jtbar = Var("1/mm", "torsional moment of inertia", value=0.01114)
    Cmw = Var("-", "negative wing moment coeff", value=0.121)
    rhosl = Var("kg/m^3", "sea level air density", value=1.225)
    Vne = Var("m/s", "never exceed vehicle speed", value=45)

    def setup(self, surface):
        self.surface = surface
        self.material = CFRPFabric()

        croot = surface.croot
        S = surface.S
        rho = self.material.rho
        tau = self.material.tau
        tmin = self.material.tmin

        return [
            self.W >= rho * S * 2 * self.t * g,
            self.t >= tmin,
            tau
            >= 1
            / self.Jtbar
            / croot**2
            / self.t
            * self.Cmw
            * S
            * self.rhosl
            * self.Vne**2,
            self.material,
        ]


class WingSecondStruct(Model):
    "Wing secondary structure model"

    W = Var("lbf", "wing skin weight")
    rhoA = Var("kg/m^2", "total aerial density", value=0.35)

    def setup(self, surface):
        self.S = surface.S

        return [self.W >= self.rhoA * self.S * g]
