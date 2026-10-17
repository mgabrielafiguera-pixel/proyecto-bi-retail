"""Recalcula desde el Excel las cifras de la sección 9 (Resultados) de README.md.

Cada función `h4x_*` devuelve un dict {clave: fila}, donde cada fila tiene la cifra
del README, el valor recalculado, el tipo de tolerancia y la definición usada.
Tolerancias: ±0,5 puntos para porcentajes, ±1 % relativo para importes y unidades
(los conteos pequeños quedan, en la práctica, como coincidencia exacta).

Uso (desde la raíz o desde scripts/): python3 scripts/hallazgos.py
Salida: docs/resultados/hallazgos.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datos import RAIZ, cargar_tablas, compras_validas, costo_con_signo  # noqa: E402

SALIDA = RAIZ / "docs" / "resultados" / "hallazgos.md"
CORTE = pd.Timestamp("2026-04-30")  # último inventario
Z = 1.65  # nivel de servicio 95 %


# ---------------------------------------------------------------- utilidades

def fila(hallazgo, cifra, readme, valor, tipo, definicion, tol=None):
    """Una fila de la tabla. tipo: 'pct' (puntos), 'num' (relativo), 'abs' (tol absoluta),
    'menor' (valor < readme) o 'mayor0' (valor > 0)."""
    return {"hallazgo": hallazgo, "cifra": cifra, "readme": readme, "valor": valor,
            "tipo": tipo, "tol": tol, "definicion": definicion}


def coincide(f):
    r, v = f["readme"], f["valor"]
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return False
    if f["tipo"] == "pct":
        return abs(v - r) <= (f["tol"] or 0.5)
    if f["tipo"] == "abs":
        return abs(v - r) <= f["tol"]
    if f["tipo"] == "menor":
        return v < r
    if f["tipo"] == "mayor0":
        return v > 0
    return abs(v - r) <= 0.01 * abs(r)


def var(a, b):
    """Variación % de a contra b."""
    return (a / b - 1) * 100


def ene_abr(df, anio, col="Fecha"):
    return df[(df[col].dt.year == anio) & (df[col].dt.month <= 4)]


def anio(df, a, col="Fecha"):
    return df[df[col].dt.year == a]


def preparar():
    """Tablas con las columnas que se usan: marca y departamento pegados a Ventas, Compras e Inventario."""
    t = cargar_tablas()
    prod = t["Producto"][["COD_SKU", "CODIGO_INTERNO_MARCA", "DEPARTAMENTO"]]
    v = t["Ventas"].copy()
    v["Costo"] = costo_con_signo(v)
    v = v.merge(prod, on="COD_SKU", how="left")
    c_todas = t["Compras"].merge(prod, on="COD_SKU", how="left")
    c = compras_validas(t["Compras"]).merge(prod, on="COD_SKU", how="left")
    inv = t["Inventario"].merge(prod, on="COD_SKU", how="left")
    return {"v": v, "c": c, "c_todas": c_todas, "inv": inv, "n_marcas": len(t["Marca"]),
            "n_clientes": len(t["Cliente"])}


def sell_through(v, c):
    return v["Cantidad"].sum() / c["Cantidad"].sum()


def ticket(v):
    f = v[v["Mov"] == "FACT"]
    return f["Total_Factura"].sum() / f["Num_Factura"].nunique()


def precio_pieza(v):
    return v["Total_Factura"].sum() / v["Cantidad"].sum()


def margen_pct(v):
    return (1 - v["Costo"].sum() / v["Total_Factura"].sum()) * 100


# ---------------------------------------------------------------- 4.1

def h41_compras_vs_ventas(d):
    v, c = d["v"], d["c"]
    exw = ene_abr(c, 2026, "Fecha_Recepcion")["Total_Costo_Ex_Works"].sum() / \
        ene_abr(c, 2025, "Fecha_Recepcion")["Total_Costo_Ex_Works"].sum()
    st = {a: sell_through(anio(v, a), anio(c, a, "Fecha_Recepcion")) for a in (2024, 2025)}
    st_ea = {a: sell_through(ene_abr(v, a), ene_abr(c, a, "Fecha_Recepcion")) for a in (2025, 2026)}
    h = "9.1"
    return {
        "exw_x": fila(h, "Compras Ex-Work ene–abr 2026 vs 2025 (veces)", 4.5, exw, "abs",
                      "ΣTotal_Costo_Ex_Works ene–abr 26 / ene–abr 25 (compras_validas, Fecha_Recepcion); tol ±0,05. Sin excluir los 6 errores da 3,01", 0.05),
        "venta_var": fila(h, "Venta importe ene–abr 2026 vs 2025 (%)", -7.3,
                          var(ene_abr(v, 2026)["Total_Factura"].sum(), ene_abr(v, 2025)["Total_Factura"].sum()),
                          "pct", "ΣTotal_Factura ene–abr 26 / ene–abr 25 − 1"),
        "st_ea25": fila(h, "Sell-through uds ene–abr 2025", 1.30, st_ea[2025], "abs",
                        "ΣCantidad ventas / ΣCantidad compras_validas, ene–abr 2025; tol ±0,005 (=0,5 pt)", 0.005),
        "st_ea26": fila(h, "Sell-through uds ene–abr 2026", 0.78, st_ea[2026], "abs",
                        "ΣCantidad ventas / ΣCantidad compras_validas, ene–abr 2026", 0.005),
        "st24": fila(h, "Sell-through uds 2024", 0.69, st[2024], "abs",
                     "ΣCantidad ventas / ΣCantidad compras_validas, año 2024", 0.005),
        "st25": fila(h, "Sell-through uds 2025", 1.16, st[2025], "abs",
                     "ΣCantidad ventas / ΣCantidad compras_validas, año 2025", 0.005),
    }


# ---------------------------------------------------------------- 4.2

def h42_precio_vs_volumen(d):
    v = d["v"]
    a, b = ene_abr(v, 2026), ene_abr(v, 2025)
    fa, fb = a[a["Mov"] == "FACT"], b[b["Mov"] == "FACT"]
    rel_a, rel_b = a[a["DEPARTAMENTO"] == "RELOJERIA"], b[b["DEPARTAMENTO"] == "RELOJERIA"]
    joy_a, joy_b = a[a["DEPARTAMENTO"] == "JOYERIA"], b[b["DEPARTAMENTO"] == "JOYERIA"]
    h = "9.2"
    return {
        "uds": fila(h, "Unidades vendidas ene–abr 26 vs 25 (%)", -1.7,
                    var(a["Cantidad"].sum(), b["Cantidad"].sum()), "pct", "ΣCantidad (neta) ene–abr 26 / 25 − 1"),
        "facturas": fila(h, "Facturas ene–abr 26 vs 25 (%)", 1.2,
                         var(fa["Num_Factura"].nunique(), fb["Num_Factura"].nunique()), "pct",
                         "nº distinto Num_Factura con Mov='FACT' (medida Facturas), ene–abr 26 / 25 − 1. Sin filtrar Mov da +0,57"),
        "clientes": fila(h, "Clientes ene–abr 26 vs 25 (%)", 6,
                         var(a["COD_CLIENTE"].nunique(), b["COD_CLIENTE"].nunique()), "pct",
                         "nº distinto COD_CLIENTE (todas las líneas), ene–abr 26 / 25 − 1"),
        "ticket": fila(h, "Ticket promedio ene–abr 26 vs 25 (%)", -11, var(ticket(a), ticket(b)), "pct",
                       "Ticket = ΣTotal_Factura(Mov='FACT') / Facturas; ene–abr 26 / 25 − 1. Con el importe neto (FACT + N/CR) da −8,34"),
        "rel_peso": fila(h, "Relojería, % de la venta ene–abr 2026", 58,
                         rel_a["Total_Factura"].sum() / a["Total_Factura"].sum() * 100, "pct",
                         "ΣTotal_Factura RELOJERIA / ΣTotal_Factura, ene–abr 2026"),
        "rel_precio": fila(h, "Relojería, precio medio por pieza (%)", -29,
                           var(precio_pieza(rel_a), precio_pieza(rel_b)), "pct",
                           "(ΣTotal_Factura/ΣCantidad) RELOJERIA ene–abr 26 / 25 − 1"),
        "rel_uds": fila(h, "Relojería, unidades (%)", 16,
                        var(rel_a["Cantidad"].sum(), rel_b["Cantidad"].sum()), "pct",
                        "ΣCantidad RELOJERIA ene–abr 26 / 25 − 1"),
        "rel_m25": fila(h, "Relojería, margen ene–abr 2025 (%)", 36, margen_pct(rel_b), "pct",
                        "margen % (costo_con_signo) RELOJERIA ene–abr 2025"),
        "rel_margen": fila(h, "Relojería, margen ene–abr 2026 (%)", 42, margen_pct(rel_a), "pct",
                           "(ΣTotal_Factura − Σcosto_con_signo)/ΣTotal_Factura, RELOJERIA ene–abr 2026. Con el costo sin corregir el signo da 35,96"),
        "joy_var": fila(h, "Joyería, venta importe (%)", 10,
                        var(joy_a["Total_Factura"].sum(), joy_b["Total_Factura"].sum()), "pct",
                        "ΣTotal_Factura JOYERIA ene–abr 26 / 25 − 1"),
        "joy_precio": fila(h, "Joyería, precio por pieza (% var., README: «sube»)", 0,
                           var(precio_pieza(joy_a), precio_pieza(joy_b)), "mayor0",
                           "(ΣTotal_Factura/ΣCantidad) JOYERIA ene–abr 26 / 25 − 1; coincide si > 0"),
        "joy_m25": fila(h, "Joyería, margen ene–abr 2025 (%)", 51, margen_pct(joy_b), "pct",
                        "margen % JOYERIA ene–abr 2025"),
        "joy_m26": fila(h, "Joyería, margen ene–abr 2026 (%)", 59, margen_pct(joy_a), "pct",
                        "margen % (costo_con_signo) JOYERIA ene–abr 2026. Con el costo sin corregir el signo da 56,56"),
    }


# ---------------------------------------------------------------- 4.3

def stock_sin_venta_12m(inv, v, fecha):
    """Unidades en stock a `fecha` de SKU sin ninguna línea de venta en los 12 meses que terminan en ese mes."""
    desde = (fecha - pd.offsets.MonthEnd(12)) + pd.Timedelta(days=1)
    con_venta = set(v.loc[(v["Fecha"] >= desde) & (v["Fecha"] <= fecha), "COD_SKU"])
    foto = inv[inv["Fecha"] == fecha]
    return foto.loc[~foto["COD_SKU"].isin(con_venta), "Unidades"].sum(), foto["Unidades"].sum()


def h43_inventario(d, reorden):
    v, inv = d["v"], d["inv"]
    s_ini = inv.loc[inv["Fecha"] == "2023-12-31", "Unidades"].sum()
    sin_venta, s_fin = stock_sin_venta_12m(inv, v, CORTE)
    foto = inv[inv["Fecha"] == CORTE]
    bel_acc = ["BELLEZA", "ACCESORIOS"]
    pct_stock = foto.loc[foto["DEPARTAMENTO"].isin(bel_acc), "Unidades"].sum() / s_fin * 100
    pct_venta = v.loc[v["DEPARTAMENTO"].isin(bel_acc), "Total_Factura"].sum() / v["Total_Factura"].sum() * 100
    h = "9.3"
    return {
        "stock_ini": fila(h, "Stock dic-2023 (uds)", 7089, s_ini, "num", "ΣInventario.Unidades, Fecha = 2023-12-31"),
        "stock_fin": fila(h, "Stock abr-2026 (uds)", 15452, s_fin, "num", "ΣInventario.Unidades, Fecha = 2026-04-30"),
        "stock_var": fila(h, "Variación stock dic-23 → abr-26 (%)", 118, var(s_fin, s_ini), "pct",
                          "stock abr-26 / stock dic-23 − 1"),
        "sin_venta": fila(h, "% unidades en stock sin venta 12M (abr-2026)", 46, sin_venta / s_fin * 100, "pct",
                          "Σuds stock abr-26 de SKU sin línea de venta may-25..abr-26 / stock abr-26"),
        "sobrestock": fila(h, "Marcas con >12 meses de cobertura", 38, reorden["sobrestock"], "num",
                           "marcas con demanda 6M > 0 y stock abr-26 > 12 × demanda (ver 4.4)"),
        "con_demanda": fila(h, "Marcas con venta (demanda 6M > 0)", 88, reorden["con_demanda"], "num",
                            "marcas con Σuds sell out nov-25..abr-26 > 0"),
        "bel_acc_stock": fila(h, "Belleza + Accesorios, % del stock (abr-2026)", 25, pct_stock, "pct",
                              "Σuds stock abr-26 BELLEZA+ACCESORIOS / stock abr-26"),
        "bel_acc_venta": fila(h, "Belleza + Accesorios, % de la venta (< 3 %)", 3, pct_venta, "menor",
                              "ΣTotal_Factura BELLEZA+ACCESORIOS / total, todo el periodo (ene–abr 2026 daría 3,42); coincide si < 3"),
    }


# ---------------------------------------------------------------- 4.4

def lead_time_dias(c):
    """Promedio por línea de días factura → recepción (sin factura nula ni recepción anterior a factura)."""
    ok = c[c["Fecha_Invoice"].notna() & (c["Fecha_Recepcion"] >= c["Fecha_Invoice"])]
    return (ok["Fecha_Recepcion"] - ok["Fecha_Invoice"]).dt.days.mean(), ok


def punto_reorden(d, corte=CORTE):
    """Punto de reorden por marca y total (03_powerbi/MODELO.md, sección 4)."""
    v, c, inv = d["v"], d["c"], d["inv"]
    meses = pd.period_range(end=corte.to_period("M"), periods=6, freq="M")
    v6 = v[v["Fecha"].dt.to_period("M").isin(meses)]
    mens = (v6.groupby(["CODIGO_INTERNO_MARCA", v6["Fecha"].dt.to_period("M")])["Cantidad"].sum()
              .unstack(fill_value=0).reindex(columns=meses, fill_value=0))
    lt_gen, ok = lead_time_dias(c)
    lt_marca = (ok["Fecha_Recepcion"] - ok["Fecha_Invoice"]).dt.days.groupby(ok["CODIGO_INTERNO_MARCA"]).mean()
    stock = inv[inv["Fecha"] == corte].groupby("CODIGO_INTERNO_MARCA")["Unidades"].sum()
    marcas = mens.index.union(stock.index)
    m = pd.DataFrame(index=marcas)
    m["dem"] = mens.sum(axis=1).reindex(marcas, fill_value=0) / 6
    m["sigma"] = mens.std(axis=1, ddof=0).reindex(marcas, fill_value=0)
    m["lt"] = lt_marca.reindex(marcas).fillna(lt_gen) / 30
    m["stock"] = stock.reindex(marcas, fill_value=0)
    m["rop"] = m["dem"] * m["lt"] + Z * m["sigma"] * np.sqrt(m["lt"])
    m["max"] = m["rop"] + m["dem"]
    con_dem = m["dem"] > 0
    reponer = con_dem & (m["stock"] <= m["rop"])
    # total: se calcula al nivel total, no sumando marcas
    tot = mens.sum(axis=0)
    rop_total = tot.mean() * lt_gen / 30 + Z * tot.std(ddof=0) * np.sqrt(lt_gen / 30)
    return {"tabla": m, "con_demanda": int(con_dem.sum()), "reponer": int(reponer.sum()),
            "sobrestock": int((con_dem & (m["stock"] > 12 * m["dem"])).sum()),
            "compra": float((m.loc[reponer, "max"] - m.loc[reponer, "stock"]).clip(lower=0).sum()),
            "rop_total": rop_total, "lt_dias": lt_gen, "dem_total": tot.mean()}


def h44_reorden(d, r):
    v, c = d["v"], d["c"]
    venta = v.groupby("CODIGO_INTERNO_MARCA")["Total_Factura"].sum().sort_values(ascending=False)
    acum = venta.cumsum() / venta.sum()
    n80 = int((acum < 0.8).sum()) + 1
    mk = "MARC0004"
    # sell-through de la marca en el periodo con compras (ene-2024 a abr-2026)
    v_p = v[(v["Fecha"] >= "2024-01-01") & (v["Fecha"] <= CORTE)]
    st_mk = sell_through(v_p[v_p["CODIGO_INTERNO_MARCA"] == mk], c[c["CODIGO_INTERNO_MARCA"] == mk])
    h = "9.4"
    return {
        "lt": fila(h, "Lead time (días)", 32, r["lt_dias"], "num",
                   "media por línea de (Fecha_Recepcion − Fecha_Invoice), Invoice no nula y recepción ≥ factura, compras_validas"),
        "reponer": fila(h, "Marcas a reponer (abr-2026)", 7, r["reponer"], "num",
                        "dem>0 y stock≤ROP; dem=uds nov-25..abr-26/6; ROP=dem·LT+1,65·σ·√LT (por marca)"),
        "compra": fila(h, "Compra sugerida (uds)", 308, r["compra"], "num",
                       "Σ max(0, ROP+dem − stock) de las marcas a reponer"),
        "rop_total": fila(h, "Punto de reorden total (uds, control)", 3615, r["rop_total"], "num",
                          "ROP al nivel total: dem total·LT general + 1,65·σ total·√LT"),
        "n80": fila(h, "Marcas que hacen el 80 % de la venta", 15, n80, "num",
                    "marcas ordenadas por ΣTotal_Factura desc (todo el periodo); nº hasta acumular 80 %"),
        "n_marcas": fila(h, "Total de marcas", 141, d["n_marcas"], "num", "filas de la tabla Marca"),
        "mk_peso": fila(h, f"{mk}, % de la venta", 8,
                        venta.get(mk, 0) / venta.sum() * 100, "pct", f"ΣTotal_Factura {mk} / total, todo el periodo"),
        "mk_st": fila(h, f"{mk}, sell-through uds", 1.27, st_mk, "abs",
                      f"Σuds venta / Σuds compras_validas de {mk}, ene-2024..abr-2026; tol ±0,005", 0.005),
    }


# ---------------------------------------------------------------- 4.5

def rolling_forecast(v, crecimiento=1.20, corte=CORTE):
    """Budget, forecast y Rolling Forecast de ventas 2026 (03_powerbi/MODELO.md, sección 4)."""
    budget = anio(v, 2025)["Total_Factura"].sum() * crecimiento
    real = v[(v["Fecha"].dt.year == 2026) & (v["Fecha"] <= corte)]["Total_Factura"].sum()
    v24_25 = v[v["Fecha"].dt.year.isin([2024, 2025])]
    uds_mes = v24_25.groupby(v24_25["Fecha"].dt.month)["Cantidad"].sum()
    estac = uds_mes / (uds_mes.sum() / 12)
    imp_mes = v24_25.groupby(v24_25["Fecha"].dt.month)["Total_Factura"].sum()
    estac_imp = imp_mes / (imp_mes.sum() / 12)
    v12 = v[(v["Fecha"] > corte - pd.DateOffset(months=12)) & (v["Fecha"] <= corte)]
    pieza = v12["Cantidad"].sum() / 12
    precio = precio_pieza(v12)
    meses_fc = range(corte.month + 1, 13)
    fc_uds = sum(pieza * estac[m] for m in meses_fc)
    rolling = real + fc_uds * precio
    return {"budget": budget, "real": real, "pieza": pieza, "precio": precio, "estac": estac, "estac_imp": estac_imp,
            "fc_uds": fc_uds, "rolling": rolling, "var_budget": var(rolling, budget),
            "var_2025": var(rolling, budget / crecimiento)}


def h45_budget(d, rf):
    h = "9.5"
    return {
        "var_budget": fila(h, "Rolling Forecast 2026 vs Budget (%)", -22.5, rf["var_budget"], "pct",
                           "rolling = venta real ene–abr 26 + uds forecast may–dic × precio 12M; budget = venta 2025 × 1,20"),
        "budget": fila(h, "Budget 2026 (control)", 24101761, rf["budget"], "num", "ΣTotal_Factura 2025 × 1,20"),
        "rolling": fila(h, "Rolling Forecast 2026 (control)", 18687201, rf["rolling"], "num",
                        "real ene–abr + Σ(pieza 12M × estacionalidad uds) may–dic × precio 12M"),
        "var_2025": fila(h, "Rolling Forecast 2026 vs venta 2025 (%)", -7, rf["var_2025"], "pct",
                         "rolling 2026 / ΣTotal_Factura 2025 − 1"),
        "dic": fila(h, "Diciembre vs mes medio, en unidades (veces)", 2.5, rf["estac"][12], "abs",
                    "estacionalidad uds dic = uds dic 24+25 / (uds 24+25 / 12); tol ±0,05", 0.05),
        "dic_imp": fila(h, "Diciembre vs mes medio, en importe (veces)", 3, rf["estac_imp"][12], "abs",
                        "Estacionalidad Ventas dic = importe dic 24+25 / (importe 24+25 / 12); tol ±0,5", 0.5),
    }


# ---------------------------------------------------------------- 4.6

def h46_concentracion(d):
    v = d["v"]
    v = v[(v["Fecha"].dt.year >= 2023) & (v["Fecha"].dt.year <= 2026)]
    alm = v.loc[v["COD_ALMACEN"] == "Almacén 1", "Total_Factura"].sum() / v["Total_Factura"].sum() * 100
    cli = v.groupby("COD_CLIENTE")["Total_Factura"].sum().sort_values(ascending=False)
    acum = cli.cumsum() / cli.sum()
    n50 = int((acum < 0.5).sum()) + 1
    h = "9.6"
    return {
        "alm1": fila(h, "Almacén 1, % de la venta", 89, alm, "pct", "ΣTotal_Factura Almacén 1 / total, 2023–2026"),
        "n50": fila(h, "Clientes que hacen el 50 % de la venta", 78, n50, "num",
                    "clientes ordenados por ΣTotal_Factura desc (todo el periodo); nº hasta acumular ≥ 50 % (los 77 primeros suman 49,88 %)"),
        "n_cli": fila(h, "Total de clientes", 13090, d["n_clientes"], "num", "filas de la tabla Cliente"),
        "top1": fila(h, "Primer cliente, % de la venta", 7.6, cli.iloc[0] / cli.sum() * 100, "pct",
                     "ΣTotal_Factura del primer cliente / total, todo el periodo"),
    }


# ---------------------------------------------------------------- 4.7

def factor_2026(c):
    c26 = anio(c, 2026, "Fecha_Recepcion")
    mar = c26[c26["Fecha_Recepcion"].dt.month == 3]
    f = lambda x: x["Total_Precio_Costo_Nacionalizado"].sum() / x["Total_Costo_Ex_Works"].sum()
    return f(c26), f(mar)


def h47_calidad(d):
    c, ct, inv = d["c"], d["c_todas"], d["inv"]
    sc = lambda x: x["Tipo_Movi"] == "Sin clasificar"
    pct_val = c.loc[sc(c), "Total_Precio_Costo_Nacionalizado"].sum() / c["Total_Precio_Costo_Nacionalizado"].sum() * 100
    pct_tod = ct.loc[sc(ct), "Total_Precio_Costo_Nacionalizado"].sum() / ct["Total_Precio_Costo_Nacionalizado"].sum() * 100
    f_mal, m_mal = factor_2026(ct)
    f_ok, _ = factor_2026(c)
    h = "9.7"
    return {
        "sin_stock": fila(h, "Casos (SKU, mes) con venta sin stock", 463,
                          int((inv["Venta_Sin_Stock"] == "Sí").sum()), "num", "filas de Inventario con Venta_Sin_Stock = 'Sí'"),
        "errores": fila(h, "Devoluciones duplicadas con costo erróneo", 6, len(ct) - len(c), "num",
                        "filas de Compras con Es_Posible_Duplicado='Sí' y Precio_Cero='Sí'"),
        "factor_mal": fila(h, "Factor importación 2026 con errores", 1.88, f_mal, "abs",
                           "ΣNacionalizado / ΣEx-Work 2026, todas las compras; tol ±0,005", 0.005),
        "factor_mar": fila(h, "Factor importación mar-2026 con errores", -9.88, m_mal, "abs",
                           "ΣNacionalizado / ΣEx-Work mar-2026, todas las compras; tol ±0,005", 0.005),
        "factor_ok": fila(h, "Factor importación 2026 sin errores", 1.27, f_ok, "abs",
                          "ΣNacionalizado / ΣEx-Work 2026, compras_validas; tol ±0,005", 0.005),
        "sin_clasif": fila(h, "Compras 'Sin clasificar' (líneas)", 1384, int(sc(c).sum()), "num",
                           "filas de compras_validas con Tipo_Movi = 'Sin clasificar' (igual con todas las compras)"),
        "sin_clasif_pct": fila(h, "Compras 'Sin clasificar', % del Sell In", 8.4, pct_val, "pct",
                               f"ΣNacionalizado 'Sin clasificar' / ΣNacionalizado, compras_validas (con todas: {pct_tod:.2f} %)".replace(".", ",")),
    }


# ---------------------------------------------------------------- salida

def fmt(x):
    """Número con formato español: miles con punto y decimales con coma."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    if float(x).is_integer() or abs(x) >= 1000:
        s = f"{x:,.0f}"
    else:
        s = f"{x:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def calcular():
    d = preparar()
    r = punto_reorden(d)
    rf = rolling_forecast(d["v"])
    filas = {}
    for bloque in (h41_compras_vs_ventas(d), h42_precio_vs_volumen(d), h43_inventario(d, r),
                   h44_reorden(d, r), h45_budget(d, rf), h46_concentracion(d), h47_calidad(d)):
        filas.update(bloque)
    for f in filas.values():
        f["ok"] = coincide(f)
    return filas


def escribir_md(filas, ruta=SALIDA):
    ok = sum(f["ok"] for f in filas.values())
    lineas = [
        "# Hallazgos del README: recálculo desde el Excel",
        "",
        "Generado por `scripts/hallazgos.py` a partir de `03_powerbi/retail_bi_powerbi.xlsx`.",
        "Tolerancia: ±0,5 puntos para porcentajes, ±1 % relativo para importes, unidades y conteos;",
        "para ratios (veces, sell-through, factor) se indica en la definición.",
        "",
        f"**{ok} de {len(filas)} cifras coinciden.**",
        "",
        "| Hallazgo | Cifra | Valor en README | Valor recalculado | ¿Coincide? | Definición usada |",
        "|---|---|---:|---:|---|---|",
    ]
    for f in filas.values():
        readme = "> 0" if f["tipo"] == "mayor0" else ("< " + fmt(f["readme"]) if f["tipo"] == "menor" else fmt(f["readme"]))
        lineas.append(f"| {f['hallazgo']} | {f['cifra']} | {readme} | {fmt(f['valor'])} | "
                      f"{'Sí' if f['ok'] else 'No coincide'} | {f['definicion']} |")
    lineas += ["", "No se recalcula aquí: «el kardex puro subestima el inventario real en un 22 % a 6 meses» "
               "(4.7), que sale del backtest de `scripts/reconstruir_inventario.py` con las fotos reales de 2025.", ""]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(lineas), encoding="utf-8")


def main():
    filas = calcular()
    escribir_md(filas)
    for f in filas.values():
        print(f"{'OK ' if f['ok'] else 'NO '} {f['hallazgo']}  {f['cifra']:<55} README {fmt(f['readme']):>12}  "
              f"recalculado {fmt(f['valor']):>12}")
    ok = sum(f["ok"] for f in filas.values())
    print(f"\n{ok} de {len(filas)} coinciden. Tabla en {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
