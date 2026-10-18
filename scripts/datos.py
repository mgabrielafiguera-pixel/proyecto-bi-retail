"""Carga compartida del Excel que lee Power BI (03_powerbi/retail_bi_powerbi.xlsx).

Leer las 11 hojas tarda unos 30 segundos. La primera lectura se guarda en
`.cache/tablas.pkl` y se reutiliza mientras el Excel no cambie (se compara la fecha
de modificación y el tamaño). La carpeta `.cache/` no se sube al repo.
"""
from pathlib import Path
import pickle

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
XLSX = RAIZ / "03_powerbi" / "retail_bi_powerbi.xlsx"
CACHE = RAIZ / ".cache" / "tablas.pkl"


def cargar_tablas(xlsx=XLSX, usar_cache=True):
    """Devuelve un dict {nombre de hoja: DataFrame} con todas las tablas del modelo."""
    xlsx = Path(xlsx)
    firma = (str(xlsx.resolve()), xlsx.stat().st_mtime_ns, xlsx.stat().st_size)
    if usar_cache and CACHE.exists():
        with open(CACHE, "rb") as f:
            guardado = pickle.load(f)
        if guardado.get("firma") == firma:
            return guardado["tablas"]
    tablas = pd.read_excel(xlsx, sheet_name=None)
    if usar_cache:
        CACHE.parent.mkdir(exist_ok=True)
        with open(CACHE, "wb") as f:
            pickle.dump({"firma": firma, "tablas": tablas}, f)
    return tablas


def compras_validas(compras):
    """Compras sin las 6 devoluciones duplicadas con costo erróneo.

    Es el mismo filtro que el paso "Excluir errores de captura" de Power Query
    (03_powerbi/MODELO.md, sección 4).
    """
    error = (compras["Es_Posible_Duplicado"] == "Sí") & (compras["Precio_Cero"] == "Sí")
    return compras[~error]


def costo_con_signo(ventas):
    """Costo de venta con el mismo signo que la cantidad (medida DAX `Costo Sell Out`)."""
    c = ventas["Costo_Total_Facturado"].abs()
    return c.where(ventas["Cantidad"] >= 0, -c)
