"spar loading"

from gpkit import Model, Var, VectorVariable
from numpy import pi

# pylint: disable=invalid-name


class SparLoading(Model):
    "Spar Loading Model"

    Nmax = Var("-", "max loading", value=5)
    Nsafety = Var("-", "safety load factor", value=1.0)
    kappa = Var("-", "max tip deflection ratio", value=0.2)
    W = Var("lbf", "loading weight")
    N = Var("-", "loading factor")
    twmax = Var("-", "max tip twist", value=15.0 * pi / 180)
    Stip = Var("N", "tip loading", value=1e-10)
    Mtip = Var("N*m", "tip moment", value=1e-10)
    throot = Var("-", "root deflection angle", value=1e-10)
    wroot = Var("m", "root deflection", value=1e-10)

    def new_qbarFun(self, c):
        "define qbar model for chord loading"
        barc = self.wing.planform.cbar
        return [f(c) for f in self.wing.substitutions[barc]]

    new_SbarFun = None

    def setup(self, wing, state, out=False):
        self.wing = wing

        b = self.b = self.wing.planform.b
        I = self.I = self.wing.spar.I
        Sy = self.Sy = self.wing.spar.Sy
        cave = self.cave = self.wing.planform.cave
        cbar = self.cbar = self.wing.planform.cbar
        E = self.wing.spar.material.E
        sigma = self.wing.spar.material.sigma
        deta = self.wing.planform.deta

        q = self.q = VectorVariable(wing.N, "q", "N/m", "distributed wing loading")
        S = self.S = VectorVariable(wing.N, "S", "N", "shear along wing")
        M = self.M = VectorVariable(wing.N, "M", "N*m", "wing section root moment")
        th = self.th = VectorVariable(wing.N, "th", "-", "deflection angle")
        w = self.w = VectorVariable(wing.N, "w", "m", "wing deflection")

        Mtw = self.Mtw = VectorVariable(
            wing.N - 1, "Mtw", "N*m", "local moment due to twisting"
        )
        theta = self.theta = VectorVariable(
            wing.N - 1, "theta", "-", "twist deflection"
        )
        self.EIbar = VectorVariable(wing.N - 1, "EIbar", "-", "EIbar")
        self.Sout = VectorVariable(wing.N - 1, "Sout", "-", "outboard variable")

        constraints = []
        if not out:
            constraints.extend(
                [
                    S[:-1] >= S[1:] + 0.5 * deta * (b / 2.0) * (q[:-1] + q[1:]),
                    M[:-1] >= M[1:] + 0.5 * deta * (b / 2) * (S[:-1] + S[1:]),
                ]
            )

        constraints.extend(
            [
                self.N == self.Nsafety * self.Nmax,
                q >= self.N * self.W / b * cbar,
                S[-1] >= self.Stip,
                M[-1] >= self.Mtip,
                th[0] >= self.throot,
                th[1:] >= th[:-1] + 0.5 * deta * (b / 2) * (M[1:] + M[:-1]) / E / I,
                w[0] >= self.wroot,
                w[1:] >= w[:-1] + 0.5 * deta * (b / 2) * (th[1:] + th[:-1]),
                sigma >= M[:-1] / Sy,
                w[-1] / (b / 2) <= self.kappa,
            ]
        )

        self.wingSparJ = hasattr(self.wing.spar, "J")

        if self.wingSparJ:
            qne = self.qne = state.qne
            J = self.J = self.wing.spar.J
            G = self.wing.spar.shearMaterial.G
            cm = self.wing.planform.CM
            constraints.extend(
                [
                    Mtw >= cm * cave**2 * qne * deta * b / 2 * self.Nsafety,
                    theta[0] >= Mtw[0] / G / J[0] * deta[0] * b / 2,
                    theta[1:] >= theta[:-1] + Mtw[1:] / G / J[1:] * deta[1:] * b / 2,
                    self.twmax >= theta[-1],
                ]
            )
        return constraints
