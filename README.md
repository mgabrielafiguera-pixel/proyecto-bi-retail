# Proyecto BI Retail · Ventas, Compras, Inventario y Finanzas

> Portafolio de Business Intelligence construido sobre datos reales de retail,
> **anonimizados**: proveedores, marcas, productos, clientes y vendedores codificados
> (`PROV####`, `MARC####`, `SKU#####`), nombres y direcciones ficticios e importes escalados.

## Estado
Fase 4 (dashboards en Power BI) en curso. Detalle en `03_powerbi/ESTADO_PROYECTO.md`
y avance en la pestaña **Issues**.

| Página del informe | Estado |
|---|---|
| Resumen anual | Terminada |
| Ventas | Terminada |
| Compras | Terminada |
| Inventario | Datos listos, página en construcción |
| Budget / Forecast | Pendiente |

## Estructura
| Carpeta | Contenido |
|---|---|
| `02_anonimizado/` | Datos anonimizados en CSV, incluido el inventario por SKU y mes |
| `03_powerbi/` | Excel que lee Power BI (`retail_bi_powerbi.xlsx`), documentación del modelo y prompts |
| `04_presentacion/` | Bocetos de las páginas (datos ficticios) |
| `scripts/` | Python: anonimización del inventario y reconstrucción con kardex |

Los datos originales (`00_original/`, `01_mapeos/`, `trabajo/`) no se suben al repo.

## Inventario
Las fotos reales llegan a jun-2025. De jul-2025 a abr-2026 el stock se reconstruye con
kardex (inventario inicial + compras − ventas), calibrado con el resumen por marca.
Método y precisión en `03_powerbi/MODELO.md`.

```
python3 scripts/reconstruir_inventario.py
```

## Stack
Excel · Power Query · Power BI · DAX · Python (pandas, openpyxl) · Git
