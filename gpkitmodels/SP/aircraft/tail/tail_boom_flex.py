"tail boom flexibility"

from gpkit import Model, SignomialsEnabled, Var
from numpy import pi


class TailBoomFlexibility(Model):
    "Tail Boom Flexibility Model"

    Fne = Var("-", "tail boom flexibility factor")
    deda = Var("-", "wing downwash derivative")
    SMcorr = Var("-", "corrected static margin", value=0.55)
    sph1 = Var("-", "flexibility helper variable 1")
    sph2 = Var("-", "flexibility helper variable 2")

    def setup(self, htail, hbending, wing):
        mh = htail.mh
        mw = wing.mw
        Vh = htail.Vh
        th = hbending.th
        CLhmin = htail.CLhmin
        CLwmax = wing.planform.CLmax
        Sw = wing.planform.S
        bw = wing.planform.b
        lh = htail.lh
        CM = wing.planform.CM

        constraints = [
            self.Fne >= 1 + mh * th,
            self.sph1 * (mw * self.Fne / mh / Vh) + self.deda <= 1,
            self.sph2 <= Vh * CLhmin / CLwmax,
            self.deda >= mw * Sw / bw / 4 / pi / lh,
        ]

        with SignomialsEnabled():
            constraints.extend([self.sph1 + self.sph2 >= self.SMcorr + CM / CLwmax])

        return constraints
