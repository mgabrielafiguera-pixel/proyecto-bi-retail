Trabaja en Power BI Service, en "Mi área de trabajo", modelo semántico **Retail BI v2**. Hay que excluir de Compras 6 devoluciones duplicadas con costo erróneo, que distorsionan el factor de importación de 2026.

## Antes de tocar nada

- **No vuelvas a subir el Excel con "Reemplazar".** Borraría las medidas y las relaciones creadas en el Service. Si la única forma de hacer el cambio fuera reemplazar el modelo, detente y avísame.
- El modelo lee el Excel desde GitHub (conexión `RetailBI_GitHub`). Esa URL ya trae una versión nueva del Excel.

## Paso 1 · Actualizar el modelo

Actualiza el modelo semántico para que lea el Excel nuevo y anota cuántas filas tienen `Compras` y `Producto` (deberían ser 16.721 y 17.721).

## Paso 2 · Excluir los errores de captura

1. Abre **Transformar datos** y la consulta `Compras`.
2. Al final, agrega un paso llamado **Excluir errores de captura** con este filtro (si el paso anterior tiene otro nombre, cámbialo en la fórmula):

```
= Table.SelectRows(#"Paso anterior", each not ([Es_Posible_Duplicado] = "Sí" and [Precio_Cero] = "Sí"))
```

3. Guarda, aplica los cambios y actualiza el modelo.

## Paso 3 · Controles

- `Compras` debe tener **16.715** filas (6 menos).
- El factor de importación de 2026 (`Importe Sell In` ÷ `Importe Sell In ExW`, filtrando Año 2026) debe quedar cerca de **1,27**, y el de marzo de 2026 cerca de **1,19**. Antes salían 1,88 y −9,88.
- Las páginas Resumen anual, Ventas y Compras deben seguir funcionando y la cascada Proveedor → Marca → Departamento también.

Repórtame las filas de Compras y Producto, los dos factores y cualquier error.
