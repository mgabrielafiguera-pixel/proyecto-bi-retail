# Estado del proyecto · Sell In / Sell Out (Power BI)

Última actualización: 15 de octubre de 2026

## Dónde está todo

| Elemento | Ubicación |
|---|---|
| Datos limpios | `03_powerbi/retail_bi_powerbi.xlsx` (repo público `mgabrielafiguera-pixel/proyecto-bi-retail`, rama `main`) |
| URL que lee Power BI | `https://raw.githubusercontent.com/mgabrielafiguera-pixel/proyecto-bi-retail/main/03_powerbi/retail_bi_powerbi.xlsx` |
| Documentación del modelo | `03_powerbi/MODELO.md` |
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
- [x] 12 relaciones varios a uno, filtro único (Proveedor NO se relaciona con Producto ni con Marca)
- [x] Calendario marcado como tabla de fechas
- [x] `Nombre_Mes` ordenado por `Mes`
- [x] Tabla `Medidas` con 38 medidas DAX base (la columna de relleno "Columna" oculta), más las medidas de Resumen anual (ver `MODELO.md`)
- [x] Tablas de parámetros desconectadas: `Tipo Costo` (Ex-Work / Puesto) y `Proyeccion` (0,80 a 2,00)
- [x] Formatos: porcentajes con 1 decimal; unidades enteras con miles; importes sin decimales con miles; ticket con 2 decimales

Totales de control (todo el periodo): Unidades Sell Out 48.052 · Importe Sell Out 44.271.198 · Unidades Sell In 44.990 · Importe Sell In 23.649.381 · Facturas 31.748 · Ticket 1.484 · Margen 41 % · Devoluciones 6 %.

## Informe: estructura nueva (15-oct-2026)

Se reemplazó el plan de 4 páginas por uno que replica las hojas del Excel de trabajo original. Cada página es una copia funcional de una hoja.

| # | Página | Hoja de Excel | Estado |
|---|---|---|---|
| 1 | **Resumen anual** | Resumen anual | ✅ Terminada |
| 2 | **Forecast por marca / proveedor** | DASHBOARD (Budget) y Forecast por marca | Boceto en revisión (`04_presentacion/forecast_marca_propuesta.png`) |

### Página 1 · Resumen anual (terminada)

Boceto de referencia: `04_presentacion/resumen_anual_propuesta.png` (datos ficticios).

- Segmentaciones: Año, Tipo de costo (Ex-Work / Puesto) y Proyección de crecimiento.
- Tarjeta de 8 indicadores: Sell In, Sell Out, Ratio de reposición (importe y unidades), Proyección, Crecimiento obtenido, Presupuesto comercial y Avance del presupuesto.
- Matrices SELL IN y SELL OUT por departamento × mes, con los 12 meses visibles (los meses sin datos en 0).
- Fila "Crec vs AA" bajo SELL OUT, con el total alineado a la tarjeta de Crecimiento obtenido.
- Gráfico de presupuesto acumulado vs Sell Out acumulado.
- Todas las comparaciones contra el año anterior usan **corte a la misma fecha** (ver `MODELO.md`).

Decisión: las 4 compras con costo Ex-Work atípico se dejan como están. Accesorios puede salir negativo en Ex-Work y la página lo indica con una nota al pie.

## Próximo paso

Página 2, **Forecast por marca / proveedor**. Antes de construirla falta:

1. Aprobar el boceto `04_presentacion/forecast_marca_propuesta.png`.
2. Identificar los códigos anonimizados (PROV/MARC) de los proveedores con **año fiscal desde abril**. Se añadirán `Proveedor[Tipo_Ejercicio]` y una columna `Año_Fiscal` en Calendario.
3. Confirmar si hay una foto de inventario por SKU (para cobertura y rotación).
4. Confirmar si el Almacén 1 es una tienda o un punto central de facturación.

Estacionalidad prevista: peso medio de cada mes en las ventas 2023 a 2025.

## Pendiente para más adelante

- Añadir inventario (existencias por almacén y fecha) para rotación y cobertura.
- Confirmar qué son las 1.384 compras "Sin clasificar" (8,4 % del Sell In, casi todas de 2026).
- Actualizar el README del repo indicando que nombres, direcciones e importes son ficticios o están escalados.
- Borrar el modelo y el informe antiguos cuando el v2 esté terminado.
