"discretized beam model"

from gpkit import Model, Variable, Vectorize


class Beam(Model):
    """
    A beam bending under a load spread along it, split into segments to track shear,
    moment, slope and deflection.
    """

    qbarFun = None
    SbarFun = None
    MbarFun = None

    def setup(self, N=6):

        with Vectorize(N - 1):
            EIbar = self.EIbar = Variable(
                "\\bar{EI}", "-", "normalized YM and moment of inertia"
            )
            dx = self.dx = Variable("dx", "-", "normalized length of element")

        with Vectorize(N):
            Sbar = Variable("\\bar{S}", "-", "normalized shear", value=self.SbarFun)
            Mbar = Variable("\\bar{M}", "-", "normalized moment", value=self.MbarFun)
            th = Variable("\\theta", "-", "deflection slope")
            dbar = Variable("\\bar{\\delta}", "-", "normalized displacement")
            self.dbar_tip = dbar[-1]

        throot = Variable("\\theta_{root}", "-", "Base angle", value=1e-10)
        dbarroot = Variable(
            "\\bar{\\delta}_{root}", "-", "Base deflection", value=1e-10
        )

        constraints = []
        if self.SbarFun is None:
            with Vectorize(N):
                qbar = self.qbar = Variable(
                    "\\bar{q}", "-", "normalized loading", value=self.qbarFun
                )
            Sbartip = Variable("\\bar{S}_{tip}", "-", "Tip loading", value=1e-10)
            constraints.extend(
                [
                    Sbar[:-1] >= Sbar[1:] + 0.5 * dx * (qbar[:-1] + qbar[1:]),
                    Sbar[-1] >= Sbartip,
                ]
            )

        if self.MbarFun is None:
            Mbartip = Variable("\\bar{M}_{tip}", "-", "Tip moment", value=1e-10)
            constraints.extend(
                [
                    Mbar[:-1] >= Mbar[1:] + 0.5 * dx * (Sbar[:-1] + Sbar[1:]),
                    Mbar[-1] >= Mbartip,
                ]
            )

        constraints.extend(
            [
                th[0] >= throot,
                th[1:] >= th[:-1] + 0.5 * dx * (Mbar[1:] + Mbar[:-1]) / EIbar,
                dbar[0] >= dbarroot,
                dbar[1:] >= dbar[:-1] + 0.5 * dx * (th[1:] + th[:-1]),
            ]
        )

        return constraints
