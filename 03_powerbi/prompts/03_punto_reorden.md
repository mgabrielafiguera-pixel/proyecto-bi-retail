Trabaja en Power BI Service, en "Mi área de trabajo": informe **Sell In Sell Out v2**, modelo semántico **Retail BI v2**. Hay que añadir a la página **Inventario** los indicadores de **punto de reorden** (punto de quiebre), stock de seguridad y compra sugerida.

## Criterio

- El punto de reorden se calcula **al nivel del filtro o de la fila** (total, marca, proveedor o departamento), no por SKU. En lujo cada SKU tiene 1 o 2 unidades y una demanda esporádica, así que un punto de reorden por SKU marca como "a reponer" a la mayoría y no sirve para decidir.
- Demanda: unidades vendidas en los **6 meses** que terminan en el mes de corte. El mes de corte es el último mes del filtro, sin pasar del último inventario (abr-2026).
- Lead time: días de factura a recepción de las compras de la selección (`Lead Time Días`), en meses. Si la selección no tiene compras, se usa el lead time general.
- Nivel de servicio: **95 %** (Z = 1,65).
- Política (s, S): cuando el stock llega al punto de reorden, se compra hasta el stock máximo = punto de reorden + 1 mes de demanda.
- Sobrestock: más de 12 meses de demanda en stock.

## PASO 0 · Antes de tocar nada

- No reemplaces el modelo ni subas el Excel.
- No modifiques ninguna medida existente.

## PASO 1 · Medidas (tabla Medidas, carpeta "Inventario · Reorden")

Si Power BI rechaza las comas, cambia `,` por `;`. Si alguna medida no admite otra medida dentro de un filtro, guárdala antes en una variable, como hiciste con `Uds Vendidas Periodo Inv`.

```dax
Fecha Corte Inv = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
```

```dax
Stock Corte Uds =
VAR _f = [Fecha Corte Inv]
RETURN CALCULATE ( SUM ( Inventario[Unidades] ), REMOVEFILTERS ( Calendario ), Inventario[Fecha] = _f ) + 0
```

```dax
Demanda Mensual Uds =
VAR _f = [Fecha Corte Inv]
RETURN
    DIVIDE ( CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _f, -6, MONTH ) ), 6 )
```

```dax
Desv Demanda Mensual Uds =
VAR _f = [Fecha Corte Inv]
RETURN
    CALCULATE (
        STDEVX.P ( VALUES ( Calendario[Año_Mes] ), [Unidades Sell Out] + 0 ),
        REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _f, -6, MONTH )
    )
```

```dax
Lead Time Meses =
VAR _sel = CALCULATE ( [Lead Time Días], REMOVEFILTERS ( Calendario ) )
VAR _gen = CALCULATE ( [Lead Time Días], REMOVEFILTERS () )
RETURN DIVIDE ( COALESCE ( _sel, _gen ), 30 )
```

```dax
Stock Seguridad Uds = 1.65 * [Desv Demanda Mensual Uds] * SQRT ( [Lead Time Meses] )
```

```dax
Punto de Reorden Uds = [Demanda Mensual Uds] * [Lead Time Meses] + [Stock Seguridad Uds]
```

```dax
Stock Maximo Uds = [Punto de Reorden Uds] + [Demanda Mensual Uds]
```

```dax
Dias hasta Reorden =
DIVIDE ( [Stock Corte Uds] - [Punto de Reorden Uds], DIVIDE ( [Demanda Mensual Uds], 30 ) )
```
Negativo = ya está por debajo del punto de reorden.

```dax
Estado Reorden =
VAR _s = [Stock Corte Uds]
VAR _d = [Demanda Mensual Uds]
RETURN
    SWITCH (
        TRUE (),
        _d = 0 || ISBLANK ( _d ), "Sin demanda",
        _s <= [Punto de Reorden Uds], "Reponer",
        _s > 12 * _d, "Sobrestock",
        "OK"
    )
```

```dax
Color Estado Reorden =
SWITCH ( [Estado Reorden], "Reponer", "#C2412D", "Sobrestock", "#E4643F", "OK", "#1F8A4C", "#C9D1E3" )
```

```dax
Marcas a Reponer =
COUNTROWS (
    FILTER ( VALUES ( Producto[CODIGO_INTERNO_MARCA] ),
        [Demanda Mensual Uds] > 0 && [Stock Corte Uds] <= [Punto de Reorden Uds] )
) + 0
```

```dax
Marcas con Demanda =
COUNTROWS ( FILTER ( VALUES ( Producto[CODIGO_INTERNO_MARCA] ), [Demanda Mensual Uds] > 0 ) ) + 0
```

```dax
Marcas en Sobrestock =
COUNTROWS (
    FILTER ( VALUES ( Producto[CODIGO_INTERNO_MARCA] ),
        [Demanda Mensual Uds] > 0 && [Stock Corte Uds] > 12 * [Demanda Mensual Uds] )
) + 0
```

```dax
Compra Sugerida Uds =
SUMX (
    VALUES ( Producto[CODIGO_INTERNO_MARCA] ),
    VAR _s = [Stock Corte Uds]
    RETURN IF ( [Demanda Mensual Uds] > 0 && _s <= [Punto de Reorden Uds], MAX ( 0, [Stock Maximo Uds] - _s ), 0 )
)
```

```dax
Compra Sugerida Costo =
SUMX (
    VALUES ( Producto[CODIGO_INTERNO_MARCA] ),
    VAR _q = [Compra Sugerida Uds]
    RETURN _q * DIVIDE ( [Valor Inventario Costo], [Stock Final Uds] )
)
```

Formatos: unidades y compra sugerida sin decimales con miles; `Lead Time Meses` con 1 decimal; `Dias hasta Reorden` sin decimales.

## PASO 2 · Página Inventario

Usa el mismo estilo que el resto de la página (bordes `#E1E4E9`, esquinas de 6 px, título con barra naranja `#E4643F`).

1. **Fila de 4 tarjetas "Punto de reorden"**, debajo de las 8 tarjetas actuales (si no cabe, reduce un poco la altura del gráfico mensual):
   - Punto de reorden (uds.) → `Punto de Reorden Uds`, subtítulo "stock de seguridad: " & `Stock Seguridad Uds`.
   - Lead time → `Lead Time Meses` × 30, en días, subtítulo "factura → recepción".
   - Marcas a reponer → `Marcas a Reponer`, subtítulo "de " & `Marcas con Demanda` & " con venta · " & `Marcas en Sobrestock` & " en sobrestock". Valor en rojo `#C2412D` si es mayor que 0.
   - Compra sugerida → `Compra Sugerida Uds`, subtítulo con `Compra Sugerida Costo` "a costo".
2. **Matriz "Inventario por segmento"** (la del parámetro "Ranking por"): añade al final las columnas `Punto de Reorden Uds`, `Dias hasta Reorden`, `Compra Sugerida Uds` y `Estado Reorden`. En `Estado Reorden` aplica color de fondo con la medida `Color Estado Reorden` (formato condicional → valor del campo) y texto blanco.
3. Añade una línea al subtítulo de la página: "Punto de reorden: demanda 6 meses, nivel de servicio 95 %, por marca."
4. Guarda el informe.

## PASO 3 · Controles

Con todos los filtros en "Todas" (valores aproximados; si la diferencia es mayor del 5 %, avísame antes de seguir):

| Control | Año 2025 (corte dic-2025) | Año 2026 (corte abr-2026) |
|---|---|---|
| Lead time | ≈ 32 días | ≈ 32 días |
| Demanda mensual (uds.) | ≈ 1.758 | ≈ 1.618 |
| Punto de reorden total (uds.) | ≈ 3.630 | ≈ 3.615 |
| Marcas con demanda | 88 | 88 |
| Marcas a reponer | ≈ 9 | ≈ 7 |
| Marcas en sobrestock | ≈ 31 | ≈ 38 |
| Compra sugerida (uds.) | ≈ 497 | ≈ 308 |

Repórtame los controles, cualquier cambio que hayas tenido que hacer en las fórmulas y una captura de la página.
