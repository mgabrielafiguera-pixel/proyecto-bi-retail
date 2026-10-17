"""Controles de calidad del Excel que lee Power BI (03_powerbi/retail_bi_powerbi.xlsx).

Cada control devuelve: registros evaluados, registros afectados, resultado y acción.
Resultados posibles:
    OK          el control se cumple
    Aviso       hay casos, pero son legítimos o están tratados en el modelo (se documentan)
    Revisar     hay casos que pueden ser errores y no están corregidos
    Error       el modelo daría cifras incorrectas; se debe corregir antes de publicar

Uso: python3 scripts/validar_modelo.py
Salidas:
    docs/resultados/controles_calidad.csv
    docs/resultados/controles_calidad.md
El script termina con código 1 si algún control da Error.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datos import RAIZ, cargar_tablas, compras_validas  # noqa: E402

SALIDA = RAIZ / "docs" / "resultados"

# Filas esperadas por tabla (ESTADO_PROYECTO.md, 16-oct-2026)
FILAS = {"Ventas": 49_936, "Compras": 16_721, "Producto": 17_721, "Cliente": 13_090,
         "Proveedor": 165, "Marca": 141, "Vendedor": 89, "Almacen": 13,
         "Departamento": 12, "Calendario": 1_461, "Inventario": 144_350}

CLAVES = {"Producto": "COD_SKU", "Cliente": "COD_CLIENTE", "Proveedor": "CODIGO_INTERNO_PROVEEDOR",
          "Marca": "CODIGO_INTERNO_MARCA", "Vendedor": "COD_VENDEDOR", "Almacen": "COD_ALMACEN",
          "Departamento": "COD_DEPARTAMENTO", "Calendario": "Fecha"}

# (tabla de hechos, columna, dimensión) para las relaciones del modelo
RELACIONES = [("Ventas", "COD_SKU", "Producto"), ("Ventas", "COD_ALMACEN", "Almacen"),
              ("Ventas", "COD_CLIENTE", "Cliente"), ("Ventas", "COD_VENDEDOR", "Vendedor"),
              ("Ventas", "CODIGO_INTERNO_PROVEEDOR", "Proveedor"),
              ("Compras", "COD_SKU", "Producto"), ("Compras", "COD_ALMACEN", "Almacen"),
              ("Compras", "CODIGO_INTERNO_PROVEEDOR", "Proveedor"),
              ("Producto", "CODIGO_INTERNO_MARCA", "Marca"),
              ("Producto", "COD_DEPARTAMENTO", "Departamento"),
              ("Inventario", "COD_SKU", "Producto")]

CRITICOS = {"Ventas": ["COD_SKU", "Cantidad", "Total_Factura", "Fecha", "COD_ALMACEN", "Mov"],
            "Compras": ["COD_SKU", "Cantidad", "Fecha_Recepcion", "Total_Costo_Ex_Works",
                        "Total_Precio_Costo_Nacionalizado"],
            "Inventario": ["COD_SKU", "Fecha", "Unidades"]}

# Totales de control de todo el periodo (ESTADO_PROYECTO.md). Sell In antes de excluir errores.
TOTALES = {"Unidades Sell Out": 48_052, "Importe Sell Out": 44_271_198,
           "Unidades Sell In": 44_990, "Importe Sell In": 23_649_381}
STOCK = {"2025-06-30": 11_715, "2025-12-31": 14_063, "2026-04-30": 15_452}


def control(nombre, tabla, evaluados, afectados, resultado, accion, tipo="Integridad"):
    return {"Tipo": tipo, "Control": nombre, "Tabla": tabla, "Evaluados": int(evaluados),
            "Afectados": int(afectados), "Resultado": resultado, "Acción": accion}


def si_no(afectados, ok="OK", mal="Error"):
    return ok if afectados == 0 else mal


def integridad(t):
    out = []
    for tabla, esperado in FILAS.items():
        n = len(t[tabla])
        out.append(control("Filas esperadas", tabla, n, abs(n - esperado), si_no(n - esperado),
                           f"Esperado {esperado:,}. Si cambia, actualizar ESTADO_PROYECTO.md"))
    for tabla, col in CLAVES.items():
        s = t[tabla][col]
        dup = s.duplicated().sum() + s.isna().sum()
        out.append(control(f"Clave única {col}", tabla, len(s), dup, si_no(dup),
                           "Una dimensión con claves repetidas duplica importes en Power BI"))
    for tabla, cols in CRITICOS.items():
        df = t[tabla]
        nulos = df[cols].isna().any(axis=1).sum()
        detalle = {c: int(df[c].isna().sum()) for c in cols if df[c].isna().any()}
        accion = "Sin nulos" if not detalle else f"Nulos por columna: {detalle}"
        res = "OK" if nulos == 0 else ("Aviso" if tabla == "Compras" and nulos <= 20 else "Revisar")
        out.append(control("Nulos en campos críticos", tabla, len(df), nulos, res, accion))
    for hecho, col, dim in RELACIONES:
        valores = t[hecho][col].dropna()
        huerf = (~valores.isin(set(t[dim][CLAVES[dim]]))).sum()
        out.append(control(f"Claves huérfanas {col} → {dim}", hecho, len(valores), huerf,
                           si_no(huerf), "Filas que no filtraría ninguna segmentación de la dimensión",
                           tipo="Consistencia"))
    return out


def fechas(t):
    out = []
    cal = t["Calendario"]["Fecha"]
    for tabla, col in [("Ventas", "Fecha"), ("Compras", "Fecha_Recepcion"), ("Inventario", "Fecha")]:
        f = t[tabla][col]
        fuera = (~f.isin(set(cal))).sum()
        out.append(control(f"{col} dentro de Calendario", tabla, len(f), fuera, si_no(fuera),
                           f"Rango {f.min():%d-%m-%Y} a {f.max():%d-%m-%Y}", tipo="Temporal"))
    f = t["Inventario"]["Fecha"]
    no_fin = (f != f + pd.offsets.MonthEnd(0)).sum()
    out.append(control("Fecha de inventario a fin de mes", "Inventario", len(f), no_fin, si_no(no_fin),
                       "Las medidas buscan el stock en EOMONTH", tipo="Temporal"))
    ult_inv = f.max()
    v = t["Ventas"]["Fecha"]
    tarde = (v > ult_inv).sum()
    out.append(control("Ventas después del último inventario", "Ventas", len(v), tarde, "Aviso",
                       f"Ventas posteriores al {ult_inv:%d-%m-%Y}. El forecast las excluye; "
                       "Resumen anual las incluye. Confirmar si son fechas reales", tipo="Temporal"))
    c = t["Compras"]
    sin_fact = c["Fecha_Invoice"].notna()
    lt = (c.loc[sin_fact, "Fecha_Recepcion"] - c.loc[sin_fact, "Fecha_Invoice"]).dt.days
    out.append(control("Recepción antes de la factura", "Compras", len(lt), (lt < 0).sum(), "Aviso",
                       "Se excluyen del lead time (la medida exige recepción ≥ factura)", tipo="Temporal"))
    out.append(control("Factura > 60 días antes de la recepción", "Compras", len(lt), (lt > 60).sum(),
                       "Revisar", "Alargan el lead time medio. Revisar la fecha de factura", tipo="Temporal"))
    out.append(control("Factura > 60 días después de la recepción", "Compras", len(lt), (lt < -60).sum(),
                       "Revisar", "Fecha de factura dudosa. No afecta: las compras se fechan por recepción",
                       tipo="Temporal"))
    return out


def importes(t):
    out = []
    v, c, inv = t["Ventas"], t["Compras"], t["Inventario"]
    dev = v["Cantidad"] < 0
    out.append(control("Cantidades negativas (devoluciones)", "Ventas", len(v), dev.sum(), "Aviso",
                       "Legítimas: restan venta. Marcadas con Es_Devolucion", tipo="Importes"))
    fact_neg = dev & (v["Mov"] == "FACT")
    out.append(control("Devolución registrada como factura (FACT negativa)", "Ventas", len(v),
                       fact_neg.sum(), "Revisar", "Bajan el ticket promedio; confirmar con el negocio",
                       tipo="Importes"))
    signo = dev & (v["Costo_Total_Facturado"] > 0)
    out.append(control("Costo con signo contrario en devoluciones", "Ventas", dev.sum(), signo.sum(),
                       "Aviso", "Corregido en la medida Costo Sell Out", tipo="Importes"))
    cero = v["Costo_Total_Facturado"].fillna(0).eq(0) & v["Cantidad"].ne(0)
    out.append(control("Venta con costo cero", "Ventas", len(v), cero.sum(), "Revisar",
                       "Margen 100 % en esas líneas: el margen total queda algo inflado", tipo="Importes"))
    for tabla, df in [("Ventas", v), ("Compras", c)]:
        for col in ["Es_Posible_Duplicado", "Precio_Cero", "Total_No_Cuadra"]:
            n = (df[col] == "Sí").sum()
            out.append(control(f"Marca {col}", tabla, len(df), n, "Aviso" if n else "OK",
                               "Marcado, no borrado. Ver MODELO.md, Calidad de datos", tipo="Importes"))
    excl = len(c) - len(compras_validas(c))
    out.append(control("Compras excluidas en Power Query", "Compras", len(c), excl,
                       "OK" if excl == 6 else "Error",
                       "Devoluciones duplicadas con costo erróneo (paso 'Excluir errores de captura')",
                       tipo="Importes"))
    sc = c["Tipo_Movi"] == "Sin clasificar"
    out.append(control("Compras sin tipo de movimiento", "Compras", len(c), sc.sum(), "Revisar",
                       "Incluidas en Sell In. Pendiente de clasificar en el origen", tipo="Importes"))
    neg = (inv["Unidades"] < 0).sum()
    out.append(control("Stock negativo", "Inventario", len(inv), neg, si_no(neg),
                       "Los negativos se llevan a 0 al reconstruir", tipo="Inventario"))
    dup = inv.duplicated(["COD_SKU", "Fecha"]).sum()
    out.append(control("Duplicados SKU + Fecha", "Inventario", len(inv), dup, si_no(dup),
                       "Duplicarían el stock", tipo="Inventario"))
    vss = (inv["Venta_Sin_Stock"] == "Sí").sum()
    out.append(control("Venta sin stock registrado (kardex negativo)", "Inventario", len(inv), vss,
                       "Aviso", "Recepciones no registradas en Compras (hallazgo 4.7)", tipo="Inventario"))
    return out


def consistencia(t):
    out = []
    p = t["Producto"].set_index("COD_SKU")
    for tabla in ["Ventas", "Compras"]:
        df = t[tabla]
        distinto = df["CODIGO_INTERNO_PROVEEDOR"].ne(df["COD_SKU"].map(p["CODIGO_INTERNO_PROVEEDOR"]))
        out.append(control(f"Proveedor de {tabla} = proveedor de Producto", tabla, len(df), distinto.sum(),
                           "Aviso" if distinto.sum() else "OK",
                           "Filtrar por Proveedor (relación con la tabla de hechos) y por Marca "
                           "(vía Producto) puede dar totales algo distintos", tipo="Consistencia"))
    sku_inv = set(t["Inventario"]["COD_SKU"])
    skui = t["Producto"]["COD_SKU"].str.startswith("SKUI")
    sin_dep = t["Producto"].loc[skui, "COD_DEPARTAMENTO"].isna().sum()
    out.append(control("SKU sin movimiento (SKUI) con departamento", "Producto", skui.sum(), sin_dep,
                       si_no(sin_dep), "Sin departamento quedan fuera de los filtros por departamento",
                       tipo="Consistencia"))
    sin_inv = (~t["Producto"].loc[skui, "COD_SKU"].isin(sku_inv)).sum()
    out.append(control("SKUI presentes en Inventario", "Producto", skui.sum(), sin_inv, si_no(sin_inv),
                       "Los SKUI solo existen para dar dimensión al stock", tipo="Consistencia"))
    return out


def confidencialidad(t):
    """Texto libre que podría identificar a la empresa. No imprime los valores."""
    a = t["Almacen"]
    cols = ["DIRECCION", "DIRECCION2", "ZONA_POSTAL", "CIUDAD", "ESTADO", "PAIS"]
    genericos = a[cols].apply(lambda s: s.isna() | s.astype(str).str.match(r"^(Ciudad|Estado|País) \d+$"))
    afectadas = (~genericos).any(axis=1).sum()
    return [control("Direcciones y ubicación de almacenes", "Almacen", len(a), afectadas,
                    "OK" if afectadas == 0 else "Revisar",
                    "Si son reales, correr scripts/generalizar_almacenes.py (requiere autorización)",
                    tipo="Confidencialidad")]


def totales(t):
    out = []
    v, c, inv = t["Ventas"], t["Compras"], t["Inventario"]
    calc = {"Unidades Sell Out": v["Cantidad"].sum(), "Importe Sell Out": v["Total_Factura"].sum(),
            "Unidades Sell In": c["Cantidad"].sum(),
            "Importe Sell In": c["Total_Precio_Costo_Nacionalizado"].sum()}
    for k, esperado in TOTALES.items():
        dif = abs(calc[k] - esperado) / esperado
        out.append(control(f"Total de control: {k}", "Ventas" if "Out" in k else "Compras", 1,
                           int(dif > 0.001), "OK" if dif <= 0.001 else "Error",
                           f"Excel {calc[k]:,.0f} vs Power BI {esperado:,}", tipo="Totales"))
    stock = inv.groupby("Fecha")["Unidades"].sum()
    for f, esperado in STOCK.items():
        real = stock.get(pd.Timestamp(f), 0)
        out.append(control(f"Stock total al {f}", "Inventario", 1, int(real != esperado),
                           si_no(real - esperado), f"Excel {real:,.0f} vs Power BI {esperado:,}",
                           tipo="Totales"))
    return out


def correr(t):
    filas = (integridad(t) + fechas(t) + importes(t) + consistencia(t) + confidencialidad(t)
             + totales(t))
    return pd.DataFrame(filas)


def escribir(res):
    SALIDA.mkdir(parents=True, exist_ok=True)
    res.to_csv(SALIDA / "controles_calidad.csv", index=False)
    cuenta = res["Resultado"].value_counts()
    lineas = ["# Controles de calidad de datos", "",
              "Generado por `scripts/validar_modelo.py` sobre `03_powerbi/retail_bi_powerbi.xlsx`.", "",
              "| Resultado | Controles |", "|---|---|"]
    lineas += [f"| {r} | {cuenta.get(r, 0)} |" for r in ["OK", "Aviso", "Revisar", "Error"]]
    lineas += ["", "**OK**: se cumple. **Aviso**: hay casos legítimos o ya tratados en el modelo. "
               "**Revisar**: posibles errores de origen sin corregir. **Error**: hay que corregir antes de publicar.",
               "", "| Tipo | Control | Tabla | Evaluados | Afectados | Resultado | Acción |",
               "|---|---|---|---:|---:|---|---|"]
    for r in res.to_dict("records"):
        lineas.append(f"| {r['Tipo']} | {r['Control']} | {r['Tabla']} | {r['Evaluados']:,} | "
                      f"{r['Afectados']:,} | {r['Resultado']} | {r['Acción']} |")
    (SALIDA / "controles_calidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    res = correr(cargar_tablas())
    escribir(res)
    print(res[["Control", "Tabla", "Afectados", "Resultado"]].to_string(index=False))
    print("\n", res["Resultado"].value_counts().to_dict())
    return 1 if (res["Resultado"] == "Error").any() else 0


if __name__ == "__main__":
    sys.exit(main())
