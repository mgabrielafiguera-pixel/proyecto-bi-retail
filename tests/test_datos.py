"""Pruebas sobre el Excel real que lee Power BI. Tardan ~1 min la primera vez (luego usan caché)."""
import pytest

import hallazgos
import validar_modelo
from datos import cargar_tablas


@pytest.fixture(scope="session")
def tablas():
    return cargar_tablas()


def test_ningun_control_de_calidad_da_error(tablas):
    res = validar_modelo.correr(tablas)
    errores = res[res["Resultado"] == "Error"]
    assert errores.empty, errores[["Control", "Tabla", "Acción"]].to_string()


def test_totales_de_control_de_power_bi(tablas):
    res = validar_modelo.correr(tablas)
    tot = res[res["Tipo"] == "Totales"]
    assert len(tot) == 7 and (tot["Resultado"] == "OK").all()


def test_punto_de_reorden_2026():
    d = hallazgos.preparar()
    r = hallazgos.punto_reorden(d)
    assert (r["con_demanda"], r["reponer"]) == (88, 7)


def test_rolling_forecast_2026():
    d = hallazgos.preparar()
    rf = hallazgos.rolling_forecast(d["v"])
    assert rf["budget"] == pytest.approx(24_101_761, rel=1e-4)


def test_cifras_del_readme_coinciden_con_los_datos():
    filas = hallazgos.calcular().values()
    no = [f"{f['hallazgo']} {f['cifra']}" for f in filas if not f["ok"]]
    assert not no, no
