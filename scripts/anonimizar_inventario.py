"""Anonimiza los archivos de inventario para el modelo de Power BI.

Corre en local. Lee los archivos reales y los mapeos de 01_mapeos, y escribe
en 02_anonimizado/ solo códigos anonimizados, fechas y unidades. No escribe
nombres, descripciones ni importes.

Uso (desde la raíz del repo):
    python scripts/anonimizar_inventario.py \
        --inventario "00_original/Inventario Final 2024-2025. 1.xlsx" \
        --resumen "00_original/RESUMEN INVETARIOS HASTA EL 25.xlsx"

Si 01_mapeos no tiene la tabla código real -> SKU, la reconstruye alineando
fila a fila las bases originales de ventas y compras con la base anonimizada
(--ventas-original y --compras-original) y la guarda en 01_mapeos/.

Salidas:
    02_anonimizado/inventario_sku_mes.csv    COD_SKU, Fecha, Unidades
    02_anonimizado/inventario_marca_mes.csv  COD_MARCA, Anio, Mes, Unidades
    trabajo/sin_mapeo_*.csv                  lo que no se pudo mapear (local, no se sube)
"""
import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def norm_txt(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def norm_cod(v):
    """Código como texto comparable: sin espacios, mayúsculas y sin '.0' de Excel."""
    if pd.isna(v):
        return None
    s = str(v).strip().upper()
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return s or None


def col(df, *nombres):
    """Busca una columna por nombre, sin importar mayúsculas ni acentos."""
    mapa = {norm_txt(c): c for c in df.columns}
    for n in nombres:
        if norm_txt(n) in mapa:
            return mapa[norm_txt(n)]
    raise KeyError(f"No encuentro la columna {nombres}. Columnas: {list(df.columns)}")


def leer_hojas(carpeta):
    ruta = Path(carpeta)
    for f in ([ruta] if ruta.is_file() else sorted(ruta.rglob("*"))):
        if f.name.startswith("~$"):
            continue
        if f.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
            for hoja, df in pd.read_excel(f, sheet_name=None, dtype=str).items():
                yield f"{f.name} / {hoja}", df
        elif f.suffix.lower() == ".csv":
            yield f.name, pd.read_csv(f, dtype=str)


def detectar_mapeo(carpetas, patron, objetivo, normalizar):
    """Busca en los archivos de mapeo todas las columnas de códigos anonimizados
    (patron) y las columnas reales que coinciden con 'objetivo', y las une.
    Si un código real aparece con varios anonimizados, se queda el más frecuente."""
    partes = []
    for carpeta in carpetas:
        if not Path(carpeta).exists():
            continue
        for origen, df in leer_hojas(carpeta):
            df = df.dropna(how="all")
            if df.empty:
                continue
            cods = [c for c in df.columns
                    if df[c].dropna().astype(str).str.strip().str.fullmatch(patron).mean() > 0.8]
            for cc in cods:
                anon = df[cc].astype(str).str.strip().str.upper()
                for cr in df.columns:
                    if cr in cods or df[cr].nunique() < 0.3 * anon.nunique():
                        continue
                    d = pd.DataFrame({"real": df[cr].map(normalizar), "anon": anon}).dropna()
                    d = d[d["anon"].str.fullmatch(patron) & d["real"].isin(objetivo)]
                    tasa = d["real"].nunique() / len(objetivo)
                    if tasa >= 0.01:
                        print(f"  Mapeo: {origen} | '{cr}' -> '{cc}' | cubre {tasa:.1%}")
                        partes.append(d)
    if not partes:
        print(f"  No hay en {', '.join(map(str, carpetas))} un mapeo con códigos {patron}.")
        return None
    d = (pd.concat(partes).groupby(["real", "anon"]).size().reset_index(name="n")
           .sort_values("n", ascending=False).drop_duplicates("real"))
    print(f"  Mapeo combinado: cubre {len(d) / len(objetivo):.1%} de los códigos")
    return dict(zip(d["real"], d["anon"]))


ANON = RAIZ / "02_anonimizado" / "retail_bi_anonimizado.xlsx"
MAPEOS = RAIZ / "01_mapeos"  # aquí se guardan los mapeos encontrados o reconstruidos


def alinear(ruta_orig, hoja_anon, objetivo):
    """Reconstruye código real -> SKU alineando fila a fila la base original con
    la anonimizada (mismo orden de filas). Devuelve (mapa, puntaje) o (None, 0)."""
    a = pd.read_excel(ANON, sheet_name=hoja_anon, usecols=["COD_SKU", "Cantidad"])
    a = a.dropna(how="all").reset_index(drop=True)
    hojas = pd.read_excel(ruta_orig, sheet_name=None, dtype=str)
    nombre, o = min(hojas.items(), key=lambda kv: abs(len(kv[1].dropna(how="all")) - len(a)))
    o = o.dropna(how="all").reset_index(drop=True)
    print(f"  {Path(ruta_orig).name} / {nombre}: {len(o):,} filas | anonimizada {hoja_anon}: {len(a):,} filas")
    if len(o) != len(a):
        print("  Las filas no coinciden: no se puede alinear por orden.")
        return None, 0
    cant = pd.to_numeric(a["Cantidad"], errors="coerce")
    orden = max((pd.to_numeric(o[c].str.replace(",", "."), errors="coerce") == cant).mean()
                for c in o.columns)
    print(f"  Orden verificado con Cantidad: {orden:.1%} de filas iguales")
    if orden < 0.95:
        return None, 0
    mejor = (None, 0, 0)
    for c in o.columns:
        d = pd.DataFrame({"real": o[c].map(norm_cod), "sku": a["COD_SKU"]}).dropna()
        if d.empty or d["real"].nunique() < 0.5 * d["sku"].nunique():
            continue
        par = d.groupby(["real", "sku"]).size()
        ida = par.groupby(level=0).max().sum() / len(d)      # real -> un solo SKU
        vuelta = par.groupby(level=1).max().sum() / len(d)   # SKU -> un solo real
        cruce = len(objetivo & set(d["real"])) / len(objetivo)
        if min(ida, vuelta) > 0.98 and cruce > mejor[2]:
            mejor = (c, min(ida, vuelta), cruce)
    if mejor[0] is None:
        print("  No encontré una columna de código consistente.")
        return None, 0
    c, puntaje, cruce = mejor
    print(f"  Columna de código: '{c}' | consistencia {puntaje:.1%} | cubre {cruce:.1%} del inventario")
    d = pd.DataFrame({"real": o[c].map(norm_cod), "COD_SKU": a["COD_SKU"]}).dropna()
    d = d.groupby(["real", "COD_SKU"]).size().reset_index(name="n")
    d = d.sort_values("n", ascending=False).drop_duplicates("real")
    return dict(zip(d["real"], d["COD_SKU"])), puntaje


def reconstruir_mapeo_sku(ventas, compras, objetivo):
    print("  Reconstruyendo el mapeo desde las bases originales")
    mapa = {}
    for ruta, hoja in [(compras, "Compras24_26"), (ventas, "Ventas23_26")]:
        if ruta:
            m, _ = alinear(ruta, hoja, objetivo)
            for k, v in (m or {}).items():
                mapa.setdefault(k, v)
    if not mapa:
        raise SystemExit("No pude reconstruir el mapeo. Pégame la salida para revisarlo.")
    return mapa


def guardar_mapeo_sku(mapa):
    MAPEOS.mkdir(exist_ok=True)
    pd.DataFrame({"codigo_real": list(mapa), "COD_SKU": list(mapa.values())}).to_csv(
        MAPEOS / "mapeo_sku.csv", index=False)
    print(f"  Guardado 01_mapeos/mapeo_sku.csv: {len(mapa):,} códigos (local, no se sube)")


def guardar_mapeo_marca(df, c_marca):
    """Deriva marca real -> MARC usando el SKU ya mapeado y el maestro anonimizado."""
    m = pd.read_excel(ANON, sheet_name="MAESTRO_SKU", usecols=["COD_SKU", "CODIGO_INTERNO_MARCA"])
    d = (df[["COD_SKU", c_marca]].dropna().merge(m, on="COD_SKU")
           .assign(real=lambda x: x[c_marca].map(norm_txt))
           .groupby(["real", "CODIGO_INTERNO_MARCA"]).size().reset_index(name="n")
           .sort_values("n", ascending=False).drop_duplicates("real"))
    d[["real", "CODIGO_INTERNO_MARCA"]].rename(columns={"real": "marca_real"}).to_csv(
        MAPEOS / "mapeo_marca.csv", index=False)
    print(f"  Guardado 01_mapeos/mapeo_marca.csv: {len(d)} marcas (local, no se sube)")


def forma(v):
    """Patrón del valor sin el dato: dígitos -> 9, letras -> A (ej. SKU00012 -> AAA99999)."""
    return re.sub(r"[^\W\d_]", "A", re.sub(r"\d", "9", str(v)))[:20]


def diagnostico(carpeta):
    """Muestra la estructura de 01_mapeos sin mostrar datos reales."""
    print(f"Carpeta: {carpeta}")
    ruta = Path(carpeta)
    archivos = [ruta] if ruta.is_file() else [f for f in sorted(ruta.rglob("*")) if f.is_file()]
    print(f"  Archivos: {len(archivos)} ({', '.join(sorted({f.suffix.lower() for f in archivos}))})")
    for origen, df in leer_hojas(carpeta):
        print(f"  {origen}: {len(df):,} filas")
        for c in df.columns:
            v = df[c].dropna()
            print(f"    - {c}: {forma(v.iloc[0]) if len(v) else '(vacía)'}")


def inventario_sku(ruta, mapeos, salida, trabajo, ventas=None, compras=None):
    print("Inventario por SKU")
    df = pd.read_excel(ruta, sheet_name="inventarios")
    c_cod = col(df, "Código", "Codigo")
    c_qty = col(df, "inventario final")
    c_fec = col(df, "fecha")
    df["real"] = df[c_cod].map(norm_cod)
    try:
        df["ref"] = df[col(df, "Ref. Prov", "Ref Prov", "Referencia Proveedor")].map(norm_cod)
    except KeyError:
        df["ref"] = None
    objetivo = set(df["real"].dropna()) | set(df["ref"].dropna())
    mapa = detectar_mapeo(mapeos, r"SKU\d+", objetivo, norm_cod)
    if mapa is None:
        if not (ventas or compras):
            raise SystemExit("Pasa --ventas-original y --compras-original para reconstruir el mapeo.")
        mapa = reconstruir_mapeo_sku(ventas, compras, objetivo)
    guardar_mapeo_sku(mapa)
    df["COD_SKU"] = df["real"].map(mapa)
    por_cod = df["COD_SKU"].notna().sum()
    df["COD_SKU"] = df["COD_SKU"].fillna(df["ref"].map(mapa))
    print(f"  Filas cruzadas por Código: {por_cod:,} | por Ref. Prov: {df['COD_SKU'].notna().sum() - por_cod:,}")
    guardar_mapeo_marca(df, col(df, "Marca"))
    sin = df[df["COD_SKU"].isna()]
    out = (df.dropna(subset=["COD_SKU"])
             .assign(Fecha=lambda d: pd.to_datetime(d[c_fec]) + pd.offsets.MonthEnd(0),
                     Unidades=lambda d: pd.to_numeric(d[c_qty], errors="coerce").fillna(0))
             .groupby(["COD_SKU", "Fecha"], as_index=False)["Unidades"].sum())
    out.to_csv(salida / "inventario_sku_mes.csv", index=False, date_format="%Y-%m-%d")
    sin[["real"]].drop_duplicates().to_csv(trabajo / "sin_mapeo_sku.csv", index=False)
    print(f"  Filas: {len(df):,} | sin mapeo: {len(sin):,} ({sin['real'].nunique():,} SKU)")
    print(f"  Salida: {len(out):,} filas, {out['COD_SKU'].nunique():,} SKU, "
          f"{out['Fecha'].nunique()} cierres de mes ({out['Fecha'].min():%Y-%m} a {out['Fecha'].max():%Y-%m})")


def inventario_marca(ruta, mapeos, salida, trabajo):
    print("Inventario por marca (resumen)")
    df = pd.read_excel(ruta, sheet_name="Inventario (valores) (2)", header=2)
    c_mar, c_anio, c_con = col(df, "Marca"), col(df, "Año", "Ano"), col(df, "Concepto")
    meses = list(df.columns[list(df.columns).index(c_con) + 1:][:12])  # bloque 1: piezas
    df = df[df[c_con].astype(str).str.contains("final", case=False)].copy()
    df["real"] = df[c_mar].map(norm_txt)
    mapa = detectar_mapeo([MAPEOS], r"MARC\d+", set(df["real"].dropna()), norm_txt) or {}
    df["COD_MARCA"] = df["real"].map(mapa)
    sin = df[df["COD_MARCA"].isna()]
    largo = (df.dropna(subset=["COD_MARCA"])
               .melt(id_vars=["COD_MARCA", c_anio], value_vars=meses, var_name="col", value_name="Unidades")
               .assign(Mes=lambda d: d["col"].map({c: i + 1 for i, c in enumerate(meses)}),
                       Unidades=lambda d: pd.to_numeric(d["Unidades"], errors="coerce").fillna(0))
               .rename(columns={c_anio: "Anio"})
               .groupby(["COD_MARCA", "Anio", "Mes"], as_index=False)["Unidades"].sum())
    largo.to_csv(salida / "inventario_marca_mes.csv", index=False)
    sin[["real"]].drop_duplicates().to_csv(trabajo / "sin_mapeo_marca.csv", index=False)
    print(f"  Marcas: {df['real'].nunique()} | sin mapeo: {sin['real'].nunique()}")
    print(f"  Salida: {len(largo):,} filas, {largo['COD_MARCA'].nunique()} marcas")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--inventario")
    p.add_argument("--resumen")
    p.add_argument("--mapeos", nargs="+", default=[RAIZ / "01_mapeos"],
                   help="carpetas o archivos con los mapeos (por defecto 01_mapeos)")
    p.add_argument("--ventas-original", help="base original de ventas (para reconstruir el mapeo)")
    p.add_argument("--compras-original", help="base original de compras (para reconstruir el mapeo)")
    p.add_argument("--diagnostico", action="store_true",
                   help="muestra la estructura de 01_mapeos (sin datos) y termina")
    a = p.parse_args()
    if a.diagnostico:
        for m in a.mapeos:
            diagnostico(m)
        return
    if not a.inventario:
        p.error("falta --inventario")
    salida, trabajo = RAIZ / "02_anonimizado", RAIZ / "trabajo"
    trabajo.mkdir(exist_ok=True)
    inventario_sku(a.inventario, a.mapeos, salida, trabajo, a.ventas_original, a.compras_original)
    if a.resumen:
        inventario_marca(a.resumen, a.mapeos, salida, trabajo)
    print("Listo. Revisa trabajo/sin_mapeo_*.csv si hay códigos sin mapear (no se suben).")


if __name__ == "__main__":
    main()
