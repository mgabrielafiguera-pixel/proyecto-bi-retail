# Registro de cambios

## 19-oct-2026 · Proyecto 06: Clientes y vendedores en Looker Studio

- `portafolio/index.html`: tarjeta del proyecto 06 con enlace al tablero público (solo lectura).
- `portafolio/img/`: capturas de las dos páginas del tablero.

## 19-oct-2026 · Capturas tras la corrección D2

- `04_presentacion/capturas/`: `01`, `05` y `06` repetidas con el corte corregido, con los departamentos difuminados.
- `portafolio/video/`: video y portada regenerados con las capturas nuevas.

## 19-oct-2026 · Corrección D2: corte de las comparaciones con el año anterior

- Modelo semántico: `Sell In Var %` corta en la última recepción de compras (30-abr-2026) y `Crecimiento Obtenido %`,
  `Histórico Crecimiento %`, `Sell Out Acumulado` y `Ritmo Esperado %` en `[Fecha Ultima Venta]`, que no cambia con
  los filtros de marca o proveedor. Sell In 2026 a Ex-Work pasa de +101,0 % a +346,3 % (Puesto: +127,5 % → +396,1 %).
- `03_powerbi/medidas_exportadas.csv` y `03_powerbi/MODELO.md`: las cinco medidas actualizadas.
- `docs/auditoria_dax.md`: D2 resuelto, con la validación.

## 18-oct-2026 · Capturas, respaldo de medidas y página Ventas diarias terminada

- `04_presentacion/capturas/`: 13 capturas reales del informe; las principales, en la sección 15 del README.
- `03_powerbi/medidas_exportadas.csv`: las 218 medidas del modelo exportadas con `INFO.VIEW.MEASURES` (tabla, medida,
  carpeta, formato y DAX).
- Hallazgo 9.6: desde abr-2026 la facturación central pasa del Almacén 1 al Almacén 6.

## 17-oct-2026 · Prompts fuera del repo

- Se retiró `03_powerbi/prompts/`. Las medidas DAX y el paso de Power Query de cada página pasan a `03_powerbi/MODELO.md`, sección 4.

## 17-oct-2026 · Página Ventas diarias

- `03_powerbi/prompts/06_ventas_diarias.md`: página nueva con ventas por día, mapa de tiendas, rankings de marca, proveedor y vendedor, y controles de 5 escenarios calculados desde el Excel.

## 17-oct-2026 · Auditoría, validación y documentación

**Nuevos**
- `scripts/datos.py`: carga compartida del Excel, con caché local en `.cache/` (no se sube).
- `scripts/validar_modelo.py`: 68 controles de calidad → `docs/resultados/controles_calidad.md` y `.csv`.
- `scripts/hallazgos.py`: recalcula las cifras de la sección de resultados del README → `docs/resultados/hallazgos.md`.
- `scripts/backtest_forecast.py`: backtest del forecast frente a dos métodos base → `docs/resultados/backtest_forecast.md` y `.csv`.
- `tests/`: 12 pruebas con pytest, incluido el backtest del inventario y las cifras del README.
- `requirements.txt`.
- `docs/`: auditoría, modelo de datos, auditoría de DAX y Power Query, catálogo de KPI, diccionario de datos, validación, guía de capturas y PDF, y resumen ejecutivo.
- `03_powerbi/prompts/05_correcciones_auditoria.md`: pruebas en Power BI del filtro de proveedor y del corte de las comparaciones.
- `04_presentacion/capturas/README.md`: lista de las capturas pendientes.

**Modificados**
- `README.md`: reescrito con 17 secciones. Corregidas 7 cifras para usar las definiciones del modelo (compras 4,5 veces, facturas +1,2 %, ticket −11 %, márgenes de Relojería 36 % → 42 % y de Joyería 51 % → 59 %, diciembre 2,5 veces en unidades y 78 clientes). Descripción del backtest con las dos cifras (−22,1 % y −7,3 %) y su fuga de información. Causa del hallazgo de compras generalizada.
- `scripts/reconstruir_inventario.py`: reemplaza las filas SKUI en cada ejecución (antes, una corrección no se aplicaba a los SKUI ya creados), guarda en un archivo temporal antes de sustituir el Excel y acepta `--xlsx` para trabajar sobre una copia. Dos ejecuciones seguidas dan un Excel idéntico al publicado.
- `03_powerbi/MODELO.md` y `03_powerbi/ESTADO_PROYECTO.md`: lectura del backtest y estado de la auditoría.
- `.gitignore`: `.cache/` y `.pytest_cache/`.

**Sin cambios** en los datos: el Excel que lee Power BI y los CSV no se modificaron.
