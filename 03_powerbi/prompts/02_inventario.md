Trabaja en Power BI Service, en "Mi área de trabajo": informe **Sell In Sell Out v2**, modelo semántico **Retail BI v2**. Hay que cargar la tabla nueva **Inventario** y crear la página **Inventario**.

El Excel actualizado ya tiene dos cambios:
- la tabla nueva `Inventario` (COD_SKU, Fecha, Unidades, Origen, Venta_Sin_Stock), con 144.350 filas;
- 1.220 SKU nuevos `SKUI#####` en la tabla `Producto`: productos con stock y sin movimiento, con en_ventas = "N" y en_compras = "N".

## PASO 0 · Antes de tocar nada (obligatorio)

1. **Respaldo de medidas.** Abre la vista de consultas DAX del modelo y ejecuta:
   `EVALUATE SELECTCOLUMNS ( INFO.VIEW.MEASURES (), "Tabla", [Table], "Medida", [Name], "DAX", [Expression] )`
   Copia el resultado completo y entrégamelo en tu reporte final. Es el respaldo de las medidas.
2. **Fuente de datos.** El modelo lee el Excel desde GitHub con el conector Web: `https://raw.githubusercontent.com/mgabrielafiguera-pixel/proyecto-bi-retail/main/03_powerbi/retail_bi_powerbi.xlsx` (conexión `RetailBI_GitHub`, anónima). Esa URL ya trae el Excel nuevo. Comprueba que el modelo use esa URL; si usa otra fuente, detente y avísame.
3. **No vuelvas a subir el Excel con "Reemplazar".** Reemplazar el modelo borraría las medidas, las relaciones y el parámetro "Ranking por" creados en el Service. Si la única forma de cargar la tabla fuera reemplazar el modelo, **detente y avísame**.

## PASO 1 · Cargar la tabla Inventario

1. Actualiza el modelo para que lea el Excel nuevo. Comprueba que `Producto` tenga 17.721 filas.
2. En Transformar datos, abre la consulta `Producto` y duplícala. En la copia, cambia el paso de navegación para que apunte a la tabla `Inventario` (Kind = "Table") del mismo libro y borra los pasos que sean propios de Producto. Llama a la consulta `Inventario`.
3. Si el editor de Power Query del Service no permite agregar la consulta, detente y avísame.

Tipos de datos: `Fecha` como fecha, `Unidades` como número entero, el resto como texto.

Relaciones (uno a varios, dirección de filtro única, activas):
- `Producto[COD_SKU]` → `Inventario[COD_SKU]`
- `Calendario[Fecha]` → `Inventario[Fecha]`

## PASO 2 · Medidas (tabla Medidas, carpeta "Inventario")

Si Power BI rechaza las comas, cambia `,` por `;`.

```dax
Fecha Ultimo Inventario = CALCULATE ( MAX ( Inventario[Fecha] ), REMOVEFILTERS () )
```

```dax
Stock Final Uds =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
RETURN
    IF (
        MIN ( Calendario[Fecha] ) > [Fecha Ultimo Inventario] || MAX ( Calendario[Fecha] ) < DATE ( 2023, 12, 1 ),
        BLANK (),
        CALCULATE ( SUM ( Inventario[Unidades] ), REMOVEFILTERS ( Calendario ), Inventario[Fecha] = _f ) + 0
    )
```

```dax
Stock Inicial Uds =
VAR _f = EOMONTH ( MIN ( Calendario[Fecha] ), -1 )
RETURN
    IF (
        _f < DATE ( 2023, 12, 31 ) || _f >= [Fecha Ultimo Inventario], BLANK (),
        CALCULATE ( SUM ( Inventario[Unidades] ), REMOVEFILTERS ( Calendario ), Inventario[Fecha] = _f ) + 0
    )
```

```dax
Meses con Inventario =
COUNTROWS (
    FILTER (
        VALUES ( Calendario[Año_Mes] ),
        VAR _m = CALCULATE ( MAX ( Calendario[Fecha] ) )
        RETURN _m >= DATE ( 2023, 12, 1 ) && _m <= [Fecha Ultimo Inventario]
    )
)
```

```dax
Inventario Promedio Uds =
AVERAGEX (
    FILTER (
        VALUES ( Calendario[Año_Mes] ),
        VAR _m = CALCULATE ( MAX ( Calendario[Fecha] ) )
        RETURN _m >= DATE ( 2023, 12, 1 ) && _m <= [Fecha Ultimo Inventario]
    ),
    [Stock Final Uds]
)
```

```dax
Uds Vendidas Periodo Inv =
CALCULATE ( [Unidades Sell Out], KEEPFILTERS ( Calendario[Fecha] <= [Fecha Ultimo Inventario] ) )
```

```dax
Rotacion Anualizada =
DIVIDE ( [Uds Vendidas Periodo Inv], [Inventario Promedio Uds] ) * DIVIDE ( 12, [Meses con Inventario] )
```

```dax
Dias de Inventario = DIVIDE ( 365, [Rotacion Anualizada] )
```

```dax
Costo Unitario SKU =
VAR _c = DIVIDE (
    CALCULATE ( SUM ( Compras[Total_Precio_Costo_Nacionalizado] ), REMOVEFILTERS ( Calendario ) ),
    CALCULATE ( SUM ( Compras[Cantidad] ), REMOVEFILTERS ( Calendario ) ) )
VAR _v = DIVIDE (
    CALCULATE ( SUM ( Ventas[Costo_Total_Facturado] ), REMOVEFILTERS ( Calendario ) ),
    CALCULATE ( SUM ( Ventas[Cantidad] ), REMOVEFILTERS ( Calendario ) ) )
VAR _marca = SELECTEDVALUE ( Producto[CODIGO_INTERNO_MARCA] )
VAR _m = CALCULATE (
    DIVIDE ( SUM ( Compras[Total_Precio_Costo_Nacionalizado] ), SUM ( Compras[Cantidad] ) ),
    REMOVEFILTERS ( Calendario ), REMOVEFILTERS ( Producto ),
    Producto[CODIGO_INTERNO_MARCA] = _marca )
RETURN COALESCE ( _c, _v, _m )
```

```dax
Valor Inventario Costo =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
VAR _t =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( Inventario[COD_SKU] ), "@u", CALCULATE ( SUM ( Inventario[Unidades] ) ) ),
        REMOVEFILTERS ( Calendario ), Inventario[Fecha] = _f )
RETURN
    IF ( ISBLANK ( [Stock Final Uds] ), BLANK (),
        SUMX ( _t, [@u] * CALCULATE ( [Costo Unitario SKU], TREATAS ( { Inventario[COD_SKU] }, Producto[COD_SKU] ) ) ) )
```

```dax
Cobertura Meses Real = DIVIDE ( [Stock Final Uds], [Venta Promedio Mensual Uds] )
```

```dax
SKU Activos 3M =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
RETURN
    COUNTROWS ( CALCULATETABLE ( VALUES ( Ventas[COD_SKU] ), REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _f, -3, MONTH ) ) )
```

```dax
SKU en Quiebre =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
VAR _venta = CALCULATETABLE ( VALUES ( Ventas[COD_SKU] ), REMOVEFILTERS ( Calendario ),
    DATESINPERIOD ( Calendario[Fecha], _f, -3, MONTH ) )
VAR _stock = CALCULATETABLE ( VALUES ( Inventario[COD_SKU] ), REMOVEFILTERS ( Calendario ),
    Inventario[Fecha] = _f, Inventario[Unidades] > 0 )
RETURN COUNTROWS ( EXCEPT ( _venta, _stock ) ) + 0
```

```dax
% SKU en Quiebre = DIVIDE ( [SKU en Quiebre], [SKU Activos 3M] )
```

```dax
Venta Perdida Est. =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
VAR _venta = CALCULATETABLE ( VALUES ( Ventas[COD_SKU] ), REMOVEFILTERS ( Calendario ),
    DATESINPERIOD ( Calendario[Fecha], _f, -3, MONTH ) )
VAR _stock = CALCULATETABLE ( VALUES ( Inventario[COD_SKU] ), REMOVEFILTERS ( Calendario ),
    Inventario[Fecha] = _f, Inventario[Unidades] > 0 )
RETURN
    SUMX ( EXCEPT ( _venta, _stock ),
        CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Calendario ),
            DATESINPERIOD ( Calendario[Fecha], _f, -3, MONTH ),
            TREATAS ( { Ventas[COD_SKU] }, Producto[COD_SKU] ) ) / 3 )
```

```dax
Stock Sin Venta 12M Uds =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
VAR _conVenta = CALCULATETABLE ( VALUES ( Ventas[COD_SKU] ), REMOVEFILTERS ( Calendario ),
    DATESINPERIOD ( Calendario[Fecha], _f, -12, MONTH ) )
RETURN
    CALCULATE ( SUM ( Inventario[Unidades] ), REMOVEFILTERS ( Calendario ),
        Inventario[Fecha] = _f, NOT Inventario[COD_SKU] IN _conVenta ) + 0
```

```dax
% Stock Sin Venta 12M = DIVIDE ( [Stock Sin Venta 12M Uds], [Stock Final Uds] )
```

```dax
Origen Inventario =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
RETURN CALCULATE ( MAX ( Inventario[Origen] ), REMOVEFILTERS ( Calendario ), REMOVEFILTERS ( Producto ), Inventario[Fecha] = _f )
```

**Reemplaza dos medidas de la página Ventas** (con el mismo nombre, para que los visuales sigan funcionando):

```dax
Inventario Final (est.) = [Stock Final Uds]
```
```dax
Inventario Inicial (est.) = [Stock Inicial Uds]
```

Formatos:
- Unidades y SKU: número entero con separador de miles.
- Valor y venta perdida: igual que `Importe Sell Out`.
- Rotación: 2 decimales y sufijo "x".
- Días y cobertura: 1 decimal.
- Porcentajes: 1 decimal.

## PASO 3 · Página Inventario

Duplica la página **Ventas** y renómbrala **Inventario**. Así se heredan el estilo, los colores y las segmentaciones en cascada. Después borra los visuales del centro y deja las segmentaciones de la izquierda: Año, Origen, Proveedor, Marca y Departamento, sincronizadas con Ventas y Compras.

Título: "Reporte de inventario · {año}". Debajo, una nota en gris: "Dic-2023 a jun-2025: inventario real. Jul–dic 2025: estimado (kardex calibrado). 2026: estimado (kardex)."

1. **Fila de tarjetas (8):**
   - Stock Final Uds
   - Valor Inventario Costo
   - Rotacion Anualizada
   - Dias de Inventario
   - Cobertura Meses Real
   - % SKU en Quiebre, con SKU en Quiebre como subtítulo
   - Venta Perdida Est.
   - % Stock Sin Venta 12M
2. **Gráfico de columnas: Stock Final Uds por mes.**
   - Eje: `Calendario[Año_Mes]`, de dic-2023 a abr-2026. Quita el filtro de Año en este visual con "Editar interacciones".
   - Color de las columnas con formato condicional según la medida `Origen Inventario`: Real `#0B2A80`, Estimado calibrado `#1A73E8`, Estimado kardex `#C9D1E3`.
   - Línea secundaria: `Unidades Sell Out`.
3. **Matriz por el parámetro "Ranking por"** (Marca / Proveedor / Departamento). Columnas:
   - Stock Final Uds
   - Valor Inventario Costo
   - Rotacion Anualizada
   - Dias de Inventario
   - Cobertura Meses Real
   - SKU en Quiebre
   - Venta Perdida Est.
   - % Stock Sin Venta 12M

   Ordénala por Valor Inventario Costo, de mayor a menor. Formato condicional:
   - Días de Inventario: escala de verde (bajo) a rojo (alto).
   - % Stock Sin Venta 12M: rojo `#C2412D` si pasa del 30 %.
4. **Tabla "Inventario sin movimiento"**: `Producto[COD_SKU]`, Marca, Departamento, Stock Final Uds y Valor Inventario Costo. Filtro: `Producto[en_ventas]` = "N" y `Producto[en_compras]` = "N". Top 20 por valor.

Guarda el informe.

## PASO 4 · Controles (repórtame cada valor)

| Control | Esperado |
|---|---|
| Stock Final Uds, sin filtros, al 30-jun-2025 | 11.715 |
| Stock Final Uds, sin filtros, al 31-dic-2025 | 14.063 |
| Stock Final Uds, sin filtros, al 30-abr-2026 | 15.452 |
| Inventario Inicial + compradas − vendidas = Inventario Final en jul-2025 a abr-2026 | Puede no cuadrar en jul–dic 2025, porque ahí hay calibración. En ene–abr 2026 debe cuadrar salvo los meses con venta sin stock. |
| Rotación anualizada de 2025, sin filtros | Entre 1 y 2,5 |
| Filas de Producto | 17.721 |
| Página Ventas, detalle mensual de 2026 | Inventario inicial y final con datos de enero a abril, y en blanco de mayo a diciembre |

Al final, entrégame el respaldo de medidas del Paso 0 y lo que encontraste sobre la fuente de datos.
