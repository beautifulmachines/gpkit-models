"""Catalog-driven smoke test for gpkit-models."""

import importlib
from pathlib import Path

import pytest
from gpkit import Model
from gpkit.tests.test_catalog import catalog_ids, load_catalog, run_catalog_test

try:
    from gpkit.tests.test_ir import ir_diff
except (ImportError, FileNotFoundError):
    ir_diff = None

_CATALOG = load_catalog(Path(__file__))


@pytest.mark.parametrize("model_entry", _CATALOG, ids=catalog_ids(_CATALOG))
def test_catalog_model(model_entry):
    run_catalog_test(model_entry)


@pytest.mark.parametrize("model_entry", _CATALOG, ids=catalog_ids(_CATALOG))
def test_catalog_ir_roundtrip(model_entry):
    """gpkit-models catalog model: IR must be identical after round-trip."""
    if ir_diff is None:
        pytest.skip("ir_diff not available (install gpkit-core from source)")
    mod = importlib.import_module(model_entry["module"])
    cls = getattr(mod, model_entry["class"])
    m = cls.default()
    ir1 = m.to_ir()
    m2 = Model.from_ir(ir1)
    ir2 = m2.to_ir()
    diff = ir_diff(ir1, ir2)
    assert diff is None, f"{cls.__name__} IR changed after round-trip:\n{diff}"
