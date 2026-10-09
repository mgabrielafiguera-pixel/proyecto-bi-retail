# Estado del proyecto · Sell In / Sell Out (Power BI)

Última actualización: 9 de octubre de 2026

## Dónde está todo

| Elemento | Ubicación |
|---|---|
| Datos limpios | `03_powerbi/retail_bi_powerbi.xlsx` (repo público `mgabrielafiguera-pixel/proyecto-bi-retail`, rama `main`) |
| URL que lee Power BI | `https://raw.githubusercontent.com/mgabrielafiguera-pixel/proyecto-bi-retail/main/03_powerbi/retail_bi_powerbi.xlsx` |
| Documentación del modelo | `03_powerbi/MODELO.md` |
| Modelo semántico | **Retail BI v2**, en "Mi área de trabajo" |
| Informe | **Sell In Sell Out v2**, en "Mi área de trabajo" (creado, vacío) |
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
- [x] Tabla `Medidas` con 38 medidas DAX (la columna de relleno "Columna" oculta)
- [x] Formatos: porcentajes con 1 decimal; unidades enteras con miles; importes sin decimales con miles; ticket con 2 decimales

Totales de control (todo el periodo): Unidades Sell Out 48.052 · Importe Sell Out 44.271.198 · Unidades Sell In 44.990 · Importe Sell In 23.649.381 · Facturas 31.748 · Ticket 1.484 · Margen 41 % · Devoluciones 6 %.

## Informe: estructura acordada (4 páginas)

| Página | Pregunta | Contenido |
|---|---|---|
| **1. Resumen** | ¿Cómo va el negocio? | Título. Filtros: Año (mosaico, 2025 por defecto), Departamento, Marca. Tarjetas: Importe Sell Out, Importe Sell Out Var %, Margen %, Sell-Through %, Ticket Promedio, Devoluciones %. Línea mensual Importe Sell Out vs Importe Sell Out AA |
| **2. Sell In vs Sell Out** | ¿Compramos en línea con lo que vendemos? | Columnas mensuales Unidades Sell In vs Unidades Sell Out. Sell-Through % por Marca, Departamento y Proveedor |
| **3. Tiendas y vendedores** | ¿Dónde y quién vende? | Ventas y ticket por tienda, con Almacén 1 separado (concentra ~80 % de las líneas). Top 10 vendedores. **Sin Sell-Through por tienda** (las compras entran solo por Almacén 1) |
| **4. Rentabilidad y calidad** | ¿Dónde ganamos y qué revisar? | Margen % por Departamento y Marca. Devoluciones. Bloque de calidad de datos: duplicados, precio cero, total que no cuadra, compras "Sin clasificar" |

## Próximo paso

Abrir **Sell In Sell Out v2** → **Editar** → página 1 "Resumen":

1. Renombrar "Página 1" a `Resumen` y añadir el título.
2. Tres segmentaciones: Calendario[Año], nombre de Departamento, nombre de Marca.
3. Seis tarjetas con las medidas de la tabla de arriba.
4. Gráfico de línea mensual: eje `Calendario[Año_Mes]` o `Nombre_Mes`, valores `Importe Sell Out` y `Importe Sell Out AA`.

## Pendiente para más adelante

- Añadir inventario (existencias por almacén y fecha) para rotación y cobertura.
- Confirmar qué son las 1.384 compras "Sin clasificar" (8,4 % del Sell In, casi todas de 2026).
- Actualizar el README del repo indicando que nombres, direcciones e importes son ficticios o están escalados.
