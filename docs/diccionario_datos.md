# Diccionario de datos

Tablas de `03_powerbi/retail_bi_powerbi.xlsx` (una hoja y una tabla de Excel por tabla del modelo). **% lleno** = filas
con valor, medido el 17-oct-2026. Todos los códigos son anónimos: `SKU#####` / `SKUI#####` (producto), `MARC####`,
`PROV####`, `CLI#####`, `VEND####`, `FAC######`, `Almacén N`, `Departamento N`. Los importes están escalados.

## Ventas (hechos · una fila = una línea de factura o nota de crédito · 49.936 filas)

| Columna | Tipo | % lleno | Descripción |
|---|---|---:|---|
| COD_ALMACEN | Texto | 100 | Almacén o tienda que vende (11 de los 13) |
| COD_SKU | Texto | 100 | Producto |
| Cantidad | Entero | 100 | Unidades. Negativa = devolución |
| Precio_Venta_Unitario | Decimal | 100 | Precio por unidad |
| Total_Factura | Decimal | 100 | Importe de la línea. **Base de `Importe Sell Out`** |
| Costo_Unitario | Decimal | 98 | Costo por unidad |
| Costo_Total_Facturado | Decimal | 100 | Costo de la línea. En el 40 % de las devoluciones viene en positivo: la medida `Costo Sell Out` corrige el signo |
| Precio_Unitario_USD | Decimal | 38 | Casi vacía. No se usa |
| Fecha | Fecha | 100 | Fecha de la factura. Relación con Calendario |
| MES, ANIO, Dia | Texto / entero | 100 | Columnas de origen. `MES` está en inglés: usar Calendario |
| Mov | Texto | 100 | `FACT` (factura) o `N/CR` (nota de crédito) |
| Num_Factura | Texto | 100 | Número de factura. Varias líneas por factura |
| COD_CLIENTE | Texto | 100 | Cliente |
| COD_VENDEDOR | Texto | 100 | Vendedor |
| CODIGO_INTERNO_PROVEEDOR | Texto | 100 | Proveedor del producto en la venta. Relación con Proveedor |
| Consigned | Texto | 96 | Mercancía en consignación (Yes / No) |
| Es_Posible_Duplicado | Sí / No | 100 | Línea idéntica a otra en todas las columnas |
| Precio_Cero | Sí / No | 100 | Precio 0 (posibles obsequios o cambios) |
| Total_No_Cuadra | Sí / No | 100 | El total se aleja más de un 1 % de cantidad × precio |
| Es_Devolucion | Sí / No | 100 | Cantidad negativa |

## Compras (hechos · una fila = una línea de recepción · 16.721 filas; 16.715 tras Power Query)

| Columna | Tipo | % lleno | Descripción |
|---|---|---:|---|
| COD_ALMACEN | Texto | 100 | Siempre `Almacén 1` (almacén central) |
| COD_SKU | Texto | 100 | Producto |
| Cantidad | Entero | 100 | Unidades recibidas. Negativa = devolución al proveedor |
| Precio_Costo_Nacionalizado, Total_Precio_Costo_Nacionalizado | Decimal | 100 | Costo puesto en destino (con flete y aranceles). **Base de `Importe Sell In`** |
| Costo_Ex_Works, Total_Costo_Ex_Works | Decimal | 100 | Costo en fábrica. **Base de `Importe Sell In ExW`** |
| Fecha_Recepcion | Fecha | 100 | Fecha de entrada al almacén. Relación con Calendario |
| Docto_Recepcion | Texto | 100 | Documento de recepción |
| Fecha_Invoice | Fecha | 92 | Fecha de la factura del proveedor. Base del lead time |
| MES, ANIO | Texto / entero | 100 | Columnas de origen |
| Num_Invoice | Texto | 89 | Número de factura del proveedor |
| Tipo_Movi | Texto | 100 | Compra Internacional, Nacional, Interna, devoluciones… "Sin clasificar" en 1.384 líneas |
| CODIGO_INTERNO_PROVEEDOR | Texto | 100 | Proveedor. Relación con Proveedor |
| Margen_Nacionalizacion, Factor_Importacion | Decimal | 50 | Costo puesto / Ex-Work. Vacío en compras locales y sin clasificar |
| Orden_Compra, Factura_Proveedor | Texto | 50 / 41 | Referencias de origen |
| Consigned | Texto | 100 | Consignación |
| Es_Posible_Duplicado, Precio_Cero, Total_No_Cuadra, Es_Devolucion | Sí / No | 100 | Igual que en Ventas |
| Sin_Fecha_Factura | Sí / No | 100 | Falta `Fecha_Invoice` |

## Inventario (hechos, foto · una fila = stock de un SKU al cierre de un mes · 144.350 filas)

| Columna | Tipo | % lleno | Descripción |
|---|---|---:|---|
| COD_SKU | Texto | 100 | Producto |
| Fecha | Fecha | 100 | Último día del mes (dic-2023 a abr-2026) |
| Unidades | Entero | 100 | Stock al cierre, mínimo 0 |
| Origen | Texto | 100 | `Real` (foto), `Estimado calibrado` (jul–dic 2025) o `Estimado kardex` (2026) |
| Venta_Sin_Stock | Sí / No | 100 | El kardex habría quedado negativo: se vendió sin recepción registrada |

Solo se guardan filas con stock mayor que 0 o con venta sin stock. Un SKU sin fila en un mes tiene stock 0.

## Producto (dimensión · una fila = un SKU · 17.721 filas)

| Columna | Tipo | % lleno | Descripción |
|---|---|---:|---|
| COD_SKU | Texto | 100 | Clave. `SKUI#####` = 1.220 productos con stock y sin ventas ni compras desde 2023 |
| CODIGO_INTERNO_MARCA | Texto | 100 | Marca. Relación con Marca |
| CODIGO_INTERNO_PROVEEDOR | Texto | 100 | Proveedor habitual. **Sin relación** (ver `docs/modelo_datos.md`) |
| TIPO_PROVEEDOR | Texto | 93 | Local, Nacional o Internacional |
| COD_DEPARTAMENTO / DEPARTAMENTO | Texto | 100 | Departamento. Relación con Departamento |
| CATEGORIA_VENTA, GENERO_NUEVO, CATEGORIA_NUEVA, SUB_CATEGORIA_NUEVA, ESPECIFICA_NUEVA, FAMILIA_NUEVA | Texto | 20–93 | Jerarquía comercial del producto |
| MODELO, PESO_GR, MEDIDA, TALLA, BRILLANTES, OTRAS_CARACTERISTICAS | Texto / decimal | 4–75 | Atributos físicos |
| TIPO_PRODUCTO, CONSIGNED, PRODUCTO_SERIADO, TIPO_REPORTE | Texto | 80–93 | Atributos de gestión |
| fecha_primera, en_ventas, en_compras, filas_ventas, filas_compras, n_variantes_atributos, revisar | Varios | 93–100 | Columnas de control de la limpieza |

## Dimensiones pequeñas

| Tabla | Filas | Clave | Columnas útiles |
|---|---:|---|---|
| Marca | 141 | CODIGO_INTERNO_MARCA | CODIGO_INTERNO_PROVEEDOR (principal), n_proveedores, DEPARTAMENTO_PRINCIPAL, MARCA_PROPIA (S/N), n_sku |
| Proveedor | 165 | CODIGO_INTERNO_PROVEEDOR | Origen_PROVEEDOR (Local / Nacional / Internacional; segmentación "Origen"), fechas de primera compra y venta |
| Departamento | 12 | COD_DEPARTAMENTO | DEPARTAMENTO_ORIGINAL (nombre) |
| Cliente | 13.090 | COD_CLIENTE | fecha_primera_compra, n_filas_ventas |
| Vendedor | 89 | COD_VENDEDOR | fecha_primera_venta, n_filas_ventas |
| Almacen | 13 | COD_ALMACEN | ESTADO_ALMACEN (activo / inactivo), fechas de primera venta. DIRECCION, DIRECCION2, ZONA_POSTAL, CIUDAD, ESTADO y PAIS: ubicación del almacén, para el mapa de ventas |
| Calendario | 1.461 | Fecha | Año, Mes, Nombre_Mes (en español, ordenado por Mes), Trimestre, Año_Mes |

## Otros archivos de datos

| Archivo | Contenido |
|---|---|
| `02_anonimizado/inventario_sku_mes.csv` | Fotos reales de inventario por SKU, dic-2023 a jun-2025 (referencia del backtest) |
| `02_anonimizado/inventario_marca_mes.csv` | Resumen de inventario por marca, ene-2024 a dic-2025 (calibración) |
| `02_anonimizado/inventario_reconstruido.csv` | Salida del script de reconstrucción (igual que la tabla Inventario) |
| `02_anonimizado/retail_bi_anonimizado.xlsx` | Libro anonimizado completo con la estructura de origen. Duplica los datos del Excel de Power BI |
