"spar loading for gust case"

import os

import pandas as pd
from adce.admath import cos
from gpkit import Var, VectorVariable
from numpy import array, hstack, pi

from gpkitmodels.tools.fit_constraintset import FitCS

from .sparloading import SparLoading

# pylint: disable=invalid-name


class GustL(SparLoading):
    "Gust Loading Model"

    vgust = Var("m/s", "gust velocity", value=10)
    Ww = Var("lbf", "wing weight")
    v = Var("m/s", "vehicle speed")
    cl = Var("-", "wing lift coefficient")

    new_qbarFun = None
    new_SbarFun = None

    def return_cosm1(self, c):
        eta = array(c[self.wing.planform.eta])
        return hstack([1e-10, 1 - array(cos(eta[1:] * pi / 2))])

    def setup(self, wing, state, out=False):
        self.load = SparLoading.setup(self, wing, state, out=out)

        cbar = self.wing.planform.cbar
        W = self.W  # from SparLoading
        q = self.q
        N = self.N
        b = self.b

        agust = VectorVariable(wing.N, "agust", "-", "gust angle of attack")
        cosminus1 = self.cosminus1 = VectorVariable(
            wing.N, "cosminus1", self.return_cosm1, "-", "1 minus cosine factor"
        )

        path = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(path + os.sep + "arctan_fit.csv").to_dict(orient="records")[0]

        constraints = [
            # fit for arctan from 0 to 1, RMS = 0.044
            FitCS(df, agust, [cosminus1 * self.vgust / self.v]),
            q >= W * N / b * cbar * (1 + 2 * pi * agust / self.cl * (1 + self.Ww / W)),
        ]

        return self.load, constraints
