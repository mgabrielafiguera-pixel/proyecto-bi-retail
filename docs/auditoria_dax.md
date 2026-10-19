# Auditoría de DAX y Power Query

**Alcance.** Se revisó el código DAX documentado en el repo: [`03_powerbi/MODELO.md`](../03_powerbi/MODELO.md), secciones 2 y 4. El modelo vive en Power BI Service y **no hay exportación
del modelo** (`.pbix` o `.bim`). Por eso:

- no se puede confirmar que el código del Service sea idéntico al documentado;
- el número de medidas (unas 140) lo reportó Power BI, no se contó en el repo;
- las consultas de Power Query no están en el repo, salvo el paso de exclusión de errores de Compras.

Para cerrar esa brecha, conviene exportar las medidas con `INFO.VIEW.MEASURES ()`. Guardar ese
resultado en `03_powerbi/medidas_exportadas.csv` permitiría auditar el código real.

## Medidas por área funcional

| Área | Medidas principales | Documentadas en |
|---|---|---|
| Ventas | Unidades / Importe Sell Out, AA, Var %, Facturas, Ticket Promedio, Devoluciones | `MODELO.md` |
| Compras | Unidades / Importe Sell In, Importe Sell In ExW, Sell In (selector), Lead Time Días, Factor de importación | `MODELO.md`, secciones 1 y 4 |
| Margen | Costo Sell Out, Margen, Margen %, AA, Var | `MODELO.md` |
| Inventario | Stock Final / Inicial Uds, Inventario Promedio, Valor Inventario Costo, Stock Sin Venta 12M | `MODELO.md`, sección 4 |
| Rotación y cobertura | Rotacion Anualizada, Dias de Inventario, Cobertura Meses Real | `MODELO.md`, sección 4 |
| Quiebres | SKU Activos 3M, SKU en Quiebre, Venta Perdida Est. | `MODELO.md`, sección 4 |
| Reposición | Demanda Mensual, Desv Demanda, Lead Time Meses, Stock Seguridad, Punto de Reorden, Compra Sugerida | `MODELO.md`, sección 4 |
| Presupuesto | Presupuesto Comercial, Presupuesto Mes / Acumulado, Avance Presupuesto %, Ritmo Esperado %, Budget $ / Uds / Compras | `MODELO.md`, secciones 1 y 4 |
| Forecast | Estacionalidad Uds / Ventas / Compras, Pieza Promedio, Forecast SO / SI, Rolling, Stock Proyectado | `MODELO.md`, sección 4 |
| Comparativos | Crecimiento Obtenido %, Sell In Var %, Histórico Crecimiento %, Var RF vs Budget % | `MODELO.md`, secciones 1 y 4 |
| Auxiliares | Textos y colores de tarjetas, Filtro Cascada | `MODELO.md` |

## Hallazgos

Estado: **Comprobado** = verificado con los datos o el código. **Por validar** = requiere probarlo en Power BI.

| # | Medida o área | Problema | Estado | Impacto | Corrección |
|---|---|---|---|---|---|
| D1 | Medidas de Inventario con filtro de Proveedor | Proveedor no llega a Inventario (ver `docs/modelo_datos.md`). Con solo un proveedor elegido, el stock, la rotación y el punto de reorden mostrarían el total de la empresa | Por validar | Alto: rotación y cobertura mezclan ventas de un proveedor con stock de todos | Prueba en Power BI: elegir PROV0069 y comparar el stock con el total (2.547 frente a 15.452 uds.). Si falla: columna de proveedor en Inventario y relación con Proveedor |
| D2 | `Crecimiento Obtenido %`, `Sell In Var %`, `Histórico Crecimiento %`, `Ritmo Esperado %`, `Sell Out Acumulado` | El corte es la última venta (8-jun-2026), pero las compras terminan el 30-abr. La Var. Sell In 2026 sale +101 % en lugar de +346 % (Ex-Work). Además, el corte respeta los filtros de marca o proveedor | **Resuelto el 19-oct-2026** | Alto: la tarjeta de compras subestimaba el aumento a menos de un tercio | Aplicado: `Sell In Var %` corta en `CALCULATE ( MAX ( Compras[Fecha_Recepcion] ), REMOVEFILTERS () )` y las cuatro de Sell Out en `[Fecha Ultima Venta]`. Validado en el modelo: Ex-Work 2026 +346,3 % y Puesto +396,1 %; 2025 y las medidas de Sell Out sin filtros no cambian. Las cuatro medidas `Var % YTD` de Ventas aún usan el corte con `REMOVEFILTERS ( Calendario )` |
| D3 | `Presupuesto Comercial`, `Budget Uds`, `Budget Compras $` | Usan `SELECTEDVALUE ( Calendario[Año] )`: con varios años elegidos devuelven vacío | Comprobado en el código | Bajo: la página fuerza un solo año | Mantener la segmentación de año en selección única (ya está). Documentado |
| D4 | `Estacionalidad Uds / Ventas / Compras ExW` | Los años de referencia `{ 2024, 2025 }` están escritos en la fórmula | Comprobado en el código | Medio: en 2027 habrá que editar tres medidas | Documentado como supuesto. Alternativa: `Calendario[Año] IN { _anio - 2, _anio - 1 }` |
| D5 | `Stock Final Uds`, `Stock Inicial Uds`, `Meses con Inventario` | La fecha de inicio `DATE ( 2023, 12, 1 )` está escrita en la fórmula | Comprobado en el código | Bajo | Alternativa: `CALCULATE ( MIN ( Inventario[Fecha] ), REMOVEFILTERS () )` |
| D6 | Var % con base negativa | `DIVIDE ( a − b, b )` con `b < 0` invierte el signo. Pasa en Accesorios con Ex-Work en 2026, por 4 devoluciones con costo atípico | Comprobado (decisión del 15-oct: se dejan y la página lo explica) | Bajo | Si se quiere blindar: `IF ( _aa <= 0, BLANK (), DIVIDE ( _act − _aa, _aa ) )`, como ya hace `Histórico Crecimiento %` |
| D7 | `Ratio Reposición` | Divide venta a precio de venta entre compra a costo, así que el margen lo infla | Comprobado y documentado | Bajo | Ya existe `Ratio Reposición Unidades`, que es la lectura correcta |
| D8 | `Costo Unitario SKU` (respaldo con ventas) | Usa `SUM ( Ventas[Costo_Total_Facturado] )` sin corregir el signo de las devoluciones | Comprobado en el código | Bajo: solo para SKU sin compras | Usar `[Costo Sell Out]` en el respaldo `_v` |
| D9 | Margen | Incluye 1.070 líneas con costo 0 (0,6 % del importe), que suben el margen | Comprobado con los datos | Bajo | Documentado. Opcional: medida de margen sin costo 0 |
| D10 | Unidades e importes | Incluyen las líneas marcadas como posible duplicado (1,95 % del importe de ventas) | Comprobado con los datos | Bajo, pero sin cuantificar el error real | Decisión del negocio. Documentado |
| D11 | `Estacionalidad Uds` frente a `Estacionalidad Ventas` | El Budget en importe usa la estacionalidad en importe, y el Forecast en unidades la de unidades. Diciembre pesa 2,95 veces un mes medio en importe y 2,46 en unidades | Comprobado con los datos | Ninguno: es coherente | Documentado en el catálogo de KPI |
| D12 | `Forecast SO $` | Multiplica las unidades por el precio de los últimos 12 meses. Sin tendencia de precio ni de volumen, en el backtest subestimó el importe un 30 % | Comprobado (backtest) | Medio: el Rolling Forecast es conservador | Documentado en `docs/validacion.md` |

### Buenas prácticas que el modelo ya cumple

- `DIVIDE` en todos los cocientes, sin divisiones directas.
- Las comparaciones con el año anterior se cortan a la misma fecha (`KEEPFILTERS` fuera de `SAMEPERIODLASTYEAR`).
- El stock no se suma entre meses: se toma el último día del periodo.
- El costo de las devoluciones se corrige de signo en `Costo Sell Out`.
- Cuando Power BI rechazó una medida dentro de un filtro, se guardó antes en una variable (`VAR`).
- Las medidas de matriz usan `COALESCE ( …, 0 )` para mostrar 0 y no vacío. Las tarjetas mantienen el vacío cuando no hay dato.

## Power Query

| Paso conocido | Estado | Comentario |
|---|---|---|
| Origen: conector Web a la URL raw de GitHub, conexión anónima | Correcto | Si el repo pasa a privado, la actualización falla. Documentado en `03_powerbi/ESTADO_PROYECTO.md` |
| Compras: "Excluir errores de captura" (`Table.SelectRows`) | Correcto y comprobado | Excluye exactamente 6 filas (control automático) |
| Inventario: copia de la consulta de Producto con navegación a la tabla Inventario | Correcto (144.350 filas cargadas) | |
| Tipos de datos | Por validar | No hay exportación de las consultas. Los tipos de fecha se fijaron como "Fecha" sin hora |

La limpieza de datos (nulos, columnas vacías, marcas Sí/No, tablas de Excel con nombres simples) se hizo **antes** de Power
Query, en el Excel. Por eso Power Query tiene pocos pasos, y la lógica queda documentada en `MODELO.md`, sección 3.

## Rendimiento

El modelo es pequeño: 144 mil filas en la tabla más grande. No se proponen optimizaciones especulativas. Las medidas
más costosas son las que iteran SKU con `EXCEPT` o `SUMX` sobre marcas (`SKU en Quiebre`, `Venta Perdida Est.`,
`Compra Sugerida`). Si una página tarda, el Analizador de rendimiento de Power BI Desktop mostraría cuál es, antes de
cambiar nada.
