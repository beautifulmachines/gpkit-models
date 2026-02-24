"cap spar"

from gpkit import Model, Var, VectorVariable

from gpkitmodels import g
from gpkitmodels.GP.materials import CFRPUD, CFRPFabric, FoamHD

from .gustloading import GustL
from .sparloading import SparLoading

# pylint: disable=invalid-name


class CapSpar(Model):
    "Cap Spar Model"

    E = Var("psi", "Young modulus of CFRP", value=2e7)
    W = Var("lbf", "spar weight")
    wlim = Var("-", "spar width to chord ratio", value=0.15)
    mfac = Var("-", "curvature knockdown factor", value=0.97)

    loading = SparLoading
    gustloading = GustL

    def setup(self, N, surface):
        self.surface = surface
        self.material = CFRPUD()
        self.shearMaterial = CFRPFabric()
        self.coreMaterial = FoamHD()

        cave = self.cave = surface.cave
        b = self.b = surface.b
        deta = surface.deta
        tau = self.tau = surface.tau
        rho = self.material.rho
        rhoshear = self.shearMaterial.rho
        rhocore = self.coreMaterial.rho
        tshearmin = self.shearMaterial.tmin

        hin = VectorVariable(N - 1, "hin", "in", "height between caps")
        I = self.I = VectorVariable(N - 1, "I", "m^4", "spar x moment of inertia")
        Sy = self.Sy = VectorVariable(N - 1, "Sy", "m^3", "section modulus")
        dm = VectorVariable(N - 1, "dm", "kg", "segment spar mass")
        w = VectorVariable(N - 1, "w", "in", "spar width")
        t = VectorVariable(N - 1, "t", "in", "spar cap thickness")
        tshear = VectorVariable(N - 1, "tshear", "in", "shear web thickness")

        return [
            I / self.mfac <= 2 * w * t * (hin / 2) ** 2,
            dm
            >= (
                rho * (2 * w * t)
                + 2 * tshear * rhoshear * (hin + 2 * t)
                + rhocore * w * hin
            )
            * b
            / 2
            * deta,
            self.W >= 2 * dm.sum() * g,
            w <= self.wlim * cave,
            cave * tau >= hin + 2 * t,
            Sy * (hin / 2 + t) <= I,
            tshear >= tshearmin,
            self.material,
            self.shearMaterial,
            self.coreMaterial,
        ]
