"vertical tail"

from gpkit import Var

from gpkitmodels.GP.aircraft.wing.wing import Wing
from gpkitmodels.GP.aircraft.wing.wing_core import WingCore

from .tail_aero import TailAero


class VerticalTail(Wing):
    "Vertical Tail Model"

    Vv = Var("-", "vertical tail volume coefficient")
    lv = Var("ft", "vertical tail moment arm")

    flight_model = TailAero
    fill_model = WingCore
    spar_model = None

    def setup(self, N=3):
        self.ascs = Wing.setup(self, N)
        self.planform.substitutions.update(
            {self.planform.lam: 0.8, self.planform.AR: 4}
        )
        if self.fill_model:
            self.foam.substitutions.update(
                {self.foam.Abar: 0.0548, self.foam.material.rho: 0.024}
            )

        return self.ascs
