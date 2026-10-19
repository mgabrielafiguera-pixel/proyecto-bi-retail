# Guía para las capturas y el PDF del informe

Las capturas y el PDF tienen que salir del informe real **Sell In Sell Out v2** en Power BI Service. No se generan
con herramientas externas ni con bocetos: los archivos `*_propuesta.png` de `04_presentacion/` son bocetos y se
presentan como tales.

**Fecha límite:** antes del **5-dic-2026**, cuando vence la prueba de Fabric de "Mi área de trabajo".

## Antes de capturar

1. Actualiza el modelo semántico (Retail BI v2 → Actualizar ahora) y espera a que termine sin errores.
2. Si ya aplicaste las correcciones D1 y D2 de `docs/auditoria_dax.md`, comprueba sus controles.
3. Pon las segmentaciones así en todas las páginas: **Año 2026**, Origen, Proveedor, Marca y Departamento en
   **"Todas"**, Tipo de costo **Ex-Work**, Proyección **1,20**.
4. Guarda el informe con esos filtros (Archivo → Guardar). Así quien abra el PDF ve lo mismo que las capturas.
5. Usa el modo de **pantalla completa** del informe (Ver → Pantalla completa) para que no salgan los menús del Service.

## Capturas

Guárdalas en `04_presentacion/capturas/` con estos nombres, que son las páginas que existen en el informe:

| Archivo | Página | Qué debe verse |
|---|---|---|
| `01_resumen_anual.png` | Resumen anual | Tarjetas, matrices SELL IN y SELL OUT por departamento y mes, presupuesto acumulado |
| `02_ventas.png` | Ventas | Tarjetas, venta por marca y departamento, estacionalidad |
| `03_compras.png` | Compras | Tarjetas, factor de importación, lead time, sell-through |
| `04_inventario.png` | Inventario | Tarjetas de stock y punto de reorden, matriz por segmento con el estado de reorden |
| `05_budget_forecast.png` | Budget / Forecast | Tarjetas de ventas y compras, matriz mensual con la estacionalidad arriba, gráfico acumulado |

En Mac: `Cmd + Shift + 4`, luego `Espacio` y clic en la ventana del navegador. Recorta los bordes del navegador si
aparecen. Formato PNG y al menos 1600 px de ancho.

## PDF

1. En el informe: **Exportar → PDF**.
2. Marca "Valores actuales" para exportar con los filtros guardados.
3. Guarda el archivo como `04_presentacion/informe_sell_in_sell_out.pdf`.
4. Ábrelo y comprueba que salen las 5 páginas y que ninguna tarjeta muestra "(En blanco)".

## Después

- Sube las 5 capturas y el PDF al repo (con un commit que mencione #5). El README ya enlaza esas rutas.
- Antes de subirlas, revisa que no aparezcan nombres reales: solo códigos `PROV`, `MARC`, `SKU` y `Almacén N`.
