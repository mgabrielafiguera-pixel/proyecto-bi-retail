Trabaja en Power BI Service, en "Mi área de trabajo": informe **Sell In Sell Out v2**, modelo semántico **Retail BI v2**. Crea la página **Budget / Forecast**, que reúne Budget, Forecast y Rolling Forecast **de ventas (Sell Out) y de compras (Sell In, a costo Ex-Work)**.

## Criterio

- **Mes de corte:** 30-abr-2026, la fecha del último inventario (`[Fecha Ultimo Inventario]`). Hasta ese mes se usa el dato real. Desde mayo, el forecast. Las ventas reales de mayo y junio de 2026 quedan fuera a propósito, porque no hay compras ni inventario de esos meses.
- **Budget de ventas:** venta del año anterior × `Proyección Crecimiento`, repartida por mes con la **estacionalidad de ventas** 2024–2025. Es fijo: no cambia con lo que se venda.
- **Budget de compras:** compras Ex-Work del año anterior × `Proyección Crecimiento`, repartidas por mes con la **estacionalidad de compras** 2024–2025.
- **Forecast** (meses después del corte), con la lógica del Excel de trabajo:
  - Venta (uds.) = pieza promedio mensual (últimos 12 meses) × estacionalidad en unidades.
  - Compra (uds.) = venta del mes anterior.
  - Inventario final = inventario inicial + compras − ventas.
  - Venta $ = uds. × precio promedio de venta de los últimos 12 meses.
  - Compra $ = uds. × costo Ex-Work promedio de los últimos 12 meses.
- **Rolling Forecast:** real hasta el corte + forecast después. Es la mejor estimación del cierre del año y se compara contra el Budget.
- La estacionalidad, el Budget y el forecast respetan los filtros de proveedor, marca y departamento.

## PASO 0 · Antes de tocar nada

- No reemplaces el modelo ni subas el Excel.
- No modifiques ninguna medida existente. En particular, `Presupuesto Mes` y `Presupuesto Acumulado` de Resumen anual se quedan como están.

## PASO 1 · Medidas (tabla Medidas, carpeta "Budget Forecast")

Si Power BI rechaza las comas, cambia `,` por `;`. Si alguna medida no admite otra medida dentro de un filtro, guárdala antes en una variable.

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

### Budget

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
Igual que `Estacionalidad Compras`, pero siempre a costo Ex-Work, sin depender del selector Tipo Costo.

```dax
Budget Compras $ =
VAR _anio = SELECTEDVALUE ( Calendario[Año] )
VAR _anual =
    CALCULATE ( [Importe Sell In ExW], REMOVEFILTERS ( Calendario ), Calendario[Año] = _anio - 1 )
        * [Proyección Crecimiento]
RETURN SUMX ( VALUES ( Calendario[Mes] ), _anual * [Estacionalidad Compras ExW] / 12 )
```

### Bases del forecast

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

### Forecast

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
Compra del mes = venta del mes anterior. La compra de mayo es la venta real de abril.

```dax
Forecast SI $ = [Forecast SI Uds] * [Costo Promedio ExW 12M]
```

### Rolling Forecast

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
Como la compra de cada mes es la venta del mes anterior, el inventario de un mes de forecast es: inventario de abril + venta real de abril − venta forecast del mes.

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
En compras, pasarse del budget es lo que se marca en rojo.

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

Formatos: importes en **miles** sin decimales; unidades sin decimales con miles; porcentajes con 1 decimal; estacionalidad con 2 decimales; precio y costo promedio con 0 decimales.

## PASO 2 · Página Budget / Forecast

Duplica la página **Ventas** (hereda fondo, segmentaciones sincronizadas con cascada y estilo) y llámala **Budget / Forecast**. Borra los visuales que no sirvan.

1. **Segmentaciones a la izquierda:** Año (selección única, 2026 por defecto), Origen, Proveedor, Marca, Departamento y **Proyección de crecimiento** (`Proyeccion`, igual que en Resumen anual).
2. **Panel "Bases del forecast"** (boceto: `04_presentacion/budget_forecast_propuesta.png`) bajo las segmentaciones: `Pieza Promedio Mensual` (uds./mes), `Precio Promedio Venta 12M` y `Costo Promedio ExW 12M`, con la nota "últimos 12 meses al 30-abr-2026".
3. **Tarjetas arriba, en dos filas:**
   Fila Ventas:
   - Budget anual → `Budget $`, subtítulo "venta año anterior × proyección".
   - Real a abril → `Real SO $`, subtítulo `Avance Real vs Budget %` & " del budget".
   - Forecast may–dic → `Forecast SO $`.
   - Cierre estimado (Rolling) → `Rolling SO $`.
   - Var. vs Budget → `Var RF vs Budget %`, color con `Color Var Budget`, subtítulo `Brecha vs Budget $`.
   - Stock proyectado a dic. → `Stock Proyectado Uds`, en uds.
   Fila Compras (Ex-Work):
   - Budget compras → `Budget Compras $`.
   - Real compras a abril → `Real SI $`.
   - Forecast compras may–dic → `Forecast SI $`.
   - Cierre estimado compras → `Rolling SI $`.
   - Var. vs Budget compras → `Var Compras RF vs Budget %`, color con `Color Var Compras`.
4. **Matriz mensual** (columnas = `Calendario[Nombre_Mes]` ordenado por Mes, valores en filas, con total):
   - Bloque $: **primera fila** `Estacionalidad Ventas` ("Estacionalidad", fondo `#FCEDE7`, negrita), porque es la base del Budget y del Forecast. Después `Budget $` ("Budget"), `Real SO $` ("Real"), `Forecast SO $` ("Forecast"), `Rolling SO $` ("Rolling Forecast", en negrita) y `Var RF vs Budget %` ("Var. vs Budget", color de fuente con `Color Var Budget`).
   - Bloque compras $: **primera fila** `Estacionalidad Compras ExW` ("Estacionalidad compras", fondo `#FCEDE7`, negrita). Después `Budget Compras $` ("Budget compras"), `Real SI $` ("Real"), `Forecast SI $` ("Forecast"), `Rolling SI $` ("Rolling Forecast compras", en negrita) y `Var Compras RF vs Budget %` ("Var. vs Budget", color con `Color Var Compras`).
   - Bloque uds.: `Rolling SO Uds` ("Venta uds."), `Rolling SI Uds` ("Compra uds.") y `Stock Proyectado Uds` ("Inventario final uds.").
   - Si la matriz queda muy larga, haz dos matrices: Ventas arriba y Compras + unidades abajo.
   - Fondo de las columnas de forecast con `Color Mes Forecast`, para distinguirlas de los meses reales.
5. **Gráfico de líneas acumulado** por `Calendario[Nombre_Mes]`: `Budget Acumulado $` (azul oscuro `#0B2A80`, discontinua), `Rolling Acumulado $` (azul `#1A73E8`) y `Real Acumulado $` (naranja `#E4643F`). Título "Budget vs Rolling Forecast acumulado".
6. **Nota al pie:** "Real hasta el 30-abr-2026 (último inventario). Forecast: venta = pieza promedio 12M × estacionalidad; compra = venta del mes anterior; IF = II + SI − SO. Budget = año anterior × proyección, repartido con la estacionalidad 2024–2025 (de ventas o de compras). Compras a costo Ex-Work."
7. Guarda el informe.

## PASO 3 · Controles

Año 2026, `Proyección Crecimiento` = 1,20, sin otros filtros (aprox.; si algo se desvía más del 2 %, avísame antes de seguir):

| Control | Valor |
|---|---|
| `Estacionalidad Uds`, total del año | 12,00 |
| Budget 2026 | ≈ 24.101.761 (venta 2025 × 1,20) |
| Budget ene–abr | ≈ 5.171.425 |
| Real ene–abr | ≈ 3.914.756 (4.399 uds.) |
| Pieza promedio mensual | ≈ 1.573 uds. |
| Precio promedio venta 12M | ≈ 1.048 |
| Costo promedio Ex-Work 12M | ≈ 544 |
| Forecast may–dic | ≈ 14.098 uds. · ≈ 14.772.444 |
| Rolling Forecast 2026 | ≈ 18.687.201 |
| Var. vs Budget | ≈ −22,5 % |
| Compra mayo | 1.129 uds. (venta real de abril) |
| Inventario final mayo | ≈ 14.551 uds. |
| Inventario final diciembre | ≈ 12.711 uds. |
| `Estacionalidad Compras ExW`, total del año | 12,00 |
| Budget compras 2026 | ≈ 9.376.735 (compras Ex-Work 2025 × 1,20) |
| Budget compras ene–abr | ≈ 1.688.360 |
| Real compras ene–abr | ≈ 2.976.207 (5.669 uds.) |
| Forecast compras may–dic | ≈ 11.357 uds. · ≈ 6.172.826 |
| Rolling Forecast compras 2026 | ≈ 9.149.033 |
| Var. compras vs Budget | ≈ −2,4 % |

Comprueba también que con Año 2025 el Rolling Forecast sea igual al real de cada mes y que al elegir un proveedor cambien la estacionalidad, el Budget y el forecast.

Repórtame los controles, cualquier cambio que hayas tenido que hacer en las fórmulas y una captura de la página.
