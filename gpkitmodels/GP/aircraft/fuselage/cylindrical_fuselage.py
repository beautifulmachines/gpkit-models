"cylindrical fuselage.py"

import numpy as np
from gpkit import Model, Var

from .fuel_tank import FuelTank
from .fuselage_skin import FuselageSkin


class Fuselage(Model):
    "The thing that carries the fuel, engine, and payload"

    R = Var("ft", "fuselage radius")
    l = Var("ft", "fuselage length")
    S = Var("ft^2", "fuselage cross sectional area")
    W = Var("lbf", "Fuselage weight")
    mfac = Var("-", "Fuselage weight margin factor", value=2.1)
    l_body = Var("ft", "center body length")
    k_body = Var("-", "fuselage body length to radius ratio")
    k_nose = Var("-", "fuselage nose length to radius ratio")
    k_bulk = Var("-", "fuselage bulk length to radius ratio")
    S_wet = Var("ft**2", "fuselage wetted area")
    S_body = Var("ft**2", "wetted surface area of body")
    S_nose = Var("ft**2", "wetted surface area of nose")
    S_bulk = Var("ft**2", "wetted surface area of bulk")
    Vol_body = Var("ft**3", "volume of body")

    def setup(self, Wfueltot):
        self.fueltank = FuelTank(Wfueltot)
        self.skin = FuselageSkin(self.S_wet, self.R, self.l_body)
        self.components = [self.fueltank, self.skin]

        constraints = [
            self.k_body == self.l_body / self.R,
            self.S_wet >= self.S_body + self.S_nose + self.S_bulk,
            self.S_body >= 2 * np.pi * self.R * self.l_body,
            self.S_nose ** (8.0 / 5.0)
            >= (
                (2 * np.pi * self.R**2) ** (8.0 / 5.0)
                * (1.0 / 3.0 + 2.0 / 3.0 * (self.k_nose) ** (8.0 / 5.0))
            ),
            self.S_bulk
            >= self.R**2
            * (0.012322 * self.k_bulk**2 + 1.524925 * self.k_bulk + 0.502498),
            self.Vol_body <= np.pi * self.R**2 * self.l_body,
            self.l
            <= 3 * self.R * (self.k_body * self.k_nose * self.k_bulk) ** (1.0 / 3),
            self.S >= np.pi * self.R**2,
            self.Vol_body >= self.fueltank.Vol,
            self.W / self.mfac >= self.fueltank.W + self.skin.W,
        ]

        return self.components, constraints

    def loading(self, Wcent):
        return FuselageLoading(self, Wcent)

    def flight_model(self, state):
        return FuselageAero(self, state)


class FuselageLoading(Model):
    "fuselage loading cases"

    def setup(self, fuselage, Wcent):
        loading = [fuselage.skin.loading(Wcent)]
        loading.append(fuselage.skin.landing(Wcent))
        return loading


class FuselageAero(Model):
    "fuselage drag model"

    Cf = Var("-", "fuselage skin friction coefficient")
    Re = Var("-", "fuselage reynolds number")
    Re_ref = Var("-", "reference Reynolds number", value=1e6)
    Cf_ref = Var("-", "reference skin friction coefficient")
    Cd = Var("-", "fuselage drag coefficient")

    def setup(self, static, state):
        constraints = [
            self.Re == state["V"] * state["\\rho"] * static.l / state["\\mu"],
            self.Cf >= 0.455 / self.Re**0.3,
            self.Cf_ref == 0.455 / self.Re_ref**0.3,
            self.Cd**0.996232
            >= self.Cf
            / self.Cf_ref
            * (
                0.00243049
                * static.k_body**0.033607
                * static.k_nose**1.21682
                * static.k_bulk**0.306251
                + 0.00255095
                * static.k_body**-0.0316887
                * static.k_nose**-0.585489
                * static.k_bulk**1.15394
                + 0.0436011
                * static.k_body**0.0545722
                * static.k_nose**0.258228
                * static.k_bulk**-1.42664
                + 0.00970479
                * static.k_body**0.8661
                * static.k_nose**-0.209136
                * static.k_bulk**-0.156166
            ),
        ]

        return constraints
