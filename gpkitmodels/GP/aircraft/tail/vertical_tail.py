"vertical tail"

from gpkit import parse_variables

from gpkitmodels.GP.aircraft.wing.wing import Wing
from gpkitmodels.GP.aircraft.wing.wing_core import WingCore

from .tail_aero import TailAero

# pylint: disable=attribute-defined-outside-init, no-member, exec-used


class VerticalTail(Wing):
    """Vertical Tail Model

    Variables
    ---------
    Vv                  [-]         vertical tail volume coefficient
    lv                  [ft]        vertical tail moment arm

    Upper Unbounded
    ---------------
    lv, Vv, W, planform.tau (if not spar_model)

    Lower Unbounded
    ---------------
    lv, Vv, planform.b, planform.tau (if not spar_model)
    spar.Sy (if spar_model), spar.J (if sparJ)

    LaTex Strings
    -------------
    Vv      V_{\\mathrm{v}}
    lv      l_{\\mathrm{v}}

    """

    flight_model = TailAero
    fill_model = WingCore
    spar_model = None

    @parse_variables(__doc__, globals())
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
