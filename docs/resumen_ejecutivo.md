# Resumen ejecutivo

**Proyecto:** Retail de lujo · Sell In, Sell Out, Inventario y Forecast en Power BI
**Datos:** ventas, compras e inventario reales y anonimizados, 2023 a abril de 2026 (importes escalados).

## Problema

Una empresa de retail de lujo que importa la mayor parte de su mercancía no podía ver en un solo lugar si compraba lo
que vendía, cuánto stock estaba parado, qué marcas reponer ni cómo iba a cerrar el año.

## Enfoque

1. Modelo en estrella en Power BI con ventas, compras e inventario (11 tablas, unas 140 medidas DAX).
2. Reconstrucción del inventario mensual por producto con un kardex, validada contra las fotos reales.
3. Punto de reorden por marca con stock de seguridad al 95 % de nivel de servicio.
4. Budget por estacionalidad y Rolling Forecast del cierre del año, con un backtest frente a métodos base.
5. 68 controles automáticos de calidad de datos y recálculo en Python de cada cifra publicada.

## Resultados comprobados (ene–abr 2026)

| Indicador | Valor |
|---|---|
| Compras Ex-Work contra el mismo periodo de 2025 | 4,5 veces |
| Venta en importe | −7,3 % |
| Ticket promedio | −11 % (las unidades, −1,7 %) |
| Stock (dic-2023 → abr-2026) | +118 %, de 7.089 a 15.452 uds. |
| Stock sin venta en 12 meses | 46 % |
| Marcas a reponer / en sobrestock | 7 / 38, de 88 con venta |
| Rolling Forecast 2026 frente al budget | −22,5 % |

## Lectura de negocio (causas validadas con la empresa)

- La caída no es de demanda sino de **logística y surtido**. Una disrupción logística internacional a finales de 2025
  retrasó la mercancía, que llegó toda junta en 2026, y faltaron relojes de alta gama, así que bajó el precio medio.
- El stock crece por la llegada acumulada y por los **mínimos de pedido** en categorías de baja rotación.
- Las marcas que concentran la venta son las que están por reponer.

## Recomendaciones

1. Reasignar la compra hacia las 15 marcas que hacen el 80 % de la venta, sin subir el total.
2. Liquidar el stock sin venta en 12 meses y frenar compras a las marcas en sobrestock.
3. Conciliar cada mes recepciones físicas contra Compras: hay 463 casos de venta sin stock registrado.
4. Recalibrar el presupuesto con la tendencia real, sabiendo que el Rolling Forecast es conservador.

## Fiabilidad

- El inventario reconstruido tiene un error del total de −22,1 % a 6 meses sin calibración y de −7,3 % con calibración
  (que usa datos del mismo periodo). Por eso se lee por marca o departamento, no por producto.
- El forecast supera a los métodos base a nivel total (WAPE del 15,9 % en unidades), pero subestima cuando el negocio
  crece. No es fiable por marca.

Detalle: [`README.md`](../README.md) · [`validacion.md`](validacion.md) · [`auditoria.md`](auditoria.md).
