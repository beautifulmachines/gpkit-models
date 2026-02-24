"wing test"

from gpkit import Model, Var, Vectorize

from gpkitmodels.GP.aircraft.wing.boxspar import BoxSpar
from gpkitmodels.GP.aircraft.wing.wing import Wing


class FlightState(Model):
    "Flight State"

    V = Var("m/s", "airspeed", value=50)
    rho = Var("kg/m^3", "air density", value=1.255)
    mu = Var("N*s/m**2", "air viscosity", value=1.5e-5)
    qne = Var("kg/s^2/m", "never exceed dynamic pressure")

    def setup(self):
        return [self.qne == self.V**2 * self.rho * 1.2]


def wing_test():
    "test wing models"

    W = Wing()
    W.substitutions[W.W] = 50
    W.substitutions[W.planform.tau] = 0.115
    fs = FlightState()
    perf = W.flight_model(W, fs)
    loading = [W.spar.loading(W, fs)]
    loading[0].substitutions["W"] = 100
    loading.append(W.spar.gustloading(W, fs))
    loading[1].substitutions["W"] = 100

    from gpkit import settings

    if settings["default_solver"] == "cvxopt":
        for l in loading:
            for v in ["Mtip", "Stip", "wroot", "throot"]:
                l.substitutions[v] = 1e-1

    m = Model(
        perf.Cd,
        [
            loading[1].v == fs.V,
            loading[1].cl == perf.CL,
            loading[1].Ww == W.W,
            loading[1].Ww <= 0.5 * fs.rho * fs.V**2 * perf.CL * W.planform.S,
            W,
            fs,
            perf,
            loading,
        ],
    )
    m.solve(verbosity=0)


def box_spar():
    "test wing models"

    class _BoxSparWing(Wing):
        spar_model = BoxSpar

    W = _BoxSparWing()
    W.substitutions[W.W] = 50
    W.substitutions[W.planform.tau] = 0.115
    fs = FlightState()
    perf = W.flight_model(W, fs)
    loading = [W.spar.loading(W, fs)]
    loading[0].substitutions["W"] = 100
    loading.append(W.spar.gustloading(W, fs))
    loading[1].substitutions["W"] = 100

    from gpkit import settings

    if settings["default_solver"] == "cvxopt":
        for l in loading:
            for v in ["Mtip", "Stip", "wroot", "throot"]:
                l.substitutions[v] = 1e-2

    m = Model(
        perf.Cd,
        [
            loading[1].v == fs.V,
            loading[1].cl == perf.CL,
            loading[1].Ww == W.W,
            loading[1].Ww <= fs.qne * perf.CL * W.planform.S,
            W,
            fs,
            perf,
            loading,
        ],
    )
    m.solve(verbosity=0)


def wing_aero_vectorized():
    "WingAero must be constructable inside Vectorize (rhoValue/muValue bool bug)"
    W = Wing()
    W.substitutions[W.planform.tau] = 0.115
    with Vectorize(5):
        fs = FlightState()
        perf = W.flight_model(W, fs)  # previously raised ValueError on bool(array)
    assert hasattr(perf, "rhoValue")
    assert perf.rhoValue is True


def test():
    "tests"
    wing_test()
    box_spar()
    wing_aero_vectorized()


if __name__ == "__main__":
    test()
