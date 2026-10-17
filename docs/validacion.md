# Validación, backtesting y limitaciones

Todas las cifras de este documento se pueden reproducir con los scripts del repo (ver la sección 6).
Fecha de la última ejecución: 17-oct-2026.

## 1. Objetivo de la validación

La validación evalúa la consistencia de los datos, la fiabilidad de los indicadores y las limitaciones de la
reconstrucción histórica del inventario y del forecast. Se distinguen tres niveles:

| Nivel | Qué se comprueba | Dónde |
|---|---|---|
| Calidad de datos | Integridad, consistencia y trazabilidad de los registros | `scripts/validar_modelo.py` → [`resultados/controles_calidad.md`](resultados/controles_calidad.md) |
| Validación analítica | Que las medidas y los hallazgos del README salgan de los datos | Totales de control en `validar_modelo.py` y [`resultados/hallazgos.md`](resultados/hallazgos.md) |
| Backtesting | Comparar lo estimado con lo real en un periodo histórico | Inventario: `scripts/reconstruir_inventario.py` (función `backtest`). Forecast: `scripts/backtest_forecast.py` → [`resultados/backtest_forecast.md`](resultados/backtest_forecast.md) |

## 2. Backtest de la reconstrucción del inventario

### Parámetros

| Parámetro | Valor |
|---|---|
| Periodo evaluado | 6 meses: ene-2025 a jun-2025 |
| Punto de partida | Foto real de inventario por SKU al 31-dic-2024 |
| Variable evaluada | Unidades en stock por SKU al cierre de cada mes |
| Referencia | Fotos reales de inventario por SKU de cada cierre de mes (`02_anonimizado/inventario_sku_mes.csv`), negativos llevados a 0 |
| Método A: kardex puro | Stock = stock del mes anterior + compras recibidas − unidades vendidas, con mínimo 0. Usa solo movimientos |
| Método B: kardex calibrado | El método A, con el total de las 41 marcas del resumen de inventario por marca escalado para seguir el índice de ese resumen (stock del resumen en el mes / stock del resumen en dic-2024) |
| Error del total (firmado) | (Σ estimado − Σ real) / Σ real × 100, por mes. Negativo = el método subestima |
| Error por SKU (WAPE) | Σ \|estimado − real\| / Σ real × 100, por mes |

### Resultados

| Mes | A. Kardex puro: error del total | B. Calibrado: error del total | A. Kardex puro: WAPE por SKU | B. Calibrado: WAPE por SKU |
|---|---:|---:|---:|---:|
| ene-2025 | −2,9 % | −7,1 % | 3 % | 7 % |
| feb-2025 | −6,9 % | −7,0 % | 7 % | 7 % |
| mar-2025 | −17,8 % | −15,1 % | 18 % | 21 % |
| abr-2025 | −16,8 % | −9,5 % | 19 % | 27 % |
| may-2025 | −21,2 % | −10,3 % | 24 % | 35 % |
| jun-2025 | −22,1 % | **−7,3 %** | 27 % | 39 % |
| Media de los 6 meses | −14,6 % | −9,4 % | 16 % | 23 % |

La prueba `tests/test_backtest_inventario.py` comprueba estas cifras en cada ejecución.

### Qué significa el −7,3 %

1. Es el **error del total en el sexto mes** con el método calibrado. No es un promedio (la media es −9,4 %) ni un
   error por producto.
2. **Hay fuga de información en el método B.** La calibración usa el resumen de inventario por marca de los mismos
   meses que se evalúan, y ese resumen sale del mismo sistema de inventario que la referencia. Por eso el −7,3 % mide
   cuánto mejora la calibración cuando se conoce el total, no la precisión de una estimación hecha a ciegas.
3. El dato **sin fuga** es el del kardex puro: **−22,1 % a 6 meses**. Es el que aplica a ene–abr 2026, donde no hay
   resumen por marca para calibrar.
4. El **sesgo es negativo y crece con el tiempo**: entra mercancía que no queda registrada en Compras. Coincide con
   los 463 casos de venta sin stock registrado (hallazgo 4.7 del README).
5. Por SKU el error es alto: **WAPE 27 % con el kardex puro y 39 % con el calibrado** en el mes 6. La calibración
   mejora el total pero empeora el reparto por SKU, porque escala todos los SKU de una marca por igual. Los
   indicadores de inventario se leen por marca, departamento o total.
6. **No se usa MAPE**: muchos SKU tienen stock real 0, y el porcentaje por fila se dividiría entre cero. El WAPE pondera
   por volumen y no tiene ese problema.

### Cómo se usa en el modelo

| Periodo de la tabla Inventario | Origen | Precisión esperada |
|---|---|---|
| dic-2023 a jun-2025 | Foto real | Exacto |
| jul-2025 a dic-2025 | Kardex calibrado | Total ±10 % (según el backtest) |
| ene-2026 a abr-2026 | Kardex puro, sin ancla | Sesgo a la baja creciente; hasta −15 a −20 % en abril si se repite el patrón de 2025 |

El resultado vale para el periodo evaluado y no garantiza la misma precisión en otros periodos o condiciones.

## 3. Backtest del forecast de ventas

El forecast del informe es una **proyección determinística**, no un modelo estadístico ni de machine learning:

- unidades del mes = pieza promedio de los 12 meses anteriores al corte × índice de estacionalidad del mes;
- importe = unidades × precio promedio de los 12 meses anteriores al corte.

### Diseño

| Pliegue | Corte | Horizonte | Estacionalidad | Pieza y precio |
|---|---|---|---|---|
| Principal | 30-abr-2025 | may–dic 2025 | 2023 y 2024 | may-2024 a abr-2025 |
| Secundario | 30-abr-2024 | may–dic 2024 | 2023 | may-2023 a abr-2024 |

Para evitar fugas, cada pliegue solo usa datos anteriores al corte. El informe usa la estacionalidad 2024–2025 con
corte en abr-2026; esa configuración no se puede comprobar hasta tener may–dic 2026.

Se compara con dos métodos base: **ingenuo estacional** (mismo mes del año anterior) y **promedio plano** (pieza
promedio 12M sin estacionalidad).

### Resultados (pliegue principal, may–dic 2025)

| Nivel | Medida | WAPE informe | WAPE ingenuo | WAPE plano | Error del total, informe |
|---|---|---:|---:|---:|---:|
| Total mensual | Unidades | **15,9 %** | 22,7 % | 29,3 % | −15,6 % |
| Total mensual | Importe | **30,0 %** | 34,7 % | 39,6 % | −30,0 % |
| Departamento × mes | Unidades | **32,1 %** | 37,1 % | 40,7 % | −15,2 % |
| Departamento × mes | Importe | **32,0 %** | 39,4 % | 44,9 % | −29,9 % |
| Marca × mes | Unidades | 65,6 % | 69,6 % | **60,9 %** | −13,8 % |
| Marca × mes | Importe | 69,6 % | 73,9 % | **67,5 %** | −26,0 % |

Tabla completa, por mes y con el pliegue secundario, MAE, sesgo y MAPE: [`resultados/backtest_forecast.md`](resultados/backtest_forecast.md).

### Lectura

- **A nivel total y departamento, el método del informe es el mejor** de los tres en los dos pliegues. La
  estacionalidad capta el pico de diciembre.
- **Subestima siempre.** El método no tiene tendencia: si las ventas crecen, se queda corto. En importe el error es
  mayor porque el precio real de may–dic 2025 fue un 20,7 % más alto que el promedio de los 12 meses anteriores.
- **Por marca no es fiable** (WAPE 61–92 % según método y pliegue). A ese nivel sirve como orden de magnitud.
- **Implicación para 2026:** el Rolling Forecast (−22,5 % contra el budget) es probablemente **conservador**. Si se
  repite el sesgo de 2025, el cierre real quedaría por encima. Es una inferencia, no una cifra comprobada.

## 4. Controles de calidad y consistencia

`scripts/validar_modelo.py` ejecuta 68 controles sobre el Excel que lee Power BI. Resultado del 17-oct-2026:
**48 OK, 15 avisos, 5 a revisar y 0 errores**. Detalle: [`resultados/controles_calidad.md`](resultados/controles_calidad.md).

| Área | Controles ejecutados | Resultado |
|---|---|---|
| Integridad | Filas esperadas por tabla, claves únicas en las 8 dimensiones, nulos en campos críticos | OK. 15 compras sin costo nacionalizado (aviso) |
| Consistencia entre tablas | Claves huérfanas en las 11 relaciones; proveedor de cada venta o compra frente al de Producto; SKU sin movimiento | Sin huérfanas. 173 ventas y 55 compras tienen un proveedor distinto del de su producto (aviso) |
| Temporal | Fechas dentro del Calendario, inventario a fin de mes, ventas después del último inventario, orden factura-recepción | OK. 2.308 ventas de may–jun 2026 posteriores al último inventario (aviso). 470 facturas fechadas más de 60 días después de la recepción (revisar) |
| Importes | Devoluciones, costo con signo contrario, costo cero, duplicados, precio cero, compras excluidas, compras sin clasificar | Marcados y tratados en el modelo. A revisar en el origen: 210 devoluciones registradas como factura, 1.070 ventas con costo 0 y 1.384 compras sin clasificar |
| Inventario | Stock negativo, duplicados SKU + fecha, venta sin stock registrado | OK. 463 ventas sin stock registrado (aviso) |
| Totales | 4 totales de ventas y compras, y stock en 3 fechas, contra lo que muestra Power BI | 7 de 7 coinciden |
| Confidencialidad | Direcciones y ubicación de los almacenes | Aviso: se publican a propósito para el mapa de ventas por almacén |

**Validación temporal.** Los backtests usan solo información anterior a cada corte, salvo la calibración del método B
del inventario, que se declara como fuga en la sección 2.

**Validación de indicadores.** `scripts/hallazgos.py` recalcula las cifras de la sección de resultados del README
(52 de 52 coinciden). En la primera ejecución, sobre el README anterior, 44 de 51 coincidían y 7 no:

- 4 se habían calculado sin las correcciones del modelo: las compras de 2026 (3 veces, son 4,5 sin los 6 errores de
  captura) y 3 márgenes (sin corregir el signo del costo de las devoluciones);
- 2 usaban otra definición que la medida del modelo: facturas y ticket promedio (el modelo cuenta solo `Mov = FACT`);
- 1 era un redondeo: hacen falta 78 clientes, no 77, para llegar al 50 % de la venta.

El README ya usa las cifras del modelo, que son las que muestra Power BI.

## 5. Limitaciones

| Limitación | Efecto | Cómo se trata |
|---|---|---|
| Recepciones no registradas en Compras | El kardex subestima el stock | Calibración hasta dic-2025; en 2026 se declara el sesgo |
| Sin fotos de inventario desde jul-2025 | El stock de jul-2025 a abr-2026 es estimado | Columna `Origen` en la tabla Inventario |
| Traspasos entre almacenes fuera de los datos | El sell-through no se puede leer por tienda | Advertencia en `03_powerbi/MODELO.md` |
| 1.384 compras sin tipo de movimiento (8,4 % del Sell In) | No se puede separar importación de compra local | Incluidas en Sell In y marcadas |
| Posibles duplicados (1.009 líneas de venta sobrantes, 1,95 % del importe) | Pueden inflar unidades e importe | Marcados, no borrados: sin número de línea no se puede saber si son errores |
| 1.070 ventas con costo 0 (0,6 % del importe) | Margen ligeramente inflado | Marcado |
| Ventas de may–jun 2026 sin compras ni inventario | Comparaciones con distinto corte | El forecast las excluye. Ver `docs/auditoria_dax.md`, corte unificado |
| Forecast sin tendencia | Sesgo a la baja si el negocio crece | Documentado en la sección 3 |
| Importes escalados por la anonimización | Los importes absolutos no son los reales | Proporciones, unidades y fechas sí lo son |

Los resultados descriptivos no demuestran causalidad. Las causas del README fueron validadas con el negocio y se
indican como tales.

## 6. Transparencia y reproducibilidad

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validar_modelo.py        # controles de calidad
python3 scripts/hallazgos.py             # recalcula las cifras del README
python3 scripts/backtest_forecast.py     # backtest del forecast
python3 -m pytest tests                  # pruebas, incluido el backtest del inventario
```

El backtest del inventario se imprime al correr `scripts/reconstruir_inventario.py`. Ese script reescribe la tabla
`Inventario` del Excel, así que para solo consultar el backtest se usa la prueba de `tests/`, o el script sobre una
copia: `python3 scripts/reconstruir_inventario.py --xlsx /ruta/copia.xlsx`.

Los datos originales y las tablas de mapeo no están en el repo. La anonimización (`scripts/anonimizar_inventario.py`)
se corre en local sobre los originales.
