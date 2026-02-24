"tail aerodynamics"

import os

import pandas as pd
from gpkit import Model, Var

from gpkitmodels.tools.fit_constraintset import FitCS


class TailAero(Model):
    "Tail Aero Model"

    Re = Var("-", "Reynolds number")
    Cd = Var("-", "drag coefficient")

    def setup(self, static, state):
        self.state = state

        self.cmac = static.planform.cmac
        b = self.b = static.planform.b
        S = self.S = static.planform.S
        tau = self.tau = static.planform.tau
        rho = self.rho = state.rho
        V = self.V = state.V
        mu = self.mu = state.mu
        path = os.path.dirname(__file__)
        fd = pd.read_csv(path + os.sep + "tail_dragfit.csv").to_dict(orient="records")[
            0
        ]

        constraints = [
            self.Re == V * rho * S / b / mu,
            FitCS(fd, self.Cd, [self.Re, tau], err_margin="RMS"),
        ]

        return constraints
