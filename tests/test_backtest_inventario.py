"""Reproduce el backtest del inventario documentado en docs/validacion.md."""
import pytest

import reconstruir_inventario as ri


@pytest.fixture(scope="module")
def bt():
    inv, res, si, so, marca, real = ri.cargar()
    t = ri.backtest(real, si, so, res, marca)
    return t.set_index(["Metodo", "Mes"])["Error_total_%"]


def test_kardex_puro_a_6_meses(bt):
    assert bt[("Kardex", "2025-06")] == pytest.approx(-22.1, abs=0.05)


def test_kardex_calibrado_a_6_meses(bt):
    assert bt[("Kardex calibrado", "2025-06")] == pytest.approx(-7.3, abs=0.05)


def test_media_calibrado_6_meses(bt):
    assert bt.xs("Kardex calibrado").mean() == pytest.approx(-9.4, abs=0.05)
