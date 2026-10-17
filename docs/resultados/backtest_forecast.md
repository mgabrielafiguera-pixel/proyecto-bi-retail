# Backtest del forecast de ventas (Sell Out)

Generado por `scripts/backtest_forecast.py`. Evalúa el método de forecast de la página Budget / Forecast
(`03_powerbi/MODELO.md`, sección 4): uds = pieza promedio 12M × estacionalidad en unidades;
$ = uds × precio promedio 12M. En departamento y marca el cálculo se rehace dentro de cada grupo, como el DAX
respeta los filtros.

## Diseño (sin fuga de información)

| Pliegue | Corte | Horizonte | Estacionalidad | Pieza y precio |
|---|---|---|---|---|
| Principal | 30-abr-2025 | may–dic 2025 | 2023 y 2024 | may-2024 a abr-2025 |
| Secundario | 30-abr-2024 | may–dic 2024 | 2023 | may-2023 a abr-2024 |

- El informe usa estacionalidad 2024–2025 con corte abr-2026. Ese escenario no se puede evaluar (may–dic 2026
  no existe aún) y en el pliegue principal no se puede usar 2025 sin mirar el horizonte, por eso se usan los
  años completos anteriores al corte. El secundario solo tiene 2023 (los datos empiezan en ene-2023), un año
  con volumen mucho menor y más irregular.
- Bases: **ingenuo estacional** = mismo mes del año anterior; **promedio 12M plano** = pieza promedio sin
  estacionalidad, al precio 12M.
- Métricas sobre las celdas grupo × mes del horizonte: error total = (Σest − Σreal)/Σreal; MAE = media de
  |est − real|; WAPE = Σ|est − real| / Σreal; sesgo = Σ(est − real)/n (positivo = sobreestima). El MAPE solo se
  calcula a nivel total mensual; en marca y departamento no, porque hay celdas con venta real 0.
- Grupos evaluados: los que tienen venta real o forecast ≠ 0 en el horizonte (principal:
  12 departamentos, 118 marcas; secundario:
  12 departamentos, 116 marcas).
  Si DIVIDE daría vacío (sin ventas en la referencia), el forecast cuenta como 0.
- Las ventas de may–jun 2026 no se usan.

## Pliegue principal: total mensual

| Mes | Real uds | Informe uds | Ingenuo uds | Plano uds | Real $ | Informe $ | Ingenuo $ | Plano $ |
|---|---|---|---|---|---|---|---|---|
| 2025-05 | 1,777 | 1,774 | 1,976 | 1,338 | 1,958,378 | 1,610,690 | 1,235,764 | 1,215,576 |
| 2025-06 | 2,150 | 1,264 | 1,373 | 1,338 | 1,706,932 | 1,148,086 | 1,063,842 | 1,215,576 |
| 2025-07 | 1,339 | 1,022 | 1,072 | 1,338 | 1,923,878 | 928,447 | 944,931 | 1,215,576 |
| 2025-08 | 1,331 | 879 | 849 | 1,338 | 1,380,422 | 798,218 | 966,971 | 1,215,576 |
| 2025-09 | 1,338 | 1,003 | 1,061 | 1,338 | 1,143,604 | 910,953 | 748,056 | 1,215,576 |
| 2025-10 | 1,235 | 1,063 | 1,113 | 1,338 | 1,277,600 | 965,377 | 985,246 | 1,215,576 |
| 2025-11 | 1,215 | 1,241 | 1,079 | 1,338 | 1,368,430 | 1,126,705 | 1,327,827 | 1,215,576 |
| 2025-12 | 4,091 | 3,977 | 3,063 | 1,338 | 5,104,591 | 3,612,065 | 3,093,310 | 1,215,576 |
| **Total** | **14,476** | **12,223** | **11,586** | **10,708** | **15,863,836** | **11,100,540** | **10,365,948** | **9,724,608** |

## Métricas por pliegue, nivel, medida y método

| Pliegue | Nivel | Medida | Método | Celdas | Error total | MAE | WAPE | Sesgo | MAPE |
|---|---|---|---|---|---|---|---|---|---|
| Principal | Total | Unidades | Informe | 8 | -15.6% | 288 | 15.9% | -282 | 17.9% |
| Principal | Total | Unidades | Ingenuo estacional | 8 | -20.0% | 411 | 22.7% | -361 | 21.3% |
| Principal | Total | Unidades | Promedio 12M plano | 8 | -26.0% | 530 | 29.3% | -471 | 18.6% |
| Principal | Total | Importe | Informe | 8 | -30.0% | 595,412 | 30.0% | -595,412 | 29.5% |
| Principal | Total | Importe | Ingenuo estacional | 8 | -34.7% | 687,236 | 34.7% | -687,236 | 31.9% |
| Principal | Total | Importe | Promedio 12M plano | 8 | -38.7% | 785,396 | 39.6% | -767,403 | 26.7% |
| Principal | Departamento | Unidades | Informe | 96 | -15.2% | 48 | 32.1% | -23 | — |
| Principal | Departamento | Unidades | Ingenuo estacional | 96 | -20.0% | 56 | 37.1% | -30 | — |
| Principal | Departamento | Unidades | Promedio 12M plano | 96 | -26.0% | 61 | 40.7% | -39 | — |
| Principal | Departamento | Importe | Informe | 96 | -29.9% | 52,931 | 32.0% | -49,453 | — |
| Principal | Departamento | Importe | Ingenuo estacional | 96 | -34.7% | 65,111 | 39.4% | -57,270 | — |
| Principal | Departamento | Importe | Promedio 12M plano | 96 | -38.7% | 74,121 | 44.9% | -63,950 | — |
| Principal | Marca | Unidades | Informe | 944 | -13.8% | 10 | 65.6% | -2 | — |
| Principal | Marca | Unidades | Ingenuo estacional | 944 | -20.0% | 11 | 69.6% | -3 | — |
| Principal | Marca | Unidades | Promedio 12M plano | 944 | -26.0% | 9 | 60.9% | -4 | — |
| Principal | Marca | Importe | Informe | 944 | -26.0% | 11,694 | 69.6% | -4,370 | — |
| Principal | Marca | Importe | Ingenuo estacional | 944 | -34.7% | 12,423 | 73.9% | -5,824 | — |
| Principal | Marca | Importe | Promedio 12M plano | 944 | -38.7% | 11,345 | 67.5% | -6,503 | — |
| Secundario | Total | Unidades | Informe | 8 | -27.9% | 584 | 40.3% | -403 | 41.2% |
| Secundario | Total | Unidades | Ingenuo estacional | 8 | -52.1% | 755 | 52.1% | -755 | 57.1% |
| Secundario | Total | Unidades | Promedio 12M plano | 8 | -43.0% | 623 | 43.0% | -623 | 33.6% |
| Secundario | Total | Importe | Informe | 8 | -44.0% | 570,455 | 44.0% | -570,455 | 51.4% |
| Secundario | Total | Importe | Ingenuo estacional | 8 | -62.1% | 804,500 | 62.1% | -804,500 | 67.1% |
| Secundario | Total | Importe | Promedio 12M plano | 8 | -55.8% | 722,869 | 55.8% | -722,869 | 47.9% |
| Secundario | Departamento | Unidades | Informe | 96 | -27.6% | 70 | 58.0% | -33 | — |
| Secundario | Departamento | Unidades | Ingenuo estacional | 96 | -52.1% | 81 | 66.7% | -63 | — |
| Secundario | Departamento | Unidades | Promedio 12M plano | 96 | -43.0% | 68 | 56.1% | -52 | — |
| Secundario | Departamento | Importe | Informe | 96 | -43.4% | 51,900 | 48.1% | -46,839 | — |
| Secundario | Departamento | Importe | Ingenuo estacional | 96 | -62.1% | 70,923 | 65.7% | -67,042 | — |
| Secundario | Departamento | Importe | Promedio 12M plano | 96 | -55.8% | 63,592 | 58.9% | -60,239 | — |
| Secundario | Marca | Unidades | Informe | 928 | -29.5% | 12 | 92.2% | -4 | — |
| Secundario | Marca | Unidades | Ingenuo estacional | 928 | -52.1% | 10 | 79.6% | -7 | — |
| Secundario | Marca | Unidades | Promedio 12M plano | 928 | -43.0% | 8 | 64.9% | -5 | — |
| Secundario | Marca | Importe | Informe | 928 | -49.1% | 8,649 | 77.4% | -5,490 | — |
| Secundario | Marca | Importe | Ingenuo estacional | 928 | -62.1% | 8,616 | 77.1% | -6,935 | — |
| Secundario | Marca | Importe | Promedio 12M plano | 928 | -55.8% | 8,044 | 72.0% | -6,232 | — |

## Quién gana (WAPE más bajo)

| Pliegue | Nivel | Medida | WAPE Informe | WAPE Ingenuo estacional | WAPE Promedio 12M plano | Gana (WAPE) | Informe < Ingenuo |
|---|---|---|---|---|---|---|---|
| Principal | Total | Unidades | 15.9% | 22.7% | 29.3% | Informe | Sí |
| Principal | Total | Importe | 30.0% | 34.7% | 39.6% | Informe | Sí |
| Principal | Departamento | Unidades | 32.1% | 37.1% | 40.7% | Informe | Sí |
| Principal | Departamento | Importe | 32.0% | 39.4% | 44.9% | Informe | Sí |
| Principal | Marca | Unidades | 65.6% | 69.6% | 60.9% | Promedio 12M plano | Sí |
| Principal | Marca | Importe | 69.6% | 73.9% | 67.5% | Promedio 12M plano | Sí |
| Secundario | Total | Unidades | 40.3% | 52.1% | 43.0% | Informe | Sí |
| Secundario | Total | Importe | 44.0% | 62.1% | 55.8% | Informe | Sí |
| Secundario | Departamento | Unidades | 58.0% | 66.7% | 56.1% | Promedio 12M plano | Sí |
| Secundario | Departamento | Importe | 48.1% | 65.7% | 58.9% | Informe | Sí |
| Secundario | Marca | Unidades | 92.2% | 79.6% | 64.9% | Promedio 12M plano | No |
| Secundario | Marca | Importe | 77.4% | 77.1% | 72.0% | Promedio 12M plano | No |

## Lectura

- **Total y departamento: el método del informe gana** en los dos pliegues y supera al ingenuo estacional en
  unidades e importe (principal, total: WAPE uds 15.9% vs
  22.7% ingenuo y 29.3% plano;
  importe 30.0% vs 34.7% y
  39.6%). Única excepción: departamento × unidades del secundario, donde
  el plano queda apenas por delante (56.1% vs
  58.0%). La estacionalidad aporta: capta el pico de diciembre que el
  plano no ve.
- **Sesgo a la baja en todos los métodos.** El total del horizonte se subestima
  (-15.6% en uds y -30.0% en importe en el
  principal; -27.9% y -44.0% en el secundario)
  porque las ventas crecieron y el método no tiene tendencia. En importe el error es mayor porque además el
  precio promedio subió: el precio 12M al corte era 908 por unidad y el real de may–dic 2025 fue
  1,096 (+20.7%).
- **Marca: ningún método es fiable** (WAPE 65.6%–92.2%
  en uds para el informe). Gana el promedio plano: probablemente la estacionalidad propia de cada marca, con uno o dos
  años de historia y pocas unidades, amplifica el ruido; en el secundario (solo 2023 de referencia) el informe
  queda incluso detrás del ingenuo. A nivel marca conviene leer el forecast como orden de magnitud.
- Con estacionalidad 2024–2025 (la del informe) la referencia es más reciente y con más volumen que en estos pliegues, pero
  esa configuración no se puede verificar hasta tener may–dic 2026; el sesgo a la baja por crecimiento y
  precio sí aplicaría igual si el negocio sigue creciendo.

