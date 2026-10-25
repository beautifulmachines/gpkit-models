"fit constraint set"

from gpkit import (
    ConstraintSet,
    NamedVariables,
    NomialArray,
    Variable,
    VectorVariable,
)
from numpy import abs as nabs
from numpy import amax, hstack, where


class FitCS(ConstraintSet):
    """Constraint set for fitted functions

    Arguments
    ---------
    fitdata : dict
        dictionary of fit parameters
    ivar : gpkit Variable, Monomial, or NomialArray
        independent variable
    dvars : list of gpkit Variables, Monomials, or NomialArrays
        dependent variables
    err_margin : string, either "Max" or "RMS"
        flag to set margin factor using RMS or max error

    """

    def __init__(self, fitdata, ivar=None, dvars=None, name="", err_margin=None):  # noqa: PLR0912

        self.fitdata = fitdata

        if ivar is None:
            with NamedVariables("fit"):
                dvars = VectorVariable(fitdata["d"], "u")
                ivar = Variable("w")

        self.dvars = dvars
        self.ivar = ivar
        self.rms_err = fitdata["rms_err"]
        self.max_err = fitdata["max_err"]

        d = fitdata["d"]
        monos = []
        for k in range(fitdata["K"]):
            mono = fitdata["c%d" % k]
            for i in range(d):
                mono = mono * dvars[i] ** fitdata["e%d%d" % (k, i)]
            monos.append(mono)

        if err_margin == "Max":
            self.mfac = Variable(
                "m_{fac-" + name + "-fit}",
                1 + self.max_err,
                "-",
                "max error of fit",
            )
        elif err_margin == "RMS":
            self.mfac = Variable(
                "m_{fac-" + name + "-fit}",
                1 + self.rms_err,
                "-",
                "RMS error of fit",
            )
        elif err_margin is None:
            self.mfac = Variable("m_{fac-" + name + "-fit}", 1.0, "-", "fit factor")
        else:
            raise ValueError("Invalid name for err_margin: valid inputs Max, RMS")

        # Written as expressions in the fit's variables, so scalar and vector
        # (one relation per operating point) inputs take the same path.
        w = ivar / self.mfac
        if fitdata["ftype"] == "ISMA":
            # 1 >= c1*u1^exp1*u2^exp2*w^(-alpha1) + ....
            alphas = [fitdata["a%d" % k] for k in range(fitdata["K"])]
            sides = [(1, sum(m / w**a for m, a in zip(monos, alphas)))]
        elif fitdata["ftype"] == "SMA":
            # w^alpha >= c1*u1^exp1 + c2*u2^exp2 + ....
            sides = [(w ** fitdata["a1"], sum(monos))]
        elif fitdata["ftype"] == "MA":
            # w >= c1*u1^exp1, w >= c2*u2^exp2, ....: one constraint per piece
            sides = [(w, m) for m in monos]
        else:
            raise ValueError(f"Invalid ftype: {fitdata['ftype']}")

        if fitdata["K"] == 1:  # when possible, return an equality constraint
            constraints = [lhs == rhs for lhs, rhs in sides]
        else:
            constraints = [lhs >= rhs for lhs, rhs in sides]

        self.bounds = {}
        for i, dvar in enumerate(self.dvars):
            self.bounds[dvar] = [fitdata["lb%d" % i], fitdata["ub%d" % i]]

        ConstraintSet.__init__(self, constraints)

    def get_fitdata(self):
        "return fit data"
        return self.fitdata

    def get_dataframe(self):
        "return a pandas DataFrame of fit parameters"
        import pandas as pd  # noqa: PLC0415

        df = pd.DataFrame(list(self.fitdata.values())).transpose()
        df.columns = list(self.fitdata.keys())
        return df

    def process_result(self, result):
        """
        make sure fit result is within bounds of fitted data
        """
        super().process_result(result)

        if self.mfac not in result.sens.variables:
            return
        if amax(nabs(result.sens.variables[self.mfac])) < 1e-5:
            return

        for dvar in self.dvars:
            if isinstance(dvar, NomialArray):
                num = [result[x] for x in dvar]
            else:
                num = result[dvar]
            direct = None
            if any(x < self.bounds[dvar][0] for x in hstack([num])):
                direct, state = "lower", "below"
                bnd = self.bounds[dvar][0]
            if any(x > self.bounds[dvar][1] for x in hstack([num])):
                direct, state = "upper", "above"
                bnd = self.bounds[dvar][1]

            if direct:
                msg = (
                    "Variable %.100s could cause inaccurate result"
                    " because it is %s"
                    % (dvar, state)
                    + " %s bound. Solution is %.4f but"
                    " bound is %.4f" % (direct, amax([num]), bnd)
                )
                print("Warning: " + msg)


class XfoilFit(FitCS):
    """Special FitCS that can post-solve compare result to XFOIL

    Arguments (in addition to the arguments to FitCS)
    ---------
    airfoil:                            airfoil of fitted data
                                            str (e.g. "xxx.dat", "naca xxxx")

    """

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        fitdata,
        ivar=None,
        dvars=None,
        name="",
        err_margin=None,
        airfoil=False,
    ):

        super().__init__(
            fitdata, ivar=ivar, dvars=dvars, name=name, err_margin=err_margin
        )

        self.airfoil = airfoil

    def process_result(self, result):
        """
        if data comes from Xfoil and airfoil is provided check against xfoil
        """
        super().process_result(result)

        if self.mfac not in result.sens.variables:
            return
        if amax(nabs(result.sens.variables[self.mfac])) < 1e-5:
            return
        if not self.airfoil:
            return

        from .xfoilWrapper import xfoil_comparison  # noqa: PLC0415

        cl, re = 0.0, 0.0
        for dvar in self.dvars:
            if "Re" in str(dvar):
                re = result[dvar]
            if "C_L" in str(dvar):
                cl = result[dvar]
        cd = result[self.ivar]
        if not hasattr(cl, "__len__") and hasattr(re, "__len__"):
            cl = [cl] * len(re)
        err, cdx = xfoil_comparison(self.airfoil, cl, re, cd)
        ind = where(err > 0.05)[0]
        for i in ind:
            msg = (
                "Drag error for %s is %.2f. Re=%.1f; CL=%.4f;"
                " Xfoil cd=%.6f, GP sol cd=%.6f"
                % (
                    ", ".join(self.ivar.descr["models"]),
                    err[i],
                    re[i],
                    cl[i],
                    cd[i],
                    cdx[i],
                )
            )
            print("Warning: %s" % msg)
