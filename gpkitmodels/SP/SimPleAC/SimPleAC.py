from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
from gpkit import Model, SignomialsEnabled, Variable, VarKey, units


class SimPleAC(Model):
    def setup(self):
        # Env. constants
        g = Variable("g", 9.81, "m/s^2", "gravitational acceleration")
        mu = Variable("\\mu", 1.775e-5, "kg/m/s", "viscosity of air", pr=4.0)
        rho = Variable("\\rho", 1.23, "kg/m^3", "density of air", pr=5.0)
        rho_f = Variable("\\rho_f", 817, "kg/m^3", "density of fuel")

        # Non-dimensional constants
        C_Lmax = Variable("C_{L,max}", 1.6, "-", "max CL with flaps down", pr=5.0)
        e = Variable("e", 0.92, "-", "Oswald efficiency factor", pr=3.0)
        k = Variable("k", 1.17, "-", "form factor", pr=10.0)
        N_ult = Variable("N_{ult}", 3.3, "-", "ultimate load factor", pr=15.0)
        S_wetratio = Variable(
            "(\\frac{S}{S_{wet}})", 2.075, "-", "wetted area ratio", pr=3.0
        )
        tau = Variable("\\tau", 0.12, "-", "airfoil thickness to chord ratio", pr=10.0)
        W_W_coeff1 = Variable(
            "W_{W_{coeff1}}", 2e-5, "1/m", "wing weight coefficent 1", pr=30.0
        )  # orig  12e-5
        W_W_coeff2 = Variable(
            "W_{W_{coeff2}}", 60.0, "Pa", "wing weight coefficent 2", pr=10.0
        )
        p_labor = Variable("p_{labor}", 1.0, "1/min", "cost of labor", pr=20.0)

        # Dimensional constants
        Range = Variable("Range", 3000, "km", "aircraft range")
        TSFC = Variable("TSFC", 0.6, "1/hr", "thrust specific fuel consumption")
        V_min = Variable("V_{min}", 25, "m/s", "takeoff speed", pr=20.0)
        W_0 = Variable("W_0", 6250, "N", "aircraft weight excluding wing", pr=20.0)

        # Free Variables
        LoD = Variable("L/D", "-", "lift-to-drag ratio")
        D = Variable("D", "N", "total drag force")
        V = Variable("V", "m/s", "cruising speed")
        W = Variable("W", "N", "total aircraft weight")
        Re = Variable("Re", "-", "Reynold's number")
        CDA0 = Variable("(CDA0)", "m^2", "fuselage drag area")  # 0.035 originally
        C_D = Variable("C_D", "-", "drag coefficient")
        C_L = Variable("C_L", "-", "lift coefficient of wing")
        C_f = Variable("C_f", "-", "skin friction coefficient")
        W_f = Variable("W_f", "N", "fuel weight")
        V_f = Variable("V_f", "m^3", "fuel volume")
        V_f_avail = Variable("V_{f_{avail}}", "m^3", "fuel volume available")
        T_flight = Variable("T_{flight}", "hr", "flight time")

        # Free variables (fixed for performance eval.)
        A = Variable("A", "-", "aspect ratio", fix=True)
        S = Variable("S", "m^2", "total wing area", fix=True)
        W_w = Variable("W_w", "N", "wing weight")  # , fix = True)
        W_w_strc = Variable("W_w_strc", "N", "wing structural weight", fix=True)
        W_w_surf = Variable("W_w_surf", "N", "wing skin weight", fix=True)
        V_f_wing = Variable("V_f_wing", "m^3", "fuel volume in the wing", fix=True)
        V_f_fuse = Variable("V_f_fuse", "m^3", "fuel volume in the fuselage", fix=True)
        constraints = []

        # Weight and lift model
        constraints += [
            W >= W_0 + W_w + W_f,
            W_0 + W_w + 0.5 * W_f <= 0.5 * rho * S * C_L * V**2,
            W <= 0.5 * rho * S * C_Lmax * V_min**2,
            T_flight >= Range / V,
            LoD == C_L / C_D,
        ]

        # Thrust and drag model
        C_D_fuse = CDA0 / S
        C_D_wpar = k * C_f * S_wetratio
        C_D_ind = C_L**2 / (np.pi * A * e)
        constraints += [
            W_f >= TSFC * T_flight * D,
            D >= 0.5 * rho * S * C_D * V**2,
            C_D >= C_D_fuse + C_D_wpar + C_D_ind,
            V_f_fuse <= 10 * units("m") * CDA0,
            Re <= (rho / mu) * V * (S / A) ** 0.5,
            C_f >= 0.074 / Re**0.2,
        ]

        # Fuel volume model
        with SignomialsEnabled():
            constraints += [
                V_f == W_f / g / rho_f,
                V_f_wing**2
                <= 0.0009
                * S**3
                / A
                * tau**2,  # linear with b and tau, quadratic with chord
                V_f_avail <= V_f_wing + V_f_fuse,  # [SP]
                V_f_avail >= V_f,
            ]

        # Wing weight model
        constraints += [
            W_w_surf >= W_W_coeff2 * S,
            W_w_strc**2.0
            >= W_W_coeff1**2.0
            / tau**2.0
            * (N_ult**2.0 * A**3.0 * ((W_0 + V_f_fuse * g * rho_f) * W * S)),
            W_w >= W_w_surf + W_w_strc,
        ]

        return constraints


def test():
    m = SimPleAC()
    m.cost = m["W_f"]
    sol = m.localsolve(verbosity=2)


if __name__ == "__main__":
    # Most basic way to execute the model
    from gpkit import Vectorize

    with Vectorize(3):
        m = SimPleAC()
    # m.cost = m['W']
    # sol1 = m.localsolve(verbosity = 2)
    m.substitutions["Range"] = [1000, 3000, 6000]
    m.extend(
        [
            m["A"] == m["A"][0],
            m["S"] == m["S"][0],
            m["W_w"] == m["W_w"][0],
            m["W_w_strc"] == m["W_w_strc"][0],
            m["W_w_surf"] == m["W_w_surf"][0],
            m["V_f_wing"] == m["V_f_wing"][0],
            m["V_f_fuse"] == m["V_f_fuse"][0],
        ]
    )
    m.cost = 3 * m["W_f"][0] + m["W_f"][1] + 0.33 * m["W_f"][2]
    sol = m.localsolve(verbosity=1)
    # print(sol1.diff(sol2))
    print(sol.table())
