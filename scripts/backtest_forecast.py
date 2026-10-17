"""Backtest del forecast de ventas (Sell Out) de la página Budget / Forecast.

Método del informe (03_powerbi/MODELO.md, sección 4), con corte C a fin de mes:
    Pieza promedio   = uds de los 12 meses que terminan en C / 12
    Estacionalidad   = uds del mes calendario en los años de referencia
                       / (uds totales de esos años / 12)
    Forecast uds (m) = pieza promedio x estacionalidad[mes calendario de m]
    Forecast $   (m) = forecast uds x precio promedio 12M (importe / uds de los 12 meses hasta C)
Igual que el DAX, todo se recalcula dentro de cada departamento o marca. DIVIDE de DAX
devuelve vacío al dividir por cero; aquí ese caso cuenta como forecast 0.

Sin fuga de información: la estacionalidad solo usa años completos anteriores al corte.
    Principal:  corte 30-abr-2025, horizonte may-dic 2025, estacionalidad 2023-2024
                (el informe usa 2024-2025; 2025 no está disponible en este corte).
    Secundario: corte 30-abr-2024, horizonte may-dic 2024, estacionalidad 2023.
Bases de comparación: ingenuo estacional (mismo mes del año anterior) y promedio 12M
plano (pieza promedio sin estacionalidad, al mismo precio 12M).
Las ventas de may-jun 2026 no se usan (el informe las excluye).

Uso: python3 scripts/backtest_forecast.py
Salidas:
    docs/resultados/backtest_forecast.md   tablas y lectura
    docs/resultados/backtest_forecast.csv  real y estimados por pliegue, nivel, grupo y mes
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datos import cargar_tablas  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "docs" / "resultados"
P = lambda s: pd.Period(s, "M")
FIN_DATOS = P("2026-04")  # último mes que usa el informe
PLIEGUES = {
    "Principal (corte abr-2025)": dict(corte=P("2025-04"), anios=[2023, 2024]),
    "Secundario (corte abr-2024)": dict(corte=P("2024-04"), anios=[2023]),
}
HORIZONTE = 8  # may-dic
NIVELES = {"Total": None, "Departamento": "DEPARTAMENTO", "Marca": "CODIGO_INTERNO_MARCA"}
METODOS = ["Informe", "Ingenuo estacional", "Promedio 12M plano"]


# ---------- funciones puras ----------

def serie_mensual(ventas, grupo=None):
    """Uds e importe por mes (filas, Period M) y grupo (columnas). Devuelve (uds, imp)."""
    v = ventas.assign(M=ventas["Fecha"].dt.to_period("M"), G=ventas[grupo] if grupo else "TOTAL")
    t = v.groupby(["M", "G"])[["Cantidad", "Total_Factura"]].sum()
    meses = pd.period_range(t.index.get_level_values("M").min(), t.index.get_level_values("M").max(), freq="M")
    uds = t["Cantidad"].unstack(fill_value=0).reindex(meses, fill_value=0)
    imp = t["Total_Factura"].unstack(fill_value=0).reindex(meses, fill_value=0)
    return uds, imp


def ventana_12m(serie, corte):
    """Filas de los 12 meses que terminan en el corte (inclusive)."""
    return serie.loc[corte - 11:corte]


def estacionalidad(serie_mensual, anios):
    """Índice por mes calendario (1-12): uds del mes en `anios` / (uds de esos años / 12)."""
    s = serie_mensual[serie_mensual.index.year.isin(anios)]
    por_mes = s.groupby(s.index.month).sum().reindex(range(1, 13), fill_value=0)
    return por_mes / (s.sum() / 12)


def forecast_informe(uds, imp, corte, anios_est, horizonte):
    """Forecast del informe para los meses `horizonte`. Devuelve (uds, imp) con forecast 0 si DIVIDE da vacío."""
    pieza = ventana_12m(uds, corte).sum() / 12
    precio = ventana_12m(imp, corte).sum() / ventana_12m(uds, corte).sum()
    est = estacionalidad(uds, anios_est)
    f_uds = pd.DataFrame([pieza * est.loc[m.month] for m in horizonte], index=horizonte)
    f_uds = f_uds.replace([np.inf, -np.inf], np.nan).fillna(0)
    f_imp = (f_uds * precio).replace([np.inf, -np.inf], np.nan).fillna(0)
    return f_uds, f_imp


def forecast_ingenuo(uds, imp, horizonte):
    """Ingenuo estacional: el mismo mes del año anterior."""
    prev = [m - 12 for m in horizonte]
    return (uds.reindex(prev, fill_value=0).set_axis(horizonte),
            imp.reindex(prev, fill_value=0).set_axis(horizonte))


def forecast_plano(uds, imp, corte, horizonte):
    """Promedio 12M plano: pieza promedio en todos los meses, al precio promedio 12M."""
    pieza = ventana_12m(uds, corte).sum() / 12
    precio = ventana_12m(imp, corte).sum() / ventana_12m(uds, corte).sum()
    f_uds = pd.DataFrame([pieza] * len(horizonte), index=horizonte)
    f_imp = (f_uds * precio).replace([np.inf, -np.inf], np.nan).fillna(0)
    return f_uds, f_imp


def metricas(real, est, mape=False):
    """Métricas sobre todas las celdas (grupo x mes) de dos arrays alineados.

    error_total = (Σest − Σreal)/Σreal; MAE = media |est−real|; WAPE = Σ|est−real|/Σreal;
    sesgo = Σ(est−real)/n; MAPE = media |est−real|/real (solo si se pide; exige real ≠ 0).
    """
    real, est = np.asarray(real, float).ravel(), np.asarray(est, float).ravel()
    e = est - real
    out = {"error_total": e.sum() / real.sum(), "MAE": np.abs(e).mean(),
           "WAPE": np.abs(e).sum() / real.sum(), "sesgo": e.mean(), "n": e.size}
    out["MAPE"] = np.mean(np.abs(e) / np.abs(real)) if mape else np.nan
    return out


# ---------- backtest ----------

def backtest(ventas, producto):
    """Devuelve (detalle largo, resumen de métricas)."""
    v = ventas[ventas["Fecha"].dt.to_period("M") <= FIN_DATOS].merge(
        producto[["COD_SKU", "DEPARTAMENTO", "CODIGO_INTERNO_MARCA"]], on="COD_SKU", how="left")
    detalle, resumen = [], []
    for pliegue, cfg in PLIEGUES.items():
        corte = cfg["corte"]
        hz = pd.period_range(corte + 1, periods=HORIZONTE, freq="M")
        for nivel, col in NIVELES.items():
            uds, imp = serie_mensual(v, col)
            uds, imp = uds.loc[:hz[-1]], imp.loc[:hz[-1]]
            est = {"Informe": forecast_informe(uds, imp, corte, cfg["anios"], hz),
                   "Ingenuo estacional": forecast_ingenuo(uds, imp, hz),
                   "Promedio 12M plano": forecast_plano(uds, imp, corte, hz)}
            real = (uds.loc[hz], imp.loc[hz])
            # Grupos evaluados: los que tienen venta real o algún forecast ≠ 0 en el horizonte
            activos = (real[0] != 0).any() | (real[1] != 0).any()
            for f in est.values():
                activos |= (f[0].reindex(columns=uds.columns, fill_value=0) != 0).any()
            grupos = activos[activos].index
            al = lambda df: df.reindex(index=hz, columns=grupos, fill_value=0)
            for medida, i in (("Unidades", 0), ("Importe", 1)):
                r = al(real[i])
                for metodo in METODOS:
                    m = metricas(r.values, al(est[metodo][i]).values, mape=(nivel == "Total"))
                    resumen.append(dict(pliegue=pliegue, nivel=nivel, medida=medida, metodo=metodo,
                                        grupos=len(grupos), **m))
            larga = {"real_uds": al(real[0]), "real_imp": al(real[1])}
            for metodo, clave in zip(METODOS, ["informe", "ingenuo", "plano"]):
                larga[f"{clave}_uds"], larga[f"{clave}_imp"] = al(est[metodo][0]), al(est[metodo][1])
            d = pd.concat({k: x.stack() for k, x in larga.items()}, axis=1).reset_index()
            d.columns = ["mes", "grupo"] + list(larga)
            detalle.append(d.assign(pliegue=pliegue, nivel=nivel))
    det = pd.concat(detalle, ignore_index=True)
    det = det[["pliegue", "nivel", "grupo", "mes"] + [c for c in det.columns if c.endswith(("_uds", "_imp"))]]
    det["mes"] = det["mes"].astype(str)
    return det, pd.DataFrame(resumen)


# ---------- informe ----------

def fmt(x, pct=False, dec=0):
    if pd.isna(x):
        return "—"
    return f"{x:+.1%}" if pct == "signo" else f"{x:.1%}" if pct else f"{x:,.{dec}f}"


def tabla_md(df):
    lineas = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    lineas += ["| " + " | ".join(map(str, fila)) + " |" for fila in df.itertuples(index=False)]
    return "\n".join(lineas)


def escribir_md(det, res):
    principal = list(PLIEGUES)[0]
    tot = det[(det["pliegue"] == principal) & (det["nivel"] == "Total")]
    filas = []
    for t in tot.itertuples():
        filas.append([t.mes, fmt(t.real_uds), fmt(t.informe_uds), fmt(t.ingenuo_uds), fmt(t.plano_uds),
                      fmt(t.real_imp), fmt(t.informe_imp), fmt(t.ingenuo_imp), fmt(t.plano_imp)])
    s = tot.sum(numeric_only=True)
    filas.append(["**Total**"] + [f"**{fmt(s[c])}**" for c in
                 ["real_uds", "informe_uds", "ingenuo_uds", "plano_uds",
                  "real_imp", "informe_imp", "ingenuo_imp", "plano_imp"]])
    t_mes = pd.DataFrame(filas, columns=["Mes", "Real uds", "Informe uds", "Ingenuo uds", "Plano uds",
                                         "Real $", "Informe $", "Ingenuo $", "Plano $"])

    r = res.copy()
    r_md = pd.DataFrame({
        "Pliegue": r["pliegue"].str.split(" ").str[0], "Nivel": r["nivel"], "Medida": r["medida"],
        "Método": r["metodo"], "Celdas": r["n"],
        "Error total": r["error_total"].map(lambda x: fmt(x, "signo")),
        "MAE": r["MAE"].map(fmt), "WAPE": r["WAPE"].map(lambda x: fmt(x, True)),
        "Sesgo": r["sesgo"].map(lambda x: f"{x:+,.0f}"),
        "MAPE": r["MAPE"].map(lambda x: fmt(x, True))})

    # Ganador por pliegue x nivel x medida según WAPE
    gan = (r.loc[r.groupby(["pliegue", "nivel", "medida"])["WAPE"].idxmin()]
             .set_index(["pliegue", "nivel", "medida"])["metodo"])
    piv = r.pivot_table(index=["pliegue", "nivel", "medida"], columns="metodo", values="WAPE", sort=False)
    g_md = pd.DataFrame({
        "Pliegue": [i[0].split(" ")[0] for i in piv.index], "Nivel": [i[1] for i in piv.index],
        "Medida": [i[2] for i in piv.index],
        **{f"WAPE {m}": piv[m].map(lambda x: fmt(x, True)).values for m in METODOS},
        "Gana (WAPE)": gan.reindex(piv.index).values,
        "Informe < Ingenuo": np.where(piv["Informe"] < piv["Ingenuo estacional"], "Sí", "No")})

    ngr = res[res["metodo"] == "Informe"].drop_duplicates(["pliegue", "nivel"]).set_index(["pliegue", "nivel"])["grupos"]
    texto = f"""# Backtest del forecast de ventas (Sell Out)

Generado por `scripts/backtest_forecast.py`. Evalúa el método de forecast de la página Budget / Forecast
(`03_powerbi/MODELO.md`, sección 4): uds = pieza promedio 12M × estacionalidad en unidades;
$ = uds × precio promedio 12M. En departamento y marca el cálculo se rehace dentro de cada grupo, como el DAX
respeta los filtros.

## Diseño (sin fuga de información)

| Pliegue | Corte | Horizonte | Estacionalidad | Pieza y precio |
|---|---|---|---|---|
| Principal | 30-abr-2025 | may–dic 2025 | 2023 y 2024 | may-2024 a abr-2025 |
| Secundario | 30-abr-2024 | may–dic 2024 | 2023 | may-2023 a abr-2024 |

- El informe usa estacionalidad 2024–2025 con corte abr-2026. Ese escenario no se puede evaluar (may–dic 2026
  no existe aún) y en el pliegue principal no se puede usar 2025 sin mirar el horizonte, por eso se usan los
  años completos anteriores al corte. El secundario solo tiene 2023 (los datos empiezan en ene-2023), un año
  con volumen mucho menor y más irregular.
- Bases: **ingenuo estacional** = mismo mes del año anterior; **promedio 12M plano** = pieza promedio sin
  estacionalidad, al precio 12M.
- Métricas sobre las celdas grupo × mes del horizonte: error total = (Σest − Σreal)/Σreal; MAE = media de
  |est − real|; WAPE = Σ|est − real| / Σreal; sesgo = Σ(est − real)/n (positivo = sobreestima). El MAPE solo se
  calcula a nivel total mensual; en marca y departamento no, porque hay celdas con venta real 0.
- Grupos evaluados: los que tienen venta real o forecast ≠ 0 en el horizonte (principal:
  {ngr[(principal, 'Departamento')]} departamentos, {ngr[(principal, 'Marca')]} marcas; secundario:
  {ngr[(list(PLIEGUES)[1], 'Departamento')]} departamentos, {ngr[(list(PLIEGUES)[1], 'Marca')]} marcas).
  Si DIVIDE daría vacío (sin ventas en la referencia), el forecast cuenta como 0.
- Las ventas de may–jun 2026 no se usan.

## Pliegue principal: total mensual

{tabla_md(t_mes)}

## Métricas por pliegue, nivel, medida y método

{tabla_md(r_md)}

## Quién gana (WAPE más bajo)

{tabla_md(g_md)}

## Lectura

{lectura(det, r)}
"""
    (SALIDA / "backtest_forecast.md").write_text(texto, encoding="utf-8")


def lectura(det, res):
    """Párrafos de lectura con las cifras del propio backtest."""
    pr, se = list(PLIEGUES)
    w = res.set_index(["pliegue", "nivel", "medida", "metodo"])
    W = lambda pl, n, md, mt: fmt(w.loc[(pl, n, md, mt), "WAPE"], True)
    E = lambda pl, n, md, mt: fmt(w.loc[(pl, n, md, mt), "error_total"], "signo")
    tot = det[(det["pliegue"] == pr) & (det["nivel"] == "Total")].sum(numeric_only=True)
    p_est, p_real = tot["informe_imp"] / tot["informe_uds"], tot["real_imp"] / tot["real_uds"]
    return f"""- **Total y departamento: el método del informe gana** en los dos pliegues y supera al ingenuo estacional en
  unidades e importe (principal, total: WAPE uds {W(pr, "Total", "Unidades", "Informe")} vs
  {W(pr, "Total", "Unidades", "Ingenuo estacional")} ingenuo y {W(pr, "Total", "Unidades", "Promedio 12M plano")} plano;
  importe {W(pr, "Total", "Importe", "Informe")} vs {W(pr, "Total", "Importe", "Ingenuo estacional")} y
  {W(pr, "Total", "Importe", "Promedio 12M plano")}). Única excepción: departamento × unidades del secundario, donde
  el plano queda apenas por delante ({W(se, "Departamento", "Unidades", "Promedio 12M plano")} vs
  {W(se, "Departamento", "Unidades", "Informe")}). La estacionalidad aporta: capta el pico de diciembre que el
  plano no ve.
- **Sesgo a la baja en todos los métodos.** El total del horizonte se subestima
  ({E(pr, "Total", "Unidades", "Informe")} en uds y {E(pr, "Total", "Importe", "Informe")} en importe en el
  principal; {E(se, "Total", "Unidades", "Informe")} y {E(se, "Total", "Importe", "Informe")} en el secundario)
  porque las ventas crecieron y el método no tiene tendencia. En importe el error es mayor porque además el
  precio promedio subió: el precio 12M al corte era {fmt(p_est)} por unidad y el real de may–dic 2025 fue
  {fmt(p_real)} ({fmt(p_real / p_est - 1, "signo")}).
- **Marca: ningún método es fiable** (WAPE {W(pr, "Marca", "Unidades", "Informe")}–{W(se, "Marca", "Unidades", "Informe")}
  en uds para el informe). Gana el promedio plano: probablemente la estacionalidad propia de cada marca, con uno o dos
  años de historia y pocas unidades, amplifica el ruido; en el secundario (solo 2023 de referencia) el informe
  queda incluso detrás del ingenuo. A nivel marca conviene leer el forecast como orden de magnitud.
- Con estacionalidad 2024–2025 (la del informe) la referencia es más reciente y con más volumen que en estos pliegues, pero
  esa configuración no se puede verificar hasta tener may–dic 2026; el sesgo a la baja por crecimiento y
  precio sí aplicaría igual si el negocio sigue creciendo.
"""


def main():
    t = cargar_tablas()
    det, res = backtest(t["Ventas"], t["Producto"])
    SALIDA.mkdir(parents=True, exist_ok=True)
    det.round(2).to_csv(SALIDA / "backtest_forecast.csv", index=False)
    escribir_md(det, res)
    pd.set_option("display.width", 200)
    print(res.drop(columns="grupos").round(3).to_string(index=False))


if __name__ == "__main__":
    main()
