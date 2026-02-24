"engine_model.py"

import os

import pandas as pd
from gpkit import Model, Var, Variable, units

from gpkitmodels.tools.fit_constraintset import FitCS


class Engine(Model):
    "engine model"

    W = Var("lbf", "Installed/Total engine weight")
    mfac = Var("-", "Engine weight margin factor", value=1.0)
    bsfc_min = Var("kg/kW/hr", "minimum BSFC", value=0.3162)
    P_ref = Var("hp", "Reference shaft power", value=10.0)
    W_engref = Var("lbf", "Reference engine weight", value=10.0)
    W_eng = Var("lbf", "engine weight")
    P_sl_max = Var("hp", "Max shaft power at sea level")

    def setup(self, DF70=False):
        self.DF70 = DF70

        path = os.path.dirname(__file__)
        df = pd.read_csv(path + os.sep + "power_lawfit.csv").to_dict(orient="records")[
            0
        ]

        constraints = [
            FitCS(df, self.W_eng / self.W_engref, [self.P_sl_max / self.P_ref]),
            self.W / self.mfac >= 2.572 * self.W_eng**0.922 * units("lbf") ** 0.078,
        ]

        return constraints

    def flight_model(self, state):
        return EnginePerf(self, state)


class EnginePerf(Model):
    "engine performance model"

    def setup(self, static, state):

        Pshaft = Variable("P_{shaft}", "hp", "Shaft power")
        bsfc = Variable("BSFC", "kg/kW/hr", "Brake specific fuel consumption")
        Pavn = Variable("P_{avn}", 40, "watts", "Avionics power")
        Ptotal = Variable("P_{total}", "hp", "Total power, avionics included")
        eta_alternator = Variable(
            "\\eta_{alternator}", 0.8, "-", "alternator efficiency"
        )
        href_val = 1000  # shared with Variable below to stay in sync
        href = Variable("h_{ref}", href_val, "ft", "reference altitude")  # noqa: F841
        h_vals = state.substitutions["h"]
        if not hasattr(h_vals, "__len__"):
            h_vals = [h_vals]
        h_units = state["h"].key.units
        lfac = [
            (-0.035 * v * h_units / (href_val * h_units)).to("").magnitude + 1.0
            for v in h_vals
        ]
        Leng = Variable("L_{eng}", lfac, "-", "shaft power loss factor")
        Pshaftmax = Variable("P_{shaft-max}", "hp", "Max shaft power at altitude")
        mfac = Variable("m_{fac}", 1.0, "-", "BSFC margin factor")

        path = os.path.dirname(__file__)
        df = pd.read_csv(path + os.sep + "powerBSFCfit.csv").to_dict(orient="records")[
            0
        ]

        constraints = [
            FitCS(df, bsfc / mfac / static.bsfc_min, [Ptotal / Pshaftmax]),
            Pshaftmax / static.P_sl_max == Leng,
            Pshaftmax >= Ptotal,
            Ptotal >= Pshaft + Pavn / eta_alternator,
        ]

        return constraints
