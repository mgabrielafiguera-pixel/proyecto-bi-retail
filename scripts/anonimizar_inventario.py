"""Anonimiza los archivos de inventario para el modelo de Power BI.

Corre en local. Lee los archivos reales y los mapeos de 01_mapeos, y escribe
en 02_anonimizado/ solo códigos anonimizados, fechas y unidades. No escribe
nombres, descripciones ni importes.

Uso (desde la raíz del repo):
    python scripts/anonimizar_inventario.py \
        --inventario "00_original/Inventario Final 2024-2025. 1.xlsx" \
        --resumen "00_original/RESUMEN INVETARIOS HASTA EL 25.xlsx"

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
    for f in sorted(Path(carpeta).rglob("*")):
        if f.name.startswith("~$"):
            continue
        if f.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
            for hoja, df in pd.read_excel(f, sheet_name=None, dtype=str).items():
                yield f"{f.name} / {hoja}", df
        elif f.suffix.lower() == ".csv":
            yield f.name, pd.read_csv(f, dtype=str)


def detectar_mapeo(carpeta, patron, objetivo, normalizar):
    """Encuentra en 01_mapeos la columna de códigos anonimizados (patron) y la
    columna real que más coincide con los valores de 'objetivo'."""
    mejor = None
    for origen, df in leer_hojas(carpeta):
        df = df.dropna(how="all")
        if df.empty:
            continue
        cods = [c for c in df.columns
                if df[c].dropna().astype(str).str.fullmatch(patron).mean() > 0.8]
        for cc in cods:
            for cr in df.columns:
                if cr == cc:
                    continue
                vals = set(df[cr].map(normalizar).dropna())
                tasa = len(objetivo & vals) / len(objetivo)
                if mejor is None or tasa > mejor[0]:
                    mejor = (tasa, origen, cr, cc, df)
    if mejor is None or mejor[0] == 0:
        raise SystemExit(f"No encontré en {carpeta} un mapeo con códigos {patron}.")
    tasa, origen, cr, cc, df = mejor
    print(f"  Mapeo: {origen} | real = '{cr}' -> anonimizado = '{cc}' | cubre {tasa:.1%}")
    m = df[[cr, cc]].dropna()
    m = m.assign(real=m[cr].map(normalizar)).drop_duplicates("real")
    return dict(zip(m["real"], m[cc].str.strip().str.upper()))


def inventario_sku(ruta, mapeos, salida, trabajo):
    print("Inventario por SKU")
    df = pd.read_excel(ruta, sheet_name="inventarios")
    c_cod = col(df, "Código", "Codigo")
    c_qty = col(df, "inventario final")
    c_fec = col(df, "fecha")
    df["real"] = df[c_cod].map(norm_cod)
    mapa = detectar_mapeo(mapeos, r"SKU\d+", set(df["real"].dropna()), norm_cod)
    df["COD_SKU"] = df["real"].map(mapa)
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
    mapa = detectar_mapeo(mapeos, r"MARC\d+", set(df["real"].dropna()), norm_txt)
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
    p.add_argument("--inventario", required=True)
    p.add_argument("--resumen")
    p.add_argument("--mapeos", default=RAIZ / "01_mapeos")
    a = p.parse_args()
    salida, trabajo = RAIZ / "02_anonimizado", RAIZ / "trabajo"
    trabajo.mkdir(exist_ok=True)
    inventario_sku(a.inventario, a.mapeos, salida, trabajo)
    if a.resumen:
        inventario_marca(a.resumen, a.mapeos, salida, trabajo)
    print("Listo. Revisa trabajo/sin_mapeo_*.csv si hay códigos sin mapear (no se suben).")


if __name__ == "__main__":
    main()
