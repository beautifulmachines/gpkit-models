"fuel tank"

from gpkit import Model, Var


class FuelTank(Model):
    """
    Returns the weight of the fuel tank.  Assumes a cylinder shape with some
    fineness ratio
    """

    W = Var("lbf", "fuel tank weight")
    f = Var("-", "fraction fuel tank weight to fuel weight", value=0.03)
    mfac = Var("-", "fuel volume margin factor", value=1.1)
    rho_fuel = Var("lbf/gallon", "density of 100LL", value=6.01)
    Vol = Var("ft^3", "fuel tank volume")

    def setup(self, Wfueltot):
        return [
            self.W >= self.f * Wfueltot,
            self.Vol / self.mfac >= Wfueltot / self.rho_fuel,
        ]
