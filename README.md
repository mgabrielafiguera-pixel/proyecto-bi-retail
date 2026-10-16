# Retail de lujo · Sell In, Sell Out, Inventario y Forecast en Power BI

> Caso de Business Intelligence construido sobre datos **reales y anonimizados** de una
> empresa de retail de lujo (relojería, joyería y accesorios). Proveedores, marcas, productos,
> clientes y vendedores están codificados (`PROV####`, `MARC####`, `SKU#####`), los nombres
> son ficticios y los **importes están escalados**. Las proporciones, tendencias y unidades
> se conservan.

## 1. Problema empresarial

La empresa importa la mayor parte de su mercancía y compra con plazos de entrega de un mes.
El área comercial y la de compras trabajaban con hojas de Excel separadas, y no podían
responder con rapidez a cuatro preguntas:

1. **¿Estamos vendiendo lo que compramos?** Relación entre compras (Sell In) y ventas (Sell Out) por proveedor, marca y departamento.
2. **¿Cuánto inventario tenemos y cuánto está parado?** No había un histórico de stock mensual que cuadrara con compras y ventas.
3. **¿Qué marcas hay que reponer y cuánto comprar?** Punto de reorden y compra sugerida.
4. **¿Cómo vamos a cerrar el año contra el presupuesto?** Budget, Forecast y Rolling Forecast.

## 2. Datos y herramientas

| Fuente | Volumen | Periodo |
|---|---|---|
| Ventas (líneas de factura) | 49.936 filas | 2023 a jun-2026 |
| Compras (recepciones) | 16.721 filas (16.715 tras excluir 6 errores) | ene-2024 a abr-2026 |
| Inventario por SKU y mes | 144.350 filas | dic-2023 a abr-2026 |
| Dimensiones | 17.721 productos, 13.090 clientes, 165 proveedores, 141 marcas, 12 departamentos, 13 almacenes | |

**Preparación**
- **Anonimización** con Python (`scripts/anonimizar_inventario.py`): se corre en local sobre los archivos originales y solo exporta códigos, fechas y unidades. Los originales y las tablas de mapeo nunca se suben al repo.
- **Limpieza y calidad**: marcas de duplicados, precio cero, devoluciones y totales que no cuadran. Ver `03_powerbi/MODELO.md`, sección Calidad de datos.
- **Reconstrucción del inventario** (`scripts/reconstruir_inventario.py`):
  - Hasta jun-2025 se usan las fotos reales de cierre de mes.
  - Desde ahí se aplica un kardex (inventario final = inicial + compras − ventas), calibrado con el resumen de inventario por marca.
  - Un **backtest** de 6 meses da un error del −7,3 % en el total.

**Herramientas:** Python (pandas, openpyxl) · Excel · Power Query · Power BI Service · DAX · Git / GitHub.

**Modelo:** modelo estrella con 11 tablas. Los hechos son Ventas, Compras e Inventario; las dimensiones, Producto, Marca, Proveedor, Departamento, Cliente, Vendedor, Almacén y Calendario. Tiene unas 140 medidas DAX documentadas en `03_powerbi/MODELO.md`.

## 3. Análisis y visualización

Informe **Sell In Sell Out v2**, con 5 páginas. Las segmentaciones se filtran en cascada Proveedor → Marca → Departamento.

| Página | Qué responde | Técnicas |
|---|---|---|
| Resumen anual | Sell In y Sell Out por departamento y mes, crecimiento y avance del presupuesto | Comparación con el año anterior cortada a la misma fecha, selector de costo Ex-Work o puesto |
| Ventas | Venta por marca, proveedor y departamento, ticket, margen y devoluciones | Estacionalidad 2024–2025, ranking dinámico |
| Compras | Compras, factor de importación, lead time y sell-through | Exclusión de errores de captura en Power Query |
| Inventario | Stock, rotación, cobertura, quiebres, stock sin venta, punto de reorden y compra sugerida | Kardex calibrado, stock de seguridad (nivel de servicio 95 %), política (s, S) por marca |
| Budget / Forecast | Budget, Forecast y Rolling Forecast de ventas y compras | Budget = año anterior × crecimiento × estacionalidad; forecast con pieza promedio y estacionalidad |

Las decisiones de diseño, las fórmulas y los controles de cada página están en `03_powerbi/MODELO.md` y `03_powerbi/prompts/`.

## 4. Hallazgos y recomendaciones

> Hallazgos obtenidos del análisis de los datos. Las causas están **validadas con el negocio**.

### 4.1 Se compra más mientras se vende menos
- **Qué pasó:** en ene–abr 2026 las compras a costo Ex-Work fueron unas **3 veces** las de ene–abr 2025, mientras la venta en importe cayó un **7,3 %**. El sell-through en unidades bajó de 1,30 a **0,78**.
- **Contexto:** es un ciclo. En 2024 se compró de más (sell-through 0,69), en 2025 se vendió ese stock (1,16) y en 2026 se vuelve a acumular.
- **Causa (validada):** a finales de 2025, la situación del país interrumpió los vuelos internacionales. La mercancía de los compromisos con proveedores internacionales no llegó en su momento y se recibió toda junta en los primeros meses de 2026. No es una sobrecompra, es un **desfase logístico**.
- **Implicación:** el sell-through de ene–abr 2026 está deformado por esa llegada acumulada. Para leer la tendencia real hay que mirar el semestre o el año completo.
- **Recomendación:** atar las compras al Rolling Forecast mensual y al punto de reorden por marca, y tener un plan de contingencia logística (rutas alternativas, más stock de seguridad en las marcas top) para los periodos de riesgo.

### 4.2 La caída de 2026 es de precio medio, no de volumen
- **Qué pasó:** en ene–abr 2026 frente a 2025, las unidades vendidas apenas cambian (−1,7 %), las facturas suben un 0,6 % y los clientes un 6 %. Pero el **ticket promedio baja un 8 %**.
- **Dónde:** en Relojería, que es el 58 % de la venta, el precio medio por pieza cae un **29 %** mientras las unidades suben un 16 %. Su margen se mantiene en 36 %.
- **Causa (validada):** como el margen no cae, no es una política de descuentos. Es un **cambio de mezcla**: hubo **menos relojes de alta gama disponibles**, por la misma interrupción logística, y se vendieron piezas de menor precio.
- **Contrapunto:** Joyería crece un 10 %, con más precio por pieza y un margen que sube del 51 % al 57 %.
- **Recomendación:** medir la venta perdida en alta gama y priorizar esas referencias en los pedidos internacionales. Cada reloj de alta gama que falta se sustituye por uno de menor precio y baja el ticket.

### 4.3 El inventario se duplicó y casi la mitad no rota
- **Qué pasó:** el stock pasó de 7.089 unidades (dic-2023) a **15.452** (abr-2026), un +118 %, con la venta en unidades estable. El **46 %** de las unidades en stock no tuvo ninguna venta en los últimos 12 meses.
- **Dónde:** **38 de 88 marcas** con venta tienen más de 12 meses de cobertura. Belleza y Accesorios guardan el 25 % del stock, pero suman menos del 3 % de la venta.
- **Causa (validada):** los **mínimos de pedido de los proveedores** obligan a comprar más de lo que se vende en las categorías de menor rotación. A eso se suma la llegada acumulada de 2026.
- **Recomendación:**
  - Plan de liquidación (outlet o promociones de temporada baja) para el stock sin venta de 12 meses.
  - Frenar las compras a las marcas en sobrestock.
  - Negociar mínimos de pedido más bajos, o pedidos combinados, en Belleza y Accesorios.

### 4.4 Pocas marcas a reponer, pero son las que venden
- **Qué pasó:** con el punto de reorden por marca (demanda de 6 meses, lead time real de unos 32 días y nivel de servicio del 95 %), **7 marcas** están por debajo del punto de reorden. La compra sugerida es de unas 308 unidades.
- **Dato:** el 80 % de la venta lo hacen **15 de 141 marcas**. La marca `MARC0004` (8 % de la venta) vende más de lo que se le compra (sell-through 1,27).
- **Causa (validada):** la interrupción de los vuelos internacionales retrasó la reposición de estas marcas.
- **Recomendación:** priorizar la reposición de las marcas que concentran la venta. La compra total no tiene que subir: hay que reasignarla.

### 4.5 El cierre de 2026 queda por debajo del presupuesto
- **Qué pasó:** con un presupuesto de +20 % sobre 2025, el Rolling Forecast cierra **22,5 %** por debajo del budget de ventas. Contra la venta de 2025, la tendencia es de **−7 %**.
- **Estacionalidad:** diciembre vale unas **3 veces** un mes normal, así que el resultado del año depende de la temporada navideña.
- **Recomendación:** recalibrar el presupuesto con la tendencia real, y asegurar el stock de las marcas top antes de octubre, porque el lead time es de un mes.

### 4.6 La concentración es un riesgo
- **Almacén:** el Almacén 1 factura el 89 % de la venta. Es una tienda y además funciona como **punto central** de facturación, así que la venta por almacén no equivale a la venta por tienda.
- **Clientes:** 77 de 13.090 clientes hacen el 50 % de la venta, y el primero el 7,6 %. Son **clientes VIP**.
- **Recomendación:** un programa de fidelización y atención personalizada para los clientes VIP, con seguimiento de su frecuencia de compra. Perder uno de ellos se nota en el resultado del año.

### 4.7 Calidad de datos que afecta a las decisiones
- **Recepciones sin registrar:** en 463 casos (SKU y mes) se vendió más de lo que había en stock, y el kardex puro subestima el inventario real en un 22 % a 6 meses. **Validado:** se vendía mercancía que aún no estaba registrada como recibida en Compras.
- **Errores de captura:** 6 devoluciones duplicadas con costo erróneo hacían que el factor de importación de 2026 saliera en 1,88 (marzo en −9,88). Sin ellas sale en 1,27. Se excluyen en Power Query.
- **Compras sin clasificar:** 1.384 compras "Sin clasificar" (8,4 % del Sell In) no tienen tipo de movimiento ni factor de importación.
- **Recomendación:**
  - Conciliar recepciones físicas contra Compras cada mes.
  - Hacer obligatorio el tipo de movimiento en el registro de compras.
  - Validar los costos atípicos antes de cerrar el mes.

## 5. Evidencia y transparencia

- **Datos:** reales y anonimizados. Los importes están escalados y los nombres son ficticios. Las unidades, fechas y proporciones son reales.
- **Código:** `scripts/` contiene la anonimización y la reconstrucción del inventario con su backtest.
- **Métricas verificables:** cada página tiene totales de control en `03_powerbi/ESTADO_PROYECTO.md` y en los prompts de `03_powerbi/prompts/`. Ejemplos: stock 11.715 / 14.063 / 15.452 unidades en jun-25 / dic-25 / abr-26, y rotación 2025 de 1,41x.
- **Bocetos:** en `04_presentacion/`.
- **Pendiente:** capturas de las 5 páginas y el informe exportado a PDF.

## Estructura del repo

| Carpeta | Contenido |
|---|---|
| `02_anonimizado/` | Datos anonimizados en CSV, incluido el inventario por SKU y mes |
| `03_powerbi/` | Excel que lee Power BI (`retail_bi_powerbi.xlsx`), documentación del modelo, estado y prompts |
| `04_presentacion/` | Bocetos de las páginas |
| `scripts/` | Python: anonimización del inventario y reconstrucción con kardex |

Los datos originales (`00_original/`, `01_mapeos/`, `trabajo/`) no se suben al repo.
