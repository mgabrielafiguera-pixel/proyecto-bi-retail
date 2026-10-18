# Modelo de datos · Retail BI

Fuente: [`retail_bi_powerbi.xlsx`](retail_bi_powerbi.xlsx) (10 tablas de Excel, una por hoja).
Datos anonimizados: códigos en lugar de nombres y montos escalados. Las proporciones y tendencias se mantienen, pero los montos absolutos no son los reales.

## 1. Relaciones

Esquema en estrella. Todas las relaciones son **uno a varios (1 → \*)**, con **dirección de filtro única** (de la dimensión hacia la tabla de hechos) y **activas**.

| # | Lado "uno" (dimensión) | Lado "varios" | Notas |
|---|---|---|---|
| 1 | `Producto[COD_SKU]` | `Ventas[COD_SKU]` | |
| 2 | `Producto[COD_SKU]` | `Compras[COD_SKU]` | |
| 3 | `Almacen[COD_ALMACEN]` | `Ventas[COD_ALMACEN]` | |
| 4 | `Almacen[COD_ALMACEN]` | `Compras[COD_ALMACEN]` | |
| 5 | `Proveedor[CODIGO_INTERNO_PROVEEDOR]` | `Ventas[CODIGO_INTERNO_PROVEEDOR]` | |
| 6 | `Proveedor[CODIGO_INTERNO_PROVEEDOR]` | `Compras[CODIGO_INTERNO_PROVEEDOR]` | |
| 7 | `Cliente[COD_CLIENTE]` | `Ventas[COD_CLIENTE]` | |
| 8 | `Vendedor[COD_VENDEDOR]` | `Ventas[COD_VENDEDOR]` | |
| 9 | `Marca[CODIGO_INTERNO_MARCA]` | `Producto[CODIGO_INTERNO_MARCA]` | Filtra Ventas y Compras a través de Producto |
| 10 | `Departamento[COD_DEPARTAMENTO]` | `Producto[COD_DEPARTAMENTO]` | Filtra Ventas y Compras a través de Producto |
| 11 | `Calendario[Fecha]` | `Ventas[Fecha]` | |
| 12 | `Calendario[Fecha]` | `Compras[Fecha_Recepcion]` | Las compras se fechan por la recepción, no por la factura |

**No crear estas relaciones** (crearían dos caminos entre Proveedor y las ventas, y Power BI daría un error de ambigüedad):

- `Proveedor` ↔ `Producto[CODIGO_INTERNO_PROVEEDOR]`
- `Proveedor` ↔ `Marca[CODIGO_INTERNO_PROVEEDOR]`

Esas columnas pueden quedarse como dato informativo (o, mejor, ocultas).

Todas las claves están completas: no hay ningún código en Ventas o Compras que falte en su dimensión.

### Ajustes del modelo

- **Calendario**: marcarla como *tabla de fechas* usando `Calendario[Fecha]`. Hay que poner `Fecha` como tipo *Fecha* (sin hora) en Calendario, Ventas y Compras. Sin esto, las medidas de año anterior no funcionan.
- `Calendario[Nombre_Mes]`: *Ordenar por columna* → `Mes`.
- Ocultar las columnas clave del lado "varios" (`COD_SKU`, `COD_ALMACEN`… en Ventas y Compras) y usar las de las dimensiones en los gráficos.
- Para filtrar por año o mes, usar siempre `Calendario`, no `Ventas[MES]` / `Ventas[ANIO]`. `MES` está en inglés y no filtra Compras.

## 2. Medidas DAX

Se recomienda crearlas en una tabla vacía llamada `Medidas`. Si Power BI rechaza las comas, la configuración regional espera `;` como separador: hay que cambiar `,` por `;`.

Convenciones:

- **Sell Out** = ventas a clientes (`Ventas`). **Sell In** = compras recibidas (`Compras`).
- Las cantidades e importes son **netos**: las devoluciones (cantidad negativa) restan.
- **AA** = año anterior (mismo periodo del año anterior). **Var %** = variación contra el año anterior. Para medidas que ya son %, la variación va en **puntos porcentuales (pp)**.

### Sell Out

```dax
Unidades Sell Out =
SUM ( Ventas[Cantidad] )
```

```dax
Importe Sell Out =
SUM ( Ventas[Total_Factura] )
```

```dax
Unidades Sell Out AA =
CALCULATE ( [Unidades Sell Out], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Unidades Sell Out Var % =
DIVIDE ( [Unidades Sell Out] - [Unidades Sell Out AA], [Unidades Sell Out AA] )
```

```dax
Importe Sell Out AA =
CALCULATE ( [Importe Sell Out], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Importe Sell Out Var % =
DIVIDE ( [Importe Sell Out] - [Importe Sell Out AA], [Importe Sell Out AA] )
```

### Sell In

```dax
Unidades Sell In =
SUM ( Compras[Cantidad] )
```

```dax
Importe Sell In =
SUM ( Compras[Total_Precio_Costo_Nacionalizado] )
```

```dax
Unidades Sell In AA =
CALCULATE ( [Unidades Sell In], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Unidades Sell In Var % =
DIVIDE ( [Unidades Sell In] - [Unidades Sell In AA], [Unidades Sell In AA] )
```

```dax
Importe Sell In AA =
CALCULATE ( [Importe Sell In], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Importe Sell In Var % =
DIVIDE ( [Importe Sell In] - [Importe Sell In AA], [Importe Sell In AA] )
```

### Sell-Through %

Unidades vendidas sobre unidades compradas en el mismo periodo. Por encima de 100 % significa que se vendió más de lo que entró (se consumió stock anterior).

```dax
Sell-Through % =
DIVIDE ( [Unidades Sell Out], [Unidades Sell In] )
```

```dax
Sell-Through % AA =
DIVIDE ( [Unidades Sell Out AA], [Unidades Sell In AA] )
```

```dax
Sell-Through % Var pp =
[Sell-Through %] - [Sell-Through % AA]
```

Esta versión ignora el filtro de `Almacen` solo en la parte de compras. Las ventas siguen filtradas por tienda, y se dividen entre todo lo comprado.

```dax
Sell-Through % (sin almacén) =
DIVIDE (
    [Unidades Sell Out],
    CALCULATE ( [Unidades Sell In], REMOVEFILTERS ( Almacen ) )
)
```

```dax
Sell-Through % (sin almacén) AA =
CALCULATE ( [Sell-Through % (sin almacén)], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Sell-Through % (sin almacén) Var pp =
[Sell-Through % (sin almacén)] - [Sell-Through % (sin almacén) AA]
```

**Cuál usar:** `Sell-Through %` en visuales sin tienda ni almacén (por producto, marca, proveedor, departamento o tiempo). `Sell-Through % (sin almacén)` cuando la página tenga un filtro de tienda: muestra qué parte de lo comprado vendió esa tienda.

> ⚠️ **El Sell-Through % no se analiza por tienda ni por almacén.** Todas las compras entran por un único almacén (`Almacén 1`) y desde ahí se traspasan a las tiendas. Esos traspasos no están en los datos. Por eso, si se filtra por tienda, `Sell-Through %` sale **en blanco** en cualquier tienda que no sea `Almacén 1`, y en `Almacén 1` da un valor engañoso (las ventas de ese almacén contra todas las compras). Analizar solo por **producto, marca, proveedor, departamento y tiempo**. Por tienda o almacén se analizan **solo las ventas**.

### Ticket Promedio

Importe de las líneas de factura (`Mov = "FACT"`) entre el número de facturas distintas. Una factura puede tener varias líneas, todas con el mismo `Num_Factura`.

```dax
Facturas =
CALCULATE ( DISTINCTCOUNT ( Ventas[Num_Factura] ), Ventas[Mov] = "FACT" )
```

```dax
Ticket Promedio =
DIVIDE (
    CALCULATE ( [Importe Sell Out], Ventas[Mov] = "FACT" ),
    [Facturas]
)
```

```dax
Ticket Promedio AA =
CALCULATE ( [Ticket Promedio], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Ticket Promedio Var % =
DIVIDE ( [Ticket Promedio] - [Ticket Promedio AA], [Ticket Promedio AA] )
```

### Margen

En el 40 % de las devoluciones, `Costo_Total_Facturado` viene en positivo aunque la cantidad sea negativa. Si se suma tal cual, cada devolución resta venta pero suma costo, y el margen sale más bajo de lo real. Esta medida le da al costo el mismo signo que la cantidad.

```dax
Costo Sell Out =
SUMX (
    Ventas,
    IF (
        Ventas[Cantidad] < 0,
        -ABS ( Ventas[Costo_Total_Facturado] ),
        ABS ( Ventas[Costo_Total_Facturado] )
    )
)
```

```dax
Margen =
[Importe Sell Out] - [Costo Sell Out]
```

```dax
Margen % =
DIVIDE ( [Margen], [Importe Sell Out] )
```

```dax
Margen AA =
CALCULATE ( [Margen], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Margen Var % =
DIVIDE ( [Margen] - [Margen AA], [Margen AA] )
```

```dax
Margen % AA =
CALCULATE ( [Margen %], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Margen % Var pp =
[Margen %] - [Margen % AA]
```

### Devoluciones

Líneas de venta con cantidad negativa (columna `Es_Devolucion = "Sí"`). Se muestran en positivo para leerlas con facilidad.

```dax
Unidades Devueltas =
-CALCULATE ( SUM ( Ventas[Cantidad] ), Ventas[Es_Devolucion] = "Sí" )
```

```dax
Importe Devoluciones =
-CALCULATE ( SUM ( Ventas[Total_Factura] ), Ventas[Es_Devolucion] = "Sí" )
```

```dax
Devoluciones % =
DIVIDE (
    [Importe Devoluciones],
    CALCULATE ( [Importe Sell Out], Ventas[Es_Devolucion] = "No" )
)
```

```dax
Unidades Devueltas AA =
CALCULATE ( [Unidades Devueltas], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Unidades Devueltas Var % =
DIVIDE ( [Unidades Devueltas] - [Unidades Devueltas AA], [Unidades Devueltas AA] )
```

```dax
Importe Devoluciones AA =
CALCULATE ( [Importe Devoluciones], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Importe Devoluciones Var % =
DIVIDE ( [Importe Devoluciones] - [Importe Devoluciones AA], [Importe Devoluciones AA] )
```

```dax
Devoluciones % AA =
CALCULATE ( [Devoluciones %], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Devoluciones % Var pp =
[Devoluciones %] - [Devoluciones % AA]
```

### Resumen anual (Fase 4)

Medidas y tablas añadidas para la página **Resumen anual**, una réplica de la hoja de Excel original del mismo nombre.

**Regla para comparar con el año anterior:** el año actual y el anterior se cortan en la **misma fecha**, que es la última venta cargada. Si no, un año incompleto se compara contra un año completo. En DAX, el corte se aplica *fuera* de la medida AA: `CALCULATE ( [X AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )`. Si `SAMEPERIODLASTYEAR` va en el mismo `CALCULATE` que el corte, el año anterior no se recorta.

#### Tablas sin relaciones (parámetros)

```dax
Tipo Costo =
DATATABLE (
    "Tipo Costo", STRING,
    "Orden", INTEGER,
    { { "Ex-Work", 1 }, { "Puesto", 2 } }
)
```

```dax
Proyeccion =
SELECTCOLUMNS ( GENERATESERIES ( 80, 200, 5 ), "Value", [Value] / 100 )
```

`GENERATESERIES ( 0.80, 2.00, 0.05 )` pierde el 2,00 por el redondeo de los decimales. Por eso la serie se genera con enteros y se divide entre 100.

#### Sell In según el tipo de costo

```dax
Importe Sell In ExW =
SUM ( Compras[Total_Costo_Ex_Works] )
```

```dax
Sell In (selector) =
SWITCH (
    SELECTEDVALUE ( 'Tipo Costo'[Tipo Costo], "Ex-Work" ),
    "Ex-Work", [Importe Sell In ExW],
    "Puesto",  [Importe Sell In]
)
```

```dax
Sell In (selector) AA =
CALCULATE ( [Sell In (selector)], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Sell In Var % =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Sell In (selector)], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Sell In (selector) AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN DIVIDE ( _act - _aa, _aa )
```

#### Matrices (meses sin datos en 0)

```dax
S/I Matriz = COALESCE ( [Sell In (selector)], 0 )
```

```dax
S/O Matriz = COALESCE ( [Importe Sell Out], 0 )
```

```dax
Histórico Crecimiento % =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Importe Sell Out], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Importe Sell Out AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN
    IF (
        NOT ISINSCOPE ( Calendario[Nombre_Mes] ),
        [Crecimiento Obtenido %],
        IF ( ISBLANK ( _act ) || _aa <= 0, 0, DIVIDE ( _act - _aa, _aa ) )
    )
```

En el total, el histórico devuelve la misma medida que la tarjeta "Crecimiento obtenido", así que los dos números siempre coinciden.

#### Tarjetas

```dax
Ratio Reposición = DIVIDE ( [Importe Sell Out], [Sell In (selector)] )
```

```dax
Ratio Reposición Unidades = DIVIDE ( [Unidades Sell Out], [Unidades Sell In] )
```

```dax
Proyección Crecimiento = SELECTEDVALUE ( Proyeccion[Value], 1.20 )
```

```dax
Crecimiento Obtenido % =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _act = CALCULATE ( [Importe Sell Out], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
VAR _aa  = CALCULATE ( [Importe Sell Out AA], KEEPFILTERS ( Calendario[Fecha] <= _ult ) )
RETURN DIVIDE ( _act - _aa, _aa )
```

```dax
Presupuesto Comercial =
VAR _anio = SELECTEDVALUE ( Calendario[Año] )
RETURN
    CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] = _anio - 1 )
        * [Proyección Crecimiento]
```

```dax
Avance Presupuesto % = DIVIDE ( [Importe Sell Out], [Presupuesto Comercial] )
```

El "Ratio Reposición" mezcla precio de venta (Sell Out) con costo (Sell In), así que sale inflado por el margen. La versión en unidades es la que mide la reposición real: si da más de 1, se está consumiendo stock.

#### Presupuesto top-down mensual

El presupuesto anual se reparte por mes con la estacionalidad del año anterior. No hace falta ninguna tabla de presupuesto.

```dax
Presupuesto Mes = [Importe Sell Out AA] * [Proyección Crecimiento]
```

```dax
Presupuesto Acumulado =
CALCULATE ( [Importe Sell Out AA], DATESYTD ( Calendario[Fecha] ) ) * [Proyección Crecimiento]
```

```dax
Sell Out Acumulado =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
RETURN
    IF (
        MIN ( Calendario[Fecha] ) > _ult,
        BLANK (),
        CALCULATE ( [Importe Sell Out], DATESYTD ( Calendario[Fecha] ) )
    )
```

```dax
Ritmo Esperado % =
VAR _ult = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS ( Calendario ) )
VAR _anio = SELECTEDVALUE ( Calendario[Año] )
VAR _aaHasta =
    CALCULATE (
        [Importe Sell Out], REMOVEFILTERS ( Calendario ),
        Calendario[Fecha] >= DATE ( _anio - 1, 1, 1 ),
        Calendario[Fecha] <= EDATE ( _ult, -12 )
    )
VAR _aaAnual =
    CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] = _anio - 1 )
RETURN DIVIDE ( _aaHasta, _aaAnual )
```

El "Ritmo esperado" es el % del año anterior que ya se había vendido a la misma fecha. Sirve para leer el "Avance del presupuesto": si vas por debajo del ritmo esperado, vas atrasada respecto al presupuesto.

#### Textos y colores de las tarjetas

```dax
Texto Var Sell In =
VAR g = [Sell In Var %]
RETURN IF ( g >= 0, "▲ ", "▼ " ) & FORMAT ( g, "0.0%", "es-ES" ) & " vs AA"
```

```dax
Texto Var Sell Out =
VAR g = [Crecimiento Obtenido %]
RETURN IF ( g >= 0, "▲ ", "▼ " ) & FORMAT ( g, "0.0%", "es-ES" ) & " vs AA"
```

```dax
Color Var Sell In = IF ( [Sell In Var %] >= 0, "#1F8A4C", "#C2412D" )
```

```dax
Color Var Sell Out = IF ( [Crecimiento Obtenido %] >= 0, "#1F8A4C", "#C2412D" )
```

En el modelo también están `Color Crec` (verde, rojo o gris para la fila "Crec. vs AA") y `Color Mes Futuro` (gris para los meses posteriores a la última venta). Esos textos fijos de las tarjetas están en la carpeta de medidas "Auxiliares".

### Filtros en cascada: Proveedor → Marca → Departamento

Proveedor no filtra Marca ni Departamento porque no hay relación entre esas tablas (ver la sección 1). En cambio, Marca y Departamento sí filtran Producto, y Producto tiene la columna del proveedor. Por eso basta una sola medida.

Esa medida se aplica como filtro de nivel de objeto visual (`Filtro Cascada` es 1) en las segmentaciones de **Marca** y **Departamento** de las páginas Ventas y Compras. No se aplica en Proveedor, que es el primer nivel. Resumen anual no tiene estas segmentaciones: es una vista global.

Orden de las segmentaciones: Año, Origen, Proveedor, Marca, Departamento.

```dax
Filtro Cascada =
VAR _prov = VALUES ( Proveedor[CODIGO_INTERNO_PROVEEDOR] )
RETURN
    IF (
        NOT ISEMPTY (
            FILTER ( Producto, Producto[CODIGO_INTERNO_PROVEEDOR] IN _prov )
        ),
        1
    )
```

### Formatos sugeridos

| Medidas | Formato |
|---|---|
| Unidades… | Número entero, separador de miles |
| Importe…, Margen, Margen AA, Costo Sell Out, Ticket Promedio… | Moneda o decimal con 2 decimales |
| … %, … Var % | Porcentaje, 1 decimal |
| … Var pp | Decimal con formato `+0.0%;-0.0%` (se lee como puntos porcentuales) |

## 3. Calidad de datos

No se borró ninguna fila. Los casos dudosos están marcados con columnas Sí/No en Ventas y Compras, para filtrarlos o excluirlos en el informe.

| Problema | Ventas | Compras | Cómo afecta |
|---|---|---|---|
| **Posibles duplicados** (`Es_Posible_Duplicado`): filas idénticas en todas las columnas. Se marcan todas las copias, incluida la primera | 1.780 filas (1.009 sobrantes) | 1.193 filas (599 sobrantes) | No hay número de línea, así que no se puede saber si son errores o dos piezas iguales en la misma factura. Si son errores, inflan unidades e importe |
| **Precio cero** (`Precio_Cero`) | 1.291 | 16 | En Ventas, 1.260 son facturas con total 0 (posibles obsequios o cambios). Suman unidades pero no importe, y bajan el ticket promedio |
| **Total no cuadra** (`Total_No_Cuadra`): el total se aleja más de un 1 % de cantidad × precio | 2.038 | 2 | Las medidas usan el total de la línea, no cantidad × precio |
| **Devoluciones** (`Es_Devolucion`): cantidad negativa | 1.695 | 493 | En Ventas: 1.485 son notas de crédito (`N/CR`) y 210 son facturas (`FACT`) con cantidad negativa. Además, 35 notas de crédito tienen cantidad positiva o cero y no cuentan como devolución |
| **Costo con signo incorrecto** en devoluciones | ~40 % de las devoluciones | — | Corregido en la medida `Costo Sell Out` |
| **Costo cero** | 1.070 | — | El margen de esas líneas sale al 100 %, así que el margen total queda algo inflado |
| **Sin fecha de factura** (`Sin_Fecha_Factura`) | — | 1.262 | No afecta: las compras se fechan por `Fecha_Recepcion`, que está completa |
| **Factura más de 60 días después de la recepción** | — | 470 | Revisar si la fecha de factura es fiable antes de usarla |
| **Ventas posteriores a abril de 2026** | 2.308 (mayo: 1.985, junio: 323) | — | El archivo original es de "Abril 2026". Pueden ser fechas mal escritas |
| **`Tipo_Movi` = "Sin clasificar"** | — | 1.384 (8,4 % del importe de Sell In) | **Compras pendientes de clasificar.** Venían con `Tipo_Movi` vacío y se rellenaron con "Sin clasificar" para que aparezcan en los gráficos por tipo de compra. Casi todas son de 2026 (1.263) y de proveedores internacionales, y tampoco tienen `Factor_Importacion`. Se incluyen en Sell In |
| **Costo Ex-Work atípico** | — | 4 | Son 4 devoluciones del mismo SKU en marzo de 2026. Tienen un costo Ex-Work unitario unas 1.800 veces mayor que el de su compra y el costo nacionalizado vacío. Dejan Accesorios en negativo con el selector en Ex-Work. **Decisión (15-oct-2026): se dejan como están** y la página lo explica en una nota al pie |
| **`Precio_Unitario_USD`** casi vacía | 18.774 de 49.936 con valor | — | No usarla en medidas |

### Rangos de fechas y comparaciones con el año anterior

- **Ventas**: 3-ene-2023 → 8-jun-2026. **Compras** (recepción): 10-ene-2024 → 30-abr-2026. **Calendario**: 1-ene-2023 → 31-dic-2026.
- No hay compras en 2023. En 2023, Sell In es 0, y en 2024 el Sell In AA está vacío. El Sell-Through % solo tiene sentido desde 2024.
- 2026 está incompleto. Si se filtra el año 2026 completo, se compara medio año contra 2025 entero. Para comparar bien hay que filtrar por meses (ene–abr para Sell In, ene–jun para Sell Out).

### Almacenes: compras y ventas

- **Compras** entran por **1 almacén** (`Almacén 1`, almacén central). **Ventas** salen por **11 almacenes** (de los 13 de la tabla `Almacen`; `Almacén 2` y `Almacén 5` están inactivos y sin ventas). `Almacén 1` también vende: concentra 39.984 de las 49.936 líneas de venta.
- Los traspasos del almacén central a las tiendas se dejaron fuera a propósito. Ver la advertencia en la sección *Sell-Through %*.

### "Compra Interna" (226 líneas)

Son compras reales y se incluyen en Sell In. No son traspasos. Representan el 3,2 % del importe de Sell In (unas 754.800 en total) y 1.870 unidades. Lo que tienen en común:

- **Almacén**: todas entran por `Almacén 1`, como el resto de compras.
- **Proveedor**: 39 proveedores, sobre todo **nacionales y locales** (184 de 226 líneas). Los dos principales son `PROV0048` (68 líneas, marca propia `MARC0003`) y `PROV0052` (39 líneas, servicios). Varios de estos proveedores solo aparecen en Compra Interna.
- **Producto**:
  - Sobre todo **joyería de oro**: 147 líneas de JOYERIA (oro amarillo y oro blanco; anillos, cadenas, zarcillos).
  - 128 líneas son de **marca propia** (`MARC0003` / `MARC0004`).
  - 32 son **baterías de litio** y 17 son **servicios de orfebrería** (departamento SERVICIOS).
  - El precio unitario mediano (451) es mucho mayor que el de una compra nacional (102).
- **Costos**: sin costo de importación. En 129 líneas `Factor_Importacion = 1` y `Margen_Nacionalizacion = 0`, y en el 77 % el costo nacionalizado es igual al Ex Works. La mayoría no tiene orden de compra (148) ni factura de proveedor (160).
- **Fechas**: de 19-ene-2024 a 20-abr-2026, repartidas en 116 documentos de recepción, sin un periodo concreto. En 148 líneas el producto aparece por primera vez en esa recepción.
- **Lectura probable**: producción o compra local de joyería de marca propia (orfebres o talleres) y suministros de servicio técnico, más que importaciones. Pendiente de confirmar.

### Compras: devoluciones duplicadas con costo erróneo

Hay 6 filas de Compras con `Es_Posible_Duplicado = Sí` y `Precio_Cero = Sí`. Son devoluciones duplicadas que no tienen costo nacionalizado. Cuatro de ellas, de marzo de 2026, traen un costo Ex-Work unitario de 242.042, cuando la mediana ronda los 200. Restan unos 968 mil al Ex-Work de 2026.

Con esas filas, el factor de importación de 2026 sale en 1,88 y el de marzo en −9,88. Sin ellas, sale en 1,27 y 1,19. Se excluyen en Power Query, en el paso "Excluir errores de captura".

En 2026, las compras "Sin clasificar" siguen siendo cerca del 45 % del Ex-Work. Es un dato real, no un error.

### Inventario

Tabla `Inventario`: stock por SKU al cierre de cada mes, de dic-2023 a abr-2026. Columnas: `COD_SKU`, `Fecha` (último día del mes), `Unidades`, `Origen` y `Venta_Sin_Stock`. La genera `scripts/reconstruir_inventario.py`.

Relaciones nuevas (uno a varios, filtro único):

- `Producto[COD_SKU]` → `Inventario[COD_SKU]`
- `Calendario[Fecha]` → `Inventario[Fecha]`

Origen de cada mes:

| Periodo | Origen | Cómo se obtiene |
|---|---|---|
| dic-2023 a jun-2025 | Real | Foto de inventario de cierre de mes. Los negativos se dejan en 0. |
| jul-2025 a dic-2025 | Estimado calibrado | Kardex desde jun-2025 (IF = IF anterior + compras − ventas, mínimo 0). El total de las 41 marcas del resumen por marca se ajusta a la tendencia de ese resumen. |
| ene-2026 a abr-2026 | Estimado kardex | Kardex desde dic-2025, sin ancla. |

`Venta_Sin_Stock = Sí` marca los meses en que el kardex habría quedado negativo: se vendió más de lo registrado, por una recepción no registrada o por un error de inventario. No es lo mismo que un quiebre; el quiebre se mide en DAX (stock 0 con venta reciente).

**Backtest** (se reconstruyó ene–jun 2025 desde la foto de dic-2024 y se comparó con las fotos reales):

| Mes | Kardex: error del total | Calibrado: error del total | Calibrado: WAPE por SKU |
|---|---|---|---|
| 2025-01 | −2,9 % | −7,1 % | 7 % |
| 2025-03 | −17,8 % | −15,1 % | 21 % |
| 2025-06 | −22,1 % | −7,3 % | 39 % |

Lectura: el kardex puro se queda corto con el tiempo porque en el primer semestre de 2025 entró mercancía que no está en Compras. La calibración corrige el total (error ±10 %), pero el reparto por SKU pierde precisión. La calibración usa el resumen por marca de los mismos meses que evalúa, así que el −7,3 % no es la precisión de una estimación a ciegas: esa es la del kardex puro (−22,1 % a 6 meses). Tabla completa y fórmulas en [`docs/validacion.md`](../docs/validacion.md). Por eso los indicadores de inventario se leen a nivel de marca, departamento o total, no de SKU. En 2026 no hay ancla, así que hay que esperar un sesgo a la baja de hasta un 15–20 % hacia abril.

SKU sin movimiento: 1.220 productos tienen stock pero ninguna venta ni compra entre 2023 y 2026. Se agregaron a `Producto` con código `SKUI#####`, `en_ventas = N` y `en_compras = N`. Son unas 22 mil unidades del total histórico de fotos y forman la base del análisis de inventario obsoleto.

### Ya resuelto en el Excel

- Hojas convertidas en tablas de Excel con nombres simples, sin filas de control ("Total", "Control", "Resultado").
- Eliminadas las columnas vacías `Compras[Lead_Time_Dias]` y `Marca[TIPO_PROVEEDOR]`.
- `Producto[PESO_GR]` es numérico. Las celdas con texto vacío ahora están vacías de verdad.
- `CATEGORIA_LOTUS` renombrada a `CATEGORIA_VENTA`.
- Tabla `Calendario` añadida con nombres de mes en español.

## 4. Medidas por página

Código DAX de las páginas 2 a 6, tal como se creó en Power BI Service. Las medidas base (Sell In, Sell Out, margen,
devoluciones, Resumen anual) están en la sección 2. Si Power BI rechaza las comas, la configuración regional espera `;`.

### Power Query · Compras: paso "Excluir errores de captura"

Excluye las 6 devoluciones duplicadas con costo erróneo (ver la sección 3). Compras queda en 16.715 filas.

```m
= Table.SelectRows(#"Paso anterior", each not ([Es_Posible_Duplicado] = "Sí" and [Precio_Cero] = "Sí"))
```

### Ventas y Compras (páginas 2 y 3)

#### Ventas

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

```dax
Det Unidades Compradas = COALESCE ( [Unidades Sell In], 0 )
```

```dax
Det Unidades Vendidas = COALESCE ( [Unidades Sell Out], 0 )
```

```dax
Det Monto Vendido = COALESCE ( [Importe Sell Out], 0 )
```

#### Compras

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

### Inventario (página 4)

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
VAR _u = [Fecha Ultimo Inventario]
RETURN CALCULATE ( [Unidades Sell Out], KEEPFILTERS ( Calendario[Fecha] <= _u ) )
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
Cobertura Meses Real =
VAR _f = EOMONTH ( MIN ( MAX ( Calendario[Fecha] ), [Fecha Ultimo Inventario] ), 0 )
VAR _venta =
    DIVIDE ( CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _f, -3, MONTH ) ), 3 )
RETURN DIVIDE ( [Stock Final Uds], _venta )
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

```dax
Inventario Final (est.) = [Stock Final Uds]
```

```dax
Inventario Inicial (est.) = [Stock Inicial Uds]
```

### Punto de reorden (página 4)

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

### Budget / Forecast (página 5)

```dax
Fecha Corte Forecast = [Fecha Ultimo Inventario]
```

```dax
Estacionalidad Uds =
VAR _meses = VALUES ( Calendario[Mes] )
VAR _total =
    CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 } )
VAR _mes =
    CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 }, _meses )
RETURN DIVIDE ( _mes, _total / 12 )
```

#### Budget

```dax
Budget $ =
VAR _anual = [Presupuesto Comercial]
RETURN SUMX ( VALUES ( Calendario[Mes] ), _anual * [Estacionalidad Ventas] / 12 )
```

```dax
Budget Uds =
VAR _anio = SELECTEDVALUE ( Calendario[Año] )
VAR _anual =
    CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ), Calendario[Año] = _anio - 1 )
        * [Proyección Crecimiento]
RETURN SUMX ( VALUES ( Calendario[Mes] ), _anual * [Estacionalidad Uds] / 12 )
```

```dax
Budget Acumulado $ = CALCULATE ( [Budget $], DATESYTD ( Calendario[Fecha] ) )
```

```dax
Estacionalidad Compras ExW =
VAR _meses = VALUES ( Calendario[Mes] )
VAR _total =
    CALCULATE ( [Importe Sell In ExW], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 } )
VAR _mes =
    CALCULATE ( [Importe Sell In ExW], REMOVEFILTERS ( Calendario ), Calendario[Año] IN { 2024, 2025 }, _meses )
RETURN DIVIDE ( _mes, _total / 12 )
```

```dax
Budget Compras $ =
VAR _anio = SELECTEDVALUE ( Calendario[Año] )
VAR _anual =
    CALCULATE ( [Importe Sell In ExW], REMOVEFILTERS ( Calendario ), Calendario[Año] = _anio - 1 )
        * [Proyección Crecimiento]
RETURN SUMX ( VALUES ( Calendario[Mes] ), _anual * [Estacionalidad Compras ExW] / 12 )
```

#### Bases del forecast

```dax
Pieza Promedio Mensual =
VAR _c = [Fecha Corte Forecast]
RETURN
    DIVIDE ( CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _c, -12, MONTH ) ), 12 )
```

```dax
Precio Promedio Venta 12M =
VAR _c = [Fecha Corte Forecast]
RETURN
    CALCULATE ( DIVIDE ( [Importe Sell Out], [Unidades Sell Out] ), REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _c, -12, MONTH ) )
```

```dax
Costo Promedio ExW 12M =
VAR _c = [Fecha Corte Forecast]
RETURN
    CALCULATE ( DIVIDE ( [Importe Sell In ExW], [Unidades Sell In] ), REMOVEFILTERS ( Calendario ),
        DATESINPERIOD ( Calendario[Fecha], _c, -12, MONTH ) )
```

#### Forecast

```dax
Forecast SO Uds =
VAR _c = [Fecha Corte Forecast]
VAR _pieza = [Pieza Promedio Mensual]
RETURN
    SUMX (
        VALUES ( Calendario[Año_Mes] ),
        IF ( CALCULATE ( MIN ( Calendario[Fecha] ) ) > _c, _pieza * [Estacionalidad Uds] )
    )
```

```dax
Forecast SO $ = [Forecast SO Uds] * [Precio Promedio Venta 12M]
```

```dax
Rolling SO Uds =
VAR _c = [Fecha Corte Forecast]
RETURN
    SUMX (
        VALUES ( Calendario[Año_Mes] ),
        IF ( CALCULATE ( MAX ( Calendario[Fecha] ) ) <= _c, [Unidades Sell Out] + 0, [Forecast SO Uds] )
    )
```

```dax
Forecast SI Uds =
VAR _c = [Fecha Corte Forecast]
RETURN
    SUMX (
        VALUES ( Calendario[Año_Mes] ),
        VAR _ini = CALCULATE ( MIN ( Calendario[Fecha] ) )
        RETURN
            IF ( _ini > _c,
                CALCULATE ( [Rolling SO Uds], REMOVEFILTERS ( Calendario ),
                    DATESBETWEEN ( Calendario[Fecha], EOMONTH ( _ini, -2 ) + 1, EOMONTH ( _ini, -1 ) ) ) )
    )
```

```dax
Forecast SI $ = [Forecast SI Uds] * [Costo Promedio ExW 12M]
```

#### Rolling Forecast

```dax
Real SO $ =
VAR _c = [Fecha Corte Forecast]
RETURN CALCULATE ( [Importe Sell Out], KEEPFILTERS ( Calendario[Fecha] <= _c ) )
```

```dax
Rolling SO $ =
VAR _c = [Fecha Corte Forecast]
RETURN
    SUMX (
        VALUES ( Calendario[Año_Mes] ),
        IF ( CALCULATE ( MAX ( Calendario[Fecha] ) ) <= _c, [Importe Sell Out] + 0, [Forecast SO $] )
    )
```

```dax
Rolling SI Uds =
VAR _c = [Fecha Corte Forecast]
RETURN
    SUMX (
        VALUES ( Calendario[Año_Mes] ),
        IF ( CALCULATE ( MAX ( Calendario[Fecha] ) ) <= _c, [Unidades Sell In] + 0, [Forecast SI Uds] )
    )
```

```dax
Rolling SI $ =
VAR _c = [Fecha Corte Forecast]
RETURN
    SUMX (
        VALUES ( Calendario[Año_Mes] ),
        IF ( CALCULATE ( MAX ( Calendario[Fecha] ) ) <= _c, [Importe Sell In ExW] + 0, [Forecast SI $] )
    )
```

```dax
Stock Proyectado Uds =
VAR _c = [Fecha Corte Forecast]
VAR _fin = MAX ( Calendario[Fecha] )
RETURN
    IF (
        _fin <= _c,
        [Stock Final Uds],
        VAR _ifc = CALCULATE ( SUM ( Inventario[Unidades] ), REMOVEFILTERS ( Calendario ), Inventario[Fecha] = _c )
        VAR _soc = CALCULATE ( [Unidades Sell Out], REMOVEFILTERS ( Calendario ),
            DATESBETWEEN ( Calendario[Fecha], EOMONTH ( _c, -1 ) + 1, _c ) )
        VAR _som = CALCULATE ( [Forecast SO Uds], REMOVEFILTERS ( Calendario ),
            DATESBETWEEN ( Calendario[Fecha], EOMONTH ( _fin, -1 ) + 1, EOMONTH ( _fin, 0 ) ) )
        RETURN MAX ( 0, _ifc + _soc - _som )
    )
```

```dax
Rolling Acumulado $ = CALCULATE ( [Rolling SO $], DATESYTD ( Calendario[Fecha] ) )
```

```dax
Real Acumulado $ =
VAR _c = [Fecha Corte Forecast]
RETURN IF ( MIN ( Calendario[Fecha] ) > _c, BLANK (), CALCULATE ( [Importe Sell Out], DATESYTD ( Calendario[Fecha] ) ) )
```

```dax
Var RF vs Budget % = DIVIDE ( [Rolling SO $] - [Budget $], [Budget $] )
```

```dax
Brecha vs Budget $ = [Rolling SO $] - [Budget $]
```

```dax
Real SI $ =
VAR _c = [Fecha Corte Forecast]
RETURN CALCULATE ( [Importe Sell In ExW], KEEPFILTERS ( Calendario[Fecha] <= _c ) )
```

```dax
Var Compras RF vs Budget % = DIVIDE ( [Rolling SI $] - [Budget Compras $], [Budget Compras $] )
```

```dax
Color Var Compras = IF ( [Var Compras RF vs Budget %] > 0, "#C2412D", "#1F8A4C" )
```

```dax
Avance Real vs Budget % = DIVIDE ( [Real SO $], [Budget $] )
```

```dax
Color Var Budget = IF ( [Var RF vs Budget %] < 0, "#C2412D", "#1F8A4C" )
```

```dax
Color Mes Forecast =
IF ( MIN ( Calendario[Fecha] ) > [Fecha Corte Forecast], "#F3F5F9", "#FFFFFF" )
```

### Ventas diarias (página 6)

```dax
Dia = DAY ( Calendario[Fecha] )
```

```dax
Ubicacion = Almacen[DIRECCION] & ", " & Almacen[CIUDAD] & ", " & Almacen[ESTADO] & ", " & Almacen[PAIS]
```

```dax
Ciudad Estado = Almacen[CIUDAD] & ", " & Almacen[ESTADO] & ", " & Almacen[PAIS]
```

```dax
Estado Pais = Almacen[ESTADO] & ", Venezuela"
```

`Estado Pais` tiene la categoría "Estado o provincia" y es la ubicación del mapa coroplético (Azure Maps, capa de relleno).
El color sale de reglas sobre `% Part Tienda`: más de 50 %, 10–50 %, 5–10 %, 1–5 % y menos de 1 %.

#### Rango de datos y periodo comparable

```dax
Fecha Primera Venta = CALCULATE ( MIN ( Ventas[Fecha] ), REMOVEFILTERS () )
```

```dax
Fecha Ultima Venta = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS () )
```

```dax
Periodo Comparable =
VAR _fin = MAX ( Calendario[Fecha] )
VAR _ini = MIN ( Calendario[Fecha] )
RETURN _fin <= [Fecha Ultima Venta] && EDATE ( _ini, -12 ) >= EOMONTH ( [Fecha Primera Venta], -1 ) + 1
```

#### Gráfico diario

```dax
Venta Diaria =
IF (
    MAX ( Calendario[Fecha] ) < [Fecha Primera Venta] || MIN ( Calendario[Fecha] ) > [Fecha Ultima Venta],
    BLANK (),
    [Importe Sell Out] + 0
)
```

```dax
Uds Diarias =
IF (
    MAX ( Calendario[Fecha] ) < [Fecha Primera Venta] || MIN ( Calendario[Fecha] ) > [Fecha Ultima Venta],
    BLANK (),
    [Unidades Sell Out] + 0
)
```

```dax
Facturas Diarias =
IF (
    MAX ( Calendario[Fecha] ) < [Fecha Primera Venta] || MIN ( Calendario[Fecha] ) > [Fecha Ultima Venta],
    BLANK (),
    [Facturas] + 0
)
```

```dax
Titulo Ventas Diarias =
VAR _mes = SELECTEDVALUE ( Calendario[Nombre_Mes] )
VAR _anio = SELECTEDVALUE ( Calendario[Año] )
RETURN
    IF (
        ISBLANK ( _mes ) || ISBLANK ( _anio ),
        "Ventas diarias · elige un mes y un año",
        "Ventas diarias · " & _mes & " " & _anio
    )
```

```dax
Nota Periodo =
IF (
    MAX ( Calendario[Fecha] ) > [Fecha Ultima Venta],
    "Datos hasta el " & FORMAT ( [Fecha Ultima Venta], "d-mmm-yyyy", "es-ES" ) & ". El resto del mes no tiene datos.",
    ""
)
```

#### Variaciones de las tarjetas

```dax
Var Ventas Diarias % =
VAR _aa = [Importe Sell Out AA]
RETURN IF ( [Periodo Comparable] && _aa > 0, DIVIDE ( [Importe Sell Out] - _aa, _aa ) )
```

```dax
Var Uds Diarias % =
VAR _aa = [Unidades Sell Out AA]
RETURN IF ( [Periodo Comparable] && _aa > 0, DIVIDE ( [Unidades Sell Out] - _aa, _aa ) )
```

```dax
Var Ticket Diarias % =
VAR _aa = [Ticket Promedio AA]
RETURN IF ( [Periodo Comparable] && _aa > 0, DIVIDE ( [Ticket Promedio] - _aa, _aa ) )
```

```dax
Var Margen Diarias pp =
VAR _aa = [Margen % AA]
VAR _baseAA = [Importe Sell Out AA]
RETURN IF ( [Periodo Comparable] && _baseAA > 0, [Margen %] - _aa )
```

```dax
Devoluciones % AA Diarias =
CALCULATE ( [Devoluciones %], SAMEPERIODLASTYEAR ( Calendario[Fecha] ) )
```

```dax
Var Devoluciones Diarias pp =
VAR _baseAA = [Importe Sell Out AA]
RETURN IF ( [Periodo Comparable] && _baseAA > 0, [Devoluciones %] - [Devoluciones % AA Diarias] )
```

```dax
Texto Var Ventas Diarias =
VAR g = [Var Ventas Diarias %]
RETURN IF ( ISBLANK ( g ), "sin comparable", IF ( g >= 0, "▲ ", "▼ " ) & FORMAT ( g, "0.0%", "es-ES" ) & " vs año anterior" )
```

```dax
Texto Var Margen Diarias =
VAR g = [Var Margen Diarias pp]
RETURN IF ( ISBLANK ( g ), "sin comparable", IF ( g >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( g ) * 100, "0.0", "es-ES" ) & " pp vs año anterior" )
```

#### Líderes del periodo

```dax
Marca Lider =
VAR _t =
    TOPN ( 1, FILTER ( VALUES ( Marca[CODIGO_INTERNO_MARCA] ), [Importe Sell Out] > 0 ),
        [Importe Sell Out], DESC, Marca[CODIGO_INTERNO_MARCA], ASC )
RETURN MAXX ( _t, Marca[CODIGO_INTERNO_MARCA] )
```

```dax
Venta Marca Lider =
VAR _m = [Marca Lider]
RETURN CALCULATE ( [Importe Sell Out], Marca[CODIGO_INTERNO_MARCA] = _m )
```

```dax
% Marca Lider = DIVIDE ( [Venta Marca Lider], [Importe Sell Out] )
```

#### Participación en los rankings

```dax
% Part Marca = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], ALLSELECTED ( Marca ) ) )
```

```dax
% Part Proveedor = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], ALLSELECTED ( Proveedor ) ) )
```

```dax
% Part Vendedor = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], ALLSELECTED ( Vendedor ) ) )
```

```dax
% Part Tienda = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], ALLSELECTED ( Almacen ) ) )
```

Las tablas Top 5 de proveedor y vendedor usan `REMOVEFILTERS` en lugar de `ALLSELECTED`: con un filtro Top N en el
visual, `ALLSELECTED` repartiría el 100 % entre los cinco.

```dax
% Venta Proveedor Periodo = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Proveedor ) ) )
```

```dax
% Venta Vendedor Periodo = DIVIDE ( [Importe Sell Out], CALCULATE ( [Importe Sell Out], REMOVEFILTERS ( Vendedor ) ) )
```

Las medidas Texto Var de esta página terminan en "vs. mismo mes año anterior".
