"""Pruebas rápidas con datos sintéticos: no leen el Excel."""
import numpy as np
import pandas as pd
import pytest

from backtest_forecast import estacionalidad, metricas
from reconstruir_inventario import calibrar, kardex

M = lambda s: pd.Period(s, "M")


def test_kardex_suma_compras_resta_ventas_y_no_baja_de_cero():
    base = pd.Series({"A": 5, "B": 1})
    meses = [M("2025-01"), M("2025-02")]
    si = pd.DataFrame({M("2025-01"): {"A": 2, "B": 0}, M("2025-02"): {"A": 0, "B": 0}})
    so = pd.DataFrame({M("2025-01"): {"A": 1, "B": 3}, M("2025-02"): {"A": 1, "B": 0}})
    stock, quiebre = kardex(base, meses, si, so)
    assert stock.loc["A"].tolist() == [6, 5]
    assert stock.loc["B"].tolist() == [0, 0]          # 1 + 0 − 3 = −2 → 0
    assert quiebre.loc["B", M("2025-01")]               # venta sin stock registrado
    assert not quiebre.loc["A"].any()


def test_calibrar_lleva_el_total_al_indice_del_resumen():
    meses = [M("2025-01")]
    stock = pd.DataFrame({M("2025-01"): {"A": 10.0, "B": 10.0}})
    base = pd.Series({"A": 10.0, "B": 10.0})
    res = pd.DataFrame({"COD_MARCA": ["X", "X"], "M": [M("2024-12"), M("2025-01")], "Unidades": [100, 150]})
    marca = pd.Series({"A": "X", "B": "X"})
    out = calibrar(stock, base, meses, M("2024-12"), res, marca)
    assert out[M("2025-01")].sum() == pytest.approx(30)  # 20 × 150 / 100


def test_estacionalidad_suma_12():
    idx = pd.period_range("2023-01", "2024-12", freq="M")
    serie = pd.Series(np.arange(1, 25, dtype=float), index=idx)
    est = estacionalidad(serie, [2023, 2024])
    assert est.sum() == pytest.approx(12)


def test_metricas_distingue_error_firmado_y_wape():
    m = metricas([100, 100], [120, 80])
    assert m["error_total"] == pytest.approx(0)      # los errores se compensan
    assert m["WAPE"] == pytest.approx(0.20)          # el WAPE no
    assert m["MAE"] == pytest.approx(20)
