# Auditoría del proyecto

Fecha: 17-oct-2026. Revisión del repo en la rama `main` después del PR #9, y del Excel que lee Power BI.

## 1. Qué se pudo inspeccionar

| Inspeccionado | No disponible |
|---|---|
| README, `03_powerbi/ESTADO_PROYECTO.md`, `03_powerbi/MODELO.md` y el código DAX de cada página | Archivo `.pbix` o exportación del modelo: el modelo vive en Power BI Service |
| `scripts/anonimizar_inventario.py`, `scripts/reconstruir_inventario.py` | Código de las consultas de Power Query (solo el paso de exclusión está documentado) |
| `03_powerbi/retail_bi_powerbi.xlsx` (11 tablas) y `02_anonimizado/` | SQL: el proyecto no lo usa |
| Historial de Git | Capturas reales e informe PDF |

Por eso el DAX se audita sobre el código documentado y los datos se auditan con scripts. Lo que solo se puede
comprobar en Power BI queda **por validar**, con una prueba descrita.

## 2. Estado por categoría

### Correcto

| Elemento | Evidencia |
|---|---|
| Modelo en estrella: claves únicas, sin huérfanas, relaciones uno a varios con filtro único | `scripts/validar_modelo.py`: 0 errores |
| Volúmenes del README (49.936 ventas, 16.721 compras, 144.350 filas de inventario, dimensiones) | Control "Filas esperadas" |
| Totales de Power BI (ventas, compras y stock en 3 fechas) | 7 de 7 controles coinciden con el Excel |
| Exclusión de los 6 errores de captura en Compras | Control automático |
| Reconstrucción del inventario y su backtest | Reproducido por `tests/test_backtest_inventario.py` |
| Punto de reorden y Rolling Forecast 2026 | Recalculados en Python con las mismas cifras que Power BI (`docs/resultados/hallazgos.md`) |
| Comparaciones con el año anterior cortadas a la misma fecha | Código DAX (`MODELO.md`) |
| Confidencialidad del historial: `00_original/`, `01_mapeos/` y `trabajo/` nunca se subieron | `git log --all` |

### Mejorable (corregido en este PR)

| Elemento | Problema | Cambio |
|---|---|---|
| Descripción del backtest (−7,3 %) | Se presentaba como la precisión del método. Es el mes 6 del método calibrado, que usa datos del mismo periodo (fuga) | `docs/validacion.md` con las dos cifras; README corregido |
| 7 cifras del README | 4 calculadas sin las correcciones del modelo (signo del costo, exclusión de errores) y 3 por definición o redondeo | `scripts/hallazgos.py`; README con las cifras del modelo |
| `scripts/reconstruir_inventario.py` | No era idempotente: una corrección de un SKUI ya creado no se aplicaba | Reemplaza los SKUI y guarda en un archivo temporal. Probado: dos ejecuciones dan el mismo Excel |
| Reproducibilidad | Sin `requirements.txt`, pruebas ni guía | `requirements.txt`, `tests/` (12 pruebas) y README sección 15 |

### Pendiente

| Elemento | Qué falta | Quién |
|---|---|---|
| Página Budget / Forecast | Creada y con los controles correctos. Faltan dos detalles de formato (fila Rolling resaltada y fondo de la estacionalidad de compras) | María Gabriela, con Claude in Chrome |
| Capturas y PDF | Sacarlas del Service antes del 5-dic | María Gabriela (`docs/guia_capturas_pdf.md`) |
| Exportación de medidas | Guardar el resultado de `INFO.VIEW.MEASURES ()` en el repo para auditar el DAX real | María Gabriela |

### Por validar

| Elemento | Cómo se valida |
|---|---|
| El filtro de Proveedor no llega a las medidas de Inventario | Prueba descrita en `docs/auditoria_dax.md`, D1 |
| La variación de Sell In se subestima por el corte en la última venta | `docs/auditoria_dax.md`, D2 (resuelto en el modelo el 19-oct-2026) |
| Unas 140 medidas en el modelo | Exportación de medidas |
| Tipos de datos de Power Query | Exportación del modelo o revisión en el editor |

## 3. Riesgos de confidencialidad

| Riesgo | Nivel | Estado |
|---|---|---|
| La tabla Almacen tiene direcciones, zona postal, ciudad, estado y país en texto libre (9 direcciones distintas, 7 ciudades, 1 país). Están en el Excel de Power BI y en `02_anonimizado/retail_bi_anonimizado.xlsx`, y también en el historial de Git | Aceptado | **Decisión del 17-oct-2026: se mantienen**, porque son la base del mapa de ventas por almacén. Riesgo asumido por la dueña del proyecto |
| Re-identificación por combinación: fechas, unidades y mezcla reales, 13 almacenes en un país, atributos de producto (quilates, medidas) y la causa de 4.1 (interrupción de vuelos internacionales a finales de 2025) | Alto | El README generaliza la causa a "disrupción logística internacional". Lo demás es inherente a usar datos reales |
| Importes | Bajo | Escalados |
| Nombres de clientes, vendedores, marcas y proveedores | Bajo | Codificados. Los mapeos no están en el repo |

## 4. Plan de trabajo por prioridad

| Prioridad | Tarea | Estado |
|---|---|---|
| Crítica | Corregir la descripción del backtest y las cifras del README | Hecho en este PR |
| Crítica | Probar el filtro de proveedor en Inventario | Prompt listo |
| Importante | Controles de calidad, pruebas y reproducibilidad | Hecho en este PR |
| Importante | Backtest del forecast frente a métodos base | Hecho en este PR |
| Importante | Corte único de las comparaciones con el año anterior | Prompt listo |
| Importante | Página Budget / Forecast | Casi terminada |
| Recomendada | Capturas y PDF | Guía lista |
| Recomendada | Exportar las medidas al repo | Pendiente |
| Opcional | Parametrizar los años de la estacionalidad y la fecha de inicio del inventario | Documentado (`docs/auditoria_dax.md`) |
| Opcional | Diseño para móvil | No se hace: el portafolio se ve en escritorio o PDF |
| Opcional | Retirar `02_anonimizado/retail_bi_anonimizado.xlsx`, que duplica los datos | Decisión de la dueña |

## 5. Estructura del repo

No se movieron carpetas. Power BI lee el Excel por su ruta en GitHub (`03_powerbi/retail_bi_powerbi.xlsx`), y moverlo
rompería la actualización del modelo. La documentación nueva va en `docs/`, las pruebas en `tests/` y los resultados
generados en `docs/resultados/`.
