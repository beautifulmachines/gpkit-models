"empennage.py"

from gpkit import Model, parse_variables

from .horizontal_tail import HorizontalTail
from .tail_boom import TailBoom
from .vertical_tail import VerticalTail


# pylint: disable=attribute-defined-outside-init, no-member
# pylint: disable=exec-used, too-many-instance-attributes
# pylint: disable=invalid-name, undefined-variable
class Empennage(Model):
    """empennage model, consisting of vertical, horizontal and tailboom

    Variables
    ---------
    mfac        1.0     [-]     tail weight margin factor
    W                   [lbf]   empennage weight

    SKIP VERIFICATION

    Upper Unbounded
    ---------------
    W, vtail.Vv, htail.Vh, tailboom.cave (if not tbSecWeight)
    htail.planform.tau (if not h_spar_model)
    vtail.planform.tau (if not v_spar_model)

    Lower Unbounded
    ---------------
    htail.lh, htail.Vh, htail.planform.b, htail.mh
    vtail.lv, vtail.Vv, vtail.planform.b
    htail.planform.tau (if not h_spar_model)
    vtail.planform.tau (if not v_spar_model)
    htail.spar.Sy (if h_spar_model), htail.spar.J (if h_spar_model)
    vtail.spar.Sy (if v_spar_model), vtail.spar.J (if v_spar_model)
    tailboom.Sy, tailboom.cave (if not tbSecWeight), tailboom.J (if tbSecWeight)

    LaTex Strings
    -------------
    mfac        m_{\\mathrm{fac}}

    """

    @parse_variables(__doc__, globals())
    def setup(
        self,
        N=2,
        htail_cls=HorizontalTail,
        vtail_cls=VerticalTail,
        tailboom_cls=TailBoom,
    ):
        self.htail = htail_cls()
        self.h_spar_model = self.htail.spar_model
        self.htail.substitutions.update({self.htail.mfac: 1.1})
        lh = self.lh = self.htail.lh
        self.vtail = vtail_cls()
        self.v_spar_model = self.vtail.spar_model
        self.vtail.substitutions.update({self.vtail.mfac: 1.1})
        lv = self.lv = self.vtail.lv
        self.tailboom = tailboom_cls(N=N)
        self.tbSecWeight = self.tailboom.secondaryWeight
        self.components = [self.htail, self.vtail, self.tailboom]
        l = self.l = self.tailboom.l

        constraints = [
            W / mfac >= sum(c.W for c in self.components),
            l >= lh,
            l >= lv,
        ]

        return self.components, constraints
