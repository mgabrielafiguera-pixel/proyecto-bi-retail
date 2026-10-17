Trabaja en Power BI Service, en "Mi área de trabajo": informe **Sell In Sell Out v2**, modelo semántico **Retail BI v2**. Hay que crear una página nueva, **Ventas diarias**, con las ventas día a día del mes elegido, el mapa de ventas por tienda y los rankings de marca, proveedor y vendedor.

## Criterio

- **Página nueva.** La página **Ventas** ya está terminada (cascada Proveedor → Marca → Departamento). No la modifiques.
- **Se reutilizan las medidas que ya existen y están revisadas**: `Importe Sell Out`, `Unidades Sell Out`, `Facturas`, `Ticket Promedio`, `Margen %`, `Devoluciones %` y sus versiones AA (año anterior). Solo se crean las medidas de esta página, en la carpeta "Ventas diarias".
- **Grano:** Ventas tiene una fila por línea de factura. La fecha es `Ventas[Fecha]` y la tienda `Ventas[COD_ALMACEN]`. Cada línea trae su proveedor (`Ventas[CODIGO_INTERNO_PROVEEDOR]`, relacionado con Proveedor) y su vendedor (`Ventas[COD_VENDEDOR]`, relacionado con Vendedor, sin vacíos). La marca llega por Producto. Todas son relaciones uno a varios: no hay doble conteo.
- **Días sin venta:** dentro del rango de datos (3-ene-2023 a 8-jun-2026) se muestran en 0. Fuera de ese rango van en blanco, para que un mes sin datos no parezca un mes con venta cero.
- **Comparación con el año anterior:** solo cuando el periodo está completo (termina antes de la última venta) y el año anterior tiene venta positiva. Si no, la tarjeta dice "sin comparable".
- Importes en la moneda del modelo (escalados). Sin símbolo de moneda.

## PASO 0 · Antes de tocar nada

- No reemplaces el modelo ni subas el Excel.
- No modifiques ninguna medida ni página existente.
- Respaldo de medidas: en la vista de consultas DAX ejecuta
  `EVALUATE SELECTCOLUMNS ( INFO.VIEW.MEASURES (), "Tabla", [Table], "Medida", [Name], "DAX", [Expression] )`
  y entrégame el resultado.
- Comprueba que `Importe Sell Out`, `Unidades Sell Out`, `Facturas`, `Ticket Promedio`, `Margen %`, `Devoluciones %`, `Importe Sell Out AA`, `Unidades Sell Out AA`, `Ticket Promedio AA` y `Margen % AA` existen. Si falta alguna, detente y avísame.

## PASO 1 · Columnas calculadas

En **Calendario**:

```dax
Dia = DAY ( Calendario[Fecha] )
```
Tipo número entero, sin resumir.

En **Almacen** (para el mapa):

```dax
Ubicacion = Almacen[DIRECCION] & ", " & Almacen[CIUDAD] & ", " & Almacen[ESTADO] & ", " & Almacen[PAIS]
```

```dax
Ciudad Estado = Almacen[CIUDAD] & ", " & Almacen[ESTADO] & ", " & Almacen[PAIS]
```

Si el editor lo permite, pon la categoría de datos de `Ubicacion` en **Dirección** y la de `Ciudad Estado` en **Lugar**.

## PASO 2 · Medidas (tabla Medidas, carpeta "Ventas diarias")

Si Power BI rechaza las comas, cambia `,` por `;`.

### Rango de datos y periodo comparable

```dax
Fecha Primera Venta = CALCULATE ( MIN ( Ventas[Fecha] ), REMOVEFILTERS () )
```

```dax
Fecha Ultima Venta = CALCULATE ( MAX ( Ventas[Fecha] ), REMOVEFILTERS () )
```

El periodo es comparable si termina antes de la última venta y el mismo periodo del año anterior cae dentro de los datos (desde ene-2023).

```dax
Periodo Comparable =
VAR _fin = MAX ( Calendario[Fecha] )
VAR _ini = MIN ( Calendario[Fecha] )
RETURN _fin <= [Fecha Ultima Venta] && EDATE ( _ini, -12 ) >= EOMONTH ( [Fecha Primera Venta], -1 ) + 1
```

### Gráfico diario

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

### Variaciones de las tarjetas

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

Texto del subtítulo de cada tarjeta (crea una para cada variación, cambiando la medida y el formato: `0.0%` para %, `+0.0;-0.0` & " pp" para puntos):

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

En devoluciones, que suba es malo: usa el color rojo `#C2412D` cuando `Var Devoluciones Diarias pp` > 0 y verde `#1F8A4C` cuando sea < 0. En el resto, al revés.

### Líderes del periodo

El empate se resuelve por código, en orden alfabético.

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

Crea las mismas tres medidas para Proveedor (`Proveedor Lider`, `Venta Proveedor Lider`, `% Proveedor Lider`, con `Proveedor[CODIGO_INTERNO_PROVEEDOR]`) y para Vendedor (`Vendedor Lider`, `Venta Vendedor Lider`, `% Vendedor Lider`, con `Vendedor[COD_VENDEDOR]`).

### Participación en los rankings

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

Formatos: importes sin decimales con separador de miles; unidades y facturas enteras; ticket con 2 decimales; porcentajes con 1 decimal.

## PASO 3 · Página "Ventas diarias"

Página nueva, 16:9, fondo `#F5F7FA`. Tarjetas y visuales en blanco, borde `#E1E4E9` de 1 px, esquinas de 8 px, sombra suave. Títulos en azul oscuro `#0B2A80`. Barras en azul `#1A73E8`. Unidades en turquesa `#14B8A6`.

### Cabecera

- Título "Ventas diarias" y subtítulo "Venta, unidades y rankings del mes elegido, por tienda. Importes escalados."
- Tres segmentaciones desplegables a la derecha, **sin sincronizar con otras páginas**:
  - **Tienda:** `Almacen[COD_ALMACEN]`, selección múltiple con "Seleccionar todo". Filtro de visual: `Almacen[ESTADO_ALMACEN]` = ACTIVO.
  - **Mes:** `Calendario[Nombre_Mes]` (ordenado por `Mes`), **selección única**.
  - **Año:** `Calendario[Año]`, **selección única**.
- Un botón **"Borrar todas las segmentaciones"** (Insertar → Botones → Borrar todas las segmentaciones) para restablecer.
- Bajo la cabecera, un cuadro de texto con la medida `Nota Periodo` (solo se ve en meses incompletos).

### Fila 1 · 5 tarjetas

| Tarjeta | Valor | Subtítulo |
|---|---|---|
| Ventas | `Importe Sell Out` | `Texto Var Ventas Diarias` |
| Unidades | `Unidades Sell Out` | texto de `Var Uds Diarias %` |
| Ticket promedio | `Ticket Promedio` | texto de `Var Ticket Diarias %` |
| Margen bruto | `Margen %` | `Texto Var Margen Diarias` |
| Devoluciones | `Devoluciones %` | texto de `Var Devoluciones Diarias pp` |

### Fila 2, izquierda (2/3 del ancho) · Gráfico diario

- **Gráfico de columnas agrupadas y líneas.**
- Eje X: `Calendario[Dia]`, tipo **categórico**, con "Mostrar elementos sin datos" activado.
- Columnas: `Venta Diaria` en `#1A73E8`. Línea: `Uds Diarias` en `#14B8A6`, en el **eje Y secundario**.
- Título: formato condicional (fx) con la medida `Titulo Ventas Diarias`.
- Información sobre herramientas: `Calendario[Fecha]` (primero), `Venta Diaria`, `Uds Diarias` y `Facturas Diarias`.
- Etiquetas de datos desactivadas. Ejes con el inicio en 0.

### Fila 2, derecha (1/3) · Mapa de ventas por tienda

1. En Visualizaciones, comprueba si está disponible el **Mapa de Azure**. Si no aparece o da un aviso de que está deshabilitado por el administrador, usa la alternativa del punto 5 y avísame.
2. Ubicación: `Almacen[Ubicacion]`. Leyenda: `Almacen[COD_ALMACEN]`. Tamaño: `Importe Sell Out`. Información sobre herramientas: `Almacen[COD_ALMACEN]`, `Importe Sell Out`, `Unidades Sell Out` y `% Part Tienda`.
3. Burbujas: escala de tamaño **logarítmica**, si el visual la ofrece. El Almacén 1 hace casi toda la venta y con escala lineal las demás tiendas no se ven.
4. Comprueba que cada burbuja cae en su ciudad. Si la dirección completa no se geocodifica bien, cambia la ubicación a `Almacen[Ciudad Estado]`. **No escribas coordenadas a mano.**
5. **Si no hay mapa disponible:** gráfico de barras horizontales "Ventas por tienda" con `Almacen[COD_ALMACEN]`, `Importe Sell Out` y `% Part Tienda` en la información sobre herramientas.

Hay 11 tiendas con ventas, pero solo 9 direcciones: dos pares de tiendas comparten dirección, y 5 tiendas están en la misma ciudad. Sus burbujas se superponen. La leyenda y la información sobre herramientas las separan.

### Fila 3 · Rankings (tres tarjetas del mismo alto)

**Izquierda · "Marca más vendida"**
- Tarjeta de varias filas: `Marca Lider`, `Venta Marca Lider` y `% Marca Lider` ("de la venta del periodo").
- Debajo, barras horizontales con las **8 primeras marcas** (`Marca[CODIGO_INTERNO_MARCA]`, `Importe Sell Out`, filtro de visual N superior = 8 por `Importe Sell Out`). Etiqueta: `% Part Marca`. Uso barras y no dona porque con 141 marcas una dona de las 8 primeras no muestra el resto y las proporciones engañan.

**Centro · "Proveedor con mayores ventas"**
- Tarjeta: `Proveedor Lider`, `Venta Proveedor Lider` y `% Proveedor Lider`.
- Barras con los 5 primeros (`Proveedor[CODIGO_INTERNO_PROVEEDOR]`, N superior = 5). Etiqueta: `% Part Proveedor`.
- Nota al pie: "Proveedor registrado en cada línea de venta".

**Derecha · "Vendedor con mayores ventas"**
- Tarjeta: `Vendedor Lider`, `Venta Vendedor Lider` y `% Vendedor Lider`.
- Barras con los 5 primeros (`Vendedor[COD_VENDEDOR]`, N superior = 5). Etiqueta: `% Part Vendedor`.

### Interacciones (Formato → Editar interacciones)

- Las tres segmentaciones filtran toda la página.
- Un clic en una tienda del mapa, o en una barra de marca, proveedor o vendedor, **filtra** (no resalta) el gráfico diario, las tarjetas y los otros rankings.
- Pruébalas de verdad: haz clic y comprueba que el resto cambia.

Guarda el informe con **Abril 2026** y todas las tiendas, el último mes con inventario.

## PASO 4 · Controles

Repórtame los valores y una captura de cada escenario. Si algo se desvía más del 1 %, avísame antes de seguir.

**Escenario A · Todas las tiendas, abril 2024**

| Control | Valor esperado |
|---|---|
| Ventas | 742.138 |
| Unidades | 1.246 |
| Facturas (información sobre herramientas, total del mes) | 840 |
| Ticket promedio | 1.047,60 |
| Margen | 38,6 % |
| Devoluciones | 15,7 % |
| Var. ventas vs abr-2023 | ≈ +720 % (2023 tiene mucha menos venta; la cifra es correcta, no un error) |
| Días en el eje | 1 a 30; día con más venta: 25 (71.887) |
| Marca líder | `MARC0004`, 97.360, 13,1 % |
| 5 proveedores | `PROV0049` 12,7 % · `PROV0065` 10,9 % · `PROV0062` 9,9 % · `PROV0050` 9,4 % · `PROV0069` 8,6 % |
| 5 vendedores | `VEND0002` 40,6 % · `VEND0004` 9,4 % · `VEND0031` 6,5 % · `VEND0006` 6,4 % · `VEND0017` 5,9 % |
| Mapa | Solo 2 tiendas con venta: Almacén 1 (99,1 %) y Almacén 7 |

**Escenario B · Almacén 7, abril 2024**

| Control | Valor esperado |
|---|---|
| Ventas · unidades · facturas | 6.381 · 156 · 100 |
| Ticket · margen · devoluciones | 63,81 · 65,0 % · 0,0 % |
| Días | 30 en el eje, 29 con venta y 1 en 0 |
| Marca líder | `MARC0002`, 88,0 % |
| Proveedor líder | `PROV0069`, 96,4 % |
| Vendedor | `VEND0001`, 100 % |
| Var. margen vs abr-2023 | Saldrá muy alta: en abr-2023 esta tienda vendió solo 214 con margen negativo. Es el dato, no un error |

**Escenario C · Todas las tiendas, febrero 2024 y mayo 2024**

| Control | Febrero 2024 | Mayo 2024 |
|---|---|---|
| Días en el eje | 1 a 29 (año bisiesto) | 1 a 31 |
| Ventas | 1.319.807 | 1.235.764 |
| Unidades | 1.418 | 1.976 |

**Escenario D · Todas las tiendas, abril 2025**

| Control | Valor esperado |
|---|---|
| Ventas · unidades · facturas | 914.584 · 1.047 · 761 |
| Ticket · margen · devoluciones | 1.303,29 · 36,6 % · 7,8 % |
| Var. vs abr-2024 | Ventas +23,2 % · unidades −16,0 % · ticket +24,4 % · margen −2,0 pp · devoluciones −7,9 pp |
| Líderes | `MARC0016` 22,0 % · `PROV0050` 21,9 % · `VEND0002` 50,5 % |

**Escenario E · Junio 2026 y clic en el mapa**

- Junio 2026: ventas 273.000, días 1 a 8 con barras, del 9 al 30 sin barra. Las tarjetas dicen "sin comparable" y aparece la nota de datos hasta el 8-jun-2026.
- Con abril 2024, haz clic en el Almacén 7 del mapa: las tarjetas y los rankings deben mostrar los valores del escenario B.

## Repórtame

1. Los controles de los 5 escenarios, con capturas.
2. Si el Mapa de Azure estaba disponible y qué ubicación usaste (dirección completa o ciudad).
3. Cualquier medida que hayas tenido que cambiar y por qué.
