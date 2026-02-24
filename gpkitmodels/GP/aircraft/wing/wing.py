"wing.py"

from os import sep
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from gpkit import Model, Var, VectorVariable

from gpkitmodels.tools.fit_constraintset import XfoilFit

from .capspar import CapSpar
from .wing_core import WingCore
from .wing_skin import WingSkin

# pylint: disable=invalid-name


class Planform(Model):
    "Planform Area Definition"

    S = Var("ft^2", "surface area")
    AR = Var("-", "aspect ratio")
    b = Var("ft", "span")
    tau = Var("-", "airfoil thickness ratio")
    CLmax = Var("-", "maximum lift coefficient", value=1.39)
    CM = Var("-", "wing moment coefficient", value=0.14)
    croot = Var("ft", "root chord")
    cmac = Var("ft", "mean aerodynamic chord")
    lam = Var("-", "taper ratio", value=0.5)
    cbarmac = Var("-", "non-dim MAC")

    def return_c(self, c):
        "return normalized chord distribution"
        lam = float(c[self.lam])
        eta = c[self.eta]
        return np.array([2.0 / (1 + lam) * (1 + (lam - 1) * e) for e in eta])

    def return_cmac(self, c):
        "return normalized MAC"
        cbar = self.return_c(c)
        lam = cbar[1:] / cbar[:-1]
        maci = 2.0 / 3 * cbar[:-1] * (1 + lam + lam**2) / (1 + lam)
        deta = np.diff(c[self.eta])
        num = sum(
            [(cbar[i] + cbar[i + 1]) / 2 * maci[i] * deta[i] for i in range(len(deta))]
        )
        den = sum([(cbar[i] + cbar[i + 1]) / 2 * deta[i] for i in range(len(deta))])
        return num / den / cbar[0]

    def return_avg(self, c):
        vals = self.return_c(c)
        return (vals[:-1] + vals[1:]) / 2.0

    def return_deta(self, c):
        return np.diff(c[self.eta])

    def setup(self, N):
        self.eta = VectorVariable(N, "eta", np.linspace(0, 1, N), "-", "(2y/b)")
        cbar = self.cbar = VectorVariable(
            N, "cbar", self.return_c, "-", "non-dim chord at nodes"
        )
        cave = self.cave = VectorVariable(N - 1, "cave", "ft", "mid section chord")
        cbave = self.cbave = VectorVariable(
            N - 1, "cbave", self.return_avg, "-", "non-dim mid section chord"
        )
        self.deta = VectorVariable(
            N - 1, "deta", self.return_deta, "-", "\\Delta (2y/b)"
        )

        constraints = [
            self.b**2 == self.S * self.AR,
            cave == cbave * self.S / self.b,
            self.croot == self.S / self.b * cbar[0],
            self.cmac == self.croot * self.cbarmac,
        ]
        return constraints, {self.cbarmac: self.return_cmac}


class WingAero(Model):
    "Wing Aero Model"

    Cd = Var("-", "wing drag coefficient")
    CL = Var("-", "lift coefficient")
    CLstall = Var("-", "stall CL", value=1.3)
    e = Var("-", "span efficiency", value=0.9)
    Re = Var("-", "reynolds number")
    cdp = Var("-", "wing profile drag coefficient")

    def setup(
        self,
        static,
        state,
        fitdata=dirname(abspath(__file__)) + sep + "jho_fitdata.csv",
    ):
        self.state = state
        self.static = static

        df = pd.read_csv(fitdata)
        fd = df.to_dict(orient="records")[0]

        AR = static.planform.AR
        cmac = static.planform.cmac
        rho = state.rho
        V = state.V
        mu = state.mu
        # needed for Climb model in solar
        self.rhoValue = rho.key.value is not None
        self.muValue = mu.key.value is not None

        if fd["d"] == 2:
            independentvars = [self.CL, self.Re]
        elif fd["d"] == 3:
            independentvars = [self.CL, self.Re, static.planform.tau]

        return [
            self.Cd >= self.cdp + self.CL**2 / np.pi / AR / self.e,
            self.Re == rho * V * cmac / mu,
            XfoilFit(fd, self.cdp, independentvars, name="polar"),
            self.CL <= self.CLstall,
        ]


class Wing(Model):
    "Wing Model"

    W = Var("lbf", "wing weight")
    mfac = Var("-", "wing weight margin factor", value=1.2)

    spar_model = CapSpar
    fill_model = WingCore
    flight_model = WingAero
    skin_model = WingSkin
    sparJ = False

    def setup(self, N=5):
        self.N = N
        self.planform = Planform(N)
        self.components = []

        if self.skin_model:
            self.skin = self.skin_model(self.planform)
            self.components.extend([self.skin])
        if self.spar_model:
            self.spar = self.spar_model(N, self.planform)
            self.components.extend([self.spar])
            self.sparJ = hasattr(self.spar, "J")
        if self.fill_model:
            self.foam = self.fill_model(self.planform)
            self.components.extend([self.foam])

        constraints = [self.W / self.mfac >= sum(c["W"] for c in self.components)]

        return constraints, self.planform, self.components
