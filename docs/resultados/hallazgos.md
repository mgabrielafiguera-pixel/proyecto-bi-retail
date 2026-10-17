# Hallazgos del README: recálculo desde el Excel

Generado por `scripts/hallazgos.py` a partir de `03_powerbi/retail_bi_powerbi.xlsx`.
Tolerancia: ±0,5 puntos para porcentajes, ±1 % relativo para importes, unidades y conteos;
para ratios (veces, sell-through, factor) se indica en la definición.

**52 de 52 cifras coinciden.**

| Hallazgo | Cifra | Valor en README | Valor recalculado | ¿Coincide? | Definición usada |
|---|---|---:|---:|---|---|
| 9.1 | Compras Ex-Work ene–abr 2026 vs 2025 (veces) | 4,50 | 4,46 | Sí | ΣTotal_Costo_Ex_Works ene–abr 26 / ene–abr 25 (compras_validas, Fecha_Recepcion); tol ±0,05. Sin excluir los 6 errores da 3,01 |
| 9.1 | Venta importe ene–abr 2026 vs 2025 (%) | -7,30 | -7,25 | Sí | ΣTotal_Factura ene–abr 26 / ene–abr 25 − 1 |
| 9.1 | Sell-through uds ene–abr 2025 | 1,30 | 1,30 | Sí | ΣCantidad ventas / ΣCantidad compras_validas, ene–abr 2025; tol ±0,005 (=0,5 pt) |
| 9.1 | Sell-through uds ene–abr 2026 | 0,78 | 0,78 | Sí | ΣCantidad ventas / ΣCantidad compras_validas, ene–abr 2026 |
| 9.1 | Sell-through uds 2024 | 0,69 | 0,69 | Sí | ΣCantidad ventas / ΣCantidad compras_validas, año 2024 |
| 9.1 | Sell-through uds 2025 | 1,16 | 1,16 | Sí | ΣCantidad ventas / ΣCantidad compras_validas, año 2025 |
| 9.2 | Unidades vendidas ene–abr 26 vs 25 (%) | -1,70 | -1,72 | Sí | ΣCantidad (neta) ene–abr 26 / 25 − 1 |
| 9.2 | Facturas ene–abr 26 vs 25 (%) | 1,20 | 1,18 | Sí | nº distinto Num_Factura con Mov='FACT' (medida Facturas), ene–abr 26 / 25 − 1. Sin filtrar Mov da +0,57 |
| 9.2 | Clientes ene–abr 26 vs 25 (%) | 6 | 6,31 | Sí | nº distinto COD_CLIENTE (todas las líneas), ene–abr 26 / 25 − 1 |
| 9.2 | Ticket promedio ene–abr 26 vs 25 (%) | -11 | -11,25 | Sí | Ticket = ΣTotal_Factura(Mov='FACT') / Facturas; ene–abr 26 / 25 − 1. Con el importe neto (FACT + N/CR) da −8,34 |
| 9.2 | Relojería, % de la venta ene–abr 2026 | 58 | 57,99 | Sí | ΣTotal_Factura RELOJERIA / ΣTotal_Factura, ene–abr 2026 |
| 9.2 | Relojería, precio medio por pieza (%) | -29 | -29,34 | Sí | (ΣTotal_Factura/ΣCantidad) RELOJERIA ene–abr 26 / 25 − 1 |
| 9.2 | Relojería, unidades (%) | 16 | 16,20 | Sí | ΣCantidad RELOJERIA ene–abr 26 / 25 − 1 |
| 9.2 | Relojería, margen ene–abr 2025 (%) | 36 | 36,32 | Sí | margen % (costo_con_signo) RELOJERIA ene–abr 2025 |
| 9.2 | Relojería, margen ene–abr 2026 (%) | 42 | 42,43 | Sí | (ΣTotal_Factura − Σcosto_con_signo)/ΣTotal_Factura, RELOJERIA ene–abr 2026. Con el costo sin corregir el signo da 35,96 |
| 9.2 | Joyería, venta importe (%) | 10 | 10,08 | Sí | ΣTotal_Factura JOYERIA ene–abr 26 / 25 − 1 |
| 9.2 | Joyería, precio por pieza (% var., README: «sube») | > 0 | 15,92 | Sí | (ΣTotal_Factura/ΣCantidad) JOYERIA ene–abr 26 / 25 − 1; coincide si > 0 |
| 9.2 | Joyería, margen ene–abr 2025 (%) | 51 | 50,76 | Sí | margen % JOYERIA ene–abr 2025 |
| 9.2 | Joyería, margen ene–abr 2026 (%) | 59 | 59,07 | Sí | margen % (costo_con_signo) JOYERIA ene–abr 2026. Con el costo sin corregir el signo da 56,56 |
| 9.3 | Stock dic-2023 (uds) | 7.089 | 7.089 | Sí | ΣInventario.Unidades, Fecha = 2023-12-31 |
| 9.3 | Stock abr-2026 (uds) | 15.452 | 15.452 | Sí | ΣInventario.Unidades, Fecha = 2026-04-30 |
| 9.3 | Variación stock dic-23 → abr-26 (%) | 118 | 117,97 | Sí | stock abr-26 / stock dic-23 − 1 |
| 9.3 | % unidades en stock sin venta 12M (abr-2026) | 46 | 45,77 | Sí | Σuds stock abr-26 de SKU sin línea de venta may-25..abr-26 / stock abr-26 |
| 9.3 | Marcas con >12 meses de cobertura | 38 | 38 | Sí | marcas con demanda 6M > 0 y stock abr-26 > 12 × demanda (ver 4.4) |
| 9.3 | Marcas con venta (demanda 6M > 0) | 88 | 88 | Sí | marcas con Σuds sell out nov-25..abr-26 > 0 |
| 9.3 | Belleza + Accesorios, % del stock (abr-2026) | 25 | 24,73 | Sí | Σuds stock abr-26 BELLEZA+ACCESORIOS / stock abr-26 |
| 9.3 | Belleza + Accesorios, % de la venta (< 3 %) | < 3 | 2,84 | Sí | ΣTotal_Factura BELLEZA+ACCESORIOS / total, todo el periodo (ene–abr 2026 daría 3,42); coincide si < 3 |
| 9.4 | Lead time (días) | 32 | 31,70 | Sí | media por línea de (Fecha_Recepcion − Fecha_Invoice), Invoice no nula y recepción ≥ factura, compras_validas |
| 9.4 | Marcas a reponer (abr-2026) | 7 | 7 | Sí | dem>0 y stock≤ROP; dem=uds nov-25..abr-26/6; ROP=dem·LT+1,65·σ·√LT (por marca) |
| 9.4 | Compra sugerida (uds) | 308 | 308,15 | Sí | Σ max(0, ROP+dem − stock) de las marcas a reponer |
| 9.4 | Punto de reorden total (uds, control) | 3.615 | 3.615 | Sí | ROP al nivel total: dem total·LT general + 1,65·σ total·√LT |
| 9.4 | Marcas que hacen el 80 % de la venta | 15 | 15 | Sí | marcas ordenadas por ΣTotal_Factura desc (todo el periodo); nº hasta acumular 80 % |
| 9.4 | Total de marcas | 141 | 141 | Sí | filas de la tabla Marca |
| 9.4 | MARC0004, % de la venta | 8 | 8,14 | Sí | ΣTotal_Factura MARC0004 / total, todo el periodo |
| 9.4 | MARC0004, sell-through uds | 1,27 | 1,27 | Sí | Σuds venta / Σuds compras_validas de MARC0004, ene-2024..abr-2026; tol ±0,005 |
| 9.5 | Rolling Forecast 2026 vs Budget (%) | -22,50 | -22,47 | Sí | rolling = venta real ene–abr 26 + uds forecast may–dic × precio 12M; budget = venta 2025 × 1,20 |
| 9.5 | Budget 2026 (control) | 24.101.761 | 24.101.761 | Sí | ΣTotal_Factura 2025 × 1,20 |
| 9.5 | Rolling Forecast 2026 (control) | 18.687.201 | 18.687.201 | Sí | real ene–abr + Σ(pieza 12M × estacionalidad uds) may–dic × precio 12M |
| 9.5 | Rolling Forecast 2026 vs venta 2025 (%) | -7 | -6,96 | Sí | rolling 2026 / ΣTotal_Factura 2025 − 1 |
| 9.5 | Diciembre vs mes medio, en unidades (veces) | 2,50 | 2,46 | Sí | estacionalidad uds dic = uds dic 24+25 / (uds 24+25 / 12); tol ±0,05 |
| 9.5 | Diciembre vs mes medio, en importe (veces) | 3 | 2,95 | Sí | Estacionalidad Ventas dic = importe dic 24+25 / (importe 24+25 / 12); tol ±0,5 |
| 9.6 | Almacén 1, % de la venta | 89 | 89,45 | Sí | ΣTotal_Factura Almacén 1 / total, 2023–2026 |
| 9.6 | Clientes que hacen el 50 % de la venta | 78 | 78 | Sí | clientes ordenados por ΣTotal_Factura desc (todo el periodo); nº hasta acumular ≥ 50 % (los 77 primeros suman 49,88 %) |
| 9.6 | Total de clientes | 13.090 | 13.090 | Sí | filas de la tabla Cliente |
| 9.6 | Primer cliente, % de la venta | 7,60 | 7,63 | Sí | ΣTotal_Factura del primer cliente / total, todo el periodo |
| 9.7 | Casos (SKU, mes) con venta sin stock | 463 | 463 | Sí | filas de Inventario con Venta_Sin_Stock = 'Sí' |
| 9.7 | Devoluciones duplicadas con costo erróneo | 6 | 6 | Sí | filas de Compras con Es_Posible_Duplicado='Sí' y Precio_Cero='Sí' |
| 9.7 | Factor importación 2026 con errores | 1,88 | 1,88 | Sí | ΣNacionalizado / ΣEx-Work 2026, todas las compras; tol ±0,005 |
| 9.7 | Factor importación mar-2026 con errores | -9,88 | -9,88 | Sí | ΣNacionalizado / ΣEx-Work mar-2026, todas las compras; tol ±0,005 |
| 9.7 | Factor importación 2026 sin errores | 1,27 | 1,27 | Sí | ΣNacionalizado / ΣEx-Work 2026, compras_validas; tol ±0,005 |
| 9.7 | Compras 'Sin clasificar' (líneas) | 1.384 | 1.384 | Sí | filas de compras_validas con Tipo_Movi = 'Sin clasificar' (igual con todas las compras) |
| 9.7 | Compras 'Sin clasificar', % del Sell In | 8,40 | 8,40 | Sí | ΣNacionalizado 'Sin clasificar' / ΣNacionalizado, compras_validas (con todas: 8,40 %) |

No se recalcula aquí: «el kardex puro subestima el inventario real en un 22 % a 6 meses» (4.7), que sale del backtest de `scripts/reconstruir_inventario.py` con las fotos reales de 2025.
