"Tests for FitCS"

from gpkit import Model, Variable, Vectorize

from gpkitmodels.tools.fit_constraintset import FitCS


def test_fitcs_sma_d1_k1():
    "FitCS with d=1, K=1 SMA fit solves correctly"
    fitdata = {
        "ftype": "SMA",
        "d": 1,
        "K": 1,
        "e00": 0.77,
        "c0": 1.28,
        "a1": 1.0,
        "rms_err": 0.01,
        "max_err": 0.02,
        "lb0": 0.1,
        "ub0": 10.0,
    }
    w = Variable("w")
    u = Variable("u", 2.0)
    cs = FitCS(fitdata, w, [u])
    m = Model(w, [cs])
    sol = m.solve(verbosity=0)
    # w = 1.28 * u^0.77, u=2 => w ≈ 2.184
    assert 2.0 < sol["w"].magnitude < 2.5


def test_fitcs_mixed_scalar_and_vectorized_dvars():
    """FitCS with mixed scalar and vectorized dvars.

    Reproduces the bug where numpy's array(dvars) fails with
    'inhomogeneous shape' when dvars contains both a vectorized
    NomialArray and a scalar Variable (different shapes).
    This is the pattern used by tail_aero.py: FitCS(fd, Cd, [Re, tau])
    where Re is vectorized across flight segments but tau is scalar.
    """
    fitdata = {
        "ftype": "SMA",
        "d": 2,
        "K": 2,
        "e00": 1.0,
        "e01": 0.0,
        "e10": 0.0,
        "e11": 1.0,
        "c0": 1.0,
        "c1": 1.0,
        "a1": 1.0,
        "rms_err": 0.01,
        "max_err": 0.02,
        "lb0": 0.1,
        "ub0": 10.0,
        "lb1": 0.1,
        "ub1": 10.0,
    }
    # u1 vectorized (like Re across flight segments); u2 scalar (like tau)
    with Vectorize(3):
        w = Variable("w")
        u1 = Variable("u_1", 2.0)
    u2 = Variable("u_2", 3.0)
    cs = FitCS(fitdata, w, [u1, u2])
    m = Model(w.prod(), [cs])
    sol = m.solve(verbosity=0)
    # w >= u1 + u2 = 5 at each point
    for i in range(3):
        assert 4.5 < sol["w"][i].magnitude < 5.5


def test_fitcs_ma_d1_k2():
    "FitCS with MA (max-affine) type, d=1, K=2"
    fitdata = {
        "ftype": "MA",
        "d": 1,
        "K": 2,
        "e00": 1.0,
        "e10": 0.5,
        "c0": 1.0,
        "c1": 2.0,
        "rms_err": 0.01,
        "max_err": 0.02,
        "lb0": 0.1,
        "ub0": 10.0,
    }
    w = Variable("w")
    u = Variable("u", 4.0)
    cs = FitCS(fitdata, w, [u])
    m = Model(w, [cs])
    sol = m.solve(verbosity=0)
    # w >= c0*u^1.0 = 4.0, w >= c1*u^0.5 = 4.0
    assert 3.5 < sol["w"].magnitude < 4.5
