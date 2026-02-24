"propeller model"

import os
from builtins import range

import pandas as pd
from gpkit import (
    Model,
    SignomialEquality,
    SignomialsEnabled,
    Var,
    Vectorize,
)
from gpkit.constraints.tight import Tight as TCS
from numpy import pi

from gpkitmodels.tools.fit_constraintset import FitCS


class BladeElementPerf(Model):
    "Single element of a propeller blade"

    dT = Var("lbf", "thrust")
    eta_i = Var("-", "local induced efficiency")
    dQ = Var("N*m", "torque")
    omega = Var("rpm", "propeller rotation rate")
    Wa = Var("m/s", "Axial total relative velocity")
    Wt = Var("m/s", "Tangential total relative velocity")
    Wr = Var("m/s", "Total relative velocity")
    va = Var("m/s", "Axial induced velocity")
    vt = Var("m/s", "Tangential induced velocity")
    G = Var("m^2/s", "Circulation")
    cl = Var("-", "local lift coefficient")
    cd = Var("-", "local drag coefficient")
    B = Var("-", "number of blades", value=2)
    r = Var("m", "local radius")
    lam_w = Var("-", "advance ratio")
    eps = Var("-", "blade efficiency")
    AR_b = Var("-", "blade aspect ratio")
    AR_b_max = Var("-", "max blade aspect ratio", value=50)
    Re = Var("-", "blade reynolds number")
    f = Var("-", "intermediate tip loss variable")
    F = Var("-", "Prandtl tip loss factor")
    cl_max = Var("-", "max airfoil cl", value=0.6)
    dr = Var("m", "length of blade element")
    M = Var("-", "Mach number")
    a = Var("m/s", "Speed of sound at altitude", value=295)

    def setup(self, static, state):
        V = state.V
        rho = state.rho
        R = static.R
        mu = state.mu
        path = os.path.dirname(__file__)
        fd = pd.read_csv(path + os.sep + "dae51_fitdata.csv").to_dict(orient="records")[
            0
        ]
        c = static.c

        dT, eta_i, dQ, omega, Wa, Wt, Wr, va, vt = (
            self.dT,
            self.eta_i,
            self.dQ,
            self.omega,
            self.Wa,
            self.Wt,
            self.Wr,
            self.va,
            self.vt,
        )
        G, cl, cd, B, r, lam_w, eps, AR_b, AR_b_max = (
            self.G,
            self.cl,
            self.cd,
            self.B,
            self.r,
            self.lam_w,
            self.eps,
            self.AR_b,
            self.AR_b_max,
        )
        Re, f, F, cl_max, dr, M, a = (
            self.Re,
            self.f,
            self.F,
            self.cl_max,
            self.dr,
            self.M,
            self.a,
        )

        constraints = [
            TCS([Wa >= V + va]),
            TCS([Wt + vt <= omega * r]),
            TCS([G == (1.0 / 2.0) * Wr * c * cl]),
            F == (2.0 / pi) * (1.01116 * f**0.0379556) ** (10),
            M == Wr / a,
            lam_w == (r / R) * (Wa / Wt),
            va == vt * (Wt / Wa),
            eps == cd / cl,
            TCS([dQ >= rho * B * G * (Wa + eps * Wt) * r * dr]),
            AR_b == R / c,
            AR_b <= AR_b_max,
            Re == Wr * c * rho / mu,
            eta_i == (V / (omega * r)) * (Wt / Wa),
            TCS([f + (r / R) * B / (2 * lam_w) <= (B / 2.0) * (1.0 / lam_w)]),
            FitCS(fd, cd, [cl, Re], name="polar"),
            cl <= cl_max,
        ]
        with SignomialsEnabled():
            constraints += [
                SignomialEquality(Wr**2, (Wa**2 + Wt**2)),
                TCS([dT <= rho * B * G * (Wt - eps * Wa) * dr]),
                TCS(
                    [
                        vt**2 * F**2 * (1.0 + (4.0 * lam_w * R / (pi * B * r)) ** 2)
                        >= (B * G / (4.0 * pi * r)) ** 2
                    ]
                ),
            ]
        return constraints


class BladeElementProp(Model):
    "Performance for a propeller with multiple elements"

    Mtip = Var("-", "Max tip mach number", value=0.5)
    omega_max = Var("rpm", "maximum rotation rate", value=10000)
    eta = Var("-", "overall efficiency")
    omega = Var("rpm", "rotation rate")
    T = Var("lbf", "total thrust")
    Q = Var("N*m", "total torque")

    def setup(self, static, state, N=5):
        Mtip, omega_max, eta, omega, T, Q = (
            self.Mtip,
            self.omega_max,
            self.eta,
            self.omega,
            self.T,
            self.Q,
        )

        with Vectorize(N):
            blade = BladeElementPerf(static, state)

        constraints = [
            blade.dr == static.R / (N),
            blade.omega == omega,
            blade.r[0] == static.R / (2.0 * N),
        ]

        for n in range(1, N):
            constraints += [
                TCS([blade.r[n] >= blade.r[n - 1] + static.R / N]),
                blade.eta_i[n] == blade.eta_i[n - 1],
            ]

        constraints += [
            TCS([Q >= sum(blade.dQ)]),
            eta == state.V * T / (omega * Q),
            blade.M[-1] <= Mtip,
            static.T_m >= T,
            omega <= omega_max,
        ]

        with SignomialsEnabled():
            constraints += [TCS([T <= sum(blade.dT)])]

        return constraints, blade
