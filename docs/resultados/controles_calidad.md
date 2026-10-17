# Controles de calidad de datos

Generado por `scripts/validar_modelo.py` sobre `03_powerbi/retail_bi_powerbi.xlsx`.

| Resultado | Controles |
|---|---|
| OK | 48 |
| Aviso | 15 |
| Revisar | 5 |
| Error | 0 |

**OK**: se cumple. **Aviso**: hay casos legítimos o ya tratados en el modelo. **Revisar**: posibles errores de origen sin corregir. **Error**: hay que corregir antes de publicar.

| Tipo | Control | Tabla | Evaluados | Afectados | Resultado | Acción |
|---|---|---|---:|---:|---|---|
| Integridad | Filas esperadas | Ventas | 49,936 | 0 | OK | Esperado 49,936. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Compras | 16,721 | 0 | OK | Esperado 16,721. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Producto | 17,721 | 0 | OK | Esperado 17,721. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Cliente | 13,090 | 0 | OK | Esperado 13,090. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Proveedor | 165 | 0 | OK | Esperado 165. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Marca | 141 | 0 | OK | Esperado 141. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Vendedor | 89 | 0 | OK | Esperado 89. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Almacen | 13 | 0 | OK | Esperado 13. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Departamento | 12 | 0 | OK | Esperado 12. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Calendario | 1,461 | 0 | OK | Esperado 1,461. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Filas esperadas | Inventario | 144,350 | 0 | OK | Esperado 144,350. Si cambia, actualizar ESTADO_PROYECTO.md |
| Integridad | Clave única COD_SKU | Producto | 17,721 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única COD_CLIENTE | Cliente | 13,090 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única CODIGO_INTERNO_PROVEEDOR | Proveedor | 165 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única CODIGO_INTERNO_MARCA | Marca | 141 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única COD_VENDEDOR | Vendedor | 89 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única COD_ALMACEN | Almacen | 13 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única COD_DEPARTAMENTO | Departamento | 12 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Clave única Fecha | Calendario | 1,461 | 0 | OK | Una dimensión con claves repetidas duplica importes en Power BI |
| Integridad | Nulos en campos críticos | Ventas | 49,936 | 0 | OK | Sin nulos |
| Integridad | Nulos en campos críticos | Compras | 16,721 | 15 | Aviso | Nulos por columna: {'Total_Precio_Costo_Nacionalizado': 15} |
| Integridad | Nulos en campos críticos | Inventario | 144,350 | 0 | OK | Sin nulos |
| Consistencia | Claves huérfanas COD_SKU → Producto | Ventas | 49,936 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_ALMACEN → Almacen | Ventas | 49,936 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_CLIENTE → Cliente | Ventas | 49,936 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_VENDEDOR → Vendedor | Ventas | 49,936 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas CODIGO_INTERNO_PROVEEDOR → Proveedor | Ventas | 49,936 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_SKU → Producto | Compras | 16,721 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_ALMACEN → Almacen | Compras | 16,721 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas CODIGO_INTERNO_PROVEEDOR → Proveedor | Compras | 16,721 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas CODIGO_INTERNO_MARCA → Marca | Producto | 17,721 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_DEPARTAMENTO → Departamento | Producto | 17,721 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Consistencia | Claves huérfanas COD_SKU → Producto | Inventario | 144,350 | 0 | OK | Filas que no filtraría ninguna segmentación de la dimensión |
| Temporal | Fecha dentro de Calendario | Ventas | 49,936 | 0 | OK | Rango 03-01-2023 a 08-06-2026 |
| Temporal | Fecha_Recepcion dentro de Calendario | Compras | 16,721 | 0 | OK | Rango 10-01-2024 a 30-04-2026 |
| Temporal | Fecha dentro de Calendario | Inventario | 144,350 | 0 | OK | Rango 31-12-2023 a 30-04-2026 |
| Temporal | Fecha de inventario a fin de mes | Inventario | 144,350 | 0 | OK | Las medidas buscan el stock en EOMONTH |
| Temporal | Ventas después del último inventario | Ventas | 49,936 | 2,308 | Aviso | Ventas posteriores al 30-04-2026. El forecast las excluye; Resumen anual las incluye. Confirmar si son fechas reales |
| Temporal | Recepción antes de la factura | Compras | 15,459 | 1,008 | Aviso | Se excluyen del lead time (la medida exige recepción ≥ factura) |
| Temporal | Factura > 60 días antes de la recepción | Compras | 15,459 | 1,775 | Revisar | Alargan el lead time medio. Revisar la fecha de factura |
| Temporal | Factura > 60 días después de la recepción | Compras | 15,459 | 470 | Revisar | Fecha de factura dudosa. No afecta: las compras se fechan por recepción |
| Importes | Cantidades negativas (devoluciones) | Ventas | 49,936 | 1,695 | Aviso | Legítimas: restan venta. Marcadas con Es_Devolucion |
| Importes | Devolución registrada como factura (FACT negativa) | Ventas | 49,936 | 210 | Revisar | Bajan el ticket promedio; confirmar con el negocio |
| Importes | Costo con signo contrario en devoluciones | Ventas | 1,695 | 641 | Aviso | Corregido en la medida Costo Sell Out |
| Importes | Venta con costo cero | Ventas | 49,936 | 1,070 | Revisar | Margen 100 % en esas líneas: el margen total queda algo inflado |
| Importes | Marca Es_Posible_Duplicado | Ventas | 49,936 | 1,780 | Aviso | Marcado, no borrado. Ver MODELO.md, Calidad de datos |
| Importes | Marca Precio_Cero | Ventas | 49,936 | 1,291 | Aviso | Marcado, no borrado. Ver MODELO.md, Calidad de datos |
| Importes | Marca Total_No_Cuadra | Ventas | 49,936 | 2,038 | Aviso | Marcado, no borrado. Ver MODELO.md, Calidad de datos |
| Importes | Marca Es_Posible_Duplicado | Compras | 16,721 | 1,193 | Aviso | Marcado, no borrado. Ver MODELO.md, Calidad de datos |
| Importes | Marca Precio_Cero | Compras | 16,721 | 16 | Aviso | Marcado, no borrado. Ver MODELO.md, Calidad de datos |
| Importes | Marca Total_No_Cuadra | Compras | 16,721 | 2 | Aviso | Marcado, no borrado. Ver MODELO.md, Calidad de datos |
| Importes | Compras excluidas en Power Query | Compras | 16,721 | 6 | OK | Devoluciones duplicadas con costo erróneo (paso 'Excluir errores de captura') |
| Importes | Compras sin tipo de movimiento | Compras | 16,721 | 1,384 | Revisar | Incluidas en Sell In. Pendiente de clasificar en el origen |
| Inventario | Stock negativo | Inventario | 144,350 | 0 | OK | Los negativos se llevan a 0 al reconstruir |
| Inventario | Duplicados SKU + Fecha | Inventario | 144,350 | 0 | OK | Duplicarían el stock |
| Inventario | Venta sin stock registrado (kardex negativo) | Inventario | 144,350 | 463 | Aviso | Recepciones no registradas en Compras (hallazgo 4.7) |
| Consistencia | Proveedor de Ventas = proveedor de Producto | Ventas | 49,936 | 173 | Aviso | Filtrar por Proveedor (relación con la tabla de hechos) y por Marca (vía Producto) puede dar totales algo distintos |
| Consistencia | Proveedor de Compras = proveedor de Producto | Compras | 16,721 | 55 | Aviso | Filtrar por Proveedor (relación con la tabla de hechos) y por Marca (vía Producto) puede dar totales algo distintos |
| Consistencia | SKU sin movimiento (SKUI) con departamento | Producto | 1,220 | 0 | OK | Sin departamento quedan fuera de los filtros por departamento |
| Consistencia | SKUI presentes en Inventario | Producto | 1,220 | 0 | OK | Los SKUI solo existen para dar dimensión al stock |
| Confidencialidad | Direcciones y ubicación de almacenes | Almacen | 13 | 13 | Aviso | Se publican a propósito para el mapa de ventas por almacén (decisión del 17-oct-2026) |
| Totales | Total de control: Unidades Sell Out | Ventas | 1 | 0 | OK | Excel 48,052 vs Power BI 48,052 |
| Totales | Total de control: Importe Sell Out | Ventas | 1 | 0 | OK | Excel 44,271,198 vs Power BI 44,271,198 |
| Totales | Total de control: Unidades Sell In | Compras | 1 | 0 | OK | Excel 44,990 vs Power BI 44,990 |
| Totales | Total de control: Importe Sell In | Compras | 1 | 0 | OK | Excel 23,649,381 vs Power BI 23,649,381 |
| Totales | Stock total al 2025-06-30 | Inventario | 1 | 0 | OK | Excel 11,715 vs Power BI 11,715 |
| Totales | Stock total al 2025-12-31 | Inventario | 1 | 0 | OK | Excel 14,063 vs Power BI 14,063 |
| Totales | Stock total al 2026-04-30 | Inventario | 1 | 0 | OK | Excel 15,452 vs Power BI 15,452 |
