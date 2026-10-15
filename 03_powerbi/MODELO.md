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

### Filtro Marca dependiente de Proveedor

Proveedor no filtra Marca porque no hay relación entre ellas (ver la sección 1). Para que la segmentación de Marca muestre solo las marcas del proveedor elegido, se usa esta medida como filtro de nivel de objeto visual (`Marca del Proveedor` es 1) en la segmentación de Marca:

```dax
Marca del Proveedor =
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

**No incluido por ahora.** Las tablas de inventario (existencias por almacén y fecha) se añadirán en una fase posterior. Hasta entonces, no hay medidas de stock, rotación ni cobertura.

### Ya resuelto en el Excel

- Hojas convertidas en tablas de Excel con nombres simples, sin filas de control ("Total", "Control", "Resultado").
- Eliminadas las columnas vacías `Compras[Lead_Time_Dias]` y `Marca[TIPO_PROVEEDOR]`.
- `Producto[PESO_GR]` es numérico. Las celdas con texto vacío ahora están vacías de verdad.
- `CATEGORIA_LOTUS` renombrada a `CATEGORIA_VENTA`.
- Tabla `Calendario` añadida con nombres de mes en español.
