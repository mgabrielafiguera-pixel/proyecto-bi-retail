"""Quita las direcciones de los almacenes de los Excel publicados.

Las columnas de dirección y zona postal se vacían, y ciudad, estado y país se cambian
por etiquetas genéricas ("Ciudad 1", "Estado 1", "País 1"). Se conservan las columnas,
así que las consultas de Power Query que las nombran siguen funcionando. La misma
ciudad recibe la misma etiqueta en los dos archivos.

El script no imprime los valores originales. Es idempotente: si ya se aplicó, no cambia nada.

Uso: python3 scripts/generalizar_almacenes.py
"""
from pathlib import Path

from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVOS = [(RAIZ / "03_powerbi" / "retail_bi_powerbi.xlsx", "Almacen"),
            (RAIZ / "02_anonimizado" / "retail_bi_anonimizado.xlsx", "BASE DATOS ALMACENES")]
VACIAR = ["DIRECCION", "DIRECCION2", "ZONA_POSTAL"]
ETIQUETAR = {"CIUDAD": "Ciudad", "ESTADO": "Estado", "PAIS": "País"}


def es_generico(valor, prefijo):
    return valor is None or str(valor).startswith(prefijo + " ")


def generalizar(ws, etiquetas):
    """Cambia la hoja en el sitio. Devuelve el número de celdas modificadas."""
    cab = {c.value: c.column for c in ws[1]}
    cambios = 0
    for fila in ws.iter_rows(min_row=2):
        for col in VACIAR:
            celda = fila[cab[col] - 1]
            if celda.value is not None:
                celda.value = None
                cambios += 1
        for col, prefijo in ETIQUETAR.items():
            celda = fila[cab[col] - 1]
            if es_generico(celda.value, prefijo):
                continue
            mapa = etiquetas[col]
            clave = str(celda.value).strip().upper()
            mapa.setdefault(clave, f"{prefijo} {len(mapa) + 1}")
            celda.value = mapa[clave]
            cambios += 1
    return cambios


def main():
    etiquetas = {col: {} for col in ETIQUETAR}
    for ruta, hoja in ARCHIVOS:
        wb = load_workbook(ruta)
        cambios = generalizar(wb[hoja], etiquetas)
        if cambios:
            wb.save(ruta)
        print(f"{ruta.relative_to(RAIZ)}: {cambios} celdas cambiadas")


if __name__ == "__main__":
    main()
