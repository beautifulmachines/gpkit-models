"wing.py"

import numpy as np
from gpkit import SignomialsEnabled, Var

from gpkitmodels.GP.aircraft.wing.wing import Wing as WingGP

# pylint: disable=invalid-name


class Wing(WingGP):
    "SP wing model"

    mw = Var("-", "span wise effectiveness")

    def setup(self, N=5):
        self.wing = WingGP.setup(self, N=N)
        with SignomialsEnabled():
            constraints = [self.mw * (1 + 2 / self.planform["AR"]) >= 2 * np.pi]

        return self.wing, constraints
