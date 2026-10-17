# Estado del proyecto · Sell In / Sell Out (Power BI)

Última actualización: 17 de octubre de 2026

## Dónde está todo

| Elemento | Ubicación |
|---|---|
| Datos limpios | `03_powerbi/retail_bi_powerbi.xlsx` (repo público `mgabrielafiguera-pixel/proyecto-bi-retail`, rama `main`) |
| URL que lee Power BI | `https://raw.githubusercontent.com/mgabrielafiguera-pixel/proyecto-bi-retail/main/03_powerbi/retail_bi_powerbi.xlsx` |
| Documentación del modelo | `03_powerbi/MODELO.md` |
| Prompts usados en Power BI | `03_powerbi/prompts/` |
| Scripts de inventario | `scripts/anonimizar_inventario.py` (se corre en local) y `scripts/reconstruir_inventario.py` |
| Modelo semántico | **Retail BI v2**, en "Mi área de trabajo" |
| Informe | **Sell In Sell Out v2**, en "Mi área de trabajo" (página 1 terminada) |
| Conexión | `RetailBI_GitHub`, autenticación Anónima, privacidad Público |

## Reglas importantes

- **"Mi área de trabajo" debe seguir en Prueba de Fabric (East US).** Si se pasa a Power BI Pro, el modelo deja de abrir.
- La prueba de Fabric vence aprox. el **5 de diciembre de 2026**. Antes de esa fecha: desactivar el formato de almacenamiento grande del modelo, comprobar que abre, y exportar el informe a PDF y capturas para el portafolio.
- No subir al repo nada de `00_original/`, `trabajo/` ni datos reales.
- El modelo y el informe antiguos ("Retail BI" y "Sell In Sell Out") no abren por un problema de región. Se pueden borrar cuando el v2 esté terminado.

## Modelo: terminado

- [x] 10 tablas cargadas: Ventas, Compras, Producto, Cliente, Proveedor, Marca, Vendedor, Almacen, Departamento, Calendario
- [x] Tabla 11, **Inventario**, con relaciones a Producto y Calendario. El modelo tiene 120 medidas
- [x] 12 relaciones varios a uno, filtro único (Proveedor NO se relaciona con Producto ni con Marca)
- [x] Calendario marcado como tabla de fechas
- [x] `Nombre_Mes` ordenado por `Mes`
- [x] Tabla `Medidas` con 38 medidas DAX base (la columna de relleno "Columna" oculta), más las medidas de Resumen anual (ver `MODELO.md`)
- [x] Tablas de parámetros desconectadas: `Tipo Costo` (Ex-Work / Puesto) y `Proyeccion` (0,80 a 2,00)
- [x] Formatos: porcentajes con 1 decimal; unidades enteras con miles; importes sin decimales con miles; ticket con 2 decimales

Totales de control (todo el periodo): Unidades Sell Out 48.052 · Importe Sell Out 44.271.198 · Unidades Sell In 44.990 · Importe Sell In 23.649.381 · Facturas 31.748 · Ticket 1.484 · Margen 41 % · Devoluciones 6 %.

## Informe: páginas (16-oct-2026)

Cada página replica una hoja del Excel de trabajo original.

| # | Página | Estado |
|---|---|---|
| 1 | **Resumen anual** | ✅ Terminada |
| 2 | **Ventas** | ✅ Terminada (`prompts/01_ventas_compras.md`) |
| 3 | **Compras** | ✅ Terminada, falta excluir 6 compras con error de captura en Power Query |
| 4 | **Inventario** | ✅ Terminada (`prompts/02_inventario.md`). Controles: stock jun-25 11.715, dic-25 14.063, abr-26 15.452; rotación 2025 1,41x. Punto de reorden por marca (`prompts/03_punto_reorden.md`): 2026 ROP 3.615 uds., 7 de 88 marcas a reponer, 38 en sobrestock, compra sugerida 308 uds. |
| 5 | **Budget / Forecast** | Prompt listo (`prompts/04_budget_forecast.md`). Boceto `04_presentacion/budget_forecast_propuesta.png` |

Ventas y Compras tienen segmentaciones en cascada **Proveedor → Marca → Departamento** con la medida `Filtro Cascada` (ver `MODELO.md`). Resumen anual se deja como vista global, sin cascada.

### Página 1 · Resumen anual (terminada)

Boceto de referencia: `04_presentacion/resumen_anual_propuesta.png` (datos ficticios).

- Segmentaciones: Año, Tipo de costo (Ex-Work / Puesto) y Proyección de crecimiento.
- Tarjeta de 8 indicadores: Sell In, Sell Out, Ratio de reposición (importe y unidades), Proyección, Crecimiento obtenido, Presupuesto comercial y Avance del presupuesto.
- Matrices SELL IN y SELL OUT por departamento × mes, con los 12 meses visibles (los meses sin datos en 0).
- Fila "Crec vs AA" bajo SELL OUT, con el total alineado a la tarjeta de Crecimiento obtenido.
- Gráfico de presupuesto acumulado vs Sell Out acumulado.
- Todas las comparaciones contra el año anterior usan **corte a la misma fecha** (ver `MODELO.md`).

Decisión: las 4 compras con costo Ex-Work atípico se dejan como están. Accesorios puede salir negativo en Ex-Work y la página lo indica con una nota al pie.

## Inventario (16-oct-2026)

- Fotos reales de cierre de mes por SKU, dic-2023 a jun-2025, anonimizadas con `scripts/anonimizar_inventario.py` → `02_anonimizado/inventario_sku_mes.csv`.
- Jul-2025 a abr-2026 reconstruido con kardex (IF = II + Sell In − Sell Out) y calibrado con el resumen por marca hasta dic-2025 → `02_anonimizado/inventario_reconstruido.csv` y tabla `Inventario` del Excel (144.350 filas).
- 1.220 SKU con stock pero sin ventas ni compras se añadieron a Producto con código `SKUI#####` (Producto pasa a 17.721 filas).
- Totales de control (unidades): jun-2025 11.715 · dic-2025 14.063 · abr-2026 15.452.
- Precisión (backtest ene–jun 2025): error del total a 6 meses de −22,1 % con el kardex puro y −7,3 % con el calibrado, que usa datos del mismo periodo. Por SKU, WAPE 27–39 %. Los KPI de inventario se leen por marca, departamento o total, no por SKU. Ver `docs/validacion.md`.

### Validación del Excel para Power BI (16-oct-2026)

Todo correcto: COD_SKU único en Producto; todos los SKU de Ventas, Compras e Inventario existen en Producto; sin duplicados SKU+Fecha; fechas de Inventario a fin de mes y dentro de Calendario; sin stock negativo; marcas, departamentos y proveedores de Producto existen en sus tablas.

Las 6 compras con error de captura siguen en el Excel y se excluyen en Power Query (paso "Excluir errores de captura", aplicado el 16-oct). Compras queda en 16.715 filas y el factor de importación de 2026 en 1,27.

## Dónde quedamos (16-oct-2026)

- Power BI: páginas Resumen anual, Ventas, Compras e Inventario (con punto de reorden) terminadas y guardadas.
- README reescrito como caso de negocio, con los hallazgos validados.
- **Siguiente sesión:** correr `prompts/04_budget_forecast.md` en Claude in Chrome y validar sus controles. Después, capturas y PDF del informe antes del 5-dic.

## Auditoría (17-oct-2026)

Auditoría completa en `docs/auditoria.md`. Nuevos: controles de calidad (`scripts/validar_modelo.py`), recálculo de las cifras del README (`scripts/hallazgos.py`), backtest del forecast (`scripts/backtest_forecast.py`), pruebas (`tests/`) y documentación en `docs/`.

Pendiente en Power BI: `prompts/05_correcciones_auditoria.md` (probar el filtro de proveedor en Inventario y el corte de las comparaciones con el año anterior). Pendiente de decisión: generalizar las direcciones de los almacenes (`scripts/generalizar_almacenes.py`).

## Próximo paso

1. Página **Budget / Forecast** con la lógica de forecast definida (estacionalidad 2024-2025).

Preguntas abiertas:

- Códigos PROV/MARC de los proveedores con **año fiscal desde abril** (para `Proveedor[Tipo_Ejercicio]` y el selector Calendario / Fiscal).
- Corte oficial del crecimiento: 30-abr-2026 (recomendado) o la última venta.
- Si el Almacén 1 es una tienda o un punto central de facturación (mapa de ventas por almacén).

## Pendiente para más adelante

- Confirmar qué son las 1.384 compras "Sin clasificar" (8,4 % del Sell In, casi todas de 2026).
- Borrar el modelo y el informe antiguos cuando el v2 esté terminado.
