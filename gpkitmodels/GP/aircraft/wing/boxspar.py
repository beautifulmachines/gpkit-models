"box spar"

from gpkit import Model, Var, Variable, VectorVariable

from gpkitmodels import g
from gpkitmodels.GP.materials import CFRPUD, CFRPFabric, FoamHD

from .gustloading import GustL
from .sparloading import SparLoading

# pylint: disable=invalid-name


class BoxSpar(Model):
    "Box Spar Model"

    W = Var("lbf", "spar weight")

    loading = SparLoading
    gustloading = GustL

    def setup(self, N, surface):
        self.surface = surface
        self.material = CFRPUD()
        self.shearMaterial = CFRPFabric()
        self.coreMaterial = FoamHD()

        # These must be created inside setup so they exist when BoxSpar.setup
        # is called as an unbound method on a TailBoom (not a BoxSpar subclass).
        wlim = self.wlim = Variable("wlim", 0.15, "-", "spar width to chord ratio")
        mfac = self.mfac = Variable("mfac", 0.97, "-", "curvature knockdown factor")
        tcoret = self.tcoret = Variable("tcoret", 0.02, "-", "core to thickness ratio")

        b = self.b = surface.b
        cave = self.cave = surface.cave
        tau = self.tau = surface.tau
        deta = surface.deta
        rho = self.material.rho
        rhoshear = self.shearMaterial.rho
        rhocore = self.coreMaterial.rho
        tshearmin = self.shearMaterial.tmin
        tmin = self.material.tmin

        hin = VectorVariable(N - 1, "hin", "in", "height between caps")
        I = self.I = VectorVariable(N - 1, "I", "m^4", "spar x moment of inertia")
        Sy = self.Sy = VectorVariable(N - 1, "Sy", "m^3", "section modulus")
        dm = VectorVariable(N - 1, "dm", "kg", "segment spar mass")
        w = VectorVariable(N - 1, "w", "in", "spar width")
        d = self.d = VectorVariable(N - 1, "d", "in", "cross sectional diameter")
        t = VectorVariable(N - 1, "t", "in", "spar cap thickness")
        tshear = VectorVariable(N - 1, "tshear", "in", "shear web thickness")
        tcore = VectorVariable(N - 1, "tcore", "in", "core thickness")

        self.weight = self.W >= 2 * dm.sum() * g

        constraints = [
            I / mfac <= w * t * hin**2,
            dm
            >= (
                rho * 4 * w * t
                + 4 * tshear * rhoshear * (hin + w)
                + 2 * rhocore * tcore * (w + hin)
            )
            * b
            / 2
            * deta,
            w <= wlim * cave,
            cave * tau >= hin + 4 * t + 2 * tcore,
            self.weight,
            t >= tmin,
            Sy * (hin / 2 + 2 * t + tcore) <= I,
            tshear >= tshearmin,
            tcore >= tcoret * cave * tau,
            d == w,
            self.material,
            self.shearMaterial,
            self.coreMaterial,
        ]

        return constraints
