"box spar"

from gpkit import SignomialsEnabled, VectorVariable

from gpkitmodels.GP.aircraft.wing.boxspar import BoxSpar as BoxSparGP

# pylint: disable=invalid-name


class BoxSpar(BoxSparGP):
    "Box Spar Model"

    def setup(self, N, surface):
        self.boxspar = BoxSparGP.setup(self, N=N, surface=surface)

        J = self.J = VectorVariable(N - 1, "J", "m^4", "spar x polar moment of inertia")

        cave = self.cave
        tau = self.tau
        w = self.w
        tshear = self.tshear

        with SignomialsEnabled():
            constraints = [J <= cave * tau * w * tshear / 3 * (cave * tau + w)]

        return self.boxspar, constraints
