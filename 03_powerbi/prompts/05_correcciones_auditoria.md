Trabaja en Power BI Service, en "Mi área de trabajo": informe **Sell In Sell Out v2**, modelo semántico **Retail BI v2**. Son dos correcciones que salen de la auditoría del proyecto (`docs/auditoria_dax.md`). Haz primero las pruebas, repórtame lo que veas y **no cambies nada hasta que yo confirme**.

## PASO 0 · Antes de tocar nada

- No reemplaces el modelo ni subas el Excel.
- Respaldo de medidas: en la vista de consultas DAX ejecuta
  `EVALUATE SELECTCOLUMNS ( INFO.VIEW.MEASURES (), "Tabla", [Table], "Medida", [Name], "DAX", [Expression] )`
  y entrégame el resultado.

## PRUEBA 1 · ¿El filtro de proveedor llega al inventario?

Proveedor se relaciona con Ventas y Compras, pero no con Producto ni con Inventario.

1. Abre la página **Inventario**. Pon todas las segmentaciones en "Todas" y el año en 2026.
2. Anota la tarjeta de stock final. Debe ser **15.452** uds.
3. Elige **solo** el proveedor `PROV0069`, sin marca ni departamento.
4. Anota de nuevo la tarjeta de stock final y las unidades vendidas.

| Resultado esperado si el filtro funciona | Resultado si NO funciona |
|---|---|
| Stock final **2.547** uds. | Stock final sigue en 15.452 |

Las ventas de ene–abr 2026 de `PROV0069` son **1.231** uds. Esa cifra debe cambiar en los dos casos, porque Ventas sí se relaciona con Proveedor.

Repite la prueba con la segmentación **Origen** (solo "INTERNACIONAL"): también filtra Proveedor y tiene el mismo problema.

**Si no funciona, la corrección que propongo** (no la apliques todavía): añadir la columna `CODIGO_INTERNO_PROVEEDOR` a la tabla Inventario desde el script de reconstrucción, con el proveedor de cada producto, y crear la relación `Proveedor[CODIGO_INTERNO_PROVEEDOR]` → `Inventario[CODIGO_INTERNO_PROVEEDOR]` (uno a varios, filtro único). Es el mismo patrón que ya usan Ventas y Compras, no crea ambigüedad (Proveedor y Producto no están relacionados) y no obliga a cambiar ninguna medida.

## PRUEBA 2 · Corte de las comparaciones con el año anterior

Las medidas `Crecimiento Obtenido %`, `Sell In Var %`, `Histórico Crecimiento %`, `Sell Out Acumulado` y `Ritmo Esperado %` cortan el año en la **última venta** (8-jun-2026). Hay dos problemas:

- **Compras:** no hay compras después del 30-abr-2026. Por eso 2026 compara ene–abr contra ene–8 jun de 2025, y la variación sale más baja de lo real.
- **Filtros:** el corte (`MAX ( Ventas[Fecha] )` con `REMOVEFILTERS ( Calendario )`) respeta los demás filtros. Si una marca no vendió después de febrero, el año anterior también se corta en febrero.

En **Resumen anual**, con el año 2026 y sin otros filtros, anota estas tarjetas:

| Tarjeta | Valor con el corte actual (8-jun) | Valor con el corte en el último inventario (30-abr) |
|---|---:|---:|
| Crecimiento obtenido (Sell Out) | ≈ −0,4 % | ≈ −7,3 % |
| Var. Sell In, Ex-Work | ≈ +101 % | ≈ +346 % |
| Var. Sell In, puesto | ≈ +127 % | ≈ +396 % |

**Corrección propuesta** (no la apliques todavía): una sola fecha de corte para todo el informe, igual a la que ya usa la página Budget / Forecast.

```dax
Fecha Corte Comparativos = [Fecha Ultimo Inventario]
```

En las 5 medidas, cambia
`VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )`
por
`VAR _ult = [Fecha Corte Comparativos]`

`[Fecha Ultimo Inventario]` ya usa `REMOVEFILTERS ()`, así que no depende de la marca ni del proveedor elegidos.

Efecto: las ventas de mayo y junio de 2026 (2.308 líneas) dejan de contar en las comparaciones, como ya pasa en el forecast. La venta total de 2026 se sigue viendo en las matrices.

## Repórtame

1. Los valores de las dos pruebas.
2. Si alguna medida tiene un código distinto del que describo aquí.
3. No apliques las correcciones hasta que te confirme.
