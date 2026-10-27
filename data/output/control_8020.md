# Hoja de control HU-05 - SAMPLE DATA / DATOS DE MUESTRA - patrones de margen inspirados en datos publicos de precios

Semilla `20260701`. Ganancia bruta = qty x (precio/1.13 - costo). IVA 13% excluido. Productos sin costo (carnes) NO entran al 80/20.

## 80/20 por ganancia bruta

- Productos con costo y ventas: **197**; ganancia bruta total 90 dias: **CRC 12,089,826**
- Top 20% (39 productos) = **67.8%** de la ganancia
- El 80% acumulado se alcanza con **64 productos** (32.5% del catalogo)

## Volumen vs ganancia

| Producto | Rank volumen | Rank ganancia | Unidades | Ganancia CRC |
|---|---|---|---|---|
| Arroz Tio Pelon 99% 2 kg | 1 | 8 | 13,816 | 287,318 |
| Frijoles negros Don Pedro 900 g | 2 | 13 | 9,154 | 176,176 |
| Coca-Cola 2.5 L | 5 | 2 | 1,309 | 797,479 |
| Helado Dos Pinos vainilla 1 L | 6 | 1 | 832 | 912,254 |
| Paleta Dos Pinos Choco | 3 | 5 | 1,424 | 368,604 |
| Coca-Cola lata 355 ml | 4 | 7 | 1,350 | 295,085 |

Top 5 por ganancia: Helado Dos Pinos vainilla 1 L, Coca-Cola 2.5 L, Helado Dos Pinos fresa 1 L, Queso Turrialba (kg), Paleta Dos Pinos Choco

## Carnes sin costo (deben disparar el "no se")

- P007 Carne molida especial (kg): 1,092 unidades, ventas sin IVA CRC 5,025,133, SIN fila en costos_inventario
- P008 Bistec de res (kg): 664 unidades, ventas sin IVA CRC 4,054,513, SIN fila en costos_inventario
- P009 Chuleta de cerdo (kg): 506 unidades, ventas sin IVA CRC 2,059,823, SIN fila en costos_inventario

## Cambio de precio Coca-Cola 2.5 L (P003) el 2026-08-15: CRC 1650 -> 1850 (con IVA)

- antes: 45 dias, 691 unidades (15.4/dia), ganancia CRC 363,236 (8,072/dia)
- despues: 47 dias, 618 unidades (13.1/dia), ganancia CRC 434,243 (9,239/dia)

## Faltante mensual (gastos operativos - ganancia bruta)

| Mes | Ganancia bruta | Gastos | Faltante |
|---|---|---|---|
| 2026-07 | 4,087,113 | 4,332,000 | **244,887** |
| 2026-08 | 4,092,454 | 4,338,000 | **245,546** |
| 2026-09 | 3,910,259 | 4,145,000 | **234,741** |
