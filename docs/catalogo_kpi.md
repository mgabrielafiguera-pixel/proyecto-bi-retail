# Catálogo de indicadores (KPI)

Cada indicador es una medida DAX del modelo **Retail BI v2**. El código está en
[`03_powerbi/MODELO.md`](../03_powerbi/MODELO.md). Las cifras de
ejemplo son del año 2026 con todos los filtros en "Todas", y salen de los controles de cada prompt o de
[`resultados/hallazgos.md`](resultados/hallazgos.md).

Convenciones: **SO** = Sell Out (ventas a clientes). **SI** = Sell In (compras recibidas). Las unidades e importes son
netos (las devoluciones restan). **AA** = mismo periodo del año anterior, cortado a la misma fecha.

## Ventas y compras

| KPI | Objetivo de negocio | Fórmula | Unidad | Granularidad válida | Interpretación | Limitaciones | Decisiones |
|---|---|---|---|---|---|---|---|
| **Sell Out** (`Importe Sell Out`) | Medir la venta | Σ Ventas[Total_Factura] | Moneda (escalada) | Cualquiera | Venta neta de devoluciones | Importes escalados por la anonimización. Incluye posibles duplicados (1,95 %) | Seguimiento contra el budget |
| **Sell In** (`Sell In (selector)`) | Medir lo comprado | Σ costo Ex-Work o puesto de Compras, según el selector | Moneda | Producto, marca, proveedor, departamento, tiempo | Ex-Work = precio de fábrica; puesto = con flete y aranceles | Fechado por recepción. Excluye 6 errores de captura | Control del presupuesto de compras |
| **Variación vs AA** (`Crecimiento Obtenido %`, `Sell In Var %`) | Ver si se crece | (actual − AA) / AA, con los dos años cortados a la misma fecha | % | Cualquiera | Positivo = crecimiento | Con base AA ≤ 0 el signo pierde sentido. El corte actual usa la última venta: ver `auditoria_dax.md`, D2 | Detectar marcas o departamentos que caen |
| **Sell-through** (`Sell-Through %`) | ¿Se vende lo que se compra? | Unidades SO / Unidades SI, mismo periodo | Ratio | Producto, marca, proveedor, departamento, tiempo. **No por tienda** | > 1: se consume stock anterior. < 1: se acumula | Sin sentido por tienda: todas las compras entran por el Almacén 1 y no hay traspasos. Desde 2024 (no hay compras de 2023) | Frenar compras con sell-through bajo y sostenido |
| **Ticket promedio** | Valor por transacción | Importe de facturas (Mov = FACT) / nº de facturas | Moneda | Tiempo, tienda, vendedor | Baja con la mezcla hacia productos más baratos | 210 devoluciones registradas como FACT lo reducen | Estrategia de precio y surtido |
| **Margen %** | Rentabilidad bruta | (Sell Out − costo con signo) / Sell Out | % | Cualquiera | Margen bruto sobre venta | Costo 0 en 1.070 líneas (0,6 % del importe) lo infla. Sin gastos operativos | Priorizar categorías con margen alto |
| **Devoluciones %** | Calidad de la venta | Importe devuelto / venta sin devoluciones | % | Cualquiera | Porcentaje de la venta que vuelve | 35 notas de crédito con cantidad ≥ 0 no cuentan | Revisar productos o vendedores con devolución alta |
| **Lead time** (`Lead Time Días`) | Plazo de reposición | Media por línea de (fecha de recepción − fecha de factura), solo si la recepción es posterior | Días | Proveedor, marca, tiempo | Unos 32 días de media | 1.262 líneas sin fecha de factura y 470 facturas fechadas más de 60 días después de la recepción (excluidas). Es un promedio por línea, no por pedido | Base del punto de reorden |
| **Factor de importación** | Costo de nacionalizar | Costo puesto / costo Ex-Work | Ratio | Proveedor, tiempo | 1,27 en 2026 | 1.384 compras "Sin clasificar" no tienen factor | Negociación de fletes y aranceles |

## Inventario

| KPI | Objetivo de negocio | Fórmula | Unidad | Granularidad válida | Interpretación | Limitaciones | Decisiones |
|---|---|---|---|---|---|---|---|
| **Stock final** (`Stock Final Uds`) | Cuánto hay | Σ unidades de Inventario el último día del periodo (sin pasar del último inventario) | Unidades | Total, departamento, marca. SKU con cautela | Foto a fin de mes: no se suma entre meses | Estimado desde jul-2025 (columna `Origen`). En 2026 tiende a subestimar | Base de todos los KPI de inventario |
| **Inventario promedio** | Base de rotación | Media del stock final de los meses del periodo | Unidades | Igual que el stock | | Igual que el stock | |
| **Rotación anualizada** | Velocidad de venta del stock | (Unidades vendidas / inventario promedio) × 12 / meses del periodo | Veces al año | Total, departamento, marca | 1,41 veces en 2025 | En unidades, no en valor: un reloj y una batería pesan igual | Comparar categorías y marcas |
| **Días de inventario** | Lo mismo, en días | 365 / rotación anualizada | Días | Igual que la rotación | Días que dura el stock al ritmo del periodo | Igual que la rotación | |
| **Cobertura** (`Cobertura Meses Real`) | ¿Cuántos meses de venta hay en stock? | Stock al corte / venta media mensual de los 3 meses anteriores | Meses | Total, departamento, marca | > 12 meses = sobrestock | Sensible a meses atípicos (diciembre) | Liquidar o frenar compras |
| **Stock sin venta 12M** | Stock inmovilizado | Unidades en stock de SKU sin ninguna venta en los 12 meses anteriores / stock | % | Total, departamento, marca | 46 % en abr-2026 | Incluye 1.220 SKU sin ningún movimiento desde 2023 | Plan de liquidación |
| **SKU en quiebre** | Riesgo de rotura | SKU con venta en los últimos 3 meses y stock 0 al corte / SKU con venta | % | Total, departamento, marca | Proporción de lo que se vende y ya no hay | En lujo cada SKU tiene 1 o 2 unidades: un quiebre por SKU es normal y no siempre es pérdida | Reposición de referencias top |
| **Venta perdida estimada** | Costo del quiebre | Σ venta media mensual (3M) de los SKU en quiebre | Moneda/mes | Total, departamento, marca | Orden de magnitud | Supone que la demanda sigue igual; no considera sustitución | Priorizar pedidos |
| **Valor del inventario a costo** | Capital inmovilizado | Σ unidades × costo unitario del SKU (compras; si no hay, ventas; si no, la marca) | Moneda | Total, departamento, marca | | Costo medio histórico, no costo de reposición | Decisiones de liquidación |

## Reposición

Se calcula por marca, departamento o total, **no por SKU**: en lujo la demanda por SKU es esporádica.

| KPI | Objetivo de negocio | Fórmula | Unidad | Interpretación | Limitaciones | Decisiones |
|---|---|---|---|---|---|---|
| **Demanda mensual** | Base de reposición | Unidades vendidas en los 6 meses anteriores al corte / 6 | Unidades/mes | | No separa la estacionalidad | |
| **Stock de seguridad** | Colchón para variaciones | 1,65 × σ de la demanda mensual × √(lead time en meses) | Unidades | Nivel de servicio del 95 % | Supone una demanda aproximadamente normal | |
| **Punto de reorden** | Cuándo pedir | Demanda × lead time + stock de seguridad | Unidades | Por debajo de este nivel, hay que pedir | | Política (s, S) |
| **Marcas a reponer** | Lista de acción | Marcas con demanda y stock ≤ punto de reorden | Nº | 7 de 88 en abr-2026 | | Pedido a esos proveedores |
| **Compra sugerida** | Cuánto pedir | Σ (punto de reorden + 1 mes de demanda − stock) de las marcas a reponer | Unidades y costo | 308 uds. en abr-2026 | No considera mínimos de pedido | Orden de compra |
| **Marcas en sobrestock** | Lista de freno | Marcas con stock > 12 meses de demanda | Nº | 38 de 88 en abr-2026 | | Frenar compras, liquidar |

## Presupuesto y forecast

| KPI | Objetivo de negocio | Fórmula | Unidad | Interpretación | Limitaciones | Decisiones |
|---|---|---|---|---|---|---|
| **Estacionalidad** (ventas, unidades, compras) | Repartir el año por meses | Valor del mes en 2024–2025 / (total de 2024–2025 / 12) | Índice (suma 12) | Diciembre: 2,95 en importe y 2,46 en unidades | Años escritos en la fórmula | Base del budget y del forecast |
| **Budget** | Meta del año | Venta (o compra Ex-Work) del año anterior × proyección × estacionalidad / 12 | Moneda | Fijo: no cambia con la venta real | Top-down, sin detalle por tienda o vendedor | Meta comercial |
| **Forecast** | Estimación de los meses que faltan | Pieza promedio 12M × estacionalidad; importe = unidades × precio medio 12M; compra = venta del mes anterior | Unidades y moneda | Proyección determinística, no un modelo estadístico | Sin tendencia: en el backtest subestimó un 15,6 % en unidades y un 30 % en importe | |
| **Rolling Forecast** | Cierre esperado del año | Real hasta el corte + forecast después | Moneda | −22,5 % contra el budget de 2026 | Probablemente conservador (ver `validacion.md`) | Ajustar compras y metas |
| **Avance del presupuesto** | ¿Vamos al ritmo? | Venta real / budget, junto al ritmo esperado (lo vendido a la misma fecha del año anterior) | % | Si el avance es menor que el ritmo esperado, se va atrasado | | Acciones comerciales |
| **Stock proyectado** | Stock al final del año | Stock al corte + venta real del mes de corte − venta forecast del mes | Unidades | 12.711 uds. a dic-2026 | Supone que se compra lo vendido el mes anterior | Plan de compras |
