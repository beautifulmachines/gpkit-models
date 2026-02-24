"horizontal tail"

import numpy as np
from gpkit import Var

from gpkitmodels.GP.aircraft.wing.wing import Wing
from gpkitmodels.GP.aircraft.wing.wing_core import WingCore

from .tail_aero import TailAero


class HorizontalTail(Wing):
    "Horizontal Tail Model"

    Vh = Var("-", "horizontal tail volume coefficient")
    lh = Var("ft", "horizontal tail moment arm")
    CLhmin = Var("-", "max downlift coefficient", value=0.75)
    mh = Var("-", "horizontal tail span effectiveness")

    flight_model = TailAero
    fill_model = WingCore
    spar_model = None

    def setup(self, N=3):
        self.ascs = Wing.setup(self, N)
        self.planform.substitutions.update(
            {self.planform.AR: 4, self.planform.lam: 0.8}
        )
        if self.fill_model:
            self.foam.substitutions.update(
                {self.foam.Abar: 0.0548, self.foam.material.rho: 0.024}
            )

        return self.ascs, self.mh * (1 + 2.0 / self.planform["AR"]) <= 2 * np.pi
