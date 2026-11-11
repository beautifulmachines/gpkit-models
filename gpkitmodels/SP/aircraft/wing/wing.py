"wing.py"

import numpy as np
from gpkit import SignomialsEnabled, Var

from gpkitmodels.GP.aircraft.wing.wing import Wing as WingGP


class Wing(WingGP):
    """
    The wing plus its lift-curve slope, for designs where tail sizing depends on it.
    Adds a signomial constraint.
    """

    mw = Var("-", "span wise effectiveness")

    def setup(self, N=5):
        self.wing = WingGP.setup(self, N=N)
        with SignomialsEnabled():
            constraints = [self.mw * (1 + 2 / self.planform.AR) >= 2 * np.pi]

        return self.wing, constraints
