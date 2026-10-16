Trabaja en el informe **Sell In Sell Out v2** (modelo semántico **Retail BI v2**, "Mi área de trabajo") de Power BI Service. Crea dos páginas nuevas, **Ventas** y **Compras**, iguales a las imágenes adjuntas. Los datos de las imágenes son ficticios: usa siempre los del modelo.

## Reglas generales

- Crea todas las medidas en la tabla `Medidas`, con carpeta de visualización **Ventas** o **Compras** según corresponda. Si Power BI rechaza las comas, cambia `,` por `;`.
- **No modifiques** las medidas que ya existen, salvo que una de abajo se llame igual. En ese caso, avísame antes.
- Estas medidas ya existen y se reutilizan: `Importe Sell Out`, `Importe Sell Out AA`, `Unidades Sell Out`, `Unidades Sell Out AA`, `Unidades Sell In`, `Unidades Sell In AA`, `Importe Sell In` (Puesto), `Importe Sell In ExW`, `Sell In (selector)`, `Sell In (selector) AA`, `Sell In Var %`, `S/I Matriz`, `S/O Matriz`, `Crecimiento Obtenido %`, `Facturas`, `Ticket Promedio`, `Ticket Promedio AA`, `Costo Sell Out`, `Margen %`, `Margen % AA`, `Devoluciones %` y `Sell-Through %`.
- **Comparación con el año anterior:** se hace siempre **cortando a la misma fecha**, con `KEEPFILTERS ( Calendario[Fecha] <= _ult )` sobre la medida AA. No pongas `SAMEPERIODLASTYEAR` en el mismo `CALCULATE` que el corte.
- **Diseño:** usa los mismos colores y estilo que la página **Resumen anual**. La forma más rápida es **duplicar Resumen anual**, renombrar la copia y borrar los visuales que no sirvan. Así se heredan el fondo, las tarjetas y los títulos.
  - Azul 2026 / actual: `#1A73E8`.
  - Azul oscuro 2025 / año anterior: `#0B2A80`.
  - Gris de meses futuros: `#C9D1E3`.
  - Barra de acento de los títulos: naranja `#E4643F`.
  - Fila de estacionalidad: fondo `#FCEDE7`.
  - Verde positivo: `#1F8A4C`. Rojo negativo: `#C2412D`.
  - Bordes: `#E1E4E9`, con esquinas redondeadas de 6 px.
- **Segmentaciones a la izquierda**, en este orden: Año (`Calendario[Año]`, selección única, 2026 por defecto), Origen (`Proveedor[Origen_PROVEEDOR]`), Departamento, Proveedor, Marca. En la página Compras se añade además **Costo Sell In** (`Tipo Costo`, en mosaico). Sincroniza estas segmentaciones entre Ventas y Compras (**Ver → Sincronizar segmentaciones**).
- El selector **Calendario / Fiscal abr–mar** todavía **no** se crea. Falta la columna de año fiscal en Proveedor.
- Al terminar cada página, guarda el informe.

---

## PÁGINA 1 · VENTAS

### 1. Medidas (carpeta "Ventas")

```dax
Vendido AA Matriz = COALESCE ( [Importe Sell Out AA], 0 )
```

```dax
Estacionalidad Ventas =
VAR _meses = VALUES ( Calendario[Mes] )
VAR _total =
    CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 } )
VAR _mes =
    CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 }, _meses )
RETURN
    DIVIDE ( _mes, _total / 12 )
```
Es el peso de cada mes en la venta 2024–2025: 1,00 es un mes promedio y el total da 12,00. Respeta los filtros de proveedor, marca y departamento, así que cambia al filtrar.

```dax
Unidades Sell Out Var % YTD =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Unidades Sell Out], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Unidades Sell Out AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN DIVIDE ( _act - _aa, _aa )
```

```dax
Facturas AA = CALCULATE ( [Facturas], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Facturas Var % YTD =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Facturas], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Facturas AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN DIVIDE ( _act - _aa, _aa )
```

```dax
Ticket Promedio Var % YTD =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Ticket Promedio], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Ticket Promedio AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN DIVIDE ( _act - _aa, _aa )
```

```dax
Margen % Var pp YTD =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Margen %], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Margen % AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN _act - _aa
```

```dax
Precio Promedio Venta = DIVIDE ( [Importe Sell Out], [Unidades Sell Out] )
```

```dax
Costo Promedio Pieza Venta = DIVIDE ( [Costo Sell Out], [Unidades Sell Out] )
```

```dax
% Venta Global =
DIVIDE (
    [Importe Sell Out],
    CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Proveedor ), REMOVEFILTERS ( Marca ), REMOVEFILTERS ( Departamento ), REMOVEFILTERS ( Producto ) )
)
```

```dax
% del Total Venta = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], ALLSELECTED () ) )
```

**Inventario estimado.** Todavía no hay tabla de inventario. Mientras tanto, el inventario se estima como compras acumuladas − ventas acumuladas desde el 1-ene-2024 (antes no hay compras), hasta la última fecha de compra. Cuando carguemos la tabla Inventario, se reemplazarán solo estas dos medidas.

```dax
Inventario Final (est.) =
VAR _fin  = MAX ( Calendario[Fecha] )
VAR _ultC = CALCULATE ( MAX ( Compras[Fecha_Recepcion] ), REMOVEFILTERS () )
RETURN
    IF (
        MIN ( Calendario[Fecha] ) > _ultC, 0,
        CALCULATE (
            [Unidades Sell In] - [Unidades Sell Out],
            REMOVEFILTERS ( Calendario ),
            Calendario[Fecha] >= DATE ( 2024, 1, 1 ),
            Calendario[Fecha] <= MIN ( _fin, _ultC )
        )
    )
```

```dax
Inventario Inicial (est.) =
VAR _ini  = MIN ( Calendario[Fecha] )
VAR _ultC = CALCULATE ( MAX ( Compras[Fecha_Recepcion] ), REMOVEFILTERS () )
RETURN
    IF (
        _ini > _ultC, 0,
        CALCULATE (
            [Unidades Sell In] - [Unidades Sell Out],
            REMOVEFILTERS ( Calendario ),
            Calendario[Fecha] >= DATE ( 2024, 1, 1 ),
            Calendario[Fecha] < _ini
        )
    )
```

```dax
Venta Promedio Mensual Uds =
DIVIDE (
    CALCULATE ( [Unidades Sell Out], DATESINPERIOD ( Calendario[Fecha], MAX ( Calendario[Fecha] ), -3, MONTH ) ),
    3
)
```

```dax
Cobertura Meses = DIVIDE ( [Inventario Final (est.)], [Venta Promedio Mensual Uds] )
```

Las medidas para la matriz de detalle muestran 0 en los meses sin datos:

```dax
Det Unidades Compradas = COALESCE ( [Unidades Sell In], 0 )
```
```dax
Det Unidades Vendidas = COALESCE ( [Unidades Sell Out], 0 )
```
```dax
Det Monto Vendido = COALESCE ( [Importe Sell Out], 0 )
```

### 2. Visuales (de arriba abajo)

1. **Título** "Reporte de ventas · [año]" y, debajo, el subtítulo "importes en miles · comparaciones contra el mismo periodo del año anterior".
2. **Banda superior (matriz):**
   - Columnas: `Calendario[Nombre_Mes]`.
   - Valores, en este orden: `Vendido AA Matriz` (etiqueta "Vendido año anterior"), `S/O Matriz` (etiqueta "Vendido") y `Estacionalidad Ventas`.
   - Activa **Formato → Valores → Mostrar en filas**.
   - Importes en **miles** sin decimales. Estacionalidad con 2 decimales.
   - Fila de estacionalidad: fondo `#FCEDE7` y negrita.
   - A la derecha, una tarjeta pequeña "Crec. YTD" con `Crecimiento Obtenido %`, en verde o rojo según el signo.
3. **Fila de 8 tarjetas** (tarjeta nueva con etiqueta de referencia, como en Resumen anual):

   | Tarjeta | Valor | Etiqueta de referencia |
   |---|---|---|
   | Venta $ | `Importe Sell Out` | `Crecimiento Obtenido %` + " vs AA" |
   | Unidades vendidas | `Unidades Sell Out` | `Unidades Sell Out Var % YTD` |
   | Facturas | `Facturas` | `Facturas Var % YTD` |
   | Ticket promedio | `Ticket Promedio` | `Ticket Promedio Var % YTD` |
   | Precio prom. pieza | `Precio Promedio Venta` | texto "venta ÷ unidades" |
   | Margen % | `Margen %` | `Margen % Var pp YTD` (en pp) |
   | Devoluciones % | `Devoluciones %` | texto "de la venta" |
   | % venta global | `% Venta Global` | texto "del total empresa" |

4. **Detalle mensual (matriz, valores en filas)**, con el título "Detalle mensual" y la barra naranja:
   - Columnas: `Calendario[Nombre_Mes]`.
   - Filas, en este orden: `Inventario Inicial (est.)`, `Det Unidades Compradas`, `Det Unidades Vendidas`, `Inventario Final (est.)`, `Det Monto Vendido`, `Costo Promedio Pieza Venta` (1 decimal), `Precio Promedio Venta` (1 decimal), `Margen %` (1 decimal), `Cobertura Meses` (1 decimal).
   - Etiquetas de fila: "Inventario inicial", "Unidades compradas", "Unidades vendidas", "Inventario final", "Monto vendido $", "Costo promedio pieza", "Precio promedio venta", "Margen %" y "Cobertura (meses)".
   - Formato condicional: fondo azul muy claro (`#1A73E8` al 10 %) en los meses con venta.
5. **Gráfico de columnas agrupadas** "Venta mensual vs año anterior":
   - Eje: `Nombre_Mes`.
   - Valores: `Importe Sell Out AA` (`#0B2A80`) e `Importe Sell Out` (`#1A73E8`).
6. **Barras horizontales** "Venta por departamento":
   - Eje: `Departamento[DEPARTAMENTO_ORIGINAL]`.
   - Valor: `% del Total Venta`, en azul `#1A73E8`.
7. **Tabla "Ranking"**:
   - Primero intenta crear un **parámetro de campos** (Modelado → Nuevo parámetro → Campos) con `Marca[CODIGO_INTERNO_MARCA]`, `Proveedor[CODIGO_INTERNO_PROVEEDOR]` y `Departamento[DEPARTAMENTO_ORIGINAL]`, y pon su segmentación encima de la tabla. Si la versión web no lo permite, usa `Marca[CODIGO_INTERNO_MARCA]`.
   - Columnas: `Importe Sell Out`, `% del Total Venta`, `Crecimiento Obtenido %` (título "Crec. vs AA", icono ▲▼ verde/rojo), `Unidades Sell Out`, `Ticket Promedio` y `Margen %`.
   - Ordenada por venta, de mayor a menor.
8. **Barras "Mix de ventas"**: eje `Proveedor[Origen_PROVEEDOR]`, valor `% del Total Venta`.
9. **Nota al pie:** "La estacionalidad es real (peso de cada mes en la venta 2024–2025) y cambia con los filtros. Inventario estimado = compras − ventas desde ene-2024; se reemplazará por la tabla de inventario."

**Controles antes de seguir:**
- Sin filtros, el total de la columna "Total" de la estacionalidad debe dar **12,00**.
- Con año 2026 y sin filtros, `Crecimiento Obtenido %` debe dar lo mismo que en Resumen anual.
- Al elegir un proveedor, la estacionalidad debe cambiar.
- En el detalle: inventario inicial + compradas − vendidas = inventario final, en cada mes hasta abril de 2026.

---

## PÁGINA 2 · COMPRAS

### 1. Medidas (carpeta "Compras")

```dax
Comprado AA Matriz = COALESCE ( [Sell In (selector) AA], 0 )
```

```dax
Estacionalidad Compras =
VAR _meses = VALUES ( Calendario[Mes] )
VAR _total =
    CALCULATE ( [Sell In (selector)], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 } )
VAR _mes =
    CALCULATE ( [Sell In (selector)], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 }, _meses )
RETURN
    DIVIDE ( _mes, _total / 12 )
```

```dax
Unidades Sell In Var % YTD =
VAR _ult = CALCULATE ( MAX ( Compras[Fecha_Recepcion] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Unidades Sell In], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Unidades Sell In AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN DIVIDE ( _act - _aa, _aa )
```

```dax
Costo Promedio Pieza Compra = DIVIDE ( [Sell In (selector)], [Unidades Sell In] )
```

```dax
Factor Importación = DIVIDE ( [Importe Sell In], [Importe Sell In ExW] )
```

```dax
Lead Time Días =
AVERAGEX (
    FILTER (
        Compras,
        NOT ISBLANK ( Compras[Fecha_Invoice] )
            && Compras[Fecha_Recepcion] >= Compras[Fecha_Invoice]
    ),
    DATEDIFF ( Compras[Fecha_Invoice], Compras[Fecha_Recepcion], DAY )
)
```
Son los días desde la factura del proveedor hasta la recepción. Se excluyen las líneas sin fecha de factura y las que tienen la recepción antes de la factura (error de captura).

```dax
% Compra Global =
DIVIDE (
    [Sell In (selector)],
    CALCULATE ( [Sell In (selector)], REMOVEFILTERS ( Proveedor ), REMOVEFILTERS ( Marca ), REMOVEFILTERS ( Departamento ), REMOVEFILTERS ( Producto ) )
)
```

```dax
% del Total Compra = DIVIDE ( [Sell In (selector)], CALCULATE ( [Sell In (selector)], ALLSELECTED () ) )
```

```dax
Compras ÷ Ventas Uds = DIVIDE ( [Unidades Sell In], [Unidades Sell Out] )
```

```dax
% Compras Sin Clasificar =
DIVIDE ( CALCULATE ( [Sell In (selector)], Compras[Tipo_Movi] = "Sin clasificar" ), [Sell In (selector)] )
```

```dax
% Devoluciones a Proveedor =
DIVIDE ( - CALCULATE ( [Sell In (selector)], Compras[Cantidad] < 0 ), [Sell In (selector)] )
```

```dax
Det Compras ExW = COALESCE ( [Importe Sell In ExW], 0 )
```
```dax
Det Compras Puesto = COALESCE ( [Importe Sell In], 0 )
```

### 2. Visuales (misma estructura que Ventas)

1. **Título** "Reporte de compras · [año]". Añade también la segmentación **Costo Sell In** (`Tipo Costo`).
2. **Banda superior (matriz, valores en filas):** `Comprado AA Matriz` ("Comprado año anterior"), `S/I Matriz` ("Comprado") y `Estacionalidad Compras`, con el mismo formato que en Ventas. A la derecha, la tarjeta "Crec. YTD" con `Sell In Var %`.
3. **8 tarjetas:**

   | Tarjeta | Valor | Etiqueta de referencia |
   |---|---|---|
   | Compras $ (según selector) | `Sell In (selector)` | `Sell In Var %` + " vs AA" |
   | Compras $ Puesto | `Importe Sell In` | texto "costo nacionalizado" |
   | Unidades compradas | `Unidades Sell In` | `Unidades Sell In Var % YTD` |
   | Costo prom. pieza | `Costo Promedio Pieza Compra` | texto "según selector" |
   | Factor importación | `Factor Importación` (2 dec.) | texto "Puesto ÷ Ex-Work" |
   | Sell-through | `Sell-Through %` | texto "vendidas ÷ compradas" |
   | Lead time | `Lead Time Días` (0 dec.) | texto "factura → recepción" |
   | % compra global | `% Compra Global` | texto "del total empresa" |

4. **Detalle mensual de compras (matriz, valores en filas):**
   - Filas, en este orden: `Inventario Inicial (est.)`, `Det Unidades Compradas`, `Det Unidades Vendidas`, `Inventario Final (est.)`, `Det Compras ExW`, `Det Compras Puesto`, `Costo Promedio Pieza Compra` (1 dec.), `Factor Importación` (2 dec.), `Sell-Through %` (2 dec.), `Compras ÷ Ventas Uds` (2 dec.) y `Cobertura Meses` (1 dec.).
   - Etiquetas: "Inventario inicial", "Unidades compradas", "Unidades vendidas", "Inventario final", "Compras $ Ex-Work", "Compras $ Puesto", "Costo prom. pieza", "Factor importación", "Sell-through (uds.)", "Ratio de reposición" y "Cobertura (meses)".
5. **Columnas agrupadas** "Compras mensuales vs año anterior": `Sell In (selector) AA` (`#0B2A80`) y `Sell In (selector)` (`#1A73E8`).
6. **Barras** "Compras por departamento" con `% del Total Compra`. Debajo, un bloque "Origen y calidad" con tres valores:
   - % internacional: `% del Total Compra` filtrado a Origen = INTERNACIONAL, o una tarjeta.
   - `% Devoluciones a Proveedor`.
   - `% Compras Sin Clasificar`.
7. **Tabla "Ranking"** (mismo parámetro de campos o Marca):
   - Columnas: `Sell In (selector)`, `% del Total Compra`, `Sell In Var %`, `Unidades Sell In`, `Costo Promedio Pieza Compra`, `Factor Importación`, `Lead Time Días` y `Sell-Through %`.
   - Formato condicional con icono de semáforo en Sell-through: **verde ≥ 0,95**, **naranja 0,80–0,95** y **rojo < 0,80** (se acumula inventario).
8. **Nota al pie:** "Estacionalidad de compras = peso de cada mes en las compras 2024–2025. Ratio de reposición = unidades compradas ÷ vendidas."

**Controles:**
- Con Ex-Work y sin filtros, el total "Comprado" 2026 debe coincidir con el Sell In de la tarjeta de Resumen anual.
- Al cambiar a Puesto, debe subir o quedarse igual.
- `Factor Importación` debe estar alrededor de 1,1–1,3. Si da menos de 1, avísame.
- `Lead Time Días` sin filtros (todos los años) debe dar unos 30 días.

---

## Al terminar

Envíame un resumen con:
1. Las medidas creadas y cualquier error.
2. Los resultados de los controles.
3. Una captura de cada página.

No muestres importes reales en el resumen: solo indica si los controles cuadran.
