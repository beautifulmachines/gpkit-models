"empennage.py"

from gpkit import Model, Var

from .horizontal_tail import HorizontalTail
from .tail_boom import TailBoom
from .vertical_tail import VerticalTail

# pylint: disable=invalid-name


class Empennage(Model):
    "empennage model, consisting of vertical, horizontal and tailboom"

    mfac = Var("-", "tail weight margin factor", value=1.0)
    W = Var("lbf", "empennage weight")

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
            self.W / self.mfac >= sum(c.W for c in self.components),
            l >= lh,
            l >= lv,
        ]

        return self.components, constraints
