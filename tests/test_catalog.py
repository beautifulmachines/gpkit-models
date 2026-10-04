"""Catalog-driven smoke test for gpkit-models."""

from pathlib import Path

import pytest
from gpkit.tests.test_catalog import (
    catalog_ids,
    load_catalog,
    run_catalog_snapshots,
    run_catalog_test,
    run_catalog_to_ir,
    run_catalog_toml_roundtrip,
)

_CATALOG = load_catalog(Path(__file__))


@pytest.mark.parametrize("model_entry", _CATALOG, ids=catalog_ids(_CATALOG))
def test_catalog_model(model_entry):
    run_catalog_test(model_entry)


@pytest.mark.parametrize("model_entry", _CATALOG, ids=catalog_ids(_CATALOG))
def test_catalog_snapshots(model_entry):
    """Regenerate each catalog entry's snapshots; drift shows as a git diff."""
    run_catalog_snapshots(model_entry, __file__)


@pytest.mark.parametrize("model_entry", _CATALOG, ids=catalog_ids(_CATALOG))
def test_catalog_to_ir(model_entry):
    """Each catalog entry exports a complete, self-consistent IR document."""
    run_catalog_to_ir(model_entry)


@pytest.mark.parametrize("model_entry", _CATALOG, ids=catalog_ids(_CATALOG))
def test_catalog_toml_roundtrip(model_entry):
    """Each catalog entry survives to_toml -> load_toml and solves the same."""
    run_catalog_toml_roundtrip(model_entry)
