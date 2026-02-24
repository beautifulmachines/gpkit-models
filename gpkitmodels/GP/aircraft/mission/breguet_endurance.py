"breguet_endurance.py"

from gpkit import Model, Var
from gpkit.constraints.tight import Tight as TCS
from gpkit.tools import te_exp_minus1

from gpkitmodels import g


class BreguetEndurance(Model):
    "breguet endurance model"

    z_bre = Var("-", "Breguet coefficient")
    t = Var("days", "Time per flight segment")
    f_fueloil = Var("-", "Fuel-oil fraction", value=0.98)
    W_fuel = Var("lbf", "Segment-fuel weight")

    def setup(self, perf):
        return [
            TCS(
                [
                    self.z_bre
                    >= (
                        perf["P_{total}"]
                        * self.t
                        * perf["BSFC"]
                        * g
                        / (perf["W_{end}"] * perf["W_{start}"]) ** 0.5
                    )
                ]
            ),
            self.f_fueloil * self.W_fuel / perf["W_{end}"]
            >= te_exp_minus1(self.z_bre, 3),
            perf["W_{start}"] >= perf["W_{end}"] + self.W_fuel,
        ]
